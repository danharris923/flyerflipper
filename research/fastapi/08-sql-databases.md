# FastAPI SQL Database Integration

## Overview
- FastAPI supports SQL databases through SQLModel, which is built on SQLAlchemy and Pydantic
- Supports multiple databases: PostgreSQL, MySQL, SQLite, Oracle, Microsoft SQL Server
- Uses SQLite in examples for simplicity

## Core Components

### 1. Database Model
- Created using SQLModel with `table=True`
- Defines database schema and table structure
- Supports field configurations like primary keys and indexes

```python
from sqlmodel import SQLModel, Field

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
```

### 2. Database Engine
- Creates a connection to the database
- Uses `create_engine()` to establish database connection
- Configurable for different database types

```python
from sqlmodel import create_engine
import os

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
```

### 3. Session Management
- Uses dependency injection to manage database sessions
- Creates a new session for each request
- Handles database transactions (commit, rollback)

```python
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/heroes/")
def read_heroes(session: Session = Depends(get_session)):
    heroes = session.exec(select(Hero)).all()
    return heroes
```

## Database Setup

### Creating Tables
```python
from sqlmodel import SQLModel

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
```

## CRUD Operations

### Create
```python
@app.post("/heroes/")
def create_hero(hero: Hero, session: Session = Depends(get_session)):
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero
```

### Read (Single)
```python
@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero
```

### Read (Multiple)
```python
from sqlmodel import select

@app.get("/heroes/")
def read_heroes(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```

### Update
```python
@app.patch("/heroes/{hero_id}")
def update_hero(
    hero_id: int,
    hero: HeroUpdate,
    session: Session = Depends(get_session)
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    hero_data = hero.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)
    
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

### Delete
```python
@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    session.delete(hero)
    session.commit()
    return {"ok": True}
```

## Best Practices
- Use dependency injection for session management
- Handle database errors with appropriate HTTP exceptions
- Use SQLModel for type safety and automatic validation
- Implement proper error handling for database operations
- Use database migrations for production deployments
- Consider connection pooling for high-traffic applications

## Database Configuration Examples

### PostgreSQL
```python
database_url = "postgresql://user:password@postgresserver/db"
engine = create_engine(database_url)
```

### MySQL
```python
database_url = "mysql://user:password@server/db"
engine = create_engine(database_url)
```

The tutorial emphasizes flexibility and ease of database integration in FastAPI applications.