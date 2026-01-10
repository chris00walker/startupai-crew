# Netlify Edge Functions

Guide to Netlify Edge Functions for server-side logic at the network edge using Deno runtime.

## Overview

Edge Functions are TypeScript/JavaScript functions that run on Netlify's worldwide network edge, powered by Deno. They execute at the location closest to each user for minimal latency.

**Key Benefits**:
- Global edge deployment
- TypeScript/JavaScript support
- Deno runtime (secure, modern)
- Response caching
- Deploy previews
- Version controlled

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Geolocation** | Localize content based on user location |
| **Authentication** | Verify tokens, protect routes |
| **A/B Testing** | Route traffic based on cookies |
| **Personalization** | Customize responses per user |
| **Request/Response Transform** | Modify headers, rewrite URLs |
| **Middleware** | Add logic before page renders |

## File Structure

```
project/
├── netlify/
│   └── edge-functions/
│       ├── hello.ts           # Edge function
│       └── middleware.ts      # Middleware function
├── netlify.toml               # Configuration
└── ...
```

## Basic Edge Function

```typescript
// netlify/edge-functions/hello.ts

import type { Context } from "@netlify/edge-functions";

export default async (request: Request, context: Context) => {
  const geo = context.geo;

  return new Response(`Hello from ${geo.city}, ${geo.country}!`, {
    headers: { "content-type": "text/plain" },
  });
};

// Configuration (in same file)
export const config = {
  path: "/hello",
};
```

## Context Object

The `Context` object provides:

```typescript
interface Context {
  // Geolocation data
  geo: {
    city?: string;
    country?: { code: string; name: string };
    subdivision?: { code: string; name: string };
    timezone?: string;
    latitude?: number;
    longitude?: number;
  };

  // Cookies
  cookies: {
    get(name: string): string | undefined;
    set(options: CookieOptions): void;
    delete(name: string): void;
  };

  // Request IP
  ip: string;

  // Next handler (for middleware)
  next(): Promise<Response>;

  // Rewrite to different URL
  rewrite(url: string | URL): Response;

  // JSON helper
  json(data: any, init?: ResponseInit): Response;
}
```

## Common Patterns

### Geolocation-Based Routing

```typescript
// netlify/edge-functions/geo-redirect.ts

export default async (request: Request, context: Context) => {
  const country = context.geo.country?.code;

  // Redirect EU users to EU site
  if (["DE", "FR", "GB", "ES", "IT"].includes(country || "")) {
    return Response.redirect("https://eu.example.com" + new URL(request.url).pathname);
  }

  return context.next();
};

export const config = {
  path: "/*",
};
```

### Authentication Middleware

```typescript
// netlify/edge-functions/auth.ts

export default async (request: Request, context: Context) => {
  const authHeader = request.headers.get("authorization");

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return new Response("Unauthorized", { status: 401 });
  }

  const token = authHeader.substring(7);

  try {
    // Verify token (example with JWT)
    const payload = await verifyToken(token);
    // Add user info to headers for downstream
    const newHeaders = new Headers(request.headers);
    newHeaders.set("x-user-id", payload.sub);

    return context.next();
  } catch {
    return new Response("Invalid token", { status: 403 });
  }
};

export const config = {
  path: "/api/*",
};
```

### A/B Testing

```typescript
// netlify/edge-functions/ab-test.ts

export default async (request: Request, context: Context) => {
  let variant = context.cookies.get("ab-variant");

  if (!variant) {
    // Randomly assign variant
    variant = Math.random() < 0.5 ? "a" : "b";
    context.cookies.set({
      name: "ab-variant",
      value: variant,
      path: "/",
      maxAge: 60 * 60 * 24 * 30, // 30 days
    });
  }

  // Rewrite to variant page
  const url = new URL(request.url);
  if (url.pathname === "/landing") {
    return context.rewrite(`/landing-${variant}`);
  }

  return context.next();
};

export const config = {
  path: "/landing",
};
```

### Response Transformation

```typescript
// netlify/edge-functions/transform.ts

export default async (request: Request, context: Context) => {
  const response = await context.next();
  const html = await response.text();

  // Inject script
  const modified = html.replace(
    "</body>",
    `<script>console.log('Edge injected!')</script></body>`
  );

  return new Response(modified, {
    status: response.status,
    headers: response.headers,
  });
};

export const config = {
  path: "/*.html",
};
```

### Request Header Modification

```typescript
// netlify/edge-functions/headers.ts

export default async (request: Request, context: Context) => {
  const newHeaders = new Headers(request.headers);
  newHeaders.set("x-custom-header", "edge-value");
  newHeaders.set("x-geo-country", context.geo.country?.code || "unknown");

  return context.next();
};

export const config = {
  path: "/*",
};
```

## Configuration

### In-File Config

```typescript
export const config = {
  path: "/api/*",              // URL pattern
  excludedPath: "/api/public", // Exclude pattern
  method: "GET",               // HTTP method filter
  cache: "manual",             // Caching mode
};
```

### netlify.toml Config

```toml
[[edge_functions]]
  function = "hello"
  path = "/hello"

[[edge_functions]]
  function = "auth"
  path = "/api/*"

[[edge_functions]]
  function = "geo"
  path = "/*"
  excludedPath = ["/static/*", "/_next/*"]
```

## Caching

```typescript
export default async (request: Request, context: Context) => {
  const response = new Response("Cached content");

  // Cache for 1 hour
  response.headers.set("Cache-Control", "public, max-age=3600");

  // Or use CDN-Cache-Control for edge caching
  response.headers.set("CDN-Cache-Control", "public, max-age=86400");

  return response;
};

export const config = {
  cache: "manual", // Enable caching
};
```

## Local Development

```bash
# Run edge functions locally
netlify dev

# Edge functions automatically available at configured paths
```

## Deployment

Edge Functions deploy automatically with your site:

```bash
# Deploy to draft URL
netlify deploy

# Deploy to production
netlify deploy --prod
```

## Limits

| Limit | Value |
|-------|-------|
| **Execution time** | 50ms (default), up to 10s |
| **Memory** | 128 MB |
| **Request body** | 40 KB |
| **Response body** | 10 MB |
| **Invocations** | Based on plan |

## Framework Integration

Edge Functions integrate with popular frameworks:

- **Next.js**: Middleware, RSC
- **Nuxt 3**: Server routes
- **SvelteKit**: Hooks
- **Remix**: Loaders
- **Astro**: SSR

## External Resources

- [Edge Functions Docs](https://docs.netlify.com/edge-functions/overview/)
- [Edge Functions Examples](https://edge-functions-examples.netlify.app)
- [Deno Documentation](https://deno.land/manual)
- [API Reference](https://docs.netlify.com/edge-functions/api/)
