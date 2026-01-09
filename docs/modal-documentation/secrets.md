# Modal Secrets

Core documentation for managing secrets and environment variables.

---

## Creating Secrets

### CLI Method

```bash
# Create secret with key-value pairs
modal secret create my-secret API_KEY=sk-xxx DB_URL=postgres://...

# Reference local environment variables
modal secret create my-secret API_KEY="$API_KEY"

# Delete a secret
modal secret delete my-secret

# List secrets
modal secret list
```

### Dashboard Method

1. Go to https://modal.com/secrets
2. Click "Create Secret"
3. Choose template or custom
4. Enter key-value pairs

### Programmatic Method

```python
import modal
import os

# From dictionary
local_secret = modal.Secret.from_dict({
    "API_KEY": os.environ["LOCAL_API_KEY"],
    "DB_URL": "postgres://...",
})

# From .env file
dotenv_secret = modal.Secret.from_dotenv()
```

---

## Using Secrets in Functions

### Single Secret

```python
@app.function(secrets=[modal.Secret.from_name("api-keys")])
def call_api():
    import os
    api_key = os.environ["API_KEY"]
    # Use api_key...
```

### Multiple Secrets

```python
@app.function(
    secrets=[
        modal.Secret.from_name("openai-keys"),
        modal.Secret.from_name("database-creds"),
    ]
)
def process():
    import os
    openai_key = os.environ["OPENAI_API_KEY"]
    db_url = os.environ["DATABASE_URL"]
```

**Note**: Later secrets override earlier ones for duplicate keys.

---

## Secret Patterns

### Application Secrets

```bash
modal secret create myapp-secrets \
  OPENAI_API_KEY=sk-xxx \
  TAVILY_API_KEY=tvly-xxx \
  SUPABASE_URL=https://xxx.supabase.co \
  SUPABASE_KEY=eyJ...
```

### Environment-Specific Secrets

```bash
# Development
modal secret create myapp-dev \
  DATABASE_URL=postgres://localhost/dev

# Production
modal secret create myapp-prod \
  DATABASE_URL=postgres://prod.db.com/prod
```

---

## Access Patterns

### Direct Environment Access

```python
import os

@app.function(secrets=[modal.Secret.from_name("config")])
def get_config():
    return {
        "api_key": os.environ["API_KEY"],
        "db_url": os.environ.get("DB_URL", "default"),
    }
```

### Lazy Loading

```python
@app.function(secrets=[modal.Secret.from_name("config")])
def process():
    # Import inside function to access secrets
    from supabase import create_client

    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]

    return create_client(url, key)
```

### Validation on Startup

```python
def validate_secrets():
    """Validate required secrets are present."""
    import os
    required = ["OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing = [k for k in required if k not in os.environ]
    if missing:
        raise ValueError(f"Missing secrets: {missing}")

@app.function(secrets=[modal.Secret.from_name("config")])
def init():
    validate_secrets()
    # Continue with setup...
```

---

## Using Secrets in Image Builds

```python
def download_private_models():
    """Download models using HuggingFace token."""
    import os
    from huggingface_hub import hf_hub_download

    token = os.environ["HF_TOKEN"]
    hf_hub_download("private/model", token=token)

image = (
    modal.Image.debian_slim()
    .pip_install("huggingface_hub")
    .run_function(
        download_private_models,
        secrets=[modal.Secret.from_name("huggingface")],
    )
)
```

---

## Security Best Practices

### 1. Never Hardcode Secrets

```python
# BAD
api_key = "sk-abc123..."

# GOOD
api_key = os.environ["API_KEY"]
```

### 2. Minimize Secret Scope

```python
# BAD - All functions get all secrets
app = modal.App(secrets=[all_secrets])

# GOOD - Functions get only what they need
@app.function(secrets=[modal.Secret.from_name("openai-only")])
def llm_task(): ...

@app.function(secrets=[modal.Secret.from_name("db-only")])
def db_task(): ...
```

### 3. Use Separate Secrets per Environment

```bash
modal secret create myapp-dev ...
modal secret create myapp-staging ...
modal secret create myapp-prod ...
```

### 4. Rotate Secrets Regularly

```bash
# Update secret values
modal secret create myapp-secrets --force \
  API_KEY=new-value
```

---

## StartupAI Example

### Secret Creation

```bash
modal secret create startupai-secrets \
  OPENAI_API_KEY=sk-... \
  TAVILY_API_KEY=tvly-... \
  SUPABASE_URL=https://eqxropalhxjeyvfcoyxg.supabase.co \
  SUPABASE_KEY=eyJ... \
  WEBHOOK_BEARER_TOKEN=startupai-modal-secret-2026 \
  NETLIFY_ACCESS_TOKEN=xxx
```

### Secret Usage

```python
import modal

app = modal.App(
    name="startupai-validation",
    image=image,
    secrets=[modal.Secret.from_name("startupai-secrets")],
)

@app.function()
def run_validation(run_id: str):
    import os
    from supabase import create_client

    # Access secrets via environment
    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_KEY"],
    )

    # Use Supabase client...
```

### Supabase Client Pattern

```python
_supabase_client = None

def get_supabase():
    """Get or create Supabase client (lazy initialization)."""
    global _supabase_client
    if _supabase_client is None:
        from supabase import create_client
        import os

        url = os.environ["SUPABASE_URL"]
        key = os.environ["SUPABASE_KEY"]
        _supabase_client = create_client(url, key)

    return _supabase_client
```

---

## Troubleshooting

### "Secret not found"

```bash
# Verify secret exists
modal secret list

# Check secret name matches exactly
modal secret create exact-name KEY=value
```

### "Environment variable not set"

```python
# Check secret is attached to function
@app.function(secrets=[modal.Secret.from_name("my-secret")])
def my_func():
    import os
    print(os.environ.keys())  # Debug: list available vars
```

---

## Related

- [Functions](functions.md) - Attach secrets to functions
- [Images](images.md) - Use secrets during build
- [Deployment](deployment.md) - CI/CD with secrets
