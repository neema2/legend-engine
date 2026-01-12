"""
Constraint definitions for Pure DSL.

Constraints define validation rules on Classes.

Example:
    # Simple constraint
    constraint("$this.age >= 0")

    # Named constraint
    constraint("$this.age >= 0", name="validAge")

    # Complex constraint with all options
    Constraint(
        name="validAge",
        function="$this.age >= 0",
        message="Age must be non-negative",
        enforcement=EnforcementLevel.ERROR,
        owner="AgeValidator",
        external_id="AGE_001"
    )
"""

from dataclasses import dataclass
from typing import Optional

from pure_dsl.core import EnforcementLevel


@dataclass
class Constraint:
    """
    A constraint on a Pure Class.

    Constraints define validation rules that must be satisfied.

    Simple constraints are just expressions:
        $this.age >= 0

    Complex constraints can have:
        - name: Named identifier
        - function: The validation expression
        - message: Error message expression
        - enforcement: Error or Warn level
        - owner: Owner name
        - external_id: External identifier

    Example:
        >>> # Simple anonymous constraint
        >>> c = Constraint(function="$this.age >= 0")

        >>> # Named simple constraint
        >>> c = Constraint(name="validAge", function="$this.age >= 0")

        >>> # Complex constraint
        >>> c = Constraint(
        ...     name="validAge",
        ...     function="$this.age >= 0",
        ...     message="'Age must be non-negative'",
        ...     enforcement=EnforcementLevel.ERROR
        ... )
    """
    function: str
    name: Optional[str] = None
    message: Optional[str] = None
    enforcement: Optional[EnforcementLevel] = None
    owner: Optional[str] = None
    external_id: Optional[str] = None

    def is_simple(self) -> bool:
        """Check if this is a simple (expression-only) constraint."""
        return (
            self.message is None
            and self.enforcement is None
            and self.owner is None
            and self.external_id is None
        )

    def to_pure(self) -> str:
        """Generate Pure code for this constraint."""
        if self.is_simple():
            # Simple constraint
            if self.name:
                return f"{self.name}: {self.function}"
            return self.function
        else:
            # Complex constraint
            lines = []
            lines.append(f"{self.name or 'constraint'}")
            lines.append("(")

            if self.owner:
                lines.append(f"  ~owner: {self.owner}")

            if self.external_id:
                lines.append(f"  ~externalId: '{self.external_id}'")

            lines.append(f"  ~function: {self.function}")

            if self.enforcement:
                lines.append(f"  ~enforcementLevel: {self.enforcement.value}")

            if self.message:
                lines.append(f"  ~message: {self.message}")

            lines.append(")")
            return "\n".join(lines)


def constraint(
    expression: str,
    name: Optional[str] = None,
    message: Optional[str] = None,
    enforcement: Optional[EnforcementLevel] = None,
) -> Constraint:
    """
    Factory function to create a constraint.

    This is a Pythonic way to define constraints:

        # Anonymous constraint
        constraint("$this.age >= 0")

        # Named constraint
        constraint("$this.age >= 0", name="validAge")

        # With message
        constraint(
            "$this.age >= 0",
            name="validAge",
            message="'Age must be non-negative'"
        )

    Args:
        expression: The constraint expression
        name: Optional constraint name
        message: Optional error message expression
        enforcement: Optional enforcement level

    Returns:
        A Constraint instance
    """
    return Constraint(
        function=expression,
        name=name,
        message=message,
        enforcement=enforcement,
    )
