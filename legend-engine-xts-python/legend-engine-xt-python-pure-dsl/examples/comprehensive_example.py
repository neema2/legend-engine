#!/usr/bin/env python3
"""
Comprehensive Example: Pure DSL for Legend Engine

This example demonstrates all the capabilities of the Pure DSL,
showing how to define a complete domain model using Pythonic syntax.

The example creates a trading domain model with:
- Profiles for metadata
- Enums for fixed values
- Classes with properties, constraints, and derived properties
- Associations for relationships
- Functions for reusable logic
- Measures for unit conversions
- Services for API endpoints
"""

import sys
import os

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src/main/python'))

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

from pure_dsl import (
    # Core types
    Multiplicity,
    AggregationKind,
    EnforcementLevel,
    pure_type,
    # Elements
    Profile,
    Enum,
    EnumValue,
    Class,
    Association,
    Function,
    Measure,
    Service,
    # Helpers
    Property,
    QualifiedProperty,
    Constraint,
    constraint,
    pure_class,
    derived_property,
    pure_function,
    lambda_expr,
    measure,
    service,
    association,
    # Model
    PureModel,
    pure_model,
)


def example_builder_style():
    """
    Example 1: Using the Builder Pattern

    This style is more explicit and gives you full control over the Pure output.
    """
    print("=" * 70)
    print("Example 1: Builder Pattern Style")
    print("=" * 70)

    # Create a model with default package
    model = PureModel("trading::model")

    # =========================================================================
    # PROFILES - Define metadata stereotypes and tags
    # =========================================================================
    trading_profile = Profile("TradingProfile") \
        .with_stereotypes("critical", "audited", "realtime") \
        .with_tags("owner", "version", "sla")
    model.add(trading_profile)

    # =========================================================================
    # ENUMS - Define fixed value sets
    # =========================================================================

    # Simple enum
    order_status = Enum("OrderStatus") \
        .with_doc("Status of a trading order") \
        .with_value("NEW", doc="Order just created") \
        .with_value("PENDING", doc="Awaiting execution") \
        .with_value("PARTIALLY_FILLED", doc="Partially executed") \
        .with_value("FILLED", doc="Fully executed") \
        .with_value("CANCELLED", doc="Order was cancelled") \
        .with_value("REJECTED", doc="Order was rejected")
    model.add(order_status)

    order_side = Enum("OrderSide") \
        .with_values("BUY", "SELL")
    model.add(order_side)

    asset_class = Enum("AssetClass") \
        .with_values("EQUITY", "FIXED_INCOME", "COMMODITY", "FX", "DERIVATIVE")
    model.add(asset_class)

    # =========================================================================
    # CLASSES - Define domain entities
    # =========================================================================

    # Entity base class
    entity = Class("Entity") \
        .with_doc("Base class for all entities") \
        .with_property("id", str) \
        .with_property("createdAt", "DateTime") \
        .with_property("updatedAt", "DateTime", multiplicity="0..1")
    model.add(entity)

    # Trader class with derived property
    trader = Class("Trader") \
        .extends("Entity") \
        .with_doc("A trader in the trading system") \
        .with_stereotype("TradingProfile", "audited") \
        .with_property("traderId", str) \
        .with_property("firstName", str) \
        .with_property("lastName", str) \
        .with_property("email", str) \
        .with_property("desk", str, multiplicity="0..1") \
        .with_property("isActive", bool, default="true") \
        .with_derived(
            "fullName",
            str,
            "$this.firstName + ' ' + $this.lastName"
        ) \
        .with_derived(
            "activeOrders",
            "Order",
            "$this.orders->filter(o | $o.status != OrderStatus.FILLED && $o.status != OrderStatus.CANCELLED)",
            multiplicity="*"
        ) \
        .with_constraint("$this.email->contains('@')", name="validEmail")
    model.add(trader)

    # Instrument class
    instrument = Class("Instrument") \
        .extends("Entity") \
        .with_doc("A tradable financial instrument") \
        .with_property("symbol", str) \
        .with_property("name", str) \
        .with_property("assetClass", "AssetClass") \
        .with_property("currency", str) \
        .with_property("exchangeCode", str, multiplicity="0..1") \
        .with_property("isin", str, multiplicity="0..1") \
        .with_constraint("$this.symbol->length() <= 10", name="symbolLength")
    model.add(instrument)

    # Order class with multiple constraints
    order = Class("Order") \
        .extends("Entity") \
        .with_doc("A trading order") \
        .with_stereotype("TradingProfile", "critical") \
        .with_tagged_value("TradingProfile", "sla", "100ms") \
        .with_property("orderId", str) \
        .with_property("side", "OrderSide") \
        .with_property("quantity", int) \
        .with_property("price", float) \
        .with_property("status", "OrderStatus", default="OrderStatus.NEW") \
        .with_property("filledQuantity", int, default="0") \
        .with_property("notes", str, multiplicity="*") \
        .with_derived(
            "totalValue",
            float,
            "$this.quantity * $this.price"
        ) \
        .with_derived(
            "remainingQuantity",
            int,
            "$this.quantity - $this.filledQuantity"
        ) \
        .with_derived(
            "fillPercentage",
            float,
            "if($this.quantity == 0, 0.0, ($this.filledQuantity / $this.quantity) * 100)"
        ) \
        .with_constraint("$this.quantity > 0", name="positiveQuantity") \
        .with_constraint("$this.price >= 0", name="nonNegativePrice") \
        .with_constraint(
            "$this.filledQuantity <= $this.quantity",
            name="validFillQuantity",
            message="'Filled quantity cannot exceed order quantity'"
        )
    model.add(order)

    # Trade (execution) class
    trade = Class("Trade") \
        .extends("Entity") \
        .with_doc("An executed trade") \
        .with_property("tradeId", str) \
        .with_property("executionPrice", float) \
        .with_property("executedQuantity", int) \
        .with_property("executionTime", "DateTime") \
        .with_property("venue", str, multiplicity="0..1") \
        .with_derived("tradeValue", float, "$this.executionPrice * $this.executedQuantity")
    model.add(trade)

    # =========================================================================
    # ASSOCIATIONS - Define relationships
    # =========================================================================

    # Trader to Orders
    trader_orders = Association("Trader_Orders") \
        .add_end("orders", "Order", "*") \
        .add_end("trader", "Trader", "1")
    model.add(trader_orders)

    # Order to Instrument
    order_instrument = Association("Order_Instrument") \
        .add_end("orders", "Order", "*") \
        .add_end("instrument", "Instrument", "1")
    model.add(order_instrument)

    # Order to Trades
    order_trades = Association("Order_Trades") \
        .add_end("trades", "Trade", "*", aggregation=AggregationKind.COMPOSITE) \
        .add_end("order", "Order", "1")
    model.add(order_trades)

    # =========================================================================
    # FUNCTIONS - Define reusable logic
    # =========================================================================

    # Calculate portfolio value
    portfolio_value = Function("calculatePortfolioValue") \
        .with_doc("Calculate the total value of a portfolio") \
        .with_param("orders", "Order", "*") \
        .returns(float) \
        .body("$orders->filter(o | $o.status == OrderStatus.FILLED).totalValue->sum()")
    model.add(portfolio_value)

    # Filter orders by status
    filter_orders = Function("filterOrdersByStatus") \
        .with_param("orders", "Order", "*") \
        .with_param("status", "OrderStatus") \
        .returns("Order", "*") \
        .body("$orders->filter(o | $o.status == $status)")
    model.add(filter_orders)

    # Get active traders
    active_traders = Function("getActiveTraders") \
        .with_param("traders", "Trader", "*") \
        .returns("Trader", "*") \
        .body("$traders->filter(t | $t.isActive == true)")
    model.add(active_traders)

    # =========================================================================
    # MEASURES - Define unit conversions
    # =========================================================================

    # Currency measure
    currency = Measure("Currency") \
        .with_canonical_unit("USD", "x", "$x") \
        .with_unit("EUR", "x", "$x * 1.10") \
        .with_unit("GBP", "x", "$x * 1.27") \
        .with_unit("JPY", "x", "$x * 0.0067")
    model.add(currency)

    # =========================================================================
    # SERVICES - Define API endpoints
    # =========================================================================

    # Orders service
    orders_service = Service("OrdersService") \
        .with_stereotype("TradingProfile", "realtime") \
        .pattern("/api/v1/orders") \
        .owners("trading-team", "platform-team") \
        .documentation("Trading Orders API - provides access to order data") \
        .single_execution(
            query="|Order.all()->project([x|$x.orderId, x|$x.side, x|$x.quantity, x|$x.price, x|$x.status], ['OrderId', 'Side', 'Quantity', 'Price', 'Status'])",
            mapping="TradingMapping",
            runtime="TradingRuntime"
        )
    model.add(orders_service)

    # Traders service
    traders_service = Service("TradersService") \
        .pattern("/api/v1/traders") \
        .owners("trading-team") \
        .documentation("Traders API") \
        .single_execution(
            query="|Trader.all()->filter(t | $t.isActive == true)->project([x|$x.traderId, x|$x.fullName, x|$x.desk], ['TraderId', 'Name', 'Desk'])",
            mapping="TradingMapping",
            runtime="TradingRuntime"
        )
    model.add(traders_service)

    # Generate and print the Pure code
    print(model.to_pure())
    return model


def example_decorator_style():
    """
    Example 2: Using Python Decorators

    This style uses Python class syntax with type annotations,
    making it feel more natural for Python developers.
    """
    print("\n" + "=" * 70)
    print("Example 2: Decorator Style (Pythonic)")
    print("=" * 70)

    # Define classes using decorators
    @pure_class(package="hr::model")
    class Employee:
        """An employee in the HR system."""
        employee_id: str
        first_name: str
        last_name: str
        email: str
        hire_date: date
        salary: Optional[float]
        skills: List[str]
        is_manager: bool = False

    @pure_class(package="hr::model")
    class Department:
        """A department in the organization."""
        department_id: str
        name: str
        budget: float
        location: Optional[str]

    # Create model and add decorated classes
    model = PureModel("hr::model")
    model.add(Employee)
    model.add(Department)

    # Generate and print
    print(model.to_pure())
    return model


def example_factory_functions():
    """
    Example 3: Using Factory Functions

    Factory functions provide a concise way to create elements
    when you don't need the full builder flexibility.
    """
    print("\n" + "=" * 70)
    print("Example 3: Factory Functions")
    print("=" * 70)

    model = PureModel("logistics::model")

    # Create a measure using factory
    distance = measure(
        "Distance",
        canonical=("Meter", "$x"),
        units={
            "Kilometer": "$x * 1000",
            "Mile": "$x * 1609.34",
            "Foot": "$x * 0.3048",
        },
        package="logistics::model"
    )
    model.add(distance)

    # Create a simple service using factory
    tracking_svc = service(
        "TrackingService",
        pattern="/api/tracking",
        query="|Shipment.all()->project([x|$x.trackingId, x|$x.status], ['ID', 'Status'])",
        mapping="LogisticsMapping",
        runtime="LogisticsRuntime",
        owners=["logistics-team"],
        documentation="Package tracking API",
        package="logistics::model"
    )
    model.add(tracking_svc)

    print(model.to_pure())
    return model


def example_inline_model():
    """
    Example 4: Inline Model Building

    Build the model using the PureModel's inline methods
    for a more fluent experience.
    """
    print("\n" + "=" * 70)
    print("Example 4: Inline Model Building")
    print("=" * 70)

    model = pure_model(
        package="inventory::model",
        imports=["meta::pure::profiles::*"]
    )

    # Build elements inline
    model.enum("ProductCategory") \
        .with_values("ELECTRONICS", "CLOTHING", "FOOD", "FURNITURE")

    model.class_("Product") \
        .with_property("sku", str) \
        .with_property("name", str) \
        .with_property("category", "ProductCategory") \
        .with_property("price", float) \
        .with_property("stock_quantity", int) \
        .with_derived("isInStock", bool, "$this.stockQuantity > 0")

    model.class_("Warehouse") \
        .with_property("warehouseId", str) \
        .with_property("location", str) \
        .with_property("capacity", int)

    model.association("Warehouse_Product") \
        .add_end("products", "Product", "*") \
        .add_end("warehouse", "Warehouse", "0..1")

    model.function("getLowStockProducts") \
        .with_param("products", "Product", "*") \
        .with_param("threshold", int) \
        .returns("Product", "*") \
        .body("$products->filter(p | $p.stockQuantity < $threshold)")

    print(model.to_pure())
    return model


def main():
    """Run all examples."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  PURE DSL FOR LEGEND ENGINE - COMPREHENSIVE EXAMPLES  ".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70 + "\n")

    # Run examples
    example_builder_style()
    example_decorator_style()
    example_factory_functions()
    example_inline_model()

    print("\n" + "=" * 70)
    print("All examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
