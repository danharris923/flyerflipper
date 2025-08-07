# FastAPI Static Files

## Overview
- Use `StaticFiles` to serve static files from a directory
- "Mounting" means adding an independent application at a specific path
- Useful for serving CSS, JavaScript, images, and other static assets

## Basic Implementation
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
```

## Configuration Parameters
- **First parameter** (`"/static"`): Defines the sub-path for static files
- **directory parameter** (`directory="static"`): Specifies the directory containing static files
- **name parameter** (`name="static"`): Provides an internal name for the static files application

## Directory Structure Example
```
project/
├── main.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   └── images/
│       └── logo.png
└── templates/
    └── index.html
```

## Usage in Templates
```html
<!DOCTYPE html>
<html>
<head>
    <title>My App</title>
    <link rel="stylesheet" type="text/css" href="/static/css/styles.css">
</head>
<body>
    <img src="/static/images/logo.png" alt="Logo">
    <script src="/static/js/script.js"></script>
</body>
</html>
```

## Multiple Static Directories
```python
app = FastAPI()

# Mount different directories for different types of files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

## Important Characteristics
- **Independent Applications**: Mounted applications are completely independent
- **OpenAPI Exclusion**: Won't include mounted content in main app's OpenAPI documentation
- **Flexible Configuration**: Allows customizing paths and directory names
- **Performance**: Efficiently serves static files without processing overhead

## Security Considerations
- Ensure static directories don't contain sensitive files
- Consider using a reverse proxy (nginx) for production static file serving
- Be careful with directory traversal vulnerabilities

## Advanced Configuration
```python
from fastapi.staticfiles import StaticFiles

# Custom static files with specific configuration
app.mount(
    "/static",
    StaticFiles(directory="static", html=True),  # Enable HTML file serving
    name="static"
)
```

## Integration with Templates
```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

## Best Practices
- Use meaningful names for mounted static applications
- Organize static files in logical directory structures
- Consider using a CDN for production deployments
- Keep static file directories outside of your main application code
- Use appropriate caching headers for better performance

For more advanced static file handling options, refer to Starlette's static files documentation.