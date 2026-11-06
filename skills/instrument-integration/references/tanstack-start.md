> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# TanStack Start

Canonical URL: https://posthog.com/docs/libraries/tanstack-start

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Installation](#installation)
- [Identifying users](#identifying-users)
- [Initialize PostHog on the client](#initialize-posthog-on-the-client)
- [Capture events on the client](#capture-events-on-the-client)
- [Initialize PostHog on the server](#initialize-posthog-on-the-server)
- [Capture events on the server](#capture-events-on-the-server)
- [Add request context to backend spans](#add-request-context-to-backend-spans)
- [Next steps](#next-steps)

This tutorial shows how to integrate PostHog with a [TanStack Start](https://tanstack.com/start) app for both client-side and server-side analytics.

## Install with the wizard

Run this command in your project directory to add PostHog to your TanStack Start project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

## Installation

Install the required packages:

```bash
npm install @posthog/react posthog-node
```

-   `@posthog/react` - React package for our [JS Web SDK](https://posthog.com/docs/libraries/js.md) for client-side usage
-   `posthog-node` - PostHog [Node.js SDK](https://posthog.com/docs/libraries/node.md) for server-side event capture

> **If your site sets a Content-Security-Policy**, it needs to allow PostHog. This applies to the snippet and to package installs alike: the SDK lazy-loads extra bundles (session replay, surveys) from PostHog's CDN, and sends events to the ingestion host. PostHog serves from subdomains of `posthog.com` that change over time, so allow the wildcard:
>
> ```
> script-src 'self' https://*.posthog.com;
> connect-src 'self' https://*.posthog.com;
> worker-src 'self' blob: data:;
> ```
>
> `script-src` covers the snippet and the lazy-loaded bundles, `connect-src` covers event ingestion and feature flags, and `worker-src` covers session replay. The [toolbar needs a few more](https://posthog.com/docs/advanced/content-security-policy.md), or use a [reverse proxy](https://posthog.com/docs/advanced/proxy.md) so everything is first-party. Failing to do so causes silent failures where `capture` and `identify` calls never send, so the integration looks complete while zero events arrive. Remember `connect-src` falls back to `default-src`, so `default-src 'self'` blocks event delivery even when the script itself is bundled.

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](https://posthog.com/docs/session-replay.md), [LLM traces](https://posthog.com/docs/ai-engineering.md), and [error tracking](https://posthog.com/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> Use a stable ID from your auth system when possible, not an email or display name. Send those as person properties instead. If your app has no other stable key, email works as a fallback if they are unique. Never a shared literal like `"anonymous"` or `"user"`, which pools many people onto one person and corrupts their data. When no ID is available at all, skip the identify and retain the anonymous distinct ID that's automatically assigned.
>
> Call `posthog.reset()` on logout, so the next person to use the browser doesn't inherit the last one's identity.
>
> See our guide on [identifying users](https://posthog.com/docs/getting-started/identify-users.md) for how to set this up.

If your app calls your own backend, `tracing_headers` adds `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` to matching `fetch` and `XMLHttpRequest` requests. This lets server-side SDKs link backend events, errors, and LLM traces back to frontend sessions and replays. Use hostnames only, without protocols or paths.

```javascript
posthog.init('<ph_project_token>', {
  api_host: 'https://us.i.posthog.com',
  // Optional: send PostHog session/user context to your backend
  tracing_headers: ['api.example.com'],
})
```

This works in local development too, but match on the hostname alone: use `'localhost'`, not `'localhost:3000'`. Ports are never part of a hostname, so a value with one in it never matches anything. `localhost` and `127.0.0.1` are also different hostnames — use whichever your app actually calls.

Tracing headers help you attribute events across front and backend consistently. When this isn't available, use your server-side stable IDs to deduce the matching `distinctId`, and pass it in when capturing the event.

## Initialize PostHog on the client

Wrap your app with `PostHogProvider` in your root route with your project token, host, and other options.

src/routes/\_\_root.tsx

```jsx
// src/routes/__root.tsx
import { HeadContent, Scripts, createRootRoute } from '@tanstack/react-router'
import { PostHogProvider } from '@posthog/react'

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
    ],
  }),
  shellComponent: RootDocument,
})

function RootDocument({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <PostHogProvider
          apiKey="<ph_project_token>"
          options={{
            api_host: 'https://us.i.posthog.com',
            defaults: '2026-08-30',
            capture_exceptions: true
          }}
        >
          {children}
        </PostHogProvider>
        <Scripts />
      </body>
    </html>
  )
}
```

Once the provider is in place, PostHog automatically captures pageviews, sessions, and web vitals.

## Capture events on the client

Use the `usePostHog` hook from `@posthog/react` in any component to capture custom events:

src/routes/checkout.tsx

```jsx
import { usePostHog } from '@posthog/react'

function CheckoutButton({ orderId, total }: { orderId: string; total: number }) {
  const posthog = usePostHog()

  const handleClick = () => {
    posthog.capture('checkout_started', {
      order_id: orderId,
      total: total,
    })
  }

  return <button onClick={handleClick}>Checkout</button>
}
```

### Identify users

Call `posthog.identify()` when a user logs in to link their events to a user ID:

```jsx
import { usePostHog } from '@posthog/react'

function LoginForm() {
  const posthog = usePostHog()

  const handleLogin = async (userId: string, email: string) => {
    // ... your login logic

    posthog.identify(userId, {
      email: email,
    })

    posthog.capture('user_logged_in')
  }
}
```

Call `posthog.reset()` on logout to clear the identified user.

## Initialize PostHog on the server

Create a server-side PostHog client using `posthog-node`. Use a singleton pattern so you reuse the same client across requests:

src/utils/posthog-server.ts

```typescript
// src/utils/posthog-server.ts
import { PostHog } from 'posthog-node'

let posthogClient: PostHog | null = null

export function getPostHogClient() {
  if (!posthogClient) {
    posthogClient = new PostHog(
      '<ph_project_token>',
      {
        host: 'https://us.i.posthog.com',
        flushAt: 1,
        flushInterval: 0,
      },
    )
  }
  return posthogClient
}
```

## Capture events on the server

Use the server client in TanStack Start API routes to capture events server-side. Server-side capture is useful for tracking events that shouldn't be spoofable from the client, like purchases or authentication:

src/routes/api/checkout.ts

```typescript
// src/routes/api/checkout.ts
import { createFileRoute } from '@tanstack/react-router'
import { getPostHogClient } from '../../utils/posthog-server'

export const Route = createFileRoute('/api/checkout')({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const body = await request.json()

        const posthog = getPostHogClient()

        posthog.capture({
          distinctId: body.userId,
          event: 'item_purchased',
          properties: {
            item_id: body.itemId,
            price: body.price,
            source: 'api',
          },
        })

        return Response.json({ success: true })
      },
    },
  },
})
```

The server-side `capture` call requires a `distinctId` (the user identifier), an `event` name, and optional `properties`.

## Add request context to backend spans

For a Node.js deployment with OpenTelemetry, reuse `getPostHogClient()` for both request context and the span processor. Add this processor to your existing tracing provider before the server accepts requests:

```typescript
import { PostHogContextSpanProcessor } from 'posthog-node/otel'
import { getPostHogClient } from './src/utils/posthog-server'

const posthogSpanProcessor = new PostHogContextSpanProcessor(getPostHogClient())
```

Include `posthogSpanProcessor` in that provider's `spanProcessors` configuration. Keep your existing exporter, sampler, and instrumentation. See the [Node.js tracing setup](https://posthog.com/docs/distributed-tracing/installation/nodejs.md#with-opentelemetry) for provider setup. Keep this setup on the server. Shut down the provider and the PostHog client through your application's shutdown hook, after requests finish.

Add global request middleware in `src/start.ts`. If that file already exists, add the middleware to its existing configuration. Keep your existing CSRF and authentication middleware. This example includes TanStack Start's CSRF middleware because defining `src/start.ts` replaces its default setup.

src/start.ts

```typescript
import {
  createCsrfMiddleware,
  createMiddleware,
  createStart,
} from '@tanstack/react-start'
import { enrichCurrentSpan } from 'posthog-node/otel'
import { getPostHogClient } from './utils/posthog-server'

function tracingHeader(request: Request, name: string): string | undefined {
  const value = request.headers.get(name)
  return value?.replace(/[\x00-\x1f\x7f-\x9f]/g, '').trim().slice(0, 1000) || undefined
}

const posthogContext = createMiddleware().server(async ({ request, next }) => {
  const posthog = getPostHogClient()
  const existing = posthog.getContext()

  return posthog.withContext(
    {
      distinctId:
        existing?.distinctId ??
        tracingHeader(request, 'X-POSTHOG-DISTINCT-ID'),
      sessionId:
        existing?.sessionId ??
        tracingHeader(request, 'X-POSTHOG-SESSION-ID'),
    },
    async () => {
      enrichCurrentSpan(posthog)
      return await next()
    },
    { fresh: true }
  )
})

export const startInstance = createStart(() => ({
  requestMiddleware: [createCsrfMiddleware({ filter: ({ handlerType }) => handlerType === 'serverFn' }), posthogContext],
}))
```

This setup was checked with TanStack Start 1.169.3 on Node.js. It runs for SSR, server routes, and server functions. It reads the two browser tracing headers without copying other headers or request data. The header helper removes control characters, trims whitespace, and limits each ID to 1,000 characters. An identity already set by application code takes precedence. Treat browser IDs as analytics data, not authentication. Set authenticated identity before this middleware when you need it to take precedence.

The processor fills missing `sessionId` and `posthogDistinctId` span attributes. Explicit canonical attributes stay unchanged, including non-string values. `user.id` alone is not an override. At request entry, the helper also fills missing attributes on the nearest recording server ancestor whose parent chain the processor observed. A sampler-dropped intermediate breaks that chain, so the earlier server span stays unchanged.

Work that the request starts, including detached tasks, keeps the IDs after `next()` returns or throws. This example does not support the edge runtime. Give separately owned background work that needs its own IDs an explicit context.

TanStack handles some route and server-function errors before middleware can see them. Capture an error once at the application handler that owns it, while request context is active:

```typescript
try {
  await savePurchase()
} catch (error) {
  getPostHogClient().captureException(error)
  throw error
}
```

Do not add a second capture if an existing error handler already reports the same error. This middleware does not enable automatic error capture.

## Next steps

Installing the JS Web SDK and Node SDK means all of their functionality is available in your TanStack Start project. To learn more about this, have a look at our [JS Web SDK docs](https://posthog.com/docs/libraries/js/usage.md) and [Node SDK docs](https://posthog.com/docs/libraries/node.md).
