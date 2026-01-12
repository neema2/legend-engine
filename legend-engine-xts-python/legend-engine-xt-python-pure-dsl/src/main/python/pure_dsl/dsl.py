"""
Type-safe Pure DSL using Python class syntax.

This module provides a Pythonic way to define Pure constructs using
native Python class syntax with type annotations.

Example:
    from pure_dsl import PureClass, PureEnum, derived, constraint
    from typing import Optional, List

    class OrderStatus(PureEnum):
        NEW = "NEW"
        PENDING = "PENDING"
        FILLED = "FILLED"
        CANCELLED = "CANCELLED"

    class Person(PureClass):
        '''A person in the system.'''
        first_name: str
        last_name: str
        age: Optional[int]
        emails: List[str]

        @derived
        def full_name(this) -> str:
            return this.first_name + " " + this.last_name

        @constraint
        def valid_age(this) -> bool:
            return this.age >= 0
"""

from __future__ import annotations
import inspect
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)
from dataclasses import dataclass, field
from enum import Enum as PyEnum

from pure_dsl.types import (
    Expr,
    This,
    Many,
    OneMany,
    ZeroOne,
    resolve_pure_type,
)

T = TypeVar("T")


# =============================================================================
# Property Descriptors
# =============================================================================

@dataclass
class PropertyDef:
    """Definition of a Pure property."""
    name: str
    python_type: Any
    pure_type: str
    multiplicity: str
    doc: Optional[str] = None
    default: Optional[str] = None
    is_derived: bool = False
    body: Optional[str] = None
    params: List[Tuple[str, str, str]] = field(default_factory=list)
    stereotypes: List[Tuple[str, str]] = field(default_factory=list)
    tags: List[Tuple[str, str, str]] = field(default_factory=list)

    def to_pure(self) -> str:
        """Generate Pure code for this property."""
        lines = []

        # Annotations
        ann_parts = []
        if self.stereotypes:
            st_refs = ", ".join(f"{p}.{n}" for p, n in self.stereotypes)
            ann_parts.append(f"<<{st_refs}>>")
        if self.tags:
            tv_refs = ", ".join(f"{p}.{t} = '{v}'" for p, t, v in self.tags)
            ann_parts.append(f"{{{tv_refs}}}")

        prefix = " ".join(ann_parts) + " " if ann_parts else ""

        if self.is_derived:
            # Qualified property
            params_str = ""
            if self.params:
                params_str = ", ".join(f"{n}: {t}{m}" for n, t, m in self.params)
            lines.append(f"{prefix}{self.name}({params_str}) {{{self.body}}}: {self.pure_type}{self.multiplicity};")
        else:
            # Simple property
            default_str = f" = {self.default}" if self.default else ""
            lines.append(f"{prefix}{self.name}: {self.pure_type}{self.multiplicity}{default_str};")

        return "\n".join(lines)


@dataclass
class ConstraintDef:
    """Definition of a Pure constraint."""
    name: Optional[str]
    expression: str
    message: Optional[str] = None
    enforcement: Optional[str] = None  # "Error" or "Warn"
    owner: Optional[str] = None
    external_id: Optional[str] = None

    def to_pure(self) -> str:
        """Generate Pure code for this constraint."""
        if self.message is None and self.enforcement is None and self.owner is None:
            # Simple constraint
            if self.name:
                return f"{self.name}: {self.expression}"
            return self.expression
        else:
            # Complex constraint
            lines = [f"{self.name or 'constraint'}"]
            lines.append("(")
            if self.owner:
                lines.append(f"  ~owner: {self.owner}")
            if self.external_id:
                lines.append(f"  ~externalId: '{self.external_id}'")
            lines.append(f"  ~function: {self.expression}")
            if self.enforcement:
                lines.append(f"  ~enforcementLevel: {self.enforcement}")
            if self.message:
                lines.append(f"  ~message: {self.message}")
            lines.append(")")
            return "\n".join(lines)


# =============================================================================
# Decorators for Methods
# =============================================================================

def derived(
    func: Callable = None,
    *,
    params: Optional[List[Tuple[str, Any]]] = None,
) -> Callable:
    """
    Decorator to mark a method as a derived (qualified) property.

    The method should take `this` as the first parameter and return
    an expression that will be converted to Pure.

    Example:
        class Person(PureClass):
            first_name: str
            last_name: str

            @derived
            def full_name(this) -> str:
                return this.first_name + " " + this.last_name

            @derived(params=[("prefix", str)])
            def formatted_name(this, prefix) -> str:
                return prefix + " " + this.first_name + " " + this.last_name
    """
    def decorator(fn: Callable) -> Callable:
        fn._is_derived = True
        fn._derived_params = params or []
        return fn

    if func is not None:
        return decorator(func)
    return decorator


def constraint(
    func: Callable = None,
    *,
    message: Optional[str] = None,
    enforcement: Optional[str] = None,
) -> Callable:
    """
    Decorator to mark a method as a constraint.

    The method should take `this` as the first parameter and return
    a boolean expression.

    Example:
        class Person(PureClass):
            age: int

            @constraint
            def valid_age(this) -> bool:
                return this.age >= 0

            @constraint(message="Email must contain @")
            def valid_email(this) -> bool:
                return this.email.contains("@")
    """
    def decorator(fn: Callable) -> Callable:
        fn._is_constraint = True
        fn._constraint_message = message
        fn._constraint_enforcement = enforcement
        return fn

    if func is not None:
        return decorator(func)
    return decorator


# =============================================================================
# Metaclass for Pure Classes
# =============================================================================

class PureClassMeta(type):
    """
    Metaclass for Pure classes.

    This metaclass:
    1. Extracts type annotations and converts them to Pure properties
    2. Processes decorated methods as derived properties or constraints
    3. Stores class metadata for Pure code generation
    """

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        **kwargs,
    ) -> "PureClassMeta":
        # Skip processing for the base PureClass itself
        if name == "PureClass":
            return super().__new__(mcs, name, bases, namespace)

        # Get configuration from class attributes
        package = namespace.pop("__package__", None)
        extends = namespace.pop("__extends__", [])
        doc = namespace.get("__doc__", None)

        # Get annotations (type hints)
        annotations = namespace.get("__annotations__", {})

        # Process properties
        properties: List[PropertyDef] = []
        constraints: List[ConstraintDef] = []
        stereotypes: List[Tuple[str, str]] = []
        tags: List[Tuple[str, str, str]] = []

        for prop_name, prop_type in annotations.items():
            if prop_name.startswith("_"):
                continue

            # Convert snake_case to camelCase
            pure_name = _snake_to_camel(prop_name)

            # Resolve Pure type
            pure_type, mult = resolve_pure_type(prop_type)

            # Check for default value
            default = namespace.get(prop_name)
            default_str = None
            if default is not None and not callable(default):
                default_str = _to_pure_literal(default)

            properties.append(PropertyDef(
                name=pure_name,
                python_type=prop_type,
                pure_type=pure_type,
                multiplicity=mult,
                default=default_str,
            ))

        # Process methods for derived properties and constraints
        for method_name, method in namespace.items():
            if callable(method) and not method_name.startswith("_"):
                if getattr(method, "_is_derived", False):
                    # Derived property
                    pure_name = _snake_to_camel(method_name)

                    # Get return type
                    hints = {}
                    try:
                        hints = get_type_hints(method)
                    except Exception:
                        hints = getattr(method, "__annotations__", {})

                    return_type = hints.get("return", Any)
                    pure_type, mult = resolve_pure_type(return_type)

                    # Get the body by calling with a This proxy
                    this_proxy = This()
                    try:
                        # Get parameters
                        sig = inspect.signature(method)
                        param_names = list(sig.parameters.keys())

                        if len(param_names) == 1:
                            # Just this
                            result = method(this_proxy)
                        else:
                            # Has additional params
                            extra_params = []
                            param_defs = []
                            for pname in param_names[1:]:
                                p_type = hints.get(pname, Any)
                                p_pure_type, p_mult = resolve_pure_type(p_type)
                                extra_params.append(Expr(f"${pname}"))
                                param_defs.append((pname, p_pure_type, p_mult))
                            result = method(this_proxy, *extra_params)

                        if isinstance(result, Expr):
                            body = result.to_pure()
                        else:
                            body = str(result)

                        properties.append(PropertyDef(
                            name=pure_name,
                            python_type=return_type,
                            pure_type=pure_type,
                            multiplicity=mult,
                            is_derived=True,
                            body=body,
                            params=param_defs if len(param_names) > 1 else [],
                        ))
                    except Exception as e:
                        # Fallback: try to extract from source
                        pass

                elif getattr(method, "_is_constraint", False):
                    # Constraint
                    this_proxy = This()
                    try:
                        result = method(this_proxy)
                        if isinstance(result, Expr):
                            expr = result.to_pure()
                        else:
                            expr = str(result)

                        constraints.append(ConstraintDef(
                            name=method_name,
                            expression=expr,
                            message=getattr(method, "_constraint_message", None),
                            enforcement=getattr(method, "_constraint_enforcement", None),
                        ))
                    except Exception:
                        pass

        # Create the class
        cls = super().__new__(mcs, name, bases, namespace)

        # Store metadata
        cls.__pure_name__ = name
        cls.__pure_package__ = package
        cls.__pure_extends__ = extends if isinstance(extends, list) else [extends]
        cls.__pure_doc__ = doc
        cls.__pure_properties__ = properties
        cls.__pure_constraints__ = constraints
        cls.__pure_stereotypes__ = stereotypes
        cls.__pure_tags__ = tags

        return cls

    def to_pure(cls) -> str:
        """Generate Pure code for this class."""
        lines = []

        # Build declaration
        decl_parts = ["Class"]

        # Stereotypes
        if cls.__pure_stereotypes__:
            st_refs = ", ".join(f"{p}.{n}" for p, n in cls.__pure_stereotypes__)
            decl_parts.append(f"<<{st_refs}>>")

        # Tags (including doc)
        tag_parts = []
        if cls.__pure_doc__:
            escaped = cls.__pure_doc__.replace("'", "\\'")
            tag_parts.append(f"doc.doc = '{escaped}'")
        for p, t, v in cls.__pure_tags__:
            tag_parts.append(f"{p}.{t} = '{v}'")
        if tag_parts:
            decl_parts.append("{" + ", ".join(tag_parts) + "}")

        # Name
        if cls.__pure_package__:
            decl_parts.append(f"{cls.__pure_package__}::{cls.__pure_name__}")
        else:
            decl_parts.append(cls.__pure_name__)

        # Extends
        if cls.__pure_extends__:
            extends_str = ", ".join(cls.__pure_extends__)
            decl_parts.append(f"extends {extends_str}")

        lines.append(" ".join(decl_parts))

        # Constraints
        if cls.__pure_constraints__:
            lines.append("[")
            for i, c in enumerate(cls.__pure_constraints__):
                c_str = c.to_pure()
                if "\n" in c_str:
                    for line in c_str.split("\n"):
                        lines.append("  " + line)
                else:
                    lines.append("  " + c_str)
                if i < len(cls.__pure_constraints__) - 1:
                    lines[-1] += ","
            lines.append("]")

        # Body
        lines.append("{")
        for prop in cls.__pure_properties__:
            prop_str = prop.to_pure()
            for line in prop_str.split("\n"):
                lines.append("  " + line)
        lines.append("}")

        return "\n".join(lines)


class PureClass(metaclass=PureClassMeta):
    """
    Base class for defining Pure classes using Python syntax.

    Example:
        class Person(PureClass):
            '''A person in the system.'''
            first_name: str
            last_name: str
            age: Optional[int]

            @derived
            def full_name(this) -> str:
                return this.first_name + " " + this.last_name

            @constraint
            def valid_age(this) -> bool:
                return this.age >= 0
    """

    __package__: ClassVar[Optional[str]] = None
    __extends__: ClassVar[Union[str, List[str]]] = []

    def __init_subclass__(cls, package: str = None, extends: Union[str, List[str]] = None, **kwargs):
        """Handle class inheritance with configuration."""
        super().__init_subclass__(**kwargs)
        if package is not None:
            cls.__pure_package__ = package
        if extends is not None:
            cls.__pure_extends__ = extends if isinstance(extends, list) else [extends]


# =============================================================================
# Pure Enum
# =============================================================================

class PureEnumMeta(type):
    """Metaclass for Pure enums."""

    def __new__(
        mcs,
        name: str,
        bases: Tuple[type, ...],
        namespace: Dict[str, Any],
        **kwargs,
    ) -> "PureEnumMeta":
        if name == "PureEnum":
            return super().__new__(mcs, name, bases, namespace)

        package = namespace.pop("__package__", None)
        doc = namespace.get("__doc__", None)

        # Collect enum values
        values = []
        for attr_name, attr_value in list(namespace.items()):
            if not attr_name.startswith("_") and isinstance(attr_value, str):
                values.append((attr_name, attr_value, None))

        cls = super().__new__(mcs, name, bases, namespace)
        cls.__pure_name__ = name
        cls.__pure_package__ = package
        cls.__pure_doc__ = doc
        cls.__pure_values__ = values

        return cls

    def to_pure(cls) -> str:
        """Generate Pure code for this enum."""
        lines = []

        # Declaration with optional doc
        decl_parts = ["Enum"]
        if cls.__pure_doc__:
            escaped = cls.__pure_doc__.replace("'", "\\'")
            decl_parts.append(f"{{doc.doc = '{escaped}'}}")

        if cls.__pure_package__:
            decl_parts.append(f"{cls.__pure_package__}::{cls.__pure_name__}")
        else:
            decl_parts.append(cls.__pure_name__)

        lines.append(" ".join(decl_parts))
        lines.append("{")

        for i, (name, value, doc) in enumerate(cls.__pure_values__):
            prefix = ""
            if doc:
                prefix = f"{{doc.doc = '{doc}'}} "
            suffix = "," if i < len(cls.__pure_values__) - 1 else ""
            lines.append(f"  {prefix}{name}{suffix}")

        lines.append("}")
        return "\n".join(lines)


class PureEnum(metaclass=PureEnumMeta):
    """
    Base class for defining Pure enums using Python syntax.

    Example:
        class OrderStatus(PureEnum):
            '''Status of an order.'''
            NEW = "NEW"
            PENDING = "PENDING"
            FILLED = "FILLED"
            CANCELLED = "CANCELLED"
    """
    __package__: ClassVar[Optional[str]] = None


# =============================================================================
# Helpers
# =============================================================================

def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    if "_" not in name:
        return name
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _to_pure_literal(value: Any) -> str:
    """Convert Python value to Pure literal."""
    if isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return "[]"
    elif isinstance(value, list):
        items = [_to_pure_literal(v) for v in value]
        return "[" + ", ".join(items) + "]"
    elif isinstance(value, Expr):
        return value.to_pure()
    else:
        return str(value)


# =============================================================================
# Association Builder (for relationships)
# =============================================================================

@dataclass
class AssociationEnd:
    """One end of an association."""
    property_name: str
    target_class: Union[str, Type["PureClass"]]
    multiplicity: str = "[1]"

    def to_pure(self) -> str:
        target = (
            self.target_class.__pure_name__
            if hasattr(self.target_class, "__pure_name__")
            else str(self.target_class)
        )
        return f"{self.property_name}: {target}{self.multiplicity};"


class PureAssociation:
    """
    Define an association between two Pure classes.

    Example:
        class FirmPerson(PureAssociation):
            firm_employees = (Firm, "employees", "[*]")
            person_employer = (Person, "employer", "[0..1]")
    """

    def __init__(
        self,
        name: str,
        end1: Tuple[Type["PureClass"], str, str],
        end2: Tuple[Type["PureClass"], str, str],
        package: str = None,
    ):
        self.name = name
        self.package = package
        self.ends = [
            AssociationEnd(end1[1], end1[0], end1[2]),
            AssociationEnd(end2[1], end2[0], end2[2]),
        ]

    def to_pure(self) -> str:
        """Generate Pure code for this association."""
        lines = []
        qualified = f"{self.package}::{self.name}" if self.package else self.name
        lines.append(f"Association {qualified}")
        lines.append("{")
        for end in self.ends:
            lines.append("  " + end.to_pure())
        lines.append("}")
        return "\n".join(lines)
