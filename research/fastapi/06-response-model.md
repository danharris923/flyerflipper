# FastAPI Response Models

## Key Concepts
- Response models define the structure and validation of API responses
- Can use Pydantic models to specify return types and filter data
- Provides automatic documentation and type checking

## Return Type Annotations
- Specify response structure using type hints
- Can use Pydantic models, lists, dictionaries
- Example: `async def read_items() -> list[Item]:`

```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

@app.get("/items/")
async def read_items() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]
```

## Response Model Filtering
- Filter sensitive information from responses
- Create separate input and output models
- Use `response_model` parameter to control output

```python
class UserIn(BaseModel):
    username: str
    password: str  # Sensitive field
    email: str
    full_name: str | None = None

class UserOut(BaseModel):
    username: str  # Safe to return
    email: str
    full_name: str | None = None

@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn):
    return user  # Password automatically filtered out
```

## Response Model Parameters

### response_model_exclude_unset
```python
@app.get("/items/{item_id}", response_model=Item, response_model_exclude_unset=True)
async def read_item(item_id: str):
    # Omit default values from response
    return items[item_id]
```

### response_model_include and response_model_exclude
```python
@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    # Only include specified fields
    return items[item_id]

@app.get(
    "/items/{item_id}/public", 
    response_model=Item,
    response_model_exclude={"tax"}
)
async def read_item_public_data(item_id: str):
    # Exclude sensitive fields
    return items[item_id]
```

## Benefits
- **Automatic data validation**: Ensures response structure matches model
- **Enhanced security**: Filters sensitive information automatically
- **Clear API documentation**: Generates accurate OpenAPI schema
- **Type checking support**: IDE support and runtime validation
- **Data conversion**: Automatic serialization of complex objects

## Use Cases
- API versioning with different response models
- Role-based data filtering
- Protecting sensitive user information
- Ensuring consistent response structures
- Documentation generation