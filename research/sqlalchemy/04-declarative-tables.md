# SQLAlchemy Declarative Table Mapping

Here are the key patterns and best practices for declarative table mapping in SQLAlchemy 2.0:

## 1. Basic Declarative Table Configuration
```python
class User(Base):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
```

## 2. Type Annotation Features
- Use `Mapped[]` for type hinting
- Automatically derive column types from Python type annotations
- Support for optional types using `Optional[]`

## 3. Advanced Column Configuration
```python
class User(Base):
    __tablename__ = "user"
    
    # Deferred column loading
    bio: Mapped[str] = mapped_column(deferred=True)
    
    # Custom column naming
    user_id: Mapped[int] = mapped_column("id", primary_key=True)
```

## 4. Enum and Literal Type Mapping
```python
class Status(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Record(Base):
    status: Mapped[Status]  # Automatically maps to Enum type
```

## 5. Reflection Strategies
- Use `DeferredReflection` for delayed table reflection
- Use `Automap` for automated class generation from database schema

## Key Best Practices
- Leverage type annotations for concise schema definition
- Use `Mapped[]` for type safety
- Customize column properties as needed
- Consider reflection techniques for existing databases