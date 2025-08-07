# SQLAlchemy 2.0 Research Documentation

This directory contains comprehensive SQLAlchemy 2.0 documentation scraped from official sources, organized for quick reference during development.

## 📁 Documentation Files

### Core Foundation
- **[01-overview.md](./01-overview.md)** - SQLAlchemy 2.0 architecture, key features, and learning path
- **[02-tutorial.md](./02-tutorial.md)** - Tutorial structure and learning approach
- **[06-engines.md](./06-engines.md)** - Engine configuration, connection pooling, and logging

### ORM Essentials
- **[03-orm-quickstart.md](./03-orm-quickstart.md)** - Quick start guide with model definition and basic operations
- **[04-declarative-tables.md](./04-declarative-tables.md)** - Declarative mapping patterns and type annotations
- **[05-session-basics.md](./05-session-basics.md)** - Session lifecycle, transaction handling, and best practices
- **[09-relationships.md](./09-relationships.md)** - Relationship configuration patterns (One-to-Many, Many-to-Many, etc.)

### Querying & Data Operations
- **[10-data-selection.md](./10-data-selection.md)** - SELECT statements, filtering, joins, and aggregation

### Database-Specific & Advanced
- **[07-sqlite-dialect.md](./07-sqlite-dialect.md)** - SQLite-specific configuration and connection patterns
- **[08-async-patterns.md](./08-async-patterns.md)** - Async SQLAlchemy with AsyncSession and FastAPI integration

## 🔑 Key Takeaways for FastAPI + SQLite Projects

### Quick Setup Pattern
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Sync version
engine = create_engine("sqlite:///./app.db", echo=True)
SessionLocal = sessionmaker(bind=engine)

# Async version  
async_engine = create_async_engine("sqlite+aiosqlite:///./app.db")
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
```

### Model Definition Best Practices
- Use `Mapped[]` type annotations
- Leverage `relationship()` with `back_populates`
- Use `mapped_column()` for column configuration
- Define `__tablename__` explicitly

### Session Management
- Always use context managers (`with Session()`)
- Create sessions at operation boundaries, not globally
- Handle transactions explicitly with `commit()` and `rollback()`
- Sessions are **not thread-safe**

### SQLite Specific Notes
- File path: `sqlite:///path/to/database.db`
- In-memory: `sqlite:///:memory:`
- Uses `QueuePool` for file databases, `SingletonThreadPool` for memory
- Consider transaction configuration for proper handling

### Async Integration
- Use `AsyncSession` for async operations
- Set `expire_on_commit=False` for accessing attributes after commit
- Use `await` for all database operations
- Integrate with FastAPI using dependency injection

## 🚀 Ready-to-Use Patterns

All documentation includes practical examples and code snippets that can be directly applied to your FastAPI + SQLAlchemy + SQLite projects. Refer to specific files for detailed implementation patterns.

---
*Documentation scraped from official SQLAlchemy 2.0 docs on 2025-08-06*