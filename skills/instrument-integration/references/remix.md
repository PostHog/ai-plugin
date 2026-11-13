> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Remix

Canonical URL: https://posthog.com/docs/libraries/remix

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://us.posthog.com` (app host for links).

## On this page

- [Installation](#installation)
- [Node.js server context and traces](#nodejs-server-context-and-traces)
- [Identifying users](#identifying-users)
- [Next steps](#next-steps)

PostHog makes it easy to get data about traffic and usage of your [Remix](https://remix.run/) app. Integrating PostHog into your site enables analytics about user behavior, custom events capture, session recordings, feature flags, and more.

**Using Remix V3?**

Remix V3 is now React Router V7 framework mode. Please refer to the [React Router V7 framework mode](https://posthog.com/docs/libraries/react-router/react-router-v7-framework-mode.md) guide instead for instructions on how to integrate PostHog.

This guide walks you through integrating PostHog into your Remix app using the [JavaScript Web SDK](https://posthog.com/docs/libraries/js.md).

## Installation

Install `posthog-js` and `@posthog/react`:

```bash
npm install --save posthog-js@1 @posthog/react@1
```

> **If your site sets a Content-Security-Policy**, it needs to allow PostHog. This applies to the snippet and to package installs alike: the SDK lazy-loads extra bundles (session replay, surveys) from PostHog's CDN, and sends events to the ingestion host. PostHog serves from subdomains of `posthog.com` that change over time, so allow the wildcard:
>
> ```
> script-src 'self' https://*.posthog.com;
> connect-src 'self' https://*.posthog.com;
> worker-src 'self' blob: data:;
> ```
>
> `script-src` covers the snippet and the lazy-loaded bundles, `connect-src` covers event ingestion and feature flags, and `worker-src` covers session replay. The [toolbar needs a few more](https://posthog.com/docs/advanced/content-security-policy.md), or use a [reverse proxy](https://posthog.com/docs/advanced/proxy.md) so everything is first-party. Failing to do so causes silent failures where `capture` and `identify` calls never send, so the integration looks complete while zero events arrive. Remember `connect-src` falls back to `default-src`, so `default-src 'self'` blocks event delivery even when the script itself is bundled.

Start by setting `posthog-js` and `@posthog/react` as external packages in your `vite.config.ts` file.

```typescript
// vite.config.ts
// ... imports and rest of config

export default defineConfig({
  plugins: [
    remix({
      future: {
        v3_fetcherPersist: true,
        v3_relativeSplatPath: true,
        v3_throwAbortReason: true,
        v3_singleFetch: true,
        v3_lazyRouteDiscovery: true,
      },
    }),
    tsconfigPaths(),
  ],
  ssr: {
    noExternal: ["posthog-js", "@posthog/react"],
  },
});
```

Next, create a `provider.tsx` file in the `app` folder. In it, set up the PostHog provider to initialize after hydration. You'll need both your API key and instance address (you can find these in your [project settings](https://us.posthog.com/project/settings)).

```typescript
// app/provider.tsx
import { useEffect, useState } from "react";
import posthog from "posthog-js";
import { PostHogProvider } from "@posthog/react";

export function PHProvider({ children }: { children: React.ReactNode }) {
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    posthog.init("<ph_project_token>", {
      api_host: "https://us.i.posthog.com",
      defaults: "2026-08-30",
    });

    setHydrated(true);
  }, []);

  if (!hydrated) return <>{children}</>;
  return <PostHogProvider client={posthog}>{children}</PostHogProvider>;
}
```

Finally, import the `PHProvider` component in your `app/root.tsx` file and use it to wrap your app.

```typescript
// app/root.tsx
// ... imports
import { PHProvider } from "./provider";

// ... links, meta, etc.

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <PHProvider>
          {children}
          <ScrollRestoration />
          <Scripts />
        </PHProvider>
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}
```

When you run your app now, PostHog will automatically capture events and pageviews. You can also use the other features of PostHog by importing and using the `usePostHog` hook in your components.

## Node.js server context and traces

For a Remix server on Node.js, use the `@remix-run/express` adapter and the shared Node SDK request middleware. The browser setup above does not add server context.

Reuse one `posthog-node` client from your server setup. Add `PostHogContextSpanProcessor` from `posthog-node/otel` to your application's existing OpenTelemetry provider. Keep your exporter, sampler, and other processors. Load your tracing setup, including HTTP and Express instrumentation, before importing the server modules below.

```typescript
import express from 'express'
import { createRequestHandler } from '@remix-run/express'
import { setupExpressRequestContext } from 'posthog-node'
import posthog from './posthog.server.js'
import * as build from './build/server/index.js'

const app = express()

setupExpressRequestContext(posthog, app)

app.all('*', createRequestHandler({
    build,
    getLoadContext: () => ({ posthog }),
}))
```

Place the middleware before `createRequestHandler`. This covers document requests, loader data requests, actions, resource routes, server rendering, and streamed responses. Wrapping only `entry.server` misses loader and action requests that do not render a document.

The middleware reads the PostHog tracing headers and fills missing context. An existing application identity takes precedence over the browser value. Use your existing authentication setup for application identity. These headers are analytics context and must not be used for authentication or authorization.

Only requests that carry the headers receive browser context. Fetch/XHR instrumentation does not add these headers to standard browser document navigations, so initial server rendering can have no browser IDs.

The optional processor adds `sessionId` and `posthogDistinctId` to application spans. At request entry, it can also fill missing IDs on the nearest recording HTTP server span through parent objects observed by the processor. Explicit canonical attributes keep their values. If the sampler drops an intermediate span, the processor cannot verify the earlier server ancestor and leaves it unchanged. Recording spans created within the request still receive context.

Request context stays active for async work that the request starts, including streaming work and work that continues after the response ends. Use a new explicit context for a background job that needs its own IDs.

Remix handles many loader and action errors inside its router, so an Express error handler alone does not capture all of them. To capture these errors, use Remix's `handleError` export in `app/entry.server.tsx` with the same server client:

```typescript
import posthog from '../posthog.server.js'

export function handleError(error: unknown) {
    posthog.captureException(error)
}
```

This setup was checked with Remix 2.17.5 and its Node.js Express adapter. Other adapters and runtimes need their own context and lifetime setup. See the [Node.js tracing guide](https://posthog.com/docs/distributed-tracing/installation/nodejs.md) for the shared processor setup and limits.

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

**Set up a reverse proxy (recommended)**

We recommend [setting up a reverse proxy](https://posthog.com/docs/advanced/proxy.md), so that events are less likely to be intercepted by tracking blockers.

We have our [own managed reverse proxy service](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md), which is free for all PostHog Cloud users, routes through our infrastructure, and makes setting up your proxy easy.

If you don't want to use our managed service then there are several other options for creating a reverse proxy, including using [Cloudflare](https://posthog.com/docs/advanced/proxy/cloudflare.md), [AWS Cloudfront](https://posthog.com/docs/advanced/proxy/cloudfront.md), and [Vercel](https://posthog.com/docs/advanced/proxy/vercel.md).

**Grouping products in one project (recommended)**

If you have multiple customer-facing products (e.g. a marketing website + mobile app + web app), it's best to install PostHog on them all and [group them in one project](https://posthog.com/docs/settings/projects.md).

This makes it possible to track users across their entire journey (e.g. from visiting your marketing website to signing up for your product), or how they use your product across multiple platforms.

**Add IPs to Firewall/WAF allowlists (recommended)**

For certain features like [heatmaps](https://posthog.com/docs/toolbar/heatmaps.md), your Web Application Firewall (WAF) may be blocking PostHog's requests to your site. Add these IP addresses to your WAF allowlist or rules to let PostHog access your site.

**EU**: `3.75.65.221`, `18.197.246.42`, `3.120.223.253`, `3.40.9.80/28`

**US**: `44.205.89.55`, `52.4.194.122`, `44.208.188.173`, `3.41.215.48/28`

These are public, stable IPs used by PostHog services.

PostHog captures heatmap screenshots using [Browserless](https://www.browserless.io), which has its own IP addresses. Browserless [publishes the current list here](https://docs.browserless.io/baas/troubleshooting/whitelisting-ips).

An allowlist does not help when your app has a private address. For apps on an internal network, see [internal and intranet applications](https://posthog.com/docs/session-replay/troubleshooting.md#internal-and-intranet-applications).

## Next steps

For any technical questions for how to integrate specific PostHog features into Remix (such as analytics, feature flags, A/B testing, surveys, etc.), have a look at our [JavaScript Web SDK docs](https://posthog.com/docs/libraries/js/usage.md) and [React](https://posthog.com/docs/libraries/react.md) docs.

Alternatively, the following tutorials can help you get started:

-   [How to set up Remix analytics, feature flags, and more](https://posthog.com/tutorials/remix-analytics.md)
-   [How to set up A/B tests in Remix](https://posthog.com/tutorials/remix-ab-tests.md)
-   [How to set up surveys in Remix](https://posthog.com/tutorials/remix-surveys.md)
