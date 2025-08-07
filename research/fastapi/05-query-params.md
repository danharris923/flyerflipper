# FastAPI Query Parameters

## Overview
- Automatically detected as parameters not part of the path
- Converted and validated based on Python type hints
- Can have default values and be optional
- Supports type conversion (e.g., strings, booleans)

## Basic Query Parameters with Defaults
```python
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

## Optional Parameters
```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

## Boolean Type Conversion
```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, short: bool = False):
    # 'short' will be True for values like 1, True, true, on, yes
    item = {"item_id": item_id}
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
```

## Required Query Parameters
```python
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    # 'needy' is a required parameter
    item = {"item_id": item_id, "needy": needy}
    return item
```

## Multiple Path and Query Parameters
```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
```

## Key Benefits
- Automatic type conversion
- Data validation
- Comprehensive documentation
- Flexible parameter handling
- Clear error messages for invalid inputs
- Interactive API documentation generation

## Type Support
- `str`: String values
- `int`: Integer values
- `float`: Float values
- `bool`: Boolean values (supports various true/false representations)
- `list`: List of values
- Custom types via Pydantic models