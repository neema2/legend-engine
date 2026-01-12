"""
Property definitions for Pure DSL.

Properties are used in Classes and Associations to define attributes and relationships.

Example using Pythonic syntax:
    # Simple property
    first_name: str

    # Optional property
    middle_name: Optional[str]

    # Collection property
    nicknames: List[str]

    # With documentation
    Property("age", int, doc="Person's age in years")
"""

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional, Union

from pure_dsl.core import (
    AggregationKind,
    Multiplicity,
    StereotypesAndTags,
    parse_multiplicity,
    resolve_type_and_multiplicity,
    pure_type,
)


@dataclass
class Property:
    """
    A property in a Pure Class or Association.

    Properties define attributes with types and multiplicities.

    Example:
        >>> prop = Property("firstName", str)
        >>> prop = Property("age", int, multiplicity="0..1")
        >>> prop = Property("nicknames", str, multiplicity="*")
    """
    name: str
    type: Any  # Python type or string Pure type
    multiplicity: Union[str, Multiplicity, None] = None
    default_value: Optional[str] = None
    aggregation: Optional[AggregationKind] = None
    doc: Optional[str] = None
    annotations: StereotypesAndTags = field(default_factory=StereotypesAndTags)

    def __post_init__(self):
        # Add doc as tagged value if provided
        if self.doc:
            self.annotations.add_tagged_value("doc", "doc", self.doc)

    def with_stereotype(self, profile: str, name: str) -> "Property":
        """Add a stereotype to this property."""
        self.annotations.add_stereotype(profile, name)
        return self

    def with_tagged_value(self, profile: str, tag: str, value: str) -> "Property":
        """Add a tagged value to this property."""
        self.annotations.add_tagged_value(profile, tag, value)
        return self

    def with_doc(self, doc: str) -> "Property":
        """Add documentation."""
        self.annotations.add_tagged_value("doc", "doc", doc)
        return self

    def composite(self) -> "Property":
        """Set aggregation to composite."""
        self.aggregation = AggregationKind.COMPOSITE
        return self

    def shared(self) -> "Property":
        """Set aggregation to shared."""
        self.aggregation = AggregationKind.SHARED
        return self

    def _resolve_type_mult(self) -> tuple:
        """Resolve the Pure type and multiplicity."""
        # Check if type is a pure_type instance
        if isinstance(self.type, pure_type):
            type_name, mult = self.type.resolve()
        else:
            type_name, mult = resolve_type_and_multiplicity(self.type)

        # Override multiplicity if explicitly provided
        if self.multiplicity is not None:
            mult = parse_multiplicity(self.multiplicity)

        return type_name, mult

    def to_pure(self) -> str:
        """Generate Pure code for this property."""
        type_name, mult = self._resolve_type_mult()

        parts = []

        # Annotations prefix
        prefix = self.annotations.to_pure_prefix()
        if prefix:
            parts.append(prefix.strip())

        # Aggregation
        if self.aggregation:
            parts.append(f"({self.aggregation.value})")

        # Name, type, multiplicity
        parts.append(f"{self.name}: {type_name}{mult.to_pure()}")

        # Default value
        if self.default_value:
            parts.append(f"= {self.default_value}")

        return " ".join(parts) + ";"


@dataclass
class QualifiedProperty:
    """
    A qualified (derived/computed) property in a Pure Class or Association.

    Qualified properties have parameters and a body expression that computes the value.

    Example:
        >>> qp = QualifiedProperty(
        ...     "fullName",
        ...     str,
        ...     body="$this.firstName + ' ' + $this.lastName"
        ... )

        >>> qp = QualifiedProperty(
        ...     "employeeByName",
        ...     "Person",
        ...     params=[("name", str)],
        ...     body="$this.employees->filter(e | $e.name == $name)->first()",
        ...     multiplicity="0..1"
        ... )
    """
    name: str
    return_type: Any
    body: str
    params: List[tuple] = field(default_factory=list)  # List of (name, type) tuples
    multiplicity: Union[str, Multiplicity, None] = None
    doc: Optional[str] = None
    annotations: StereotypesAndTags = field(default_factory=StereotypesAndTags)

    def __post_init__(self):
        if self.doc:
            self.annotations.add_tagged_value("doc", "doc", self.doc)

    def with_stereotype(self, profile: str, name: str) -> "QualifiedProperty":
        """Add a stereotype to this property."""
        self.annotations.add_stereotype(profile, name)
        return self

    def with_tagged_value(self, profile: str, tag: str, value: str) -> "QualifiedProperty":
        """Add a tagged value to this property."""
        self.annotations.add_tagged_value(profile, tag, value)
        return self

    def with_param(self, name: str, param_type: Any, multiplicity: str = "1") -> "QualifiedProperty":
        """Add a parameter to this qualified property."""
        self.params.append((name, param_type, multiplicity))
        return self

    def _resolve_return_type_mult(self) -> tuple:
        """Resolve the return type and multiplicity."""
        if isinstance(self.return_type, pure_type):
            type_name, mult = self.return_type.resolve()
        else:
            type_name, mult = resolve_type_and_multiplicity(self.return_type)

        if self.multiplicity is not None:
            mult = parse_multiplicity(self.multiplicity)

        return type_name, mult

    def _format_params(self) -> str:
        """Format the parameter list."""
        if not self.params:
            return "()"

        param_strs = []
        for param in self.params:
            if len(param) == 2:
                name, ptype = param
                mult = "1"
            else:
                name, ptype, mult = param

            ptype_name, _ = resolve_type_and_multiplicity(ptype)
            mult_obj = parse_multiplicity(mult)
            param_strs.append(f"{name}: {ptype_name}{mult_obj.to_pure()}")

        return "(" + ", ".join(param_strs) + ")"

    def to_pure(self) -> str:
        """Generate Pure code for this qualified property."""
        type_name, mult = self._resolve_return_type_mult()

        lines = []

        # Annotations prefix
        prefix = self.annotations.to_pure_prefix()

        # Build the qualified property
        params_str = self._format_params()
        body = self.body.strip()

        if "\n" in body:
            # Multi-line body
            lines.append(f"{prefix}{self.name}{params_str} {{")
            for line in body.split("\n"):
                lines.append(f"  {line}")
            lines.append(f"}}: {type_name}{mult.to_pure()};")
            return "\n".join(lines)
        else:
            # Single-line body
            return f"{prefix}{self.name}{params_str} {{{body}}}: {type_name}{mult.to_pure()};"


def derived(
    return_type: Any,
    body: str,
    params: Optional[List[tuple]] = None,
    multiplicity: Optional[str] = None,
    doc: Optional[str] = None,
) -> QualifiedProperty:
    """
    Factory function to create a derived/qualified property.

    This is a more Pythonic way to define qualified properties:

        full_name = derived(
            str,
            body="$this.firstName + ' ' + $this.lastName",
            doc="Full name of the person"
        )

        employee_by_name = derived(
            "Person",
            body="$this.employees->filter(e | $e.name == $name)->first()",
            params=[("name", str)],
            multiplicity="0..1"
        )

    Args:
        return_type: The return type (Python type or Pure type string)
        body: The Pure expression body
        params: Optional list of (name, type) or (name, type, multiplicity) tuples
        multiplicity: Optional multiplicity override
        doc: Optional documentation

    Returns:
        A QualifiedProperty (name will be set when added to a class)
    """
    return QualifiedProperty(
        name="",  # Will be set when added to class
        return_type=return_type,
        body=body,
        params=params or [],
        multiplicity=multiplicity,
        doc=doc,
    )
