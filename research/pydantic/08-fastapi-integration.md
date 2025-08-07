# Pydantic-FastAPI Integration

## Note
The official Pydantic documentation page for FastAPI integration returned a 404 error. However, here are the key integration points based on common usage patterns:

## Key Integration Features

### 1. Request/Response Models
- Use Pydantic models as FastAPI request bodies
- Automatic validation of incoming data
- Type hints for IDE support

### 2. Path and Query Parameters
- Pydantic models can validate path and query parameters
- Automatic conversion and validation

### 3. Schema Generation
- FastAPI automatically generates OpenAPI schemas from Pydantic models
- Interactive documentation (Swagger UI) based on model definitions

### 4. Error Handling
- FastAPI handles Pydantic ValidationError automatically
- Returns HTTP 422 status for validation errors
- Detailed error messages in response

## Common Usage Example:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    tax: float = 0.0

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}
```

## Best Practices
- Use separate models for requests and responses when needed
- Leverage Pydantic's validation features
- Take advantage of automatic schema generation
- Handle validation errors appropriately

*Note: For complete and up-to-date information on Pydantic-FastAPI integration, consult the official FastAPI documentation.*