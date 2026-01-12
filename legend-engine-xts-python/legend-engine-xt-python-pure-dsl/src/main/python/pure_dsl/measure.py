"""
Measure definitions for Pure DSL.

Measures define units of measurement with conversion functions.

Example:
    mass = Measure("Mass") \\
        .with_canonical_unit("Gram", "x", "$x") \\
        .with_unit("Kilogram", "x", "$x * 1000") \\
        .with_unit("Pound", "x", "$x * 453.59")

    # Or using a more Pythonic syntax
    mass = Measure("Mass").with_units(
        canonical=("Gram", lambda x: x),
        Kilogram=lambda x: x * 1000,
        Pound=lambda x: x * 453.59,
    )
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple, Union

from pure_dsl.core import PureElement


@dataclass
class Unit:
    """
    A unit within a Measure.

    Each unit has a name and a conversion expression from the canonical unit.
    """
    name: str
    variable: str
    expression: str
    is_canonical: bool = False

    def to_pure(self) -> str:
        """Generate Pure code for this unit."""
        prefix = "*" if self.is_canonical else ""
        return f"{prefix}{self.name}: {self.variable} -> {self.expression};"


@dataclass
class NonConvertibleUnit:
    """
    A non-convertible unit (standalone without conversion).
    """
    name: str

    def to_pure(self) -> str:
        """Generate Pure code for this unit."""
        return f"{self.name};"


class Measure(PureElement):
    """
    A Pure Measure definition.

    Measures define units of measurement with conversion functions.
    One unit is marked as the canonical (base) unit.

    Example:
        >>> mass = Measure("Mass")
        >>> mass.with_canonical_unit("Gram", "x", "$x")
        >>> mass.with_unit("Kilogram", "x", "$x * 1000")
        >>> print(mass.to_pure())
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize a Measure.

        Args:
            name: Measure name (can be qualified)
            package: Optional package override
        """
        # Handle qualified names
        if "::" in name and package is None:
            parts = name.rsplit("::", 1)
            package = parts[0]
            name = parts[1]

        super().__init__(name, package)
        self._units: List[Union[Unit, NonConvertibleUnit]] = []
        self._has_canonical: bool = False

    def with_canonical_unit(
        self,
        name: str,
        variable: str = "x",
        expression: str = "$x",
    ) -> "Measure":
        """
        Add the canonical (base) unit.

        The canonical unit is the base for all conversions.
        Its expression is typically just the identity ($x).

        Args:
            name: Unit name
            variable: Variable name for conversion
            expression: Conversion expression

        Returns:
            self for chaining
        """
        if self._has_canonical:
            raise ValueError("Measure already has a canonical unit")

        self._units.append(Unit(
            name=name,
            variable=variable,
            expression=expression,
            is_canonical=True,
        ))
        self._has_canonical = True
        return self

    def with_unit(
        self,
        name: str,
        variable: str = "x",
        expression: str = "$x",
    ) -> "Measure":
        """
        Add a derived unit.

        The expression defines how to convert from this unit
        to the canonical unit.

        Args:
            name: Unit name
            variable: Variable name for conversion
            expression: Conversion expression

        Returns:
            self for chaining
        """
        self._units.append(Unit(
            name=name,
            variable=variable,
            expression=expression,
            is_canonical=False,
        ))
        return self

    def with_non_convertible_unit(self, name: str) -> "Measure":
        """
        Add a non-convertible unit.

        Non-convertible units have no conversion to other units.

        Args:
            name: Unit name

        Returns:
            self for chaining
        """
        self._units.append(NonConvertibleUnit(name=name))
        return self

    def to_pure(self) -> str:
        """Generate Pure code for this Measure."""
        lines = []

        lines.append(f"Measure {self.qualified_name}")
        lines.append("{")

        for unit in self._units:
            lines.append("  " + unit.to_pure())

        lines.append("}")

        return "\n".join(lines)


def measure(
    name: str,
    canonical: Tuple[str, str],
    units: Optional[dict] = None,
    package: Optional[str] = None,
) -> Measure:
    """
    Factory function to create a Measure with a more Pythonic syntax.

    Example:
        mass = measure(
            "Mass",
            canonical=("Gram", "$x"),
            units={
                "Kilogram": "$x * 1000",
                "Pound": "$x * 453.59",
            }
        )

    Args:
        name: Measure name
        canonical: Tuple of (unit_name, expression) for canonical unit
        units: Optional dict of {unit_name: expression} for derived units
        package: Optional package

    Returns:
        Measure instance
    """
    m = Measure(name, package)

    # Add canonical unit
    m.with_canonical_unit(canonical[0], "x", canonical[1])

    # Add derived units
    if units:
        for unit_name, expr in units.items():
            m.with_unit(unit_name, "x", expr)

    return m
