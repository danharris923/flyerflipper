# Pydantic Fields

## Key Aspects of Pydantic Fields

### 1. Field Definition
- Created using `Field()` function
- Can be defined with various constraints and metadata
- Supports two primary definition patterns:
  ```python
  # Standard assignment
  name: str = Field(frozen=True)
  
  # Annotated pattern
  name: Annotated[str, Field(strict=True)]
  ```

### 2. Field Constraints

#### Numeric Constraints:
- `gt`: Greater than
- `lt`: Less than
- `ge`: Greater than or equal to
- `le`: Less than or equal to
- `multiple_of`: Divisibility check

#### String Constraints:
- `min_length`: Minimum string length
- `max_length`: Maximum string length
- `pattern`: Regular expression matching

### 3. Default Values
- Can be set directly or via `default` parameter
- Support for `default_factory` for dynamic default generation
- Optional validation of default values

### 4. Field Aliases
Three alias types:
- `alias`: Used for both validation and serialization
- `validation_alias`: Used only during validation
- `serialization_alias`: Used only during serialization

### 5. Advanced Features
- Strict mode validation
- Immutability with `frozen`
- Deprecation warnings
- Computed fields
- JSON Schema customization

## Example demonstrating multiple features:
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    age: int = Field(gt=0, lt=120)
    email: str = Field(validation_alias='user_email')
```

This overview captures the core functionality of Pydantic fields based on the provided documentation.