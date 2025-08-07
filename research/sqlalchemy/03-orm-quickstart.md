# SQLAlchemy ORM Quickstart Guide

## Model Definition
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[str | None]
    
    addresses: Mapped[list["Address"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )

class Address(Base):
    __tablename__ = "address"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    
    user: Mapped[User] = relationship(back_populates="addresses")
```

## Engine and Session Setup
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Create database engine
engine = create_engine("sqlite://", echo=True)

# Create tables
Base.metadata.create_all(engine)

# Create session
with Session(engine) as session:
    # Insert data
    user = User(name="spongebob", fullname="Spongebob Squarepants")
    session.add(user)
    session.commit()
```

## Basic Querying
```python
from sqlalchemy import select

# Simple select
stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))
users = session.scalars(stmt).all()

# Select with join
stmt = (
    select(Address)
    .join(Address.user)
    .where(User.name == "sandy")
)
address = session.scalars(stmt).one()
```

## Key Patterns
- Use `DeclarativeBase` for model definitions
- Leverage `Mapped[]` type annotations for columns
- Use `relationship()` for defining associations
- Create sessions with context managers
- Use `select()` for modern query construction