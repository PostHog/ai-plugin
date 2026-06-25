# TanStack Start - Docs

This tutorial shows how to integrate PostHog with a [TanStack Start](https://tanstack.com/start) app for both client-side and server-side analytics.

## Installation

Install the required packages:

Terminal

PostHog AI

```bash
npm install @posthog/react posthog-node
```

-   `@posthog/react` - React package for our [JS Web SDK](/docs/libraries/js.md) for client-side usage
-   `posthog-node` - PostHog [Node.js SDK](/docs/libraries/node.md) for server-side event capture

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Initialize PostHog on the client

Wrap your app with `PostHogProvider` in your root route with your project token, host, and other options.

src/routes/\_\_root.tsx

PostHog AI

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
            defaults: '2026-05-30',
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

PostHog AI

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

TSX

PostHog AI

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

PostHog AI

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

PostHog AI

```typescript
// src/routes/api/checkout.ts
import { createFileRoute } from '@tanstack/react-router'
import { json } from '@tanstack/react-start'
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
        return json({ success: true })
      },
    },
  },
})
```

The server-side `capture` call requires a `distinctId` (the user identifier), an `event` name, and optional `properties`.

## Next steps

Installing the JS Web SDK and Node SDK means all of their functionality is available in your TanStack Start project. To learn more about this, have a look at our [JS Web SDK docs](/docs/libraries/js/usage.md) and [Node SDK docs](/docs/libraries/node.md).

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better