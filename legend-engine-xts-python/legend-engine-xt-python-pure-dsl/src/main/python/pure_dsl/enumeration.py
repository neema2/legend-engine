"""
Enumeration definition for Pure DSL.

Enums define a fixed set of values with optional stereotypes and tagged values.

Example:
    status = Enum("my::package::Status") \\
        .with_doc("Order status values") \\
        .with_value("PENDING", doc="Order is pending") \\
        .with_value("PROCESSING") \\
        .with_value("COMPLETED") \\
        .with_value("CANCELLED")

    print(status.to_pure())
"""

from dataclasses import dataclass, field
from typing import List, Optional

from pure_dsl.core import PureElement, StereotypesAndTags


@dataclass
class EnumValue:
    """
    A value within a Pure Enum.

    Enum values can have stereotypes and tagged values.

    Example:
        >>> val = EnumValue("PENDING")
        >>> val.with_doc("Order is pending")
    """
    name: str
    annotations: StereotypesAndTags = field(default_factory=StereotypesAndTags)

    def with_stereotype(self, profile: str, name: str) -> "EnumValue":
        """Add a stereotype to this enum value."""
        self.annotations.add_stereotype(profile, name)
        return self

    def with_tagged_value(self, profile: str, tag: str, value: str) -> "EnumValue":
        """Add a tagged value to this enum value."""
        self.annotations.add_tagged_value(profile, tag, value)
        return self

    def with_doc(self, doc: str) -> "EnumValue":
        """Add documentation using the standard doc profile."""
        return self.with_tagged_value("doc", "doc", doc)

    def to_pure(self) -> str:
        """Generate Pure code for this enum value."""
        prefix = self.annotations.to_pure_prefix()
        return f"{prefix}{self.name}"


class Enum(PureElement):
    """
    A Pure Enum definition.

    Enums define a fixed set of named values with optional annotations.

    Example:
        >>> status = Enum("Status")
        >>> status.with_value("ACTIVE")
        >>> status.with_value("INACTIVE")
        >>> print(status.to_pure())
        Enum Status
        {
          ACTIVE,
          INACTIVE
        }
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize an Enum.

        Args:
            name: Enum name (can be qualified like "my::package::Status")
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._values: List[EnumValue] = []

    def with_value(
        self,
        name: str,
        doc: Optional[str] = None,
    ) -> "Enum":
        """
        Add a value to this enum.

        Args:
            name: Value name
            doc: Optional documentation

        Returns:
            self for chaining
        """
        value = EnumValue(name)
        if doc:
            value.with_doc(doc)
        self._values.append(value)
        return self

    def with_annotated_value(self, value: EnumValue) -> "Enum":
        """
        Add a pre-configured EnumValue.

        Args:
            value: EnumValue instance with annotations

        Returns:
            self for chaining
        """
        self._values.append(value)
        return self

    def with_values(self, *names: str) -> "Enum":
        """
        Add multiple values at once.

        Args:
            *names: Value names

        Returns:
            self for chaining
        """
        for name in names:
            self._values.append(EnumValue(name))
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Enum."""
        prefix = self._annotations_prefix()
        lines = [f"Enum {prefix}{self.qualified_name}"]
        lines.append("{")

        value_strs = []
        for val in self._values:
            value_strs.append(f"  {val.to_pure()}")

        lines.append(",\n".join(value_strs))
        lines.append("}")
        return "\n".join(lines)
