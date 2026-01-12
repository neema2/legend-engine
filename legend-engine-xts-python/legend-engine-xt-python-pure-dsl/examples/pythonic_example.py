#!/usr/bin/env python3
"""
Pythonic Pure DSL Example

This example demonstrates the type-safe, Pythonic approach to defining
Pure constructs using native Python class syntax.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/main/python'))

from typing import Optional, List
from datetime import date

from pure_dsl import (
    # Type-safe DSL
    PureClass,
    PureEnum,
    PureAssociation,
    derived,
    constraint,
    # Multiplicity types
    Many,
    OneMany,
    ZeroOne,
)


# =============================================================================
# ENUMS - Define using Python class syntax
# =============================================================================

class OrderStatus(PureEnum):
    """Status of a trading order."""
    NEW = "NEW"
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OrderSide(PureEnum):
    """Side of an order (buy or sell)."""
    BUY = "BUY"
    SELL = "SELL"


class AssetClass(PureEnum):
    """Asset class categories."""
    EQUITY = "EQUITY"
    FIXED_INCOME = "FIXED_INCOME"
    COMMODITY = "COMMODITY"
    FX = "FX"
    DERIVATIVE = "DERIVATIVE"


# =============================================================================
# CLASSES - Define using Python class syntax with type annotations
# =============================================================================

class Entity(PureClass):
    """Base class for all domain entities."""
    id: str
    created_at: date
    updated_at: Optional[date]


class Person(PureClass, extends="Entity"):
    """A person in the system."""

    # Properties with automatic type mapping
    first_name: str               # -> String[1]
    last_name: str                # -> String[1]
    age: Optional[int]            # -> Integer[0..1]
    emails: List[str]             # -> String[*]
    is_active: bool = True        # -> Boolean[1] with default

    # Derived property using @derived decorator
    @derived
    def full_name(this) -> str:
        """The person's full name."""
        return this.first_name + " " + this.last_name

    @derived
    def email_count(this) -> int:
        """Number of email addresses."""
        return this.emails.size()

    # Constraints using @constraint decorator
    @constraint
    def valid_age(this) -> bool:
        """Age must be non-negative if provided."""
        return this.age >= 0

    @constraint(message="'Email list cannot be empty for active users'")
    def active_has_email(this) -> bool:
        """Active users must have at least one email."""
        return ~this.is_active | this.emails.isNotEmpty()


class Trader(PureClass, extends="Person"):
    """A trader in the trading system."""

    trader_id: str
    desk: Optional[str]
    trading_limit: float

    @derived
    def active_orders(this) -> List["Order"]:
        """Orders that are still active."""
        return this.orders.filter(
            lambda o: (o.status != "OrderStatus.FILLED") & (o.status != "OrderStatus.CANCELLED")
        )

    @derived
    def total_order_value(this) -> float:
        """Total value of all orders."""
        return this.orders.map(lambda o: o.total_value).sum()

    @constraint
    def valid_limit(this) -> bool:
        """Trading limit must be positive."""
        return this.trading_limit > 0


class Instrument(PureClass, extends="Entity"):
    """A tradable financial instrument."""

    symbol: str
    name: str
    asset_class: "AssetClass"
    currency: str
    exchange_code: Optional[str]
    isin: Optional[str]

    @constraint
    def symbol_length(this) -> bool:
        """Symbol must be 10 characters or less."""
        return this.symbol.length() <= 10


class Order(PureClass, extends="Entity"):
    """A trading order."""

    order_id: str
    side: "OrderSide"
    quantity: int
    price: float
    status: "OrderStatus"
    filled_quantity: int = 0
    notes: List[str]

    @derived
    def total_value(this) -> float:
        """Total order value (quantity * price)."""
        return this.quantity * this.price

    @derived
    def remaining_quantity(this) -> int:
        """Quantity not yet filled."""
        return this.quantity - this.filled_quantity

    @derived
    def fill_percentage(this) -> float:
        """Percentage of order that has been filled."""
        return (this.filled_quantity / this.quantity) * 100

    @constraint
    def positive_quantity(this) -> bool:
        """Quantity must be positive."""
        return this.quantity > 0

    @constraint
    def non_negative_price(this) -> bool:
        """Price must be non-negative."""
        return this.price >= 0

    @constraint(message="'Filled quantity cannot exceed order quantity'")
    def valid_fill(this) -> bool:
        """Filled quantity must not exceed order quantity."""
        return this.filled_quantity <= this.quantity


class Trade(PureClass, extends="Entity"):
    """An executed trade."""

    trade_id: str
    execution_price: float
    executed_quantity: int
    venue: Optional[str]

    @derived
    def trade_value(this) -> float:
        """Value of this trade."""
        return this.execution_price * this.executed_quantity


# =============================================================================
# ASSOCIATIONS - Define relationships between classes
# =============================================================================

# Association between Trader and Orders
# Format: (target_type, property_name, multiplicity)
# Property "orders" points to Order, property "trader" points to Trader
trader_orders = PureAssociation(
    "Trader_Orders",
    ("Order", "orders", "[*]"),     # Property "orders" of type Order[*]
    ("Trader", "trader", "[1]"),    # Property "trader" of type Trader[1]
)

# Association between Order and Instrument
order_instrument = PureAssociation(
    "Order_Instrument",
    ("Instrument", "instrument", "[1]"),  # Property "instrument" of type Instrument[1]
    ("Order", "orders", "[*]"),           # Property "orders" of type Order[*]
)

# Association between Order and Trades
order_trades = PureAssociation(
    "Order_Trades",
    ("Trade", "trades", "[*]"),    # Property "trades" of type Trade[*]
    ("Order", "order", "[1]"),     # Property "order" of type Order[1]
)


# =============================================================================
# GENERATE PURE CODE
# =============================================================================

def main():
    print("=" * 70)
    print("PYTHONIC PURE DSL - Generated Pure Code")
    print("=" * 70)
    print()

    # Generate and print each element
    elements = [
        ("Enum: OrderStatus", OrderStatus),
        ("Enum: OrderSide", OrderSide),
        ("Enum: AssetClass", AssetClass),
        ("Class: Entity", Entity),
        ("Class: Person", Person),
        ("Class: Trader", Trader),
        ("Class: Instrument", Instrument),
        ("Class: Order", Order),
        ("Class: Trade", Trade),
        ("Association: Trader_Orders", trader_orders),
        ("Association: Order_Instrument", order_instrument),
        ("Association: Order_Trades", order_trades),
    ]

    for name, element in elements:
        print(f"// {'-' * 60}")
        print(f"// {name}")
        print(f"// {'-' * 60}")
        print(element.to_pure())
        print()


if __name__ == "__main__":
    main()
