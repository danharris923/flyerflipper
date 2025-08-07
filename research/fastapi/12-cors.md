# FastAPI CORS Configuration

## CORS (Cross-Origin Resource Sharing) Overview
- Manages communication between frontend and backend running on different origins
- An "origin" combines protocol, domain, and port (e.g., `http://localhost:8080`)
- Required when frontend and backend are served from different domains/ports
- Browser security feature that blocks cross-origin requests by default

## Basic CORS Setup

### Import and Configuration
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000",    # React development server
    "http://localhost:8080",    # Vue.js development server
    "https://mydomain.com",     # Production frontend
    "https://www.mydomain.com", # Production frontend with www
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Configuration Parameters

### allow_origins
- **List of strings**: Specific origins allowed to make requests
- **["*"]**: Allow all origins (use with caution in production)
- **Examples**: `["http://localhost:3000", "https://myapp.com"]`

### allow_credentials
- **True**: Enable cookies and authorization headers in cross-origin requests
- **False**: Disable credentials (default for security)
- **Important**: Cannot use with `allow_origins=["*"]`

### allow_methods
- **["*"]**: Allow all HTTP methods
- **List of methods**: `["GET", "POST", "PUT", "DELETE"]`
- **Default**: `["GET"]`

### allow_headers
- **["*"]**: Allow all headers
- **List of headers**: `["Content-Type", "Authorization"]`
- **Default**: Basic headers only

## Practical Examples

### Development Configuration (Permissive)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Production Configuration (Restrictive)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://myapp.com",
        "https://www.myapp.com",
        "https://admin.myapp.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)
```

### API-only Configuration (No Credentials)
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can use * when credentials are False
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

## Advanced Configuration

### Conditional CORS Based on Environment
```python
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Different origins for different environments
if os.getenv("ENVIRONMENT") == "development":
    origins = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ]
elif os.getenv("ENVIRONMENT") == "staging":
    origins = [
        "https://staging.myapp.com",
        "https://staging-admin.myapp.com"
    ]
else:  # production
    origins = [
        "https://myapp.com",
        "https://www.myapp.com",
        "https://admin.myapp.com"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Multiple CORS Configurations
```python
# For different route groups, you might need different middleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# General API CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# For webhook endpoints (different requirements)
webhook_app = FastAPI()
webhook_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

app.mount("/webhooks", webhook_app)
```

## Security Considerations

### Best Practices
```python
# ✅ Good: Specific origins with credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://myapp.com", "https://admin.myapp.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# ❌ Bad: Wildcard with credentials (will fail)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # This combination is not allowed
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ Acceptable for public APIs only: Wildcard without credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

## CORS Types Handled by Browsers

### Simple Requests
- GET, HEAD, POST with simple content types
- No custom headers
- Sent directly by browser

### Preflight Requests
- Other HTTP methods (PUT, DELETE, PATCH)
- Custom headers
- Complex content types
- Browser sends OPTIONS request first

## Debugging CORS Issues

### Common Error Messages
```
Access to fetch at 'http://localhost:8000/api' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present.
```

### Debug Configuration
```python
import logging

# Enable CORS debugging
logging.getLogger("uvicorn.error").setLevel(logging.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Frontend Integration Examples

### JavaScript/React
```javascript
// When credentials are enabled
fetch('http://localhost:8000/api/data', {
    method: 'GET',
    credentials: 'include',  // Include cookies
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token'
    }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Axios Configuration
```javascript
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    withCredentials: true,  // Include cookies
    headers: {
        'Content-Type': 'application/json'
    }
});
```

## Recommended Practices
- **Specify exact origins** instead of wildcards for production
- **Configure middleware early** in your application setup
- **Test CORS configuration** with different frontend scenarios
- **Use environment-specific configurations** for different deployment stages
- **Monitor and log CORS errors** for debugging
- **Consider using a reverse proxy** (nginx) for additional CORS control in production

Browsers handle preflight and simple CORS requests automatically when properly configured.