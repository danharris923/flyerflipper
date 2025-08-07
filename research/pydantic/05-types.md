# Pydantic Types

## Key Aspects of Pydantic Types

### 1. Type Handling
- Pydantic primarily uses standard library types
- Provides custom type implementations for complex scenarios
- Supports type conversion and validation

### 2. Type Categories
- **Standard Library Types**
- **Strict Types** (e.g., `StrictBool`, `StrictInt`)
- **Constrained Types** (e.g., `conint()`, `constr()`)
- **Custom Generic Types**

### 3. Type Validation Mechanisms
- Supports type coercion in strict and lax modes
- Allows custom validation through:
  - Annotated patterns
  - `__get_pydantic_core_schema__` method
  - Custom generic class handling

### 4. Custom Type Creation Strategies
- Use `Annotated` with validation constraints
- Implement `__get_pydantic_core_schema__`
- Create type aliases
- Handle generic types with type parameters

### 5. Key Features
- Flexible type validation
- JSON schema generation
- Support for complex type constraints
- Extensible type system

## Example of Custom Type Creation:
```python
Username = Annotated[str, AfterValidator(str.lower)]

class Model(BaseModel):
    name: Username
```

This approach demonstrates Pydantic's powerful and flexible type system, enabling developers to create precise, self-documenting data models with robust validation.