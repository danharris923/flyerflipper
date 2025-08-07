# FastAPI Docker Deployment

## Overview
- Containers are lightweight, isolated environments for applications
- Container images are static packages of files and dependencies
- Each container typically runs a single process
- Docker provides consistent deployment across different environments

## Dockerfile Best Practices

### Optimized Dockerfile Structure
```dockerfile
# Use official Python runtime as base image
FROM python:3.9

# Set working directory in container
WORKDIR /code

# Copy requirements file first to optimize build caching
COPY ./requirements.txt /code/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy application code
COPY ./app /code/app

# Define startup command
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

### Alternative with Uvicorn
```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
```

## Requirements File Example
```text
fastapi[standard]>=0.104.0,<1.0.0
```

## Project Structure
```
project/
├── app/
│   ├── __init__.py
│   └── main.py
├── requirements.txt
└── Dockerfile
```

### Sample FastAPI Application (app/main.py)
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

## Build and Run Commands

### Building the Docker Image
```bash
docker build -t myimage .
```

### Running the Container
```bash
# Run in detached mode
docker run -d --name mycontainer -p 80:80 myimage

# Run with custom port mapping
docker run -d --name mycontainer -p 8000:80 myimage

# Run interactively for debugging
docker run -it --name mycontainer -p 80:80 myimage
```

## Advanced Configuration

### Multi-stage Build
```dockerfile
# Build stage
FROM python:3.9 as builder
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --user -r /code/requirements.txt

# Production stage
FROM python:3.9-slim
WORKDIR /code
COPY --from=builder /root/.local /root/.local
COPY ./app /code/app

# Update PATH
ENV PATH=/root/.local/bin:$PATH

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

### Environment Variables
```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Set environment variables
ENV PYTHONPATH=/code
ENV PORT=80

CMD ["sh", "-c", "fastapi run app/main.py --port $PORT"]
```

## Deployment Strategies

### Single Process Container (Recommended)
- Use single process per container for cluster environments
- Handle HTTPS and load balancing externally
- Better for Kubernetes, Docker Swarm, etc.

### Production Considerations
```dockerfile
FROM python:3.9-slim

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /code

# Install dependencies as root
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy app and change ownership
COPY ./app /code/app
RUN chown -R appuser:appuser /code

# Switch to non-root user
USER appuser

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

## Container Orchestration

### Docker Compose Example
```yaml
version: "3.8"

services:
  web:
    build: .
    ports:
      - "8000:80"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-app
  template:
    metadata:
      labels:
        app: fastapi-app
    spec:
      containers:
      - name: fastapi-app
        image: myimage:latest
        ports:
        - containerPort: 80
        env:
        - name: DATABASE_URL
          value: "postgresql://user:pass@postgres:5432/myapp"
```

## Performance Optimization

### Caching Layers
```dockerfile
FROM python:3.9

WORKDIR /code

# Cache pip dependencies
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy app code (changes more frequently)
COPY ./app /code/app

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

### Health Checks
```dockerfile
FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:80/health || exit 1

CMD ["fastapi", "run", "app/main.py", "--port", "80"]
```

## Key Recommendations
- **Avoid complex base images**: Use slim or alpine versions when possible
- **Optimize build performance**: Copy requirements first for better caching
- **Use --proxy-headers**: When behind a TLS proxy
- **Memory constraints**: Consider memory limits in production
- **Security**: Run as non-root user in production
- **Monitoring**: Implement proper logging and health checks

## Common Deployment Patterns
1. **Single container**: Simple applications
2. **Multi-container**: With database and other services
3. **Container orchestration**: Kubernetes, Docker Swarm
4. **Cloud platforms**: AWS ECS, Google Cloud Run, Azure Container Instances

Choose deployment approach based on specific use case, scalability requirements, and infrastructure constraints.