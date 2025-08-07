# Pydantic Serialization

## Key Serialization Methods

### 1. `model_dump()`
- Converts a Pydantic model to a dictionary
- Supports advanced filtering via parameters like:
  - `include`: Select specific fields
  - `exclude`: Remove specific fields
  - `by_alias`: Use serialization aliases
  - `exclude_unset`: Omit fields not explicitly set
  - `exclude_defaults`: Skip fields with default values
  - `exclude_none`: Remove fields with None values

### 2. `model_dump_json()`
- Serializes model directly to a JSON-encoded string
- Handles complex types like datetime, UUID automatically
- Supports similar parameters to `model_dump()`

## Custom Serialization Techniques
- `@field_serializer`: Customize individual field serialization
- `@model_serializer`: Override entire model serialization
- `SerializeAsAny`: Enable duck-typing serialization
- `serialize_as_any` runtime flag: Control serialization behavior

## Advanced Features
- Nested field inclusion/exclusion
- Serialization context for dynamic behavior
- Support for pickling Pydantic models
- Handling of subclass serialization with fine-grained control

## Example of Basic Serialization:
```python
class User(BaseModel):
    name: str
    password: SecretStr = Field(exclude=True)

user = User(name='John', password='secret')
print(user.model_dump())  # Excludes password
```

The documentation emphasizes flexibility and security in data serialization, providing developers multiple ways to control how their models are converted to different formats.