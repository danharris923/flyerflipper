# FastAPI First Steps

## Installation
- Assumes Python 3.8+ is already installed
- Install FastAPI: `pip install "fastapi[standard]"`

## Basic Application Creation
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## Running the Server
- Command: `fastapi dev main.py`
- Server starts at: `http://127.0.0.1:8000`
- Development mode with auto-reload

## Key Features
- Automatic interactive API documentation
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`
- Generates OpenAPI schema automatically
- Supports multiple HTTP methods (GET, POST, PUT, DELETE, etc.)

## Path Operation Components
- **Path**: URL endpoint (e.g., "/")
- **Operation**: HTTP method (GET, POST)
- **Decorator**: `@app.get("/")` defines the route
- **Function**: Handles the request and returns a response

## Response Handling
- Can return dictionaries, lists, strings, integers
- Supports automatic JSON conversion
- Pydantic models can be used for more complex responses

The documentation emphasizes FastAPI's simplicity, automatic documentation, and flexible routing capabilities.