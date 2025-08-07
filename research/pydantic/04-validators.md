# Pydantic Validators

## Key Validator Types

### 1. Field Validators (4 modes):
- **After Validators**: Run after internal validation
- **Before Validators**: Run before parsing, handle raw input
- **Plain Validators**: Terminate validation immediately
- **Wrap Validators**: Most flexible, can interrupt or modify validation process

### 2. Model Validators (3 modes):
- **After Validators**: Run post-model validation
- **Before Validators**: Run before model instantiation
- **Wrap Validators**: Most flexible model-level validation

## Validation Approaches

### 1. Annotated Pattern:
- Reusable validators
- Clear type annotations
- Example: `EvenNumber = Annotated[int, AfterValidator(is_even)]`

### 2. Decorator Pattern:
- Apply validators to multiple fields
- Use `@field_validator()` decorator
- Can validate all fields with `'*'`

## Validation Error Handling
- `ValueError`: Most common
- `AssertionError`: Skipped with Python optimization
- `PydanticCustomError`: Most flexible, provides detailed error context

## Advanced Features
- Validation context
- Validation info access
- Special types like `InstanceOf` and `SkipValidation`

## Best Practice
Choose validator type based on specific validation requirements and desired flexibility.