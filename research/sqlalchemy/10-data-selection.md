# SQLAlchemy Data Selection Patterns

Here's a summary of SQLAlchemy SELECT statement techniques:

## Key SELECT Statement Patterns:

### 1. Basic Selection
- Select entire table: `select(user_table)`
- Select specific columns: `select(user_table.c.name, user_table.c.fullname)`
- ORM selection: `select(User)`

### 2. Filtering Techniques
- Where clause: `select(user_table).where(user_table.c.name == "spongebob")`
- Multiple conditions: `select(user_table).where(condition1, condition2)`
- Logical operators: Use `and_()`, `or_()` functions

### 3. Joining Tables
- Simple join: `select(user_table.c.name, address_table.c.email_address).join(address_table)`
- Explicit join: `select(...).join_from(user_table, address_table)`
- Outer joins: Use `isouter=True` or `full=True` parameters

### 4. Advanced Querying
- Subqueries: Use `.subquery()` method
- Unions: `union_all(stmt1, stmt2)`
- Aggregate functions: `func.count()`, `func.sum()`
- Ordering: `.order_by(user_table.c.name)`
- Grouping: `.group_by(User.name)`

### 5. ORM-Specific Techniques
- Select entities: `session.scalars(select(User))`
- Filtering ORM attributes: `select(User).where(User.name == "spongebob")`

## Practical Examples:

### Basic Filtering
```python
from sqlalchemy import select

# Simple where clause
stmt = select(User).where(User.name == "spongebob")
user = session.scalar(stmt)

# Multiple conditions
stmt = select(User).where(
    User.name == "spongebob",
    User.fullname.like("%Squarepants%")
)
```

### Joins and Relationships
```python
# Join with explicit condition
stmt = (
    select(User.name, Address.email_address)
    .join(Address)
    .where(User.name == "sandy")
)

# Using relationship for joining
stmt = (
    select(Address)
    .join(Address.user)
    .where(User.name == "sandy")
)
```

### Aggregation
```python
from sqlalchemy import func

# Count records
stmt = select(func.count(User.id))
count = session.scalar(stmt)

# Group by with aggregation
stmt = (
    select(User.name, func.count(Address.id))
    .join(Address)
    .group_by(User.name)
)
```

### Advanced Filtering
```python
# Using IN clause
stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))

# Using OR conditions
from sqlalchemy import or_
stmt = select(User).where(
    or_(User.name == "spongebob", User.name == "sandy")
)

# Using LIKE for pattern matching
stmt = select(User).where(User.fullname.like("%Squarepants%"))
```

The tutorial emphasizes SQLAlchemy's flexible, "generative" approach to constructing SQL queries.