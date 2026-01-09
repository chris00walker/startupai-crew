# Modal CLI Reference

Complete reference for Modal CLI commands. Use these commands to deploy, manage, and debug Modal applications.

**Fetched**: 2026-01-09
**Source**: https://modal.com/docs/guide

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `modal deploy` | Deploy app to production |
| `modal serve` | Local dev with hot reload |
| `modal run` | Run function/app once |
| `modal app list` | List deployed apps |
| `modal app stop` | Stop deployed app |
| `modal secret` | Manage secrets |
| `modal environment` | Manage environments |
| `modal token` | Authentication |
| `modal setup` | Initial setup |

---

## App Deployment

### modal deploy

Deploy an application to Modal for production use.

```bash
# Basic deployment
modal deploy app.py

# Deploy specific module
modal deploy -m mypackage.main

# Deploy to specific environment
modal deploy --env=production app.py
modal deploy --env=staging app.py

# Deploy with custom app name
modal deploy --name=my-custom-app app.py
```

**Flags:**
- `--env=<name>` - Deploy to specific environment (dev/staging/prod)
- `--name=<name>` - Override app name
- `-m <module>` - Deploy from module path

### modal serve

Start local development server with hot reload.

```bash
# Basic serve
modal serve app.py

# Serve specific app
modal serve app.py::my_app
```

Hot reloads on file changes. Use for testing web endpoints locally before deployment.

### modal run

Run a function or app once (ephemeral execution).

```bash
# Run default entrypoint
modal run app.py

# Run specific function
modal run app.py::my_function

# Run with arguments
modal run app.py::greet --name="World"

# Run detached (keeps running after client exits)
modal run --detach app.py
```

**Flags:**
- `--detach` - Keep running after client disconnects
- Function arguments passed as CLI flags

---

## App Management

### modal app list

List all deployed applications.

```bash
modal app list
```

Shows app name, status, and deployment info.

### modal app stop

Stop a running deployed application.

```bash
modal app stop <app-name>
```

**Warning:** Stopped apps cannot be restarted. Must redeploy.

### modal app logs

View logs for a deployed application.

```bash
# Stream logs
modal app logs <app-name>

# View recent logs
modal app logs <app-name> --tail=100
```

---

## Environment Management

### modal environment

Manage deployment environments (dev, staging, production).

```bash
# List environments
modal environment list

# Create new environment
modal environment create <name>

# Delete environment
modal environment delete <name>

# Set default environment
modal environment set-default <name>
```

**Usage with deploy:**
```bash
modal deploy --env=staging app.py
modal deploy --env=production app.py
```

---

## Secrets Management

### modal secret

Manage secrets (environment variables, API keys).

```bash
# Create secret with key-value pairs
modal secret create my-secret KEY1=value1 KEY2=value2

# Create secret from .env file
modal secret create my-secret --from-env-file=.env

# List all secrets
modal secret list

# Delete a secret
modal secret delete my-secret
```

**Usage in code:**
```python
@app.function(secrets=[modal.Secret.from_name("my-secret")])
def my_function():
    import os
    api_key = os.environ["KEY1"]
```

---

## Container Management

### modal container

Manage running containers.

```bash
# List running containers
modal container list

# View container details
modal container inspect <container-id>

# Stop a container
modal container stop <container-id>
```

---

## Authentication & Setup

### modal setup

Initial Modal CLI setup and authentication.

```bash
modal setup
```

Opens browser for authentication, creates `~/.modal.toml` config file.

### modal token

Manage authentication tokens.

```bash
# Generate new token
modal token new

# Set token from environment
modal token set --token-id=$MODAL_TOKEN_ID --token-secret=$MODAL_TOKEN_SECRET
```

**Config file location:** `~/.modal.toml`

### modal profile

Manage multiple Modal profiles.

```bash
# List profiles
modal profile list

# Switch profile
modal profile activate <profile-name>

# Create new profile
modal profile create <profile-name>
```

---

## Debugging Commands

### modal shell

Start interactive shell in Modal container.

```bash
# Shell with default image
modal shell

# Shell with specific image
modal shell --image=python:3.11

# Shell with GPU
modal shell --gpu=T4
```

### modal nfs

Manage network file systems.

```bash
# List NFS volumes
modal nfs list

# Create NFS volume
modal nfs create <volume-name>
```

---

## CI/CD Integration

### GitHub Actions

```yaml
- name: Deploy to Modal
  env:
    MODAL_TOKEN_ID: ${{ secrets.MODAL_TOKEN_ID }}
    MODAL_TOKEN_SECRET: ${{ secrets.MODAL_TOKEN_SECRET }}
  run: |
    pip install modal
    modal deploy app.py
```

### Environment Variables for CI

| Variable | Purpose |
|----------|---------|
| `MODAL_TOKEN_ID` | Authentication token ID |
| `MODAL_TOKEN_SECRET` | Authentication token secret |
| `MODAL_ENVIRONMENT` | Default environment |

---

## Common Patterns

### Deploy to Multiple Environments

```bash
# Deploy to staging first
modal deploy --env=staging app.py

# Then promote to production
modal deploy --env=production app.py
```

### Local Development Workflow

```bash
# 1. Start local server
modal serve app.py

# 2. Test endpoints locally
curl http://localhost:8000/endpoint

# 3. Deploy when ready
modal deploy app.py
```

### Debug Failing Functions

```bash
# 1. Check app logs
modal app logs my-app

# 2. List containers
modal container list

# 3. Start debug shell
modal shell --gpu=T4
```

---

## Related Topics

- **Functions**: Configuration options → `functions.md`
- **Secrets**: Secret management patterns → `secrets.md`
- **Deployment**: CI/CD patterns → `deployment.md`
- **GPUs**: GPU configuration → `gpus.md`
