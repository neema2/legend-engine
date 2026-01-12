# Pure DSL for Legend Engine

A Pythonic, type-safe DSL for generating Pure code. Define Pure language constructs using natural Python syntax with type annotations, then generate valid Pure code for Legend Engine.

## Features

- **Native Python Syntax**: Define Pure classes using Python class definitions
- **Type Safety**: Use Python type annotations that map directly to Pure types
- **Expression Building**: Build Pure expressions using Python operators
- **Automatic Conversion**: snake_case -> camelCase, Python types -> Pure types
- **Full Pure Support**: Classes, Enums, Associations, Functions, Profiles, Measures, Services

## Installation

```bash
cd legend-engine-xts-python/legend-engine-xt-python-pure-dsl
pip install -e .
```

## Quick Start

### Define Pure Classes with Python Syntax

```python
from pure_dsl import PureClass, PureEnum, derived, constraint
from typing import Optional, List

# Define an Enum
class OrderStatus(PureEnum):
    '''Status of an order.'''
    NEW = "NEW"
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"

# Define a Class with properties, derived properties, and constraints
class Person(PureClass):
    '''A person in the system.'''

    # Properties - Python types map automatically to Pure types
    first_name: str               # -> String[1]
    last_name: str                # -> String[1]
    age: Optional[int]            # -> Integer[0..1]
    emails: List[str]             # -> String[*]
    is_active: bool = True        # -> Boolean[1] with default

    # Derived property - use Python expressions
    @derived
    def full_name(this) -> str:
        return this.first_name + " " + this.last_name

    # Constraint - returns boolean expression
    @constraint
    def valid_age(this) -> bool:
        return this.age >= 0

# Generate Pure code
print(Person.to_pure())
```

**Output:**
```pure
Class {doc.doc = 'A person in the system.'} Person
[
  valid_age: $this.age >= 0
]
{
  firstName: String[1];
  lastName: String[1];
  age: Integer[0..1];
  emails: String[*];
  isActive: Boolean[1] = true;
  fullName() {$this.firstName + ' ' + $this.lastName}: String[1];
}
```

## Type Mapping

| Python Type | Pure Type |
|-------------|-----------|
| `str` | `String[1]` |
| `int` | `Integer[1]` |
| `float` | `Float[1]` |
| `bool` | `Boolean[1]` |
| `date` | `Date[1]` |
| `datetime` | `DateTime[1]` |
| `Decimal` | `Decimal[1]` |
| `Optional[X]` | `X[0..1]` |
| `List[X]` | `X[*]` |
| `ZeroOne[X]` | `X[0..1]` |
| `Many[X]` | `X[*]` |
| `OneMany[X]` | `X[1..*]` |

For Pure class references, use string annotations: `"my::package::MyClass"`

## Expression Building

Build Pure expressions using Python operators:

```python
class Order(PureClass):
    quantity: int
    price: float
    status: "OrderStatus"
    filled_quantity: int = 0

    @derived
    def total_value(this) -> float:
        return this.quantity * this.price

    @derived
    def remaining_quantity(this) -> int:
        return this.quantity - this.filled_quantity

    @constraint
    def positive_quantity(this) -> bool:
        return this.quantity > 0

    @constraint(message="'Filled quantity cannot exceed total'")
    def valid_fill(this) -> bool:
        return this.filled_quantity <= this.quantity
```

### Collection Operations

```python
class Trader(PureClass):
    trading_limit: float

    @derived
    def active_orders(this) -> List["Order"]:
        return this.orders.filter(
            lambda o: o.status != "OrderStatus.CANCELLED"
        )

    @derived
    def total_order_value(this) -> float:
        return this.orders.map(lambda o: o.total_value).sum()
```

### String Operations

```python
@constraint
def valid_email(this) -> bool:
    return this.email.contains("@") & (this.email.length() > 5)
```

## Class Inheritance

```python
class Entity(PureClass):
    '''Base entity class.'''
    id: str
    created_at: date

class Person(PureClass, extends="Entity"):
    '''A person extending Entity.'''
    first_name: str
    last_name: str
```

## Associations

```python
from pure_dsl import PureAssociation

# Format: (target_type, property_name, multiplicity)
firm_person = PureAssociation(
    "Firm_Person",
    ("Person", "employees", "[*]"),    # Property "employees" of type Person[*]
    ("Firm", "employer", "[0..1]"),    # Property "employer" of type Firm[0..1]
)

print(firm_person.to_pure())
```

**Output:**
```pure
Association Firm_Person
{
  employees: Person[*];
  employer: Firm[0..1];
}
```

## Builder Pattern (Alternative)

For more control, use the builder pattern:

```python
from pure_dsl import Class, Enum, Association, PureModel

model = PureModel("my::domain")

person = Class("Person") \
    .with_property("firstName", str) \
    .with_property("lastName", str) \
    .with_property("age", int, multiplicity="0..1") \
    .with_derived("fullName", str, "$this.firstName + ' ' + $this.lastName") \
    .with_constraint("$this.age >= 0", name="validAge")

model.add(person)
print(model.to_pure())
```

## Additional Constructs

### Functions

```python
from pure_dsl import Function

calc_total = Function("calculateTotal") \
    .with_param("orders", "Order", "*") \
    .returns(float) \
    .body("$orders.totalValue->sum()")
```

### Profiles

```python
from pure_dsl import Profile

trading = Profile("TradingProfile") \
    .with_stereotypes("critical", "audited") \
    .with_tags("owner", "version")
```

### Measures

```python
from pure_dsl import Measure

mass = Measure("Mass") \
    .with_canonical_unit("Gram", "x", "$x") \
    .with_unit("Kilogram", "x", "$x * 1000") \
    .with_unit("Pound", "x", "$x * 453.59")
```

### Services

```python
from pure_dsl import Service

order_service = Service("OrderService") \
    .pattern("/api/orders") \
    .owners("trading-team") \
    .documentation("Trading Orders API") \
    .single_execution(
        query="|Order.all()->project([x|$x.orderId], ['ID'])",
        mapping="OrderMapping",
        runtime="H2Runtime"
    )
```

## Running Examples

```bash
python examples/pythonic_example.py
```

## License

Apache 2.0 - Same as Legend Engine
