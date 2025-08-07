# SQLAlchemy Relationship Configuration

Based on the SQLAlchemy 2.0 documentation for Relationship Configuration, here are key insights:

## Key Relationship Configuration Patterns:

### 1. Basic Relationship Types
- One-to-Many
- Many-to-One
- One-to-One
- Many-to-Many

### 2. Advanced Relationship Techniques:
- Configuring custom join conditions
- Handling multiple join paths
- Creating custom foreign key conditions
- Supporting self-referential relationships
- Managing large collections

### 3. Collection Management Strategies:
- Dynamic relationship loaders
- Write-only relationships
- Custom collection implementations
- Dictionary-based collections

### 4. Important Relationship Configuration Parameters:
- `uselist`: Controls whether relationship is a collection or scalar
- `secondary`: Defines many-to-many association tables
- `foreign_keys`: Explicitly specify foreign key columns
- `viewonly`: Creates read-only relationship mappings

### 5. Relationship Configuration Best Practices:
- Use late evaluation for relationship arguments
- Carefully design join conditions
- Choose appropriate collection types
- Consider performance with large collections

## Example Relationship Patterns:

### One-to-Many
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )

class Address(Base):
    __tablename__ = "addresses"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship(back_populates="addresses")
```

### Many-to-Many
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    keywords: Mapped[list["Keyword"]] = relationship(
        secondary="user_keyword_association",
        back_populates="users"
    )

class Keyword(Base):
    __tablename__ = "keywords"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    users: Mapped[list["User"]] = relationship(
        secondary="user_keyword_association",
        back_populates="keywords"
    )

# Association table
user_keyword_association = Table(
    "user_keyword_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id")),
    Column("keyword_id", ForeignKey("keywords.id"))
)
```

The documentation emphasizes flexibility in defining complex database relationships using SQLAlchemy's ORM relationship configuration.