# Modal Container Images

Core documentation for building custom container images.

---

## Basic Image Definition

```python
import modal

image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("requests", "pydantic")
)

app = modal.App(name="my-app", image=image)
```

---

## Base Images

| Base | Description | Use Case |
|------|-------------|----------|
| `debian_slim()` | Minimal Debian | Most applications |
| `micromamba()` | Conda-based | Complex scientific deps |
| `from_registry()` | Docker Hub/ECR | Existing images |

### Python Version

```python
# Specify Python version
image = modal.Image.debian_slim(python_version="3.11")

# Match local version (default)
image = modal.Image.debian_slim()
```

---

## Installing Dependencies

### Python Packages

**Recommended: uv (faster)**
```python
image = modal.Image.debian_slim().uv_pip_install(
    "crewai>=0.80.0",
    "fastapi>=0.115.0",
    "pydantic>=2.0.0",
)
```

**Alternative: pip**
```python
image = modal.Image.debian_slim().pip_install(
    "crewai>=0.80.0",
    "fastapi>=0.115.0",
)
```

### System Packages

```python
image = modal.Image.debian_slim().apt_install(
    "git",
    "curl",
    "build-essential",
)
```

---

## Adding Local Files

### Local Directory

```python
image = modal.Image.debian_slim().add_local_dir(
    "src",                    # Local path
    remote_path="/root/src",  # Container path
)
```

### Local Python Source

```python
# For importable Python modules
image = modal.Image.debian_slim().add_local_python_source("my_module")
```

### Single File

```python
image = modal.Image.debian_slim().add_local_file(
    "config.yaml",
    remote_path="/root/config.yaml",
)
```

---

## Environment Variables

```python
image = modal.Image.debian_slim().env({
    "PYTHONPATH": "/root/src",
    "LOG_LEVEL": "INFO",
})
```

---

## Running Commands

### Shell Commands

```python
image = (
    modal.Image.debian_slim()
    .apt_install("git")
    .run_commands(
        "git clone https://github.com/org/repo /root/repo",
        "chmod +x /root/repo/setup.sh",
    )
)
```

### Python Functions

```python
def download_models():
    """Download models during image build."""
    import huggingface_hub
    huggingface_hub.hf_hub_download("org/model", "weights.bin")

image = (
    modal.Image.debian_slim()
    .pip_install("huggingface_hub")
    .run_function(
        download_models,
        secrets=[modal.Secret.from_name("huggingface")],
    )
)
```

---

## Method Chaining

Build images with method chaining (order matters for caching):

```python
image = (
    modal.Image.debian_slim(python_version="3.11")
    # 1. System packages (change rarely)
    .apt_install("git", "curl")
    # 2. Python packages (change occasionally)
    .pip_install(
        "crewai>=0.80.0",
        "crewai-tools>=0.14.0",
        "fastapi>=0.115.0",
        "pydantic>=2.0.0",
        "supabase>=2.0.0",
        "openai>=1.0.0",
    )
    # 3. Local code (changes frequently)
    .add_local_dir("src", remote_path="/root/src")
)
```

**Tip**: Place frequently-changing layers last to maximize cache hits.

---

## Caching Behavior

- Modal caches each layer independently
- Rebuilds only when layer definition changes
- Force rebuild with `force_build=True`:

```python
image = modal.Image.debian_slim().pip_install(
    "my-package",
    force_build=True,  # Always rebuild this layer
)
```

Or via environment variable:
```bash
MODAL_FORCE_BUILD=1 modal deploy app.py
```

---

## GPU Images

For GPU-accelerated builds:

```python
image = (
    modal.Image.debian_slim()
    .pip_install("torch", gpu="A10G")  # Build with GPU
)

@app.function(image=image, gpu="A10G")
def train_model():
    import torch
    # CUDA available
```

---

## Imports Context Manager

For shared imports across functions:

```python
image = modal.Image.debian_slim().pip_install("pandas", "numpy")

with image.imports():
    import pandas as pd
    import numpy as np

@app.function(image=image)
def analyze(data: list):
    df = pd.DataFrame(data)  # pd is available
    return df.describe().to_dict()
```

---

## StartupAI Example

```python
# Define the container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "crewai>=0.80.0",
        "crewai-tools>=0.14.0",
        "fastapi>=0.115.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "supabase>=2.0.0",
        "openai>=1.0.0",
        "tavily-python>=0.3.0",
        "httpx>=0.27.0",
    )
    .add_local_dir("src", remote_path="/root/src")
)

# Create the Modal App
app = modal.App(
    name="startupai-validation",
    image=image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
)
```

---

## Best Practices

1. **Pin versions tightly** for reproducibility:
   ```python
   .pip_install("torch==2.1.0")  # Good
   .pip_install("torch")         # Less predictable
   ```

2. **Order layers by change frequency**:
   - System packages first (stable)
   - Python packages second (occasional)
   - Local code last (frequent)

3. **Use `add_local_python_source`** for importable modules:
   ```python
   .add_local_python_source("src")
   ```

4. **Import inside functions** if packages unavailable locally:
   ```python
   @app.function(image=image)
   def my_func():
       import crewai  # Import inside function
   ```

---

## Related

- [Functions](functions.md) - Use images in functions
- [Secrets](secrets.md) - Inject secrets during build
- [Deployment](deployment.md) - Deploy with custom images
