"""
Function definitions for Pure DSL.

Functions define reusable operations with typed parameters and return types.

Example using builder:
    greet = Function("greet") \\
        .with_param("name", str) \\
        .returns(str) \\
        .body("'Hello, ' + $name + '!'")

Example using decorator:
    @pure_function
    def greet(name: str) -> str:
        '''Greet someone by name.'''
        return "'Hello, ' + $name + '!'"
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union, get_type_hints

from pure_dsl.core import (
    Multiplicity,
    PureElement,
    StereotypesAndTags,
    parse_multiplicity,
    resolve_type_and_multiplicity,
)


@dataclass
class Parameter:
    """
    A function parameter.

    Example:
        >>> param = Parameter("name", str)
        >>> param = Parameter("ages", int, "*")
    """
    name: str
    type: Any
    multiplicity: Union[str, Multiplicity, None] = None

    def to_pure(self) -> str:
        """Generate Pure parameter syntax."""
        type_name, mult = resolve_type_and_multiplicity(self.type)

        if self.multiplicity is not None:
            mult = parse_multiplicity(self.multiplicity)

        return f"{self.name}: {type_name}{mult.to_pure()}"


class Function(PureElement):
    """
    A Pure Function definition.

    Functions define reusable operations with parameters and return types.

    Example:
        >>> fn = Function("greet")
        >>> fn.with_param("name", str)
        >>> fn.returns(str)
        >>> fn.body("'Hello, ' + $name")
        >>> print(fn.to_pure())
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize a Function.

        Args:
            name: Function name (can be qualified)
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._params: List[Parameter] = []
        self._return_type: Optional[str] = None
        self._return_multiplicity: Multiplicity = Multiplicity.one()
        self._body: Optional[str] = None
        self._is_native: bool = False

    def with_param(
        self,
        name: str,
        param_type: Any,
        multiplicity: Optional[str] = None,
    ) -> "Function":
        """
        Add a parameter to this function.

        Args:
            name: Parameter name
            param_type: Parameter type
            multiplicity: Optional multiplicity override

        Returns:
            self for chaining
        """
        self._params.append(Parameter(name, param_type, multiplicity))
        return self

    def with_params(self, *params: Tuple[str, Any]) -> "Function":
        """
        Add multiple parameters.

        Args:
            *params: Tuples of (name, type) or (name, type, multiplicity)

        Returns:
            self for chaining
        """
        for param in params:
            if len(param) == 2:
                name, ptype = param
                self._params.append(Parameter(name, ptype))
            else:
                name, ptype, mult = param
                self._params.append(Parameter(name, ptype, mult))
        return self

    def returns(
        self,
        return_type: Any,
        multiplicity: Optional[str] = None,
    ) -> "Function":
        """
        Set the return type.

        Args:
            return_type: Return type
            multiplicity: Optional multiplicity override

        Returns:
            self for chaining
        """
        type_name, mult = resolve_type_and_multiplicity(return_type)
        self._return_type = type_name

        if multiplicity is not None:
            self._return_multiplicity = parse_multiplicity(multiplicity)
        else:
            self._return_multiplicity = mult

        return self

    def body(self, code: str) -> "Function":
        """
        Set the function body.

        Args:
            code: Pure expression code

        Returns:
            self for chaining
        """
        self._body = code
        return self

    def native(self) -> "Function":
        """
        Mark this function as native (no body).

        Returns:
            self for chaining
        """
        self._is_native = True
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Function."""
        lines = []

        # Function declaration
        prefix = self._annotations_prefix()

        if self._is_native:
            decl = f"native function {prefix}{self.qualified_name}"
        else:
            decl = f"function {prefix}{self.qualified_name}"

        lines.append(decl)

        # Parameters
        params_str = ", ".join(p.to_pure() for p in self._params)

        # Return type
        return_str = f"{self._return_type}{self._return_multiplicity.to_pure()}"

        # Combine signature
        signature = f"({params_str}): {return_str}"

        if self._is_native:
            return lines[0] + signature + ";"

        lines[0] = lines[0] + signature

        # Body
        lines.append("{")
        if self._body:
            body = self._body.strip()
            if "\n" in body:
                for line in body.split("\n"):
                    lines.append("  " + line)
            else:
                lines.append("  " + body)
        lines.append("}")

        return "\n".join(lines)


def pure_function(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    package: Optional[str] = None,
    native: bool = False,
) -> Union[Callable, Function]:
    """
    Decorator to create a Pure Function from a Python function.

    The function body should return a string containing the Pure expression.

    Example:
        @pure_function
        def greet(name: str) -> str:
            '''Greet someone by name.'''
            return "'Hello, ' + $name + '!'"

        @pure_function(package="my::utils")
        def add(a: int, b: int) -> int:
            return "$a + $b"

    Args:
        func: The function to decorate
        name: Optional Pure function name override
        package: Optional package path
        native: If True, creates a native function declaration

    Returns:
        A Function instance or decorator function
    """
    def decorator(func: Callable) -> Function:
        # Get function name
        fn_name = name or func.__name__

        # Create Pure Function
        pure_fn = Function(fn_name, package)

        # Add documentation
        if func.__doc__:
            pure_fn.with_doc(func.__doc__.strip())

        # Get type hints
        try:
            hints = get_type_hints(func)
        except Exception:
            hints = getattr(func, "__annotations__", {})

        # Get return type
        return_hint = hints.pop("return", None)
        if return_hint:
            pure_fn.returns(return_hint)
        else:
            pure_fn.returns("Any", "*")

        # Add parameters (in order)
        import inspect
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param_name in hints:
                pure_fn.with_param(param_name, hints[param_name])
            else:
                pure_fn.with_param(param_name, "Any")

        # Get body by calling the function with None values
        # The function should return the Pure expression string
        if native:
            pure_fn.native()
        else:
            try:
                # Try to call with appropriate placeholders
                args = [None] * len(sig.parameters)
                body = func(*args)
                if isinstance(body, str):
                    pure_fn.body(body)
            except Exception:
                # If calling fails, try to get from source
                pass

        # Store reference
        func._pure_function = pure_fn

        return pure_fn

    if func is None:
        return decorator
    return decorator(func)


def lambda_expr(
    params: List[Tuple[str, Any]],
    body: str,
) -> str:
    """
    Create a Pure lambda expression string.

    Example:
        >>> lambda_expr([("x", int)], "$x + 1")
        '{x: Integer[1] | $x + 1}'

        >>> lambda_expr([("a", str), ("b", str)], "$a + $b")
        '{a: String[1], b: String[1] | $a + $b}'

    Args:
        params: List of (name, type) tuples
        body: Lambda body expression

    Returns:
        Pure lambda expression string
    """
    param_strs = []
    for name, ptype in params:
        type_name, mult = resolve_type_and_multiplicity(ptype)
        param_strs.append(f"{name}: {type_name}{mult.to_pure()}")

    return "{" + ", ".join(param_strs) + " | " + body + "}"
