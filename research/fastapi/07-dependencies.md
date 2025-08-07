# FastAPI Dependency Injection

## Key Concepts
- Dependency Injection allows code to declare required components that will be automatically "injected" by the framework
- Dependencies are functions that can take the same parameters as path operation functions
- Dependencies can be used to:
  - Share common logic
  - Manage database connections
  - Enforce security and authentication
  - Minimize code repetition

## Core Characteristics

### 1. Simple to Define
- Create a function that can take parameters
- Use `Depends()` to integrate the dependency
- No special registration required

### 2. Flexible Usage
- Can use `async def` or regular `def`
- Supports nested/hierarchical dependencies
- Integrated with OpenAPI documentation

## Example Code Structure

### Basic Dependency
```python
from fastapi import Depends, FastAPI
from typing import Annotated

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

app = FastAPI()

@app.get("/items/")
async def read_items(commons: Annotated[dict, Depends(common_parameters)]):
    return commons

@app.get("/users/")
async def read_users(commons: Annotated[dict, Depends(common_parameters)]):
    return commons
```

### Class-based Dependencies
```python
class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: Annotated[CommonQueryParams, Depends(CommonQueryParams)]):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip : commons.skip + commons.limit]
    response.update({"items": items})
    return response
```

### Sub-dependencies
```python
def query_extractor(q: str | None = None):
    return q

def query_or_cookie_extractor(
    q: Annotated[str, Depends(query_extractor)], 
    last_query: Annotated[str | None, Cookie()] = None
):
    if not q:
        return last_query
    return q

@app.get("/items/")
async def read_query(query_or_default: Annotated[str, Depends(query_or_cookie_extractor)]):
    return {"q_or_cookie": query_or_default}
```

## Advanced Patterns

### Dependencies at Path Operation Level
```python
@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Portal Gun"}, {"item": "Plumbus"}]
```

### Application-level Dependencies
```python
app = FastAPI(dependencies=[Depends(verify_token), Depends(verify_key)])
```

## Key Benefits
- **Code Reusability**: Share common logic across multiple endpoints
- **Database Integration**: Highly compatible with databases and external APIs
- **Security**: Enables complex permission hierarchies
- **Type Safety**: Preserves type information for IDE support
- **Automatic Resolution**: Automatic parameter resolution and validation
- **Testing**: Easy to mock and test dependencies

## Use Cases
- Database session management
- Authentication and authorization
- Input validation and transformation
- External API integration
- Configuration injection
- Request preprocessing

The dependency injection system is designed to be "simple and powerful", allowing developers to create sophisticated dependency trees with minimal complexity.