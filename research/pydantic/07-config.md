# Pydantic Model Configuration

## Configuration Methods

Pydantic offers multiple ways to configure model behavior:

### 1. Configuration Methods:
- Using `model_config` class attribute with `ConfigDict`
- Using class arguments
- Setting `__pydantic_config__` for dataclasses and TypedDict
- Using `with_config` decorator

### 2. Key Configuration Options:
- Control validation rules
- Set serialization behavior
- Define field constraints
- Manage extra field handling

### 3. Configuration Inheritance:
- Subclasses can inherit and merge parent configurations
- Global behavior can be modified by creating custom base classes

### 4. Configuration Scopes:
- Applies to BaseModel
- Supports Pydantic dataclasses
- Works with TypeAdapter
- Can be set for standard library dataclasses and TypedDict

## Example of configuration inheritance:
```python
class Parent(BaseModel):
    model_config = ConfigDict(extra='allow')

class Model(Parent):
    x: str

m = Model(x='foo', y='bar')
```

This approach allows flexible and granular control over Pydantic model validation and behavior.