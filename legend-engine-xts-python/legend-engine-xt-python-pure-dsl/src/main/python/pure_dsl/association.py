"""
Association definitions for Pure DSL.

Associations define bidirectional relationships between two classes.

Example:
    # Simple association
    firm_employee = Association("FirmEmployee") \\
        .from_class("Firm", "employees", "Person", "*") \\
        .to_class("Person", "firm", "Firm", "0..1")

    # Or using a more Pythonic builder
    firm_employee = association(
        "FirmEmployee",
        ("Firm", "employees", List["Person"]),
        ("Person", "firm", Optional["Firm"])
    )
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Tuple, Union

from pure_dsl.core import (
    AggregationKind,
    Multiplicity,
    PureElement,
    StereotypesAndTags,
    parse_multiplicity,
    resolve_type_and_multiplicity,
)
from pure_dsl.property import Property, QualifiedProperty


@dataclass
class AssociationEnd:
    """
    One end of an Association.

    Each association has exactly two ends, defining the relationship
    from each class's perspective.
    """
    property_name: str
    target_class: str
    multiplicity: Union[str, Multiplicity] = "1"
    aggregation: Optional[AggregationKind] = None
    doc: Optional[str] = None
    annotations: StereotypesAndTags = field(default_factory=StereotypesAndTags)
    default_value: Optional[str] = None

    def to_pure(self) -> str:
        """Generate Pure code for this association end."""
        mult = parse_multiplicity(self.multiplicity)

        parts = []

        # Annotations
        prefix = self.annotations.to_pure_prefix()
        if prefix:
            parts.append(prefix.strip())

        # Aggregation
        if self.aggregation:
            parts.append(f"({self.aggregation.value})")

        # Name and type
        parts.append(f"{self.property_name}: {self.target_class}{mult.to_pure()}")

        # Default value
        if self.default_value:
            parts.append(f"= {self.default_value}")

        return " ".join(parts) + ";"


class Association(PureElement):
    """
    A Pure Association definition.

    Associations define bidirectional relationships between exactly two classes.

    Example:
        >>> assoc = Association("FirmPerson")
        >>> assoc.add_end("employees", "Person", "*")
        >>> assoc.add_end("employer", "Firm", "0..1")
        >>> print(assoc.to_pure())
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize an Association.

        Args:
            name: Association name (can be qualified)
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._ends: List[AssociationEnd] = []
        self._qualified_properties: List[QualifiedProperty] = []

    def add_end(
        self,
        property_name: str,
        target_class: str,
        multiplicity: str = "1",
        aggregation: Optional[AggregationKind] = None,
        doc: Optional[str] = None,
    ) -> "Association":
        """
        Add an association end.

        Args:
            property_name: Name of the property
            target_class: Target class name
            multiplicity: Multiplicity string
            aggregation: Optional aggregation kind
            doc: Optional documentation

        Returns:
            self for chaining
        """
        end = AssociationEnd(
            property_name=property_name,
            target_class=target_class,
            multiplicity=multiplicity,
            aggregation=aggregation,
            doc=doc,
        )
        if doc:
            end.annotations.add_tagged_value("doc", "doc", doc)
        self._ends.append(end)
        return self

    def from_class(
        self,
        source_class: str,
        property_name: str,
        target_class: str,
        multiplicity: str = "1",
    ) -> "Association":
        """
        Define the 'from' side of the association.

        This adds a property to the source class pointing to target class.

        Args:
            source_class: Source class (not stored, just for documentation)
            property_name: Property name as seen from source class
            target_class: Target class name
            multiplicity: Multiplicity

        Returns:
            self for chaining
        """
        return self.add_end(property_name, target_class, multiplicity)

    def to_class(
        self,
        source_class: str,
        property_name: str,
        target_class: str,
        multiplicity: str = "1",
    ) -> "Association":
        """
        Define the 'to' side of the association.

        This adds a property to the source class pointing to target class.

        Args:
            source_class: Source class (not stored, just for documentation)
            property_name: Property name as seen from source class
            target_class: Target class name
            multiplicity: Multiplicity

        Returns:
            self for chaining
        """
        return self.add_end(property_name, target_class, multiplicity)

    def with_qualified_property(
        self,
        name: str,
        return_type: Any,
        body: str,
        params: Optional[List[tuple]] = None,
        multiplicity: Optional[str] = None,
    ) -> "Association":
        """
        Add a qualified property to this association.

        Args:
            name: Property name
            return_type: Return type
            body: Pure expression body
            params: Optional parameters
            multiplicity: Optional multiplicity

        Returns:
            self for chaining
        """
        qp = QualifiedProperty(
            name=name,
            return_type=return_type,
            body=body,
            params=params or [],
            multiplicity=multiplicity,
        )
        self._qualified_properties.append(qp)
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Association."""
        if len(self._ends) != 2 and not self._qualified_properties:
            raise ValueError("Association must have exactly 2 ends")

        lines = []

        # Association declaration
        prefix = self._annotations_prefix()
        lines.append(f"Association {prefix}{self.qualified_name}")
        lines.append("{")

        # Ends
        for end in self._ends:
            lines.append("  " + end.to_pure())

        # Qualified properties
        for qp in self._qualified_properties:
            qp_str = qp.to_pure()
            for line in qp_str.split("\n"):
                lines.append("  " + line)

        lines.append("}")

        return "\n".join(lines)


def association(
    name: str,
    end1: Tuple[str, str, Any],
    end2: Tuple[str, str, Any],
    package: Optional[str] = None,
) -> Association:
    """
    Factory function to create an association with a more Pythonic syntax.

    Example:
        firm_person = association(
            "FirmPerson",
            ("Firm", "employees", List["Person"]),
            ("Person", "employer", Optional["Firm"])
        )

    Args:
        name: Association name
        end1: Tuple of (class_name, property_name, type_with_multiplicity)
        end2: Tuple of (class_name, property_name, type_with_multiplicity)
        package: Optional package

    Returns:
        Association instance
    """
    assoc = Association(name, package)

    for class_name, prop_name, type_hint in [end1, end2]:
        type_name, mult = resolve_type_and_multiplicity(type_hint)
        assoc.add_end(prop_name, type_name, mult.to_pure().strip("[]"))

    return assoc
