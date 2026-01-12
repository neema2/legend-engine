"""
Comprehensive tests for Pure DSL.

Run with: python -m pytest test_pure_dsl.py -v
"""

import sys
import os

# Add the source directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../main/python'))

from typing import List, Optional
from pure_dsl import (
    # Core
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
    # Model
    PureModel,
    pure_model,
)


class TestMultiplicity:
    """Tests for Multiplicity class."""

    def test_one(self):
        m = Multiplicity.one()
        assert m.to_pure() == "[1]"

    def test_zero_one(self):
        m = Multiplicity.zero_one()
        assert m.to_pure() == "[0..1]"

    def test_many(self):
        m = Multiplicity.many()
        assert m.to_pure() == "[*]"

    def test_one_many(self):
        m = Multiplicity.one_many()
        assert m.to_pure() == "[1..*]"

    def test_custom_range(self):
        m = Multiplicity(2, 5)
        assert m.to_pure() == "[2..5]"

    def test_from_string(self):
        assert Multiplicity.from_string("1").to_pure() == "[1]"
        assert Multiplicity.from_string("0..1").to_pure() == "[0..1]"
        assert Multiplicity.from_string("*").to_pure() == "[*]"
        assert Multiplicity.from_string("1..*").to_pure() == "[1..*]"


class TestProfile:
    """Tests for Profile class."""

    def test_simple_profile(self):
        p = Profile("doc")
        p.with_stereotypes("deprecated", "internal")
        p.with_tags("doc", "since")

        pure = p.to_pure()
        assert "Profile doc" in pure
        assert "stereotypes: [deprecated, internal];" in pure
        assert "tags: [doc, since];" in pure

    def test_qualified_profile(self):
        p = Profile("my::package::MyProfile")
        p.with_stereotype("flag")

        pure = p.to_pure()
        assert "Profile my::package::MyProfile" in pure


class TestEnum:
    """Tests for Enum class."""

    def test_simple_enum(self):
        e = Enum("Status")
        e.with_values("ACTIVE", "INACTIVE", "PENDING")

        pure = e.to_pure()
        assert "Enum Status" in pure
        assert "ACTIVE" in pure
        assert "INACTIVE" in pure
        assert "PENDING" in pure

    def test_enum_with_docs(self):
        e = Enum("Virus")
        e.with_doc("List of known viruses")
        e.with_value("SARS", doc="SARS virus")
        e.with_value("COVID19", doc="COVID-19 virus")

        pure = e.to_pure()
        assert "doc.doc = 'List of known viruses'" in pure
        assert "doc.doc = 'SARS virus'" in pure

    def test_qualified_enum(self):
        e = Enum("my::domain::OrderStatus")
        e.with_values("NEW", "PROCESSING", "SHIPPED")

        pure = e.to_pure()
        assert "Enum my::domain::OrderStatus" in pure


class TestClass:
    """Tests for Class class."""

    def test_simple_class(self):
        c = Class("Person")
        c.with_property("firstName", str)
        c.with_property("lastName", str)

        pure = c.to_pure()
        assert "Class Person" in pure
        assert "firstName: String[1];" in pure
        assert "lastName: String[1];" in pure

    def test_class_with_optional_property(self):
        c = Class("Person")
        c.with_property("age", int, multiplicity="0..1")

        pure = c.to_pure()
        assert "age: Integer[0..1];" in pure

    def test_class_with_list_property(self):
        c = Class("Person")
        c.with_property("emails", str, multiplicity="*")

        pure = c.to_pure()
        assert "emails: String[*];" in pure

    def test_class_with_extends(self):
        c = Class("Employee")
        c.extends("Person", "Entity")

        pure = c.to_pure()
        assert "Class Employee extends Person, Entity" in pure

    def test_class_with_derived_property(self):
        c = Class("Person")
        c.with_property("firstName", str)
        c.with_property("lastName", str)
        c.with_derived("fullName", str, "$this.firstName + ' ' + $this.lastName")

        pure = c.to_pure()
        assert "fullName()" in pure
        assert "$this.firstName + ' ' + $this.lastName" in pure
        assert "String[1]" in pure

    def test_class_with_constraint(self):
        c = Class("Person")
        c.with_property("age", int)
        c.with_constraint("$this.age >= 0", name="validAge")

        pure = c.to_pure()
        assert "validAge: $this.age >= 0" in pure

    def test_class_with_aggregation(self):
        c = Class("Order")
        c.with_property("items", "OrderItem", multiplicity="*", aggregation=AggregationKind.COMPOSITE)

        pure = c.to_pure()
        assert "(composite) items:" in pure

    def test_class_with_doc(self):
        c = Class("Person")
        c.with_doc("Represents a person in the system")
        c.with_property("name", str)

        pure = c.to_pure()
        assert "doc.doc = 'Represents a person in the system'" in pure

    def test_snake_case_conversion(self):
        c = Class("Person")
        c.with_property("first_name", str)
        c.with_property("last_name", str)

        pure = c.to_pure()
        assert "firstName:" in pure
        assert "lastName:" in pure


class TestAssociation:
    """Tests for Association class."""

    def test_simple_association(self):
        a = Association("FirmPerson")
        a.add_end("employees", "Person", "*")
        a.add_end("employer", "Firm", "0..1")

        pure = a.to_pure()
        assert "Association FirmPerson" in pure
        assert "employees: Person[*];" in pure
        assert "employer: Firm[0..1];" in pure

    def test_association_with_qualified_property(self):
        a = Association("FirmPerson")
        a.add_end("employees", "Person", "*")
        a.add_end("employer", "Firm", "0..1")
        a.with_qualified_property(
            "seniorEmployees",
            "Person",
            "$this.employees->filter(e | $e.age > 40)",
            multiplicity="*"
        )

        pure = a.to_pure()
        assert "seniorEmployees()" in pure
        assert "filter" in pure


class TestFunction:
    """Tests for Function class."""

    def test_simple_function(self):
        f = Function("greet")
        f.with_param("name", str)
        f.returns(str)
        f.body("'Hello, ' + $name")

        pure = f.to_pure()
        assert "function greet" in pure
        assert "name: String[1]" in pure
        assert "String[1]" in pure
        assert "'Hello, ' + $name" in pure

    def test_function_with_multiple_params(self):
        f = Function("add")
        f.with_param("a", int)
        f.with_param("b", int)
        f.returns(int)
        f.body("$a + $b")

        pure = f.to_pure()
        assert "a: Integer[1], b: Integer[1]" in pure

    def test_native_function(self):
        f = Function("nativeOp")
        f.with_param("x", int)
        f.returns(int)
        f.native()

        pure = f.to_pure()
        assert "native function nativeOp" in pure
        assert pure.strip().endswith(";")


class TestMeasure:
    """Tests for Measure class."""

    def test_simple_measure(self):
        m = Measure("Mass")
        m.with_canonical_unit("Gram", "x", "$x")
        m.with_unit("Kilogram", "x", "$x * 1000")
        m.with_unit("Pound", "x", "$x * 453.59")

        pure = m.to_pure()
        assert "Measure Mass" in pure
        assert "*Gram: x -> $x;" in pure
        assert "Kilogram: x -> $x * 1000;" in pure
        assert "Pound: x -> $x * 453.59;" in pure


class TestService:
    """Tests for Service class."""

    def test_simple_service(self):
        s = Service("PersonService")
        s.pattern("/api/persons")
        s.owners("user1", "user2")
        s.documentation("Get all persons")
        s.single_execution(
            query="|Person.all()",
            mapping="PersonMapping",
            runtime="H2Runtime"
        )

        pure = s.to_pure()
        assert "Service PersonService" in pure
        assert "pattern: '/api/persons';" in pure
        assert "'user1'" in pure
        assert "'user2'" in pure
        assert "execution: Single" in pure
        assert "query: |Person.all();" in pure


class TestPureModel:
    """Tests for PureModel class."""

    def test_complete_model(self):
        model = PureModel("my::domain")

        # Add profile
        profile = Profile("MyProfile")
        profile.with_stereotypes("flag")
        profile.with_tags("doc")
        model.add(profile)

        # Add enum
        status = Enum("Status")
        status.with_values("ACTIVE", "INACTIVE")
        model.add(status)

        # Add class
        person = Class("Person")
        person.with_property("name", str)
        person.with_property("status", "Status")
        model.add(person)

        pure = model.to_pure()

        # Check order and content
        assert "Profile my::domain::MyProfile" in pure
        assert "Enum my::domain::Status" in pure
        assert "Class my::domain::Person" in pure

        # Profiles should come before classes
        profile_pos = pure.find("Profile")
        class_pos = pure.find("Class")
        assert profile_pos < class_pos

    def test_model_with_imports(self):
        model = PureModel("my::domain")
        model.add_import("meta::pure::profiles::*")

        person = Class("Person")
        person.with_property("name", str)
        model.add(person)

        pure = model.to_pure()
        assert "import meta::pure::profiles::*;" in pure


class TestDecoratorStyle:
    """Tests for decorator-based class definitions."""

    def test_pure_class_decorator(self):
        @pure_class
        class Person:
            """A person in the system."""
            first_name: str
            last_name: str
            age: Optional[int]

        pure = Person.to_pure()
        assert "Class Person" in pure
        assert "firstName: String[1];" in pure
        assert "lastName: String[1];" in pure
        assert "age: Integer[0..1];" in pure
        assert "doc.doc = 'A person in the system.'" in pure

    def test_pure_class_with_list(self):
        @pure_class
        class Person:
            emails: List[str]

        pure = Person.to_pure()
        assert "emails: String[*];" in pure


class TestLambdaExpr:
    """Tests for lambda expression helper."""

    def test_simple_lambda(self):
        expr = lambda_expr([("x", int)], "$x + 1")
        assert expr == "{x: Integer[1] | $x + 1}"

    def test_multi_param_lambda(self):
        expr = lambda_expr([("a", str), ("b", str)], "$a + $b")
        assert expr == "{a: String[1], b: String[1] | $a + $b}"


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""

    def test_firm_person_model(self):
        """Test a complete Firm-Person domain model."""
        model = PureModel("model::domain")

        # Enum
        employment_type = Enum("EmploymentType")
        employment_type.with_values("FULL_TIME", "PART_TIME", "CONTRACT")
        model.add(employment_type)

        # Person class
        person = Class("Person")
        person.with_property("firstName", str)
        person.with_property("lastName", str)
        person.with_property("age", int, multiplicity="0..1")
        person.with_property("employmentType", "EmploymentType")
        person.with_derived(
            "fullName",
            str,
            "$this.firstName + ' ' + $this.lastName"
        )
        person.with_constraint("$this.age >= 0", name="validAge")
        model.add(person)

        # Firm class
        firm = Class("Firm")
        firm.with_property("legalName", str)
        firm.with_property("yearFounded", int, multiplicity="0..1")
        firm.with_derived(
            "averageEmployeeAge",
            float,
            "$this.employees.age->average()",
            multiplicity="0..1"
        )
        model.add(firm)

        # Association
        firm_person = Association("Firm_Person")
        firm_person.add_end("employees", "Person", "*")
        firm_person.add_end("employer", "Firm", "0..1")
        model.add(firm_person)

        pure = model.to_pure()

        # Verify all elements present
        assert "Enum model::domain::EmploymentType" in pure
        assert "Class model::domain::Person" in pure
        assert "Class model::domain::Firm" in pure
        assert "Association model::domain::Firm_Person" in pure
        assert "fullName()" in pure
        assert "averageEmployeeAge()" in pure
        assert "validAge:" in pure


def run_demo():
    """Run a demonstration of the Pure DSL capabilities."""
    print("=" * 60)
    print("Pure DSL Demonstration")
    print("=" * 60)

    # Create a complete model
    model = PureModel("demo::trading")

    # Profile
    profile = Profile("TradingProfile")
    profile.with_stereotypes("critical", "audited")
    profile.with_tags("owner", "version")
    model.add(profile)

    # Enums
    order_status = Enum("OrderStatus")
    order_status.with_doc("Status of a trading order")
    order_status.with_value("NEW", doc="Order just created")
    order_status.with_value("PENDING", doc="Order awaiting execution")
    order_status.with_value("FILLED", doc="Order fully executed")
    order_status.with_value("CANCELLED", doc="Order was cancelled")
    model.add(order_status)

    # Classes
    trader = Class("Trader")
    trader.with_doc("A trader in the system")
    trader.with_property("traderId", str)
    trader.with_property("firstName", str)
    trader.with_property("lastName", str)
    trader.with_property("desk", str, multiplicity="0..1")
    trader.with_derived("fullName", str, "$this.firstName + ' ' + $this.lastName")
    model.add(trader)

    order = Class("Order")
    order.with_doc("A trading order")
    order.with_property("orderId", str)
    order.with_property("symbol", str)
    order.with_property("quantity", int)
    order.with_property("price", float)
    order.with_property("status", "OrderStatus")
    order.with_property("createdAt", "DateTime")
    order.with_derived(
        "totalValue",
        float,
        "$this.quantity * $this.price"
    )
    order.with_constraint("$this.quantity > 0", name="positiveQuantity")
    order.with_constraint("$this.price > 0", name="positivePrice")
    model.add(order)

    # Association
    trader_orders = Association("TraderOrders")
    trader_orders.add_end("orders", "Order", "*")
    trader_orders.add_end("trader", "Trader", "1")
    model.add(trader_orders)

    # Function
    calc_total = Function("calculatePortfolioValue")
    calc_total.with_param("orders", "Order", "*")
    calc_total.returns(float)
    calc_total.body("$orders.totalValue->sum()")
    model.add(calc_total)

    # Service
    order_service = Service("OrderService")
    order_service.pattern("/api/orders")
    order_service.owners("trading-team")
    order_service.documentation("Trading orders API")
    order_service.single_execution(
        query="|Order.all()->project([x|$x.orderId, x|$x.symbol, x|$x.status], ['ID', 'Symbol', 'Status'])",
        mapping="OrderMapping",
        runtime="TradingRuntime"
    )
    model.add(order_service)

    # Generate and print
    print(model.to_pure())


if __name__ == "__main__":
    # Run demo
    run_demo()

    # Run tests
    print("\n" + "=" * 60)
    print("Running Tests...")
    print("=" * 60)

    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
