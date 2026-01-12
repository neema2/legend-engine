"""
Type-safe Pure type system.

This module provides Python types that map directly to Pure types,
enabling type-safe property and expression definitions.
"""

from __future__ import annotations
from typing import (
    Any,
    Callable,
    Generic,
    List as PyList,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    overload,
)
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal as PyDecimal
from enum import Enum as PyEnum
from abc import ABC, abstractmethod


# Type variable for generic Pure types
T = TypeVar("T")
R = TypeVar("R")


class PureType(ABC):
    """Base class for all Pure types."""

    @abstractmethod
    def pure_type_name(self) -> str:
        """Return the Pure type name."""
        ...

    @abstractmethod
    def multiplicity(self) -> str:
        """Return the multiplicity string."""
        ...


# =============================================================================
# Multiplicity Types - Use these in type annotations
# =============================================================================

class One(Generic[T]):
    """
    Exactly one value: [1]

    Usage:
        name: One[str]  # -> String[1]
    """
    _inner_type: Type[T]

    def __class_getitem__(cls, item: Type[T]) -> "One[T]":
        instance = object.__new__(cls)
        instance._inner_type = item
        return instance


class ZeroOne(Generic[T]):
    """
    Zero or one value: [0..1]

    Usage:
        age: ZeroOne[int]  # -> Integer[0..1]

    Note: You can also use Optional[T] for the same effect.
    """
    _inner_type: Type[T]

    def __class_getitem__(cls, item: Type[T]) -> "ZeroOne[T]":
        instance = object.__new__(cls)
        instance._inner_type = item
        return instance


class Many(Generic[T]):
    """
    Zero or more values: [*]

    Usage:
        emails: Many[str]  # -> String[*]

    Note: You can also use List[T] for the same effect.
    """
    _inner_type: Type[T]

    def __class_getitem__(cls, item: Type[T]) -> "Many[T]":
        instance = object.__new__(cls)
        instance._inner_type = item
        return instance


class OneMany(Generic[T]):
    """
    One or more values: [1..*]

    Usage:
        addresses: OneMany[Address]  # -> Address[1..*]
    """
    _inner_type: Type[T]

    def __class_getitem__(cls, item: Type[T]) -> "OneMany[T]":
        instance = object.__new__(cls)
        instance._inner_type = item
        return instance


class Ranged(Generic[T]):
    """
    Custom range multiplicity: [n..m]

    Usage:
        items: Ranged[Product, 1, 10]  # -> Product[1..10]
    """
    _inner_type: Type[T]
    _lower: int
    _upper: int

    def __class_getitem__(cls, args) -> "Ranged[T]":
        if isinstance(args, tuple) and len(args) == 3:
            item, lower, upper = args
        else:
            raise TypeError("Ranged requires [Type, lower, upper]")
        instance = object.__new__(cls)
        instance._inner_type = item
        instance._lower = lower
        instance._upper = upper
        return instance


# =============================================================================
# Pure Expression System - Type-safe expression building
# =============================================================================

class Expr(Generic[T]):
    """
    A Pure expression that evaluates to type T.

    This is the base for building type-safe Pure expressions.
    """

    def __init__(self, expr: str, result_type: Type[T] = None):
        self._expr = expr
        self._result_type = result_type

    def to_pure(self) -> str:
        """Convert to Pure expression string."""
        return self._expr

    def __str__(self) -> str:
        return self._expr

    # Arithmetic operations
    def __add__(self, other: Union["Expr", int, float, str]) -> "Expr":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} + {other._expr}")
        return Expr(f"{self._expr} + {_to_pure_literal(other)}")

    def __radd__(self, other: Union[int, float, str]) -> "Expr":
        return Expr(f"{_to_pure_literal(other)} + {self._expr}")

    def __sub__(self, other: Union["Expr", int, float]) -> "Expr":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} - {other._expr}")
        return Expr(f"{self._expr} - {other}")

    def __mul__(self, other: Union["Expr", int, float]) -> "Expr":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} * {other._expr}")
        return Expr(f"{self._expr} * {other}")

    def __truediv__(self, other: Union["Expr", int, float]) -> "Expr":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} / {other._expr}")
        return Expr(f"{self._expr} / {other}")

    # Comparison operations
    def __eq__(self, other: Union["Expr", Any]) -> "Expr[bool]":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} == {other._expr}", bool)
        return Expr(f"{self._expr} == {_to_pure_literal(other)}", bool)

    def __ne__(self, other: Union["Expr", Any]) -> "Expr[bool]":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} != {other._expr}", bool)
        return Expr(f"{self._expr} != {_to_pure_literal(other)}", bool)

    def __lt__(self, other: Union["Expr", int, float]) -> "Expr[bool]":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} < {other._expr}", bool)
        return Expr(f"{self._expr} < {other}", bool)

    def __le__(self, other: Union["Expr", int, float]) -> "Expr[bool]":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} <= {other._expr}", bool)
        return Expr(f"{self._expr} <= {other}", bool)

    def __gt__(self, other: Union["Expr", int, float]) -> "Expr[bool]":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} > {other._expr}", bool)
        return Expr(f"{self._expr} > {other}", bool)

    def __ge__(self, other: Union["Expr", int, float]) -> "Expr[bool]":
        if isinstance(other, Expr):
            return Expr(f"{self._expr} >= {other._expr}", bool)
        return Expr(f"{self._expr} >= {other}", bool)

    # Boolean operations
    def __and__(self, other: "Expr[bool]") -> "Expr[bool]":
        return Expr(f"{self._expr} && {other._expr}", bool)

    def __or__(self, other: "Expr[bool]") -> "Expr[bool]":
        return Expr(f"{self._expr} || {other._expr}", bool)

    def __invert__(self) -> "Expr[bool]":
        return Expr(f"!{self._expr}", bool)

    # Collection operations (for Many types)
    def filter(self, predicate: Callable[["Expr[T]"], "Expr[bool]"]) -> "Expr[Many[T]]":
        """Filter collection elements."""
        param = Expr("x", self._result_type)
        pred_expr = predicate(param)
        return Expr(f"{self._expr}->filter(x | {pred_expr._expr})")

    def map(self, mapper: Callable[["Expr[T]"], "Expr[R]"]) -> "Expr[Many[R]]":
        """Map over collection elements."""
        param = Expr("x", self._result_type)
        map_expr = mapper(param)
        return Expr(f"{self._expr}->map(x | {map_expr._expr})")

    def first(self) -> "Expr[ZeroOne[T]]":
        """Get first element or empty."""
        return Expr(f"{self._expr}->first()")

    def toOne(self) -> "Expr[T]":
        """Convert optional to required (fails if empty)."""
        return Expr(f"{self._expr}->toOne()")

    def exists(self, predicate: Callable[["Expr[T]"], "Expr[bool]"]) -> "Expr[bool]":
        """Check if any element matches predicate."""
        param = Expr("x", self._result_type)
        pred_expr = predicate(param)
        return Expr(f"{self._expr}->exists(x | {pred_expr._expr})", bool)

    def forAll(self, predicate: Callable[["Expr[T]"], "Expr[bool]"]) -> "Expr[bool]":
        """Check if all elements match predicate."""
        param = Expr("x", self._result_type)
        pred_expr = predicate(param)
        return Expr(f"{self._expr}->forAll(x | {pred_expr._expr})", bool)

    def size(self) -> "Expr[int]":
        """Get collection size."""
        return Expr(f"{self._expr}->size()", int)

    def isEmpty(self) -> "Expr[bool]":
        """Check if collection is empty."""
        return Expr(f"{self._expr}->isEmpty()", bool)

    def isNotEmpty(self) -> "Expr[bool]":
        """Check if collection is not empty."""
        return Expr(f"{self._expr}->isNotEmpty()", bool)

    def sum(self) -> "Expr[float]":
        """Sum numeric collection."""
        return Expr(f"{self._expr}->sum()", float)

    def average(self) -> "Expr[float]":
        """Average of numeric collection."""
        return Expr(f"{self._expr}->average()", float)

    def min(self) -> "Expr[T]":
        """Minimum value in collection."""
        return Expr(f"{self._expr}->min()")

    def max(self) -> "Expr[T]":
        """Maximum value in collection."""
        return Expr(f"{self._expr}->max()")

    # String operations
    def contains(self, substring: Union["Expr[str]", str]) -> "Expr[bool]":
        """Check if string contains substring."""
        if isinstance(substring, str):
            return Expr(f"{self._expr}->contains('{substring}')", bool)
        return Expr(f"{self._expr}->contains({substring._expr})", bool)

    def startsWith(self, prefix: Union["Expr[str]", str]) -> "Expr[bool]":
        """Check if string starts with prefix."""
        if isinstance(prefix, str):
            return Expr(f"{self._expr}->startsWith('{prefix}')", bool)
        return Expr(f"{self._expr}->startsWith({prefix._expr})", bool)

    def endsWith(self, suffix: Union["Expr[str]", str]) -> "Expr[bool]":
        """Check if string ends with suffix."""
        if isinstance(suffix, str):
            return Expr(f"{self._expr}->endsWith('{suffix}')", bool)
        return Expr(f"{self._expr}->endsWith({suffix._expr})", bool)

    def length(self) -> "Expr[int]":
        """Get string length."""
        return Expr(f"{self._expr}->length()", int)

    def toLower(self) -> "Expr[str]":
        """Convert to lowercase."""
        return Expr(f"{self._expr}->toLower()", str)

    def toUpper(self) -> "Expr[str]":
        """Convert to uppercase."""
        return Expr(f"{self._expr}->toUpper()", str)

    def trim(self) -> "Expr[str]":
        """Trim whitespace."""
        return Expr(f"{self._expr}->trim()", str)

    # Property access
    def __getattr__(self, name: str) -> "Expr":
        """Access a property on this expression."""
        if name.startswith("_"):
            raise AttributeError(name)
        # Convert snake_case to camelCase
        pure_name = _snake_to_camel(name)
        return Expr(f"{self._expr}.{pure_name}")


def _snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    if "_" not in name:
        return name
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def _to_pure_literal(value: Any) -> str:
    """Convert a Python value to a Pure literal."""
    if isinstance(value, str):
        return f"'{value}'"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return "[]"
    elif isinstance(value, Expr):
        return value._expr
    else:
        return str(value)


class This(Generic[T]):
    """
    Represents $this in Pure expressions.

    Use this in derived properties and constraints to reference
    the current object in a type-safe way.

    Example:
        class Person(PureClass):
            first_name: str
            last_name: str

            @derived
            def full_name(this: This[Person]) -> str:
                return this.first_name + " " + this.last_name
    """

    def __init__(self, cls: Type[T] = None):
        self._cls = cls

    def __getattr__(self, name: str) -> Expr:
        """Access a property on $this."""
        if name.startswith("_"):
            raise AttributeError(name)
        # Convert snake_case to camelCase
        pure_name = _snake_to_camel(name)
        return Expr(f"$this.{pure_name}")


# =============================================================================
# Type Resolution
# =============================================================================

# Python to Pure type name mapping
_PYTHON_TO_PURE: dict = {
    str: "String",
    int: "Integer",
    float: "Float",
    bool: "Boolean",
    date: "Date",
    datetime: "DateTime",
    PyDecimal: "Decimal",
}


def resolve_pure_type(python_type: Any) -> Tuple[str, str]:
    """
    Resolve a Python type annotation to Pure type and multiplicity.

    Returns:
        Tuple of (pure_type_name, multiplicity_string)
    """
    origin = get_origin(python_type)
    args = get_args(python_type)

    # Handle our multiplicity wrappers
    if hasattr(python_type, "_inner_type"):
        inner_type, _ = resolve_pure_type(python_type._inner_type)

        if isinstance(python_type, One):
            return inner_type, "[1]"
        elif isinstance(python_type, ZeroOne):
            return inner_type, "[0..1]"
        elif isinstance(python_type, Many):
            return inner_type, "[*]"
        elif isinstance(python_type, OneMany):
            return inner_type, "[1..*]"
        elif isinstance(python_type, Ranged):
            return inner_type, f"[{python_type._lower}..{python_type._upper}]"

    # Handle Optional[X] -> X[0..1]
    if origin is Union:
        non_none = [a for a in args if a is not type(None)]
        if len(non_none) == 1:
            inner_type, _ = resolve_pure_type(non_none[0])
            return inner_type, "[0..1]"

    # Handle List[X] -> X[*]
    if origin is list:
        if args:
            inner_type, _ = resolve_pure_type(args[0])
            return inner_type, "[*]"
        return "Any", "[*]"

    # Handle basic Python types
    if python_type in _PYTHON_TO_PURE:
        return _PYTHON_TO_PURE[python_type], "[1]"

    # Handle Pure class references
    if isinstance(python_type, type):
        if hasattr(python_type, "__pure_name__"):
            return python_type.__pure_name__, "[1]"
        return python_type.__name__, "[1]"

    # Handle string references (forward references)
    if isinstance(python_type, str):
        return python_type, "[1]"

    # Handle ForwardRef (from typing module)
    from typing import ForwardRef
    if isinstance(python_type, ForwardRef):
        # Extract the string from ForwardRef
        type_name = python_type.__forward_arg__
        return type_name, "[1]"

    # Default
    return str(python_type), "[1]"
