# FastAPI Request Body

## Overview
- Request bodies are data sent by the client to your API using HTTP methods like POST, PUT, PATCH
- FastAPI uses Pydantic models to declare, validate, and document request bodies
- Automatic JSON parsing, validation, and conversion to Python objects
- Generates interactive API documentation automatically

## Basic Pydantic Model
```python
from fastapi import FastAPI
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## Request Body with Path Parameters
```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.model_dump()}
```

## Request Body + Path + Query Parameters
```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item,
    q: str | None = None
):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
```

## Advanced Pydantic Models

### Nested Models
```python
class Image(BaseModel):
    url: str
    name: str

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Example JSON for nested model:
```json
{
    "name": "Foo",
    "description": "A very nice Item",
    "price": 35.4,
    "tax": 3.2,
    "tags": ["electronics", "gadgets"],
    "images": [
        {
            "url": "http://example.com/baz.jpg",
            "name": "The Foo live"
        }
    ]
}
```

## Field Validation and Configuration

### Using Field for Additional Validation
```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="The price must be greater than zero")
    tax: float | None = Field(None, ge=0)
    tags: set[str] = Field(set(), description="Set of tags")

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Field Validation Examples
```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr
    full_name: str | None = Field(None, max_length=100)
    age: int = Field(..., ge=0, le=120)
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

@app.post("/users/")
async def create_user(user: User):
    return user
```

## Multiple Request Bodies
```python
class Item(BaseModel):
    name: str
    description: str | None = None

class User(BaseModel):
    username: str
    full_name: str | None = None

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results
```

Expected JSON:
```json
{
    "item": {
        "name": "Foo",
        "description": "A very nice Item"
    },
    "user": {
        "username": "dave",
        "full_name": "Dave Grohl"
    }
}
```

## Request Body with Additional Validation

### Custom Validators
```python
from pydantic import BaseModel, validator

class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None

    @validator('name')
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('name must contain a space')
        return v.title()

    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Root Validators
```python
from pydantic import BaseModel, root_validator

class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None
    total: float | None = None

    @root_validator
    def calculate_total(cls, values):
        price = values.get('price')
        tax = values.get('tax')
        if price is not None and tax is not None:
            values['total'] = price + tax
        return values

@app.post("/items/")
async def create_item(item: Item):
    return item
```

## Response Integration

### Using Same Model for Request and Response
```python
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    # Process the item (save to database, etc.)
    processed_item = process_item(item)
    return processed_item
```

### Separate Models for Input and Output
```python
class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float
    created_at: datetime

@app.post("/items/", response_model=ItemResponse)
async def create_item(item: ItemCreate):
    # Create item with generated ID and timestamp
    new_item = create_item_in_db(item)
    return new_item
```

## Error Handling with Request Bodies

### Automatic Validation Errors
```python
from fastapi import HTTPException

@app.post("/items/")
async def create_item(item: Item):
    if item.price < 0:
        raise HTTPException(status_code=400, detail="Price cannot be negative")
    return item
```

### Custom Exception Handling
```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body}
    )
```

## File Uploads as Request Body

### Single File Upload
```python
from fastapi import File, UploadFile

@app.post("/files/")
async def create_file(file: UploadFile = File(...)):
    return {"filename": file.filename, "content_type": file.content_type}
```

### Multiple Files Upload
```python
@app.post("/files/")
async def create_files(files: list[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}
```

### Combined File Upload with Other Data
```python
class FileMetadata(BaseModel):
    title: str
    description: str | None = None

@app.post("/files/")
async def create_file_with_metadata(
    metadata: FileMetadata,
    file: UploadFile = File(...)
):
    return {
        "metadata": metadata,
        "filename": file.filename,
        "content_type": file.content_type
    }
```

## Key Features and Benefits

### Automatic Features
- **JSON Parsing**: Automatic conversion from JSON to Python objects
- **Data Validation**: Type checking and constraint validation
- **Error Messages**: Clear, detailed validation error messages
- **Documentation**: Automatic OpenAPI/Swagger documentation
- **IDE Support**: Full autocompletion and type checking

### Performance Benefits
- **Efficient Parsing**: Fast JSON parsing with validation
- **Memory Efficient**: Optimized object creation
- **Type Safety**: Compile-time and runtime type checking

## Best Practices
- Use descriptive field names and add documentation
- Implement appropriate validation constraints
- Separate input and output models when needed
- Handle validation errors gracefully
- Use nested models for complex data structures
- Add examples in field definitions for better documentation
- Implement custom validators for business logic
- Use response models to control output structure

Request bodies in FastAPI provide a powerful, type-safe way to handle complex data input with minimal code while maintaining excellent performance and automatic documentation generation.