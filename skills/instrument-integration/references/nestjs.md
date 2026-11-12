> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# NestJS

Canonical URL: https://posthog.com/docs/libraries/nestjs

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setting up the interceptor](#setting-up-the-interceptor)
- [Error Tracking](#error-tracking)
- [Trace context](#trace-context)
- [Next steps](#next-steps)

PostHog integrates with your [NestJS](https://nestjs.com/) app to enable analytics, custom events capture, Feature Flags, Error Tracking, and more.

This guide walks you through integrating PostHog with your NestJS app using the `PostHogInterceptor`, which provides automatic context propagation and optional exception capture.

## Prerequisites

To follow this guide along, you need:

1.  A PostHog instance (either [Cloud](https://app.posthog.com/signup) or [self-hosted](https://posthog.com/docs/self-host.md))
2.  A NestJS application (v8+)

## Installation

Install the `posthog-node` package:

```bash
npm install posthog-node@5
# or
yarn add posthog-node@5
# or
pnpm add posthog-node@5
# or
bun add posthog-node@5
```

## Setting up the interceptor

The `PostHogInterceptor` is a NestJS interceptor that automatically propagates context (session ID, distinct ID, request metadata) to all `posthog.capture()` calls within a request. It uses `AsyncLocalStorage` under the hood for per-request isolation.

In your `main.ts`, create a PostHog client and register the interceptor globally:

main.ts

```typescript
import { NestFactory } from '@nestjs/core'
import { PostHog } from 'posthog-node'
import { PostHogInterceptor } from 'posthog-node/nestjs'
import { AppModule } from './app.module'

async function bootstrap() {
  const app = await NestFactory.create(AppModule)

  const posthog = new PostHog('<ph_project_token>', {
    host: 'https://us.i.posthog.com',
  })

  app.useGlobalInterceptors(new PostHogInterceptor(posthog))

  await app.listen(3000)
}
bootstrap()
```

### Context propagation

The interceptor reads the following headers from incoming requests and attaches them as context to all PostHog calls within that request:

| Header | Context property | Description |
| --- | --- | --- |
| `x-posthog-session-id` | `sessionId` | Links server events to a client session |
| `x-posthog-distinct-id` | `distinctId` | Sets the event distinct ID |

It also automatically captures request metadata as properties:

-   `$current_url` – the request URL
-   `$request_method` – the HTTP method (GET, POST, etc.)
-   `$request_path` – the request path
-   `$user_agent` – the user agent string
-   `$ip` – the client IP (parsed from `x-forwarded-for` if behind a proxy)

Tracing headers are client-controlled analytics context, not authentication or authorization. Pass an authenticated `distinctId` explicitly for security-sensitive server-side decisions.

### Send headers from the client

If you're using [PostHog JS](https://posthog.com/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) for your NestJS backend hostname so browser requests include `X-POSTHOG-SESSION-ID` and `X-POSTHOG-DISTINCT-ID`, which the `PostHogInterceptor` reads automatically.

### Capturing events in controllers

With the interceptor active, any `posthog.capture()` call within a request automatically includes the propagated context:

app.controller.ts

```typescript
import { Controller, Get, Post, Body } from '@nestjs/common'
import { PostHog } from 'posthog-node'

@Controller()
export class AppController {
  constructor(private readonly posthog: PostHog) {}

  @Post('checkout')
  checkout(@Body() body: any) {
    this.posthog.capture({
      event: 'checkout_started',
      // distinctId, sessionId, and request properties
      // are automatically included from the interceptor context
    })
    return { status: 'ok' }
  }
}
```

## Error Tracking

The `PostHogInterceptor` supports optional exception capture. When enabled, it automatically captures unhandled exceptions thrown during request handling and sends them to PostHog [Error Tracking](https://posthog.com/docs/error-tracking.md).

By default, exception capture is **disabled**. To enable it:

main.ts

```typescript
// Capture server errors (5xx) only (default threshold)
app.useGlobalInterceptors(
  new PostHogInterceptor(posthog, { captureExceptions: true })
)
```

### Configuring the minimum status to capture

By default, 4xx errors (like `NotFoundException` or `BadRequestException`) are skipped – only 5xx errors are captured. You can lower the threshold:

main.ts

```typescript
// Also capture 4xx errors
app.useGlobalInterceptors(
  new PostHogInterceptor(posthog, {
    captureExceptions: { minStatusToCapture: 400 },
  })
)
```

**How exception capture works**

The interceptor uses an RxJS `catchError` operator to observe exceptions without interfering with NestJS's exception filter pipeline. It:

-   Skips exceptions that have already been captured (deduplication)
-   Skips `HttpException`s with a status code below `minStatusToCapture` (default: 500)
-   Re-throws the exception after capturing, so NestJS exception filters still work as expected

For more details on Error Tracking setup, see the [NestJS Error Tracking installation guide](https://posthog.com/docs/error-tracking/installation/nestjs.md).

## Trace context

Register the [optional Node context processor](https://posthog.com/docs/distributed-tracing/installation/nodejs.md#with-opentelemetry) on your existing OpenTelemetry provider before requests start. Use the same client passed to `PostHogInterceptor`. Keep your provider, exporter, and sampler.

The interceptor adds missing `sessionId` and `posthogDistinctId` attributes to an active request span after reading the request headers. The processor adds them to child spans when they start. Existing canonical attributes take precedence. Missing IDs stay absent.

With the Express and Fastify HTTP adapters, the context stays active for work that the request starts, including work that continues after the response ends. Existing spans keep their IDs. A background job that needs its own IDs needs an explicit context.

This setup was verified for HTTP on both adapters. WebSocket, GraphQL, and custom adapters need separate verification.

## Next steps

To read more about how to integrate specific PostHog features into NestJS, have a look at our [Node SDK docs](https://posthog.com/docs/libraries/node.md) for concepts such as:

-   [Capturing custom events, setting properties, and more.](https://posthog.com/docs/libraries/node.md#capturing-events)
-   [Setting up Feature Flags including variants and payloads.](https://posthog.com/docs/libraries/node.md#feature-flags)
-   [Using contexts for per-request state management.](https://posthog.com/docs/libraries/node.md#contexts)
