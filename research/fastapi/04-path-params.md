# FastAPI Path Parameters

## Basic Syntax
- Declared using Python format string syntax
- Can be defined directly in route decorator
- Example: `@app.get("/items/{item_id}")`

## Type Annotations
- Support type validation using standard Python type hints
- Automatically handles data conversion and validation
- Supports types like `int`, `str`, `float`, `bool`

## Example Code
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}
```

## Data Validation Features
- Automatically rejects invalid type inputs
- Provides clear error messages
- Generates interactive API documentation

## Enum Support
- Can define predefined valid path parameter values
- Create an `Enum` class inheriting from `str` and `Enum`
- Enables strict value constraints

```python
from enum import Enum
from fastapi import FastAPI

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}
```

## Advanced Path Handling
- Can include paths within path parameters using `:path` convertor
- Supports complex file path scenarios
- Example: `@app.get("/files/{file_path:path}")`

## Key Benefits
- Automatic request parsing
- Built-in data validation
- Interactive API documentation
- Enhanced editor support
- Leverages Pydantic for type checking

**Unique Characteristic**: Achieves multiple advanced API features through simple, standard Python type declarations.