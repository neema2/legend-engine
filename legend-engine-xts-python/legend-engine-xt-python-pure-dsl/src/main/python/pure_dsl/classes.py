"""
Class definitions for Pure DSL.

Classes are the primary domain modeling construct in Pure.

There are two ways to define classes:

1. Using the Class builder (imperative style):

    person = Class("Person") \\
        .with_property("firstName", str) \\
        .with_property("lastName", str) \\
        .with_property("age", int, multiplicity="0..1") \\
        .with_derived("fullName", str, "$this.firstName + ' ' + $this.lastName")

2. Using the @pure_class decorator (declarative style):

    @pure_class
    class Person:
        '''A person in the system.'''
        first_name: str
        last_name: str
        age: Optional[int]

        @derived
        def full_name(self) -> str:
            return "$this.firstName + ' ' + $this.lastName"
"""

import re
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Type, Union, get_type_hints

from pure_dsl.core import (
    AggregationKind,
    Multiplicity,
    PureElement,
    StereotypesAndTags,
    indent,
    parse_multiplicity,
    resolve_type_and_multiplicity,
    pure_type,
)
from pure_dsl.property import Property, QualifiedProperty
from pure_dsl.constraint import Constraint


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class Class(PureElement):
    """
    A Pure Class definition.

    Classes define domain entities with properties, constraints, and behaviors.

    Example:
        >>> person = Class("Person")
        >>> person.with_property("firstName", str)
        >>> person.with_property("lastName", str)
        >>> person.extends("Entity")
        >>> print(person.to_pure())
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize a Class.

        Args:
            name: Class name (can be qualified like "my::package::Person")
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._extends: List[str] = []
        self._properties: List[Property] = []
        self._qualified_properties: List[QualifiedProperty] = []
        self._constraints: List[Constraint] = []

    def extends(self, *superclasses: Union[str, "Class"]) -> "Class":
        """
        Add superclasses to extend.

        Args:
            *superclasses: Class names or Class instances to extend

        Returns:
            self for chaining
        """
        for sc in superclasses:
            if isinstance(sc, Class):
                self._extends.append(sc.qualified_name)
            else:
                self._extends.append(sc)
        return self

    def with_property(
        self,
        name: str,
        prop_type: Any,
        multiplicity: Optional[str] = None,
        default: Optional[str] = None,
        aggregation: Optional[AggregationKind] = None,
        doc: Optional[str] = None,
    ) -> "Class":
        """
        Add a property to this class.

        Args:
            name: Property name (will be converted to camelCase if snake_case)
            prop_type: Python type or Pure type string
            multiplicity: Optional multiplicity override
            default: Optional default value expression
            aggregation: Optional aggregation kind
            doc: Optional documentation

        Returns:
            self for chaining
        """
        # Convert snake_case to camelCase
        pure_name = _snake_to_camel(name) if "_" in name else name

        prop = Property(
            name=pure_name,
            type=prop_type,
            multiplicity=multiplicity,
            default_value=default,
            aggregation=aggregation,
            doc=doc,
        )
        self._properties.append(prop)
        return self

    def with_derived(
        self,
        name: str,
        return_type: Any,
        body: str,
        params: Optional[List[tuple]] = None,
        multiplicity: Optional[str] = None,
        doc: Optional[str] = None,
    ) -> "Class":
        """
        Add a derived (qualified) property to this class.

        Args:
            name: Property name
            return_type: Return type
            body: Pure expression body
            params: Optional list of (name, type) or (name, type, mult) tuples
            multiplicity: Optional multiplicity override
            doc: Optional documentation

        Returns:
            self for chaining
        """
        pure_name = _snake_to_camel(name) if "_" in name else name

        qp = QualifiedProperty(
            name=pure_name,
            return_type=return_type,
            body=body,
            params=params or [],
            multiplicity=multiplicity,
            doc=doc,
        )
        self._qualified_properties.append(qp)
        return self

    def with_constraint(
        self,
        expression: str,
        name: Optional[str] = None,
        message: Optional[str] = None,
    ) -> "Class":
        """
        Add a constraint to this class.

        Args:
            expression: Constraint expression
            name: Optional constraint name
            message: Optional error message expression

        Returns:
            self for chaining
        """
        self._constraints.append(Constraint(
            function=expression,
            name=name,
            message=message,
        ))
        return self

    def add_property(self, prop: Property) -> "Class":
        """Add a pre-configured Property."""
        self._properties.append(prop)
        return self

    def add_qualified_property(self, qp: QualifiedProperty) -> "Class":
        """Add a pre-configured QualifiedProperty."""
        self._qualified_properties.append(qp)
        return self

    def add_constraint(self, constraint: Constraint) -> "Class":
        """Add a pre-configured Constraint."""
        self._constraints.append(constraint)
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Class."""
        lines = []

        # Class declaration
        prefix = self._annotations_prefix()
        decl = f"Class {prefix}{self.qualified_name}"

        # Extends clause
        if self._extends:
            decl += " extends " + ", ".join(self._extends)

        lines.append(decl)

        # Constraints
        if self._constraints:
            lines.append("[")
            constraint_strs = []
            for c in self._constraints:
                c_str = c.to_pure()
                # Indent multiline constraints
                if "\n" in c_str:
                    c_lines = c_str.split("\n")
                    c_str = "\n".join("  " + line for line in c_lines)
                else:
                    c_str = "  " + c_str
                constraint_strs.append(c_str)
            lines.append(",\n".join(constraint_strs))
            lines.append("]")

        # Body
        lines.append("{")

        # Properties
        for prop in self._properties:
            lines.append("  " + prop.to_pure())

        # Qualified properties
        for qp in self._qualified_properties:
            qp_str = qp.to_pure()
            # Indent each line
            for line in qp_str.split("\n"):
                lines.append("  " + line)

        lines.append("}")

        return "\n".join(lines)


def pure_class(
    cls: Optional[Type] = None,
    *,
    name: Optional[str] = None,
    package: Optional[str] = None,
    extends: Optional[List[str]] = None,
) -> Union[Callable, Class]:
    """
    Decorator to create a Pure Class from a Python class definition.

    This allows you to define Pure classes using natural Python syntax:

        @pure_class
        class Person:
            '''A person in the system.'''
            first_name: str
            last_name: str
            age: Optional[int]
            addresses: List[str]

    The decorator will:
    - Convert snake_case property names to camelCase
    - Map Python types to Pure types
    - Handle Optional[X] as X[0..1]
    - Handle List[X] as X[*]
    - Use docstrings for documentation

    Args:
        cls: The class to decorate
        name: Optional Pure class name override
        package: Optional package path
        extends: Optional list of superclass names

    Returns:
        A Class instance or decorator function
    """
    def decorator(cls: Type) -> Class:
        # Get class name
        class_name = name or cls.__name__

        # Create Pure Class
        pure_cls = Class(class_name, package)

        # Add documentation from docstring
        if cls.__doc__:
            pure_cls.with_doc(cls.__doc__.strip())

        # Add extends
        if extends:
            pure_cls.extends(*extends)

        # Get type hints
        try:
            hints = get_type_hints(cls)
        except Exception:
            hints = getattr(cls, "__annotations__", {})

        # Process attributes
        for attr_name, attr_type in hints.items():
            if attr_name.startswith("_"):
                continue

            # Convert snake_case to camelCase
            pure_name = _snake_to_camel(attr_name)

            # Check if it's a qualified property (defined as a method)
            method = getattr(cls, attr_name, None)
            if callable(method) and hasattr(method, "_pure_derived"):
                # It's a derived property
                qp = QualifiedProperty(
                    name=pure_name,
                    return_type=method._pure_return_type,
                    body=method._pure_body,
                    params=getattr(method, "_pure_params", []),
                    multiplicity=getattr(method, "_pure_multiplicity", None),
                    doc=method.__doc__,
                )
                pure_cls.add_qualified_property(qp)
            else:
                # Regular property
                type_name, mult = resolve_type_and_multiplicity(attr_type)

                # Check for default value
                default_val = getattr(cls, attr_name, None)
                default_str = None
                if default_val is not None and not callable(default_val):
                    if isinstance(default_val, str):
                        default_str = f"'{default_val}'"
                    elif isinstance(default_val, bool):
                        default_str = "true" if default_val else "false"
                    elif isinstance(default_val, (int, float)):
                        default_str = str(default_val)
                    elif isinstance(default_val, list):
                        items = []
                        for item in default_val:
                            if isinstance(item, str):
                                items.append(f"'{item}'")
                            else:
                                items.append(str(item))
                        default_str = "[" + ", ".join(items) + "]"

                prop = Property(
                    name=pure_name,
                    type=type_name,
                    multiplicity=mult,
                    default_value=default_str,
                )
                pure_cls.add_property(prop)

        # Process methods for derived properties
        for method_name in dir(cls):
            if method_name.startswith("_"):
                continue
            method = getattr(cls, method_name)
            if callable(method) and hasattr(method, "_pure_derived"):
                pure_name = _snake_to_camel(method_name)
                qp = QualifiedProperty(
                    name=pure_name,
                    return_type=method._pure_return_type,
                    body=method._pure_body,
                    params=getattr(method, "_pure_params", []),
                    multiplicity=getattr(method, "_pure_multiplicity", None),
                    doc=method.__doc__,
                )
                pure_cls.add_qualified_property(qp)

        # Store reference back to Pure class
        cls._pure_class = pure_cls
        cls._pure_name = pure_cls.qualified_name

        return pure_cls

    if cls is None:
        return decorator
    return decorator(cls)


def derived_property(
    return_type: Any,
    body: str,
    params: Optional[List[tuple]] = None,
    multiplicity: Optional[str] = None,
) -> Callable:
    """
    Decorator to mark a method as a derived (qualified) property.

    Use this with @pure_class to define computed properties:

        @pure_class
        class Person:
            first_name: str
            last_name: str

            @derived_property(str, "$this.firstName + ' ' + $this.lastName")
            def full_name(self):
                '''The person's full name.'''
                pass

    Args:
        return_type: Return type
        body: Pure expression body
        params: Optional list of (name, type) tuples for parameters
        multiplicity: Optional multiplicity

    Returns:
        Decorator function
    """
    def decorator(method: Callable) -> Callable:
        method._pure_derived = True
        method._pure_return_type = return_type
        method._pure_body = body
        method._pure_params = params or []
        method._pure_multiplicity = multiplicity
        return method
    return decorator
