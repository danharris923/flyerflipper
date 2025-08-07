# SQLAlchemy Async Patterns

Here are key async SQLAlchemy patterns and AsyncSession usage examples:

## 1. Basic AsyncSession Setup
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Create async engine
engine = create_async_engine("postgresql+asyncpg://user:pass@host/db")

# Create async session factory
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def main():
    async with async_session() as session:
        async with session.begin():
            # Perform database operations
            session.add(new_object)
            await session.commit()
```

## 2. Key AsyncSession Characteristics
- Not thread-safe: "A single instance of AsyncSession is not safe for use in multiple, concurrent tasks"
- Requires explicit await for database operations
- Uses async context managers for transactions

## 3. Preventing Implicit I/O
```python
# Use AsyncAttrs for lazy-loading relationships
class Base(AsyncAttrs, DeclarativeBase):
    pass

# Access relationships as awaitables
a1 = await session.scalars(select(A)).one()
for b1 in await a1.awaitable_attrs.bs:
    print(b1)
```

## 4. Streaming Results
```python
async with engine.connect() as conn:
    async_result = await conn.stream(select(table))
    async for row in async_result:
        print(row)
```

## 5. Running Synchronous Code
```python
def sync_function(session):
    # Traditional synchronous SQLAlchemy code
    result = session.execute(select(Model))

async def async_main():
    async with AsyncSession(engine) as session:
        await session.run_sync(sync_function)
```

## Key Recommendations:
- Use `async_sessionmaker` for consistent session configuration
- Set `expire_on_commit=False` to access attributes after commit
- Use `AsyncAttrs` or explicit eager loading to manage relationships
- Leverage `run_sync()` for integrating synchronous code

## FastAPI Integration Pattern
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Engine setup (usually in database.py)
engine = create_async_engine("sqlite+aiosqlite:///./test.db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Usage in FastAPI endpoint
@app.post("/users/")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(name=user.name)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```