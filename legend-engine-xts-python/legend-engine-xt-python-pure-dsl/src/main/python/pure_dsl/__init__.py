"""
Pure DSL - A Pythonic, Type-Safe DSL for generating Pure code

This module provides a natural Python way to define Pure language constructs
using Python class syntax, type annotations, and decorators.

Quick Start:
------------

Define Pure classes using Python class syntax:

    from pure_dsl import PureClass, PureEnum, derived, constraint
    from typing import Optional, List

    class OrderStatus(PureEnum):
        '''Status of an order.'''
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

    # Generate Pure code
    print(Person.to_pure())

Type Mapping:
-------------
    str             -> String[1]
    int             -> Integer[1]
    float           -> Float[1]
    bool            -> Boolean[1]
    Optional[X]     -> X[0..1]
    List[X]         -> X[*]
    ZeroOne[X]      -> X[0..1]
    Many[X]         -> X[*]
    OneMany[X]      -> X[1..*]

Expressions:
------------
The DSL provides type-safe expression building:

    @derived
    def full_name(this) -> str:
        return this.first_name + " " + this.last_name

    @derived
    def active_orders(this) -> List["Order"]:
        return this.orders.filter(lambda o: o.status != "CANCELLED")

    @constraint
    def valid_email(this) -> bool:
        return this.email.contains("@") & this.email.length() > 5
"""

# Core types and expressions
from pure_dsl.types import (
    # Multiplicity wrappers
    One,
    ZeroOne,
    Many,
    OneMany,
    Ranged,
    # Expression building
    Expr,
    This,
    # Type resolution
    resolve_pure_type,
)

# Original builder-style classes (for advanced use)
from pure_dsl.core import (
    Multiplicity,
    Stereotype,
    TaggedValue,
    AggregationKind,
    EnforcementLevel,
    pure_type,
    PureElement,
)

from pure_dsl.profile import Profile
from pure_dsl.enumeration import Enum, EnumValue
from pure_dsl.property import Property, QualifiedProperty
from pure_dsl.constraint import Constraint  # Import this first to avoid shadowing

# DSL classes (imported after to ensure decorators are correct)
from pure_dsl.dsl import (
    # Base classes
    PureClass,
    PureEnum,
    PureAssociation,
    # Decorators
    derived,
    constraint,  # This decorator will be the final value
    # Property/Constraint definitions
    PropertyDef,
    ConstraintDef,
    AssociationEnd,
)
from pure_dsl.classes import Class
from pure_dsl.association import Association
from pure_dsl.function import Function, Parameter, lambda_expr
from pure_dsl.measure import Measure, Unit, measure
from pure_dsl.service import (
    Service,
    ServiceExecution,
    SingleExecution,
    MultiExecution,
    service,
)
from pure_dsl.model import PureModel, pure_model

__all__ = [
    # === New Pythonic DSL (recommended) ===
    # Multiplicity types
    "One",
    "ZeroOne",
    "Many",
    "OneMany",
    "Ranged",
    # Expression system
    "Expr",
    "This",
    # Base classes
    "PureClass",
    "PureEnum",
    "PureAssociation",
    # Decorators
    "derived",
    "constraint",
    # Definitions
    "PropertyDef",
    "ConstraintDef",
    "AssociationEnd",

    # === Builder-style API (for advanced use) ===
    # Core types
    "Multiplicity",
    "Stereotype",
    "TaggedValue",
    "AggregationKind",
    "EnforcementLevel",
    "pure_type",
    "PureElement",
    # Profile
    "Profile",
    # Enumeration (builder style)
    "Enum",
    "EnumValue",
    # Property
    "Property",
    "QualifiedProperty",
    # Constraint
    "Constraint",
    # Class (builder style)
    "Class",
    # Association (builder style)
    "Association",
    # Function
    "Function",
    "Parameter",
    "lambda_expr",
    # Measure
    "Measure",
    "Unit",
    "measure",
    # Service
    "Service",
    "ServiceExecution",
    "SingleExecution",
    "MultiExecution",
    "service",
    # Model
    "PureModel",
    "pure_model",
    # Type resolution
    "resolve_pure_type",
]

__version__ = "0.1.0"
