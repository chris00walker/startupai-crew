# Netlify API Deployment Methods

Official documentation for programmatic deployments via Netlify API.

**Source**: https://docs.netlify.com/api/get-started/
**Last Updated**: 2026-01-10

---

## Overview

Netlify supports two primary deployment methods for programmatic API deployments:

1. **File Digest Method** (RECOMMENDED)
2. **ZIP File Method**

---

## Method 1: File Digest Method (RECOMMENDED)

### Why Recommended

- ✓ Efficient for incremental deployments (only changed files uploaded)
- ✓ Supports serverless functions
- ✓ Better performance for large sites
- ✓ Optimal for frequent updates

**Official quote**: "The file digest method is recommended for most use cases."

### Process

**Step 1: Create Deploy with File Digests**

```bash
POST /api/v1/sites/{site_id}/deploys
Content-Type: application/json
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>

{
  "files": {
    "/index.html": "907d14fb3af2b0d4f18c2d46abe8aedce17367bd",
    "/main.css": "f18c2d7367bd9046abe8aedce17d14fb3af2b0d4"
  },
  "functions": {
    "hello-world": "708b029d8aa9c8fa513d1a25b97ffb6efb12b423"
  }
}
```

**Hash Requirements**:
- Regular files: SHA1
- Serverless functions: SHA256

**Response**:
```json
{
  "id": "deploy-id-1234",
  "required": ["907d14fb3af2b0d4f18c2d46abe8aedce17367bd"],
  "required_functions": ["708b029d8aa9c8fa513d1a25b97ffb6efb12b423"]
}
```

The `required` array contains only files Netlify doesn't already have (incremental upload).

**Step 2: Upload Required Files**

```bash
PUT /api/v1/deploys/{deploy_id}/files/{file_path}
Content-Type: application/octet-stream
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>

[binary file contents]
```

**Important**:
- File path must be URL-encoded
- No `#` or `?` characters in paths
- Use raw file contents as request body

**Step 3: Upload Functions (if needed)**

```bash
PUT /api/v1/deploys/{deploy_id}/functions/{function_name}?runtime=js
Content-Type: application/octet-stream
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>

[zipped function contents]
```

**Runtimes**:
- `runtime=js`: Node.js or bundled JavaScript (must be zipped)
- `runtime=go`: Go binaries

**Step 4: Poll for Completion**

```bash
GET /api/v1/deploys/{deploy_id}
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>
```

**Deploy States**:
`preparing` → `prepared` → `uploading` → `uploaded` → `ready`

Deploy is live when `state === "ready"`.

### Async Requests for Large Deploys

For requests exceeding 30 seconds, use `async` mode:

```json
{
  "async": true,
  "files": {
    "/index.html": "907d14fb3af2b0d4f18c2d46abe8aedce17367bd"
  }
}
```

Then poll for completion as usual.

---

## Method 2: ZIP File Method

### Limitations

- ❌ 25,000 file limit per ZIP extraction
- ❌ Must upload complete site every time (no incremental updates)
- ❌ Less efficient for frequent deployments
- ✓ Simpler for one-off deploys

### Process

```bash
curl -H "Content-Type: application/zip" \
     -H "Authorization: Bearer YOUR_PERSONAL_ACCESS_TOKEN" \
     --data-binary "@website.zip" \
     https://api.netlify.com/api/v1/sites/{site_id}/deploys
```

**Or via raw POST**:
```bash
POST /api/v1/sites/{site_id}/deploys
Content-Type: application/zip
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>

[binary ZIP file contents]
```

---

## Authentication

### Required Header

```
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>
```

### How to Generate Personal Access Token (PAT)

1. Go to **Applications > Personal access tokens** in Netlify UI
2. Select **New access token**
3. Enter descriptive name
4. **For team access**: Check "Allow access to my SAML-based Netlify team"
5. Choose expiration date
6. Select **Generate token**
7. Copy token immediately (cannot be retrieved later)

**Important**: SAML SSO teams must grant team access when generating the token, or API requests will fail with 401.

---

## File Upload Endpoint Specification

### Endpoint

```
PUT /api/v1/deploys/{deploy_id}/files/{file_path}
```

### Required Headers

```
Authorization: Bearer <YOUR_PERSONAL_ACCESS_TOKEN>
Content-Type: application/octet-stream
```

### Request Body

Raw file contents (binary)

### Path Constraints

- ✓ Must be URL-encoded
- ❌ No `#` characters
- ❌ No `?` characters

### Example

```bash
curl -X PUT \
  -H "Authorization: Bearer nfp_abc123..." \
  -H "Content-Type: application/octet-stream" \
  --data-binary "@index.html" \
  https://api.netlify.com/api/v1/deploys/64abc123/files/index.html
```

---

## Common Issues & Troubleshooting

### 401 Unauthorized Errors

**Causes**:
1. Missing `Authorization` header
2. Invalid token format (must be `Bearer <token>`)
3. Expired personal access token
4. SAML SSO: Token doesn't have team access

**Solutions**:
- ✓ Verify header format: `Authorization: Bearer <token>`
- ✓ Check token hasn't expired
- ✓ For teams: Regenerate token with "Allow access to my SAML-based Netlify team" checked
- ✓ Ensure `Content-Type: application/octet-stream` is set

### 400 Bad Request

**Causes**:
- Invalid file path (contains `#` or `?`)
- File path not URL-encoded
- Missing `Content-Type` header

**Solutions**:
- URL-encode file paths
- Remove special characters from paths
- Add `Content-Type: application/octet-stream`

### Timeout Errors (>30 seconds)

**Cause**: Large file uploads exceeding timeout

**Solution**: Use `async: true` when creating deploy:
```json
{
  "async": true,
  "files": { ... }
}
```

Then poll deploy state until `ready`.

---

## Rate Limiting

- **General API**: 500 requests/minute
- **Deployments**: 3 deploys/minute, 100 deploys/day

**Check headers**:
```
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 56
X-RateLimit-Reset: 1372700873
```

---

## Best Practices

1. ✓ **Use file digest method** for production deployments
2. ✓ **Escape file paths** to avoid special character issues
3. ✓ **Use async mode** for large deployments (>30 seconds)
4. ✓ **Cache unchanged files** (Netlify handles via digests)
5. ✓ **Poll deploy state** until `ready` before considering deploy complete
6. ✓ **Retry uploads** if timeouts occur (safe to retry)
7. ✓ **Check rate limits** to avoid hitting deployment caps

---

## StartupAI Use Case

For StartupAI's programmatic landing page deployment from CrewAI workflows:

**Recommended**: File Digest Method

**Why**:
- ✓ Official Netlify recommendation
- ✓ Supports incremental updates
- ✓ Better performance for frequent deployments
- ✓ No file count limitations

**ZIP method**: Valid but offers no advantages for this use case.

---

## External Resources

- [Netlify API Documentation](https://docs.netlify.com/api/get-started/)
- [OpenAPI Reference](https://open-api.netlify.com)
- [Go Client](https://github.com/netlify/open-api#go-client)
- [JS Client](https://github.com/netlify/open-api#js-client)
- [Netlify Forums - API Help](https://answers.netlify.com)
