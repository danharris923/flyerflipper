# FastAPI Background Tasks

## Overview
- Background tasks run after returning a response
- Useful for operations that don't require immediate client waiting
- Typical use cases include email notifications and data processing

## Key Concepts
- Tasks execute after the response is sent to the client
- Client doesn't need to wait for the task to complete
- Runs in the same process as the main application
- Supports both sync and async functions

## Basic Implementation

### Import and Setup
```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def write_notification(email: str, message: str = ""):
    with open("log.txt", mode="w") as email_file:
        content = f"notification for {email}: {message}"
        email_file.write(content)

@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_notification, email, message="some notification")
    return {"message": "Notification sent in the background"}
```

### Multiple Background Tasks
```python
def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)

def send_email(email: str, message: str = ""):
    # Email sending logic here
    pass

@app.post("/send-notification/{email}")
async def send_notification(
    email: str, 
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_email, email, message="Thank you for using our service")
    background_tasks.add_task(write_log, f"Email sent to {email}")
    return {"message": "Message sent"}
```

## Implementation Details

### Task Function Definition
```python
# Sync function
def process_data(data: dict):
    # Process the data
    result = heavy_computation(data)
    save_to_database(result)

# Async function
async def async_process_data(data: dict):
    # Async processing
    result = await async_heavy_computation(data)
    await async_save_to_database(result)

@app.post("/process/")
async def process_endpoint(data: dict, background_tasks: BackgroundTasks):
    background_tasks.add_task(process_data, data)
    # or for async function:
    # background_tasks.add_task(async_process_data, data)
    return {"status": "processing started"}
```

### With Dependencies
```python
def get_database():
    # Database connection logic
    return database

@app.post("/items/")
async def create_item(
    item: Item,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_database)
):
    # Create item immediately
    created_item = create_item_in_db(db, item)
    
    # Process in background
    background_tasks.add_task(update_search_index, created_item.id)
    background_tasks.add_task(send_welcome_email, created_item.user_email)
    
    return created_item
```

## Key Features
- **Dependency Injection Support**: Works seamlessly with FastAPI's dependency system
- **Multiple Tasks**: Can add multiple background tasks to a single request
- **Cross-Operation Support**: Works across path operations and dependencies
- **Type Safety**: Full type checking support with proper annotations

## Use Cases

### Email Notifications
```python
@app.post("/register/")
async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks
):
    # Create user immediately
    created_user = create_user_in_db(user)
    
    # Send welcome email in background
    background_tasks.add_task(
        send_welcome_email, 
        created_user.email, 
        created_user.name
    )
    
    return {"message": "User registered successfully"}
```

### Data Processing
```python
@app.post("/upload/")
async def upload_file(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    # Save file immediately
    file_path = save_upload_file(file)
    
    # Process file in background
    background_tasks.add_task(process_uploaded_file, file_path)
    background_tasks.add_task(generate_thumbnails, file_path)
    
    return {"message": "File uploaded and processing started"}
```

## Limitations and Considerations
- **Lightweight Tasks Only**: Best for quick, non-blocking operations
- **Same Process**: Tasks run in the same process as the main application
- **Memory Usage**: Be mindful of memory consumption for long-running tasks
- **Error Handling**: Background task errors won't affect the response
- **Complex Processing**: For heavy computational tasks, consider using Celery

## Alternative Solutions
For more complex background processing:
- **Celery**: For distributed task queues
- **RQ (Redis Queue)**: For simpler Redis-based task queues  
- **External Services**: Separate microservices for heavy processing

## Best Practices
- Keep background tasks lightweight and fast
- Handle errors gracefully within task functions
- Use appropriate logging for background task monitoring
- Consider using external task queues for production workloads
- Test background tasks thoroughly
- Use `Annotated` type hints for better code clarity

## Technical Note
Background tasks come from Starlette's implementation, integrated directly into FastAPI for seamless usage.