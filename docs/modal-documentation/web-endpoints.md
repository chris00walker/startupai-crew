# Modal Web Endpoints

Core documentation for creating HTTP endpoints with Modal.

---

## Decorators Overview

| Decorator | Use Case | Runtime |
|-----------|----------|---------|
| `@modal.fastapi_endpoint()` | Simple REST endpoints | FastAPI (auto) |
| `@modal.asgi_app()` | Full ASGI frameworks (FastAPI, Starlette) | Your framework |
| `@modal.wsgi_app()` | WSGI frameworks (Flask, Django) | Your framework |
| `@modal.web_server(port)` | Custom HTTP servers | Any |

---

## Simple Endpoints

### GET Endpoint

```python
@app.function()
@modal.fastapi_endpoint()
def hello():
    return {"message": "Hello, world!"}
```

### POST with JSON Body

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    quantity: int = 1

@app.function()
@modal.fastapi_endpoint(method="POST")
def create_item(item: Item):
    return {"created": item.name, "qty": item.quantity}
```

### Query Parameters

```python
@app.function()
@modal.fastapi_endpoint()
def search(query: str, limit: int = 10):
    return {"query": query, "limit": limit}
```

---

## Full FastAPI Application

For complex applications with multiple routes, CORS, and middleware:

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

web_app = FastAPI(title="My API", version="1.0.0")

# CORS configuration
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@web_app.get("/health")
def health():
    return {"status": "healthy"}

@web_app.post("/process")
def process(data: dict):
    return {"processed": data}

# Mount to Modal
@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app
```

---

## Authentication

### Bearer Token Pattern

```python
import os
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

auth_scheme = HTTPBearer()

@app.function(secrets=[modal.Secret.from_name("api-tokens")])
@modal.fastapi_endpoint()
async def protected_endpoint(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme)
):
    expected_token = os.environ["API_TOKEN"]

    if token.credentials != expected_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"status": "authorized"}
```

### HMAC Comparison (Secure)

```python
import hmac

def verify_token(provided: str, expected: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    return hmac.compare_digest(provided, expected)
```

---

## Request Handling

### Access Request Object

```python
from fastapi import Request

@app.function()
@modal.fastapi_endpoint()
def get_client_info(request: Request):
    return {
        "client_ip": request.client.host,
        "headers": dict(request.headers),
        "method": request.method,
    }
```

### Background Tasks

```python
from fastapi import BackgroundTasks

@app.function()
@modal.fastapi_endpoint(method="POST")
async def kickoff(data: dict, background_tasks: BackgroundTasks):
    # Spawn Modal function in background
    process_async.spawn(data)

    # Return immediately
    return {"status": "accepted"}
```

---

## CORS Configuration

For `@modal.asgi_app()` with FastAPI:

```python
from fastapi.middleware.cors import CORSMiddleware

web_app = FastAPI()

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.startupai.site",
        "https://startupai.site",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Concurrency

### High-Throughput Endpoints

```python
@app.function()
@modal.concurrent(max_inputs=100)
@modal.asgi_app()
def high_throughput_api():
    return web_app
```

**Note**: Each container handles up to 100 concurrent requests.

---

## URL Management

### Deployed URLs

```
Format: https://{workspace}--{app-name}-{function-name}.modal.run

Example: https://chris00walker--startupai-validation-fastapi-app.modal.run
```

### Development URLs

```
Format: https://{workspace}-dev--{app-name}-{function-name}.modal.run

Example: https://chris00walker-dev--startupai-validation-fastapi-app.modal.run
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Requests/second | 200 (sustained) |
| Burst multiplier | 5x for 5 seconds |
| Request body size | Up to 4 GiB |
| WebSocket message | Up to 2 MiB |

---

## StartupAI Example

```python
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from uuid import UUID, uuid4

web_app = FastAPI(title="StartupAI Validation API")

web_app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.startupai.site",
        "https://startupai.site",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class KickoffRequest(BaseModel):
    project_id: UUID
    user_id: UUID
    entrepreneur_input: str = Field(..., min_length=10)

class KickoffResponse(BaseModel):
    run_id: UUID
    status: str = "started"

@web_app.post("/kickoff", response_model=KickoffResponse, status_code=202)
async def kickoff(
    request: KickoffRequest,
    background_tasks: BackgroundTasks,
    authorization: str = Header(...),
):
    verify_bearer_token(authorization)

    run_id = uuid4()
    run_validation.spawn(str(run_id))

    return KickoffResponse(run_id=run_id, status="started")

@web_app.get("/health")
def health():
    return {"status": "healthy", "service": "startupai-validation"}

# Mount to Modal
@app.function(
    image=image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
)
@modal.asgi_app()
def fastapi_app():
    return web_app
```

---

## Related

- [Functions](functions.md) - Core function configuration
- [Secrets](secrets.md) - Authentication tokens
- [Deployment](deployment.md) - Deploy web endpoints
