"""
Core types for Pure DSL.

This module provides fundamental types used throughout the Pure DSL:
- Multiplicity: Defines cardinality of properties (e.g., [1], [0..1], [*], [1..*])
- Stereotype: Profile stereotypes (e.g., <<doc.deprecated>>)
- TaggedValue: Profile tagged values (e.g., {doc.doc = 'description'})
- AggregationKind: Property aggregation types (none, shared, composite)
- EnforcementLevel: Constraint enforcement levels (Error, Warn)

Python Type Mapping:
    str         -> String[1]
    int         -> Integer[1]
    float       -> Float[1]
    bool        -> Boolean[1]
    date        -> Date[1]
    datetime    -> DateTime[1]
    Decimal     -> Decimal[1]
    Optional[X] -> X[0..1]
    List[X]     -> X[*]
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import (
    Any,
    Dict,
    ForwardRef,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

# Type alias for Pure types
PureType = Union[str, Type]


class AggregationKind(PyEnum):
    """Aggregation kind for properties in classes and associations."""
    NONE = "none"
    SHARED = "shared"
    COMPOSITE = "composite"


class EnforcementLevel(PyEnum):
    """Enforcement level for constraints."""
    ERROR = "Error"
    WARN = "Warn"


# Python to Pure type mapping
PYTHON_TO_PURE_TYPE: Dict[Type, str] = {
    str: "String",
    int: "Integer",
    float: "Float",
    bool: "Boolean",
    date: "Date",
    datetime: "DateTime",
    Decimal: "Decimal",
}


@dataclass
class Multiplicity:
    """
    Represents multiplicity in Pure (e.g., [1], [0..1], [*], [1..*]).

    Attributes:
        lower: The lower bound (0 or positive integer)
        upper: The upper bound (positive integer or None for unbounded)

    Examples:
        >>> Multiplicity.one()          # [1]
        >>> Multiplicity.zero_one()     # [0..1]
        >>> Multiplicity.many()         # [*]
        >>> Multiplicity.one_many()     # [1..*]
        >>> Multiplicity(2, 5)          # [2..5]
    """
    lower: int
    upper: Optional[int]  # None means unbounded (*)

    def __post_init__(self):
        if self.lower < 0:
            raise ValueError("Lower bound must be non-negative")
        if self.upper is not None and self.upper < self.lower:
            raise ValueError("Upper bound must be >= lower bound")

    def to_pure(self) -> str:
        """Convert to Pure multiplicity syntax."""
        if self.upper is None:
            if self.lower == 0:
                return "[*]"
            else:
                return f"[{self.lower}..*]"
        elif self.lower == self.upper:
            return f"[{self.lower}]"
        else:
            return f"[{self.lower}..{self.upper}]"

    @classmethod
    def one(cls) -> "Multiplicity":
        """Exactly one: [1]"""
        return cls(1, 1)

    @classmethod
    def zero_one(cls) -> "Multiplicity":
        """Zero or one: [0..1]"""
        return cls(0, 1)

    @classmethod
    def many(cls) -> "Multiplicity":
        """Zero or more: [*]"""
        return cls(0, None)

    @classmethod
    def one_many(cls) -> "Multiplicity":
        """One or more: [1..*]"""
        return cls(1, None)

    @classmethod
    def from_string(cls, s: str) -> "Multiplicity":
        """
        Parse a multiplicity string.

        Args:
            s: Multiplicity string like "1", "0..1", "*", "1..*", "2..5"

        Returns:
            Multiplicity instance
        """
        s = s.strip()
        if s == "*":
            return cls.many()
        elif ".." in s:
            parts = s.split("..")
            lower = int(parts[0])
            upper = None if parts[1] == "*" else int(parts[1])
            return cls(lower, upper)
        else:
            n = int(s)
            return cls(n, n)


def resolve_type_and_multiplicity(
    python_type: Any,
) -> Tuple[str, Multiplicity]:
    """
    Resolve a Python type annotation to Pure type and multiplicity.

    Handles:
        - Basic types: str, int, float, bool -> String[1], Integer[1], etc.
        - Optional[X] -> X[0..1]
        - List[X] -> X[*]
        - ForwardRef strings for Pure types

    Args:
        python_type: Python type annotation

    Returns:
        Tuple of (pure_type_name, multiplicity)
    """
    origin = get_origin(python_type)

    # Handle Optional[X] -> X[0..1]
    if origin is Union:
        args = get_args(python_type)
        # Optional is Union[X, None]
        non_none_args = [a for a in args if a is not type(None)]
        if len(non_none_args) == 1:
            inner_type, inner_mult = resolve_type_and_multiplicity(non_none_args[0])
            # Make it optional
            return inner_type, Multiplicity.zero_one()
        else:
            raise TypeError(f"Unsupported Union type: {python_type}")

    # Handle List[X] -> X[*]
    if origin is list:
        args = get_args(python_type)
        if args:
            inner_type, _ = resolve_type_and_multiplicity(args[0])
            return inner_type, Multiplicity.many()
        return "Any", Multiplicity.many()

    # Handle forward references (string type names)
    if isinstance(python_type, str):
        return python_type, Multiplicity.one()

    if isinstance(python_type, ForwardRef):
        return python_type.__forward_arg__, Multiplicity.one()

    # Handle basic Python types
    if python_type in PYTHON_TO_PURE_TYPE:
        return PYTHON_TO_PURE_TYPE[python_type], Multiplicity.one()

    # Handle classes that might be Pure classes
    if isinstance(python_type, type):
        # Check if it has a Pure name (from our DSL)
        if hasattr(python_type, "_pure_name"):
            return python_type._pure_name, Multiplicity.one()
        # Use the class name directly
        return python_type.__name__, Multiplicity.one()

    # Default: use string representation
    return str(python_type), Multiplicity.one()


def parse_multiplicity(mult: Union[str, Multiplicity, None]) -> Multiplicity:
    """
    Parse multiplicity from various formats.

    Args:
        mult: Can be a string ("1", "0..1", "*"), Multiplicity instance, or None (defaults to [1])

    Returns:
        Multiplicity instance
    """
    if mult is None:
        return Multiplicity.one()
    elif isinstance(mult, Multiplicity):
        return mult
    elif isinstance(mult, str):
        return Multiplicity.from_string(mult)
    else:
        raise TypeError(f"Expected str or Multiplicity, got {type(mult)}")


@dataclass
class Stereotype:
    """
    A stereotype reference in Pure (e.g., <<profile::Path.stereotypeName>>).

    Stereotypes are defined in Profiles and can be applied to various
    Pure elements like Classes, Properties, Enums, Functions, etc.

    Attributes:
        profile: The profile path (e.g., "doc", "meta::pure::profiles::doc")
        name: The stereotype name (e.g., "deprecated", "doc")

    Example:
        >>> st = Stereotype("doc", "deprecated")
        >>> st.to_pure()  # 'doc.deprecated'
    """
    profile: str
    name: str

    def to_pure(self) -> str:
        """Convert to Pure stereotype reference syntax."""
        return f"{self.profile}.{self.name}"

    @classmethod
    def from_string(cls, s: str) -> "Stereotype":
        """
        Parse a stereotype from string format "profile.name".

        Args:
            s: Stereotype string like "doc.deprecated" or "my::profile.flag"

        Returns:
            Stereotype instance
        """
        # Find the last dot to split profile from name
        last_dot = s.rfind(".")
        if last_dot == -1:
            raise ValueError(f"Invalid stereotype format: {s}. Expected 'profile.name'")
        return cls(s[:last_dot], s[last_dot + 1:])


@dataclass
class TaggedValue:
    """
    A tagged value in Pure (e.g., {profile::Path.tagName = 'value'}).

    Tagged values are defined in Profiles and provide metadata
    for Pure elements like Classes, Properties, Enums, Functions, etc.

    Attributes:
        profile: The profile path (e.g., "doc", "meta::pure::profiles::doc")
        tag: The tag name (e.g., "doc", "deprecated")
        value: The tag value (string)

    Example:
        >>> tv = TaggedValue("doc", "doc", "This is a person class")
        >>> tv.to_pure()  # "doc.doc = 'This is a person class'"
    """
    profile: str
    tag: str
    value: str

    def to_pure(self) -> str:
        """Convert to Pure tagged value syntax."""
        # Escape single quotes in value
        escaped_value = self.value.replace("'", "\\'")
        return f"{self.profile}.{self.tag} = '{escaped_value}'"


@dataclass
class StereotypesAndTags:
    """
    Container for stereotypes and tagged values.

    Used by Classes, Properties, Enums, Functions, and other Pure elements
    that support annotations.
    """
    stereotypes: List[Stereotype] = field(default_factory=list)
    tagged_values: List[TaggedValue] = field(default_factory=list)

    def add_stereotype(self, profile: str, name: str) -> "StereotypesAndTags":
        """Add a stereotype."""
        self.stereotypes.append(Stereotype(profile, name))
        return self

    def add_tagged_value(self, profile: str, tag: str, value: str) -> "StereotypesAndTags":
        """Add a tagged value."""
        self.tagged_values.append(TaggedValue(profile, tag, value))
        return self

    def has_annotations(self) -> bool:
        """Check if there are any annotations."""
        return bool(self.stereotypes or self.tagged_values)

    def stereotypes_to_pure(self) -> str:
        """Convert stereotypes to Pure syntax."""
        if not self.stereotypes:
            return ""
        refs = ", ".join(st.to_pure() for st in self.stereotypes)
        return f"<<{refs}>>"

    def tagged_values_to_pure(self) -> str:
        """Convert tagged values to Pure syntax."""
        if not self.tagged_values:
            return ""
        refs = ", ".join(tv.to_pure() for tv in self.tagged_values)
        return f"{{{refs}}}"

    def to_pure_prefix(self) -> str:
        """
        Get the combined prefix for stereotypes and tagged values.

        Returns a string like "<<doc.deprecated>> {doc.doc = 'description'} "
        with a trailing space if there are annotations.
        """
        parts = []
        st_str = self.stereotypes_to_pure()
        tv_str = self.tagged_values_to_pure()

        if st_str:
            parts.append(st_str)
        if tv_str:
            parts.append(tv_str)

        if parts:
            return " ".join(parts) + " "
        return ""


class PureElement:
    """
    Base class for all Pure elements.

    Provides common functionality for:
    - Qualified names (package::Name)
    - Stereotypes and tagged values
    - Code generation
    """

    def __init__(self, name: str, package: Optional[str] = None):
        """
        Initialize a Pure element.

        Args:
            name: Simple name of the element
            package: Optional package path (e.g., "my::package")
        """
        self._name = name
        self._package = package
        self._annotations = StereotypesAndTags()

    @property
    def name(self) -> str:
        """Get the simple name."""
        return self._name

    @property
    def package(self) -> Optional[str]:
        """Get the package path."""
        return self._package

    @package.setter
    def package(self, value: Optional[str]):
        """Set the package path."""
        self._package = value

    @property
    def qualified_name(self) -> str:
        """Get the fully qualified name (package::Name)."""
        if self._package:
            return f"{self._package}::{self._name}"
        return self._name

    def with_stereotype(self, profile: str, name: str) -> "PureElement":
        """
        Add a stereotype to this element.

        Args:
            profile: Profile path (e.g., "doc", "my::profile")
            name: Stereotype name

        Returns:
            self for chaining
        """
        self._annotations.add_stereotype(profile, name)
        return self

    def with_tagged_value(self, profile: str, tag: str, value: str) -> "PureElement":
        """
        Add a tagged value to this element.

        Args:
            profile: Profile path (e.g., "doc", "my::profile")
            tag: Tag name
            value: Tag value

        Returns:
            self for chaining
        """
        self._annotations.add_tagged_value(profile, tag, value)
        return self

    def with_doc(self, doc: str) -> "PureElement":
        """
        Add documentation using the standard doc profile.

        Shorthand for with_tagged_value("doc", "doc", doc)

        Args:
            doc: Documentation string

        Returns:
            self for chaining
        """
        return self.with_tagged_value("doc", "doc", doc)

    def _annotations_prefix(self) -> str:
        """Get the annotations prefix for code generation."""
        return self._annotations.to_pure_prefix()

    def to_pure(self) -> str:
        """
        Generate Pure code for this element.

        Subclasses must override this method.
        """
        raise NotImplementedError("Subclasses must implement to_pure()")


def indent(text: str, spaces: int = 2) -> str:
    """
    Indent each line of text by the specified number of spaces.

    Args:
        text: The text to indent
        spaces: Number of spaces for indentation

    Returns:
        Indented text
    """
    prefix = " " * spaces
    lines = text.split("\n")
    return "\n".join(prefix + line if line.strip() else line for line in lines)


def format_code_block(code: str) -> str:
    """
    Format a Pure code block, handling multiline expressions.

    Args:
        code: The Pure expression code

    Returns:
        Formatted code block
    """
    code = code.strip()
    if "\n" in code:
        # Multiline: indent and format nicely
        return code
    return code


# Convenience type aliases for Pythonic usage
class Many(List):
    """Marker type for [*] multiplicity. Use as Many[Type]."""
    pass


class OneMany(List):
    """Marker type for [1..*] multiplicity. Use as OneMany[Type]."""
    pass


class pure_type:
    """
    Decorator and type wrapper for custom Pure types.

    Use this to specify Pure types that don't map directly from Python:

        # As a direct type specification
        age: pure_type("Integer", "0..1")

        # For extended primitives
        name: pure_type("meta::pure::precisePrimitives::Varchar(200)")
    """

    def __init__(
        self,
        type_name: str,
        multiplicity: Union[str, Multiplicity] = "1",
    ):
        self.type_name = type_name
        self.multiplicity = parse_multiplicity(multiplicity)

    def resolve(self) -> Tuple[str, Multiplicity]:
        """Resolve to type name and multiplicity."""
        return self.type_name, self.multiplicity
