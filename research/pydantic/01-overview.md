# Pydantic Overview

## Key Features
- Data validation library for Python 3.9+
- Powered by type hints
- Core validation logic written in Rust
- Supports JSON Schema generation
- Offers strict and lax validation modes

## Main Advantages
- Fast performance
- Seamless IDE and static analysis integration
- Supports dataclasses, TypedDicts
- Highly customizable
- Extensive ecosystem (used by ~8,000 PyPI packages)

## Installation
```bash
pip install pydantic
```

## Basic Usage Example
```python
from pydantic import BaseModel, PositiveInt
from datetime import datetime

class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',
    'tastes': {
        'wine': 9,
        'cheese': 7,
        'cabbage': '1',
    }
}

user = User(**external_data)
print(user.model_dump())
```

## Validation Handling
- Automatically converts and validates input data
- Raises detailed `ValidationError` with specific issue locations
- Supports type coercion in lax mode

## Notable Users
- All FAANG companies
- 20 of 25 largest NASDAQ companies
- Organizations like Adobe, Amazon, Apple, Google, Microsoft

## Monitoring
Integrates with Logfire for application monitoring and validation tracking.