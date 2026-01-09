# Modal GPU Acceleration

GPU acceleration for Modal functions. Source: https://modal.com/docs/guide/gpu

**Fetched**: 2026-01-09

---

## Requesting a GPU

Use the `gpu` parameter in `@app.function()`:

```python
@app.function(gpu="A100")
def run():
    import torch
    assert torch.cuda.is_available()
```

## Available GPU Types

| GPU | VRAM | Best For |
|-----|------|----------|
| **T4** | 16 GB | Budget inference |
| **L4** | 24 GB | Inference, light training |
| **A10** | 24 GB | Inference, medium training |
| **A100-40GB** | 40 GB | Training, large models |
| **A100-80GB** | 80 GB | Large model training |
| **L40S** | 48 GB | Best cost-performance for inference |
| **H100** | 80 GB | High-performance training |
| **H200** | 141 GB | Largest models |
| **B200** | 192 GB | Cutting-edge training |

## GPU Configuration

### Single GPU

```python
@app.function(gpu="A100")
def my_function():
    ...
```

### Multiple GPUs

Append `:n` to specify count (max 8 for most GPUs):

```python
# Eight H100s (1,536 GB total)
@app.function(gpu="H100:8")
def run_llama_405b_fp8():
    ...

# Four A10s (96 GB total)
@app.function(gpu="A10:4")
def train_model():
    ...
```

### GPU Fallbacks

Specify preference order for availability:

```python
@app.function(gpu=["H100", "A100-40GB:2"])
def flexible_compute():
    ...
```

## Best Practices

### 1. Choose the Right GPU

- **Inference**: L40S offers best cost-performance with 48 GB RAM
- **Training**: A100-80GB or H100 for serious training workloads
- **Budget**: T4 for simple inference tasks

### 2. Understand Memory vs Compute

Single-prompt LLM inference is **memory-bound**, not compute-bound. Higher-tier GPUs may not justify cost for inference-only workloads.

### 3. H100 to H200 Upgrades

Modal automatically upgrades H100 → H200 at no extra cost. Use `H100!` to prevent this:

```python
@app.function(gpu="H100!")  # Force H100, no upgrade
def strict_h100():
    ...
```

### 4. Multi-GPU Training

For frameworks like PyTorch Lightning that re-execute entrypoints:

```python
@app.function(gpu="A100:4")
def train_distributed():
    import subprocess
    subprocess.run(["python", "train.py"])
```

## Code Examples

### Basic GPU Function

```python
import modal

app = modal.App("gpu-example")

@app.function(gpu="T4")
def gpu_inference():
    import torch
    device = torch.device("cuda")
    # Run inference on GPU
    return torch.cuda.get_device_name(0)
```

### LLM Inference with vLLM

```python
@app.function(
    gpu="A100-80GB",
    timeout=600,
    container_idle_timeout=300,
)
def run_vllm():
    from vllm import LLM
    llm = LLM(model="meta-llama/Llama-2-70b-hf")
    return llm.generate("Hello, world!")
```

### Multi-GPU Training

```python
@app.function(gpu="H100:8", timeout=3600)
def distributed_training():
    import torch.distributed as dist
    dist.init_process_group(backend="nccl")
    # Training code here
```

## Maximum Configurations

| GPU | Max Count | Max Total VRAM |
|-----|-----------|----------------|
| B200 | 8 | 1,536 GB |
| H200 | 8 | 1,128 GB |
| H100 | 8 | 640 GB |
| A100-80GB | 8 | 640 GB |
| A100-40GB | 8 | 320 GB |
| L40S | 8 | 384 GB |
| L4 | 8 | 192 GB |
| A10 | 4 | 96 GB |
| T4 | 8 | 128 GB |

## Related Topics

- **Images**: Configure CUDA in container images → `images.md`
- **Functions**: Timeout and retry configuration → `functions.md`
- **Secrets**: API keys for model downloads → `secrets.md`
