# Modal Functions

Core documentation for `@app.function` decorator and function configuration.

---

## Defining Functions

### Basic Function

```python
import modal

app = modal.App(name="my-app")

@app.function()
def hello():
    return "Hello, world!"
```

### Function with Configuration

```python
@app.function(
    timeout=3600,              # 1 hour max execution
    retries=modal.Retries(
        max_retries=3,
        initial_delay=1.0,
        backoff_coefficient=2.0,
    ),
    cpu=2.0,                   # 2 CPU cores
    memory=4096,               # 4 GiB RAM
    secrets=[modal.Secret.from_name("my-secrets")],
    image=my_custom_image,
)
def process_data(input: str) -> dict:
    return {"result": input.upper()}
```

---

## Configuration Parameters

### Compute Resources

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `cpu` | float | CPU cores (0.25 to 8.0) | 0.25 |
| `memory` | int | Memory in MiB (128 to 32768) | 128 |
| `gpu` | str | GPU type (`"T4"`, `"A10G"`, `"A100"`, `"H100"`) | None |
| `ephemeral_disk` | int | Ephemeral disk in MiB | 10240 |

### Execution Control

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `timeout` | int | Max execution time in seconds | 300 (5 min) |
| `retries` | Retries | Retry configuration | None |
| `concurrency_limit` | int | Max concurrent executions | None |
| `allow_concurrent_inputs` | int | Inputs per container | 1 |

### Dependencies

| Parameter | Type | Description |
|-----------|------|-------------|
| `secrets` | list[Secret] | Secrets to inject as env vars |
| `image` | Image | Custom container image |
| `volumes` | dict | Mounted volumes |
| `network_file_systems` | dict | Network file systems |

---

## Retries Configuration

```python
from modal import Retries

@app.function(
    retries=Retries(
        max_retries=3,           # Total retry attempts
        initial_delay=1.0,       # First retry delay (seconds)
        backoff_coefficient=2.0, # Exponential backoff multiplier
    )
)
def flaky_function():
    # May fail occasionally
    pass
```

**Retry Behavior**:
- Delay sequence: 1s → 2s → 4s (with backoff_coefficient=2.0)
- Only retries on exceptions, not on explicit returns
- Container may be reused between retries

---

## Running Functions

### Remote Invocation

```python
# Call from local code
result = my_function.remote(arg1, arg2)

# Spawn async (fire-and-forget)
my_function.spawn(arg1, arg2)

# Local execution (for testing)
result = my_function.local(arg1, arg2)
```

### Entry Points

```python
@app.local_entrypoint()
def main(input_file: str, count: int = 10):
    """CLI entry point with auto-parsed arguments."""
    result = process_data.remote(input_file)
    print(f"Processed: {result}")
```

**Usage**: `modal run script.py --input-file data.json --count 20`

---

## Function Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│                    Function Invocation                       │
├──────────────┬──────────────┬──────────────┬───────────────┤
│  Cold Start  │   Warm       │  Execution   │  Termination  │
│  (container) │   Start      │              │               │
├──────────────┼──────────────┼──────────────┼───────────────┤
│  ~1-5s       │   ~50ms      │  your code   │  container    │
│  if no       │   if         │  runs here   │  may persist  │
│  container   │   container  │              │  for reuse    │
│  available   │   exists     │              │               │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

**Optimization**: Use `enable_memory_snapshot=True` for faster cold starts (captures container state after first run).

---

## Concurrency

### Multiple Inputs per Container

```python
@app.function(allow_concurrent_inputs=10)
def batch_process(item: dict):
    # 10 concurrent requests per container
    return process(item)
```

### Using @modal.concurrent

```python
@app.function()
@modal.concurrent(max_inputs=100)
def high_throughput(request):
    # Up to 100 concurrent requests per container
    return handle(request)
```

---

## Best Practices

### 1. Set Appropriate Timeouts

```python
# Short tasks (API calls, simple processing)
@app.function(timeout=60)

# Medium tasks (data processing)
@app.function(timeout=600)

# Long tasks (LLM operations, batch processing)
@app.function(timeout=3600)
```

### 2. Configure Retries for External Services

```python
@app.function(
    retries=Retries(max_retries=3, initial_delay=1.0),
    timeout=300,
)
def call_external_api():
    # Will retry on transient failures
    pass
```

### 3. Use Spawn for Async Operations

```python
# Don't wait for result
background_task.spawn(data)

# Continue immediately
return {"status": "accepted"}
```

---

## StartupAI Example

```python
@app.function(
    secrets=[modal.Secret.from_name("startupai-secrets")],
    timeout=3600,  # 1 hour for LLM operations
    cpu=2.0,
    memory=4096,
    retries=modal.Retries(max_retries=2, initial_delay=1.0),
)
def run_validation(run_id: str):
    """Execute validation pipeline for a project."""
    from src.modal_app.phases import phase_0, phase_1, phase_2

    # Execute phases sequentially
    state = {}
    for phase_fn in [phase_0, phase_1, phase_2]:
        state = phase_fn.execute(run_id, state)

        if state.get("hitl_checkpoint"):
            # Save state and terminate
            return {"checkpoint": state["hitl_checkpoint"]}

    return {"status": "completed", "state": state}
```

---

## Related

- [Web Endpoints](web-endpoints.md) - HTTP endpoints with FastAPI
- [Images](images.md) - Custom container configuration
- [Secrets](secrets.md) - Environment variable management
