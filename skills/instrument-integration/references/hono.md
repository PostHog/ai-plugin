> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Hono

Canonical URL: https://posthog.com/docs/libraries/hono

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://us.posthog.com` or `https://app.posthog.com` (app host for links).

## On this page

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Error tracking](#error-tracking)
- [Trace context on Node.js](#trace-context-on-nodejs)
- [Next steps](#next-steps)

PostHog makes it easy to get data about usage of your [Hono](https://hono.dev/) app. Integrating PostHog into your app enables analytics, custom events capture, feature flags, and more.

This guide walks you through integrating PostHog with your Hono app running on the [Node.js](https://hono.dev/docs/getting-started/nodejs) runtime, but has also been tested with Cloudflare Workers, Vercel, and Bun. You can hook into the same middleware and `onError` for other runtimes to capture events.

## Prerequisites

To follow this guide along, you need:

1.  A PostHog instance (either [Cloud](https://app.posthog.com/signup) or [self-hosted](https://posthog.com/docs/self-host.md))
2.  A Hono application. We suggest trying first with a fresh [Hono Node.js starter template](https://hono.dev/docs/getting-started/nodejs#_1-setup).

## Installation

Start by installing the `posthog-node` package using your package manager.

```bash
npm install --save posthog-node
```

Then, create a [middleware](https://hono.dev/docs/guides/middleware) to capture events for your routes. Remember to **export** your [project token](https://us.posthog.com/settings/project#variables) as an environment variable.

index.ts

```javascript
import { env } from 'hono/adapter'
import { createMiddleware } from 'hono/factory'
import { PostHog } from 'posthog-node'

const posthog = new PostHog(process.env.POSTHOG_PUBLIC_KEY, { host: 'https://us.i.posthog.com' })

const posthogServerMiddleware = createMiddleware(async (c, next) => {

  posthog.capture({
      distinctId: 'distinct_id_of_user', // Their user id or email
      event: 'user_did_something',
  })

  await next()

  await posthog.flush()
})
```

**Shutdown**

Keep one PostHog client for the Node.js application. Call `await posthog.shutdown()` once during application cleanup, after requests stop. Use `flush()` when an invocation must wait for buffered events, without shutting down the shared client.

Next, apply this middleware to your app. This middleware will be called on every request handled by Hono, denoted by the wildcard `*`.

index.ts

```typescript
// use the middleware on all (*) routes.
app.use('*', posthogServerMiddleware)
```

In your routes, you can pass information to be captured by your middleware using [context `set()` and `get()` pair](https://hono.dev/docs/api/context#set-get)

**Cloudflare Pages**

Cloudflare Pages uses its own middleware system that is different from Hono's middleware. Follow the [Hono documentation on Cloudflare Pages](https://hono.dev/docs/getting-started/cloudflare-pages#cloudflare-pages-middleware) to handle middleware.

## Error tracking

Hono uses [`app.onError`](https://hono.dev/docs/api/exception#handling-httpexception) for root-level error handling. You can take advantage of this for [Error tracking](https://posthog.com/docs/error-tracking.md).

Reuse the existing client in your application's error handler:

index.ts

```typescript
app.onError(async (err, c) => {
  await posthog.captureExceptionImmediate(err, undefined, {
    path: c.req.path,
    method: c.req.method,
    // ... other properties
  })
  await posthog.flush()
  // other error handling logic
  return c.text('Internal Server Error', 500)
})
```

## Trace context on Node.js

For Node.js, register the [optional context processor](https://posthog.com/docs/distributed-tracing/installation/nodejs.md#with-opentelemetry) on your existing OpenTelemetry provider before requests start. Reuse the existing `posthog` client. Keep your exporter and sampler, and put tracing middleware outside the PostHog middleware.

Configure [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) for your backend hostname. Replace the earlier `posthogServerMiddleware` with this middleware and register it before your routes:

```javascript
import { enrichCurrentSpan } from 'posthog-node/otel'

function readTracingId(value) {
    return value?.replace(/[\x00-\x1f\x7f-\x9f]/g, '').trim().slice(0, 1000) || undefined
}

const posthogServerMiddleware = createMiddleware(async (c, next) => {
    const user = c.get('user')
    return posthog.withContext(
        {
            distinctId: user?.id ?? readTracingId(c.req.header('x-posthog-distinct-id')),
            sessionId: readTracingId(c.req.header('x-posthog-session-id')),
        },
        async () => {
            enrichCurrentSpan(posthog)
            await next()
        },
        { fresh: true }
    )
})
```

The optional `user` value belongs to your application. Set it in earlier authentication middleware with a verified string `id`, or omit it and use header fallback for analytics. Header IDs are client-controlled analytics context, never authentication or authorization.

The helper enriches an active request span; the processor snapshots IDs for child spans. Existing canonical `sessionId` and `posthogDistinctId` attributes take precedence. Missing IDs stay absent. Work that the request starts keeps its IDs after `next()` returns, including after failures. Stream body work that starts outside the request needs its own explicit context.

This automatic context setup requires the Node.js entry point. The SDK's edge entry point does not provide async request context. Explicit event properties in other runtimes are a separate path; this example does not establish Workers span support.

## Next steps

To read more about how to integrate specific PostHog features into Hono, have a look at our [Node SDK docs](https://posthog.com/docs/libraries/node.md) for concepts such as:

-   [Capturing custom events, setting properties, and more.](https://posthog.com/docs/libraries/node.md#capturing-events)
-   [Setting up feature flags including variants and payloads.](https://posthog.com/docs/libraries/node.md#feature-flags)
