# Nuxt.js - Docs

PostHog makes it easy to get data about usage of your [Nuxt.js](https://nuxt.com/) app. Integrating PostHog into your app enables analytics about user behavior, custom events capture, session replays, feature flags, and more.

This guide covers Nuxt v4.x and v3.7+. For these versions, we recommend using `@posthog/nuxt` module for client-side capture.

The `@posthog/nuxt` module provides:

-   Automatic client-side PostHog initialization
-   Auto-imported composables for PostHog and feature flags
-   Automatic exception capture for error tracking
-   Source map configuration and upload for error tracking

For server-side event capture beyond error tracking, use the `posthog-node` SDK directly.

> **Using an older version?** See our docs for [Nuxt 3.0-3.6](/docs/libraries/nuxt-js-3-6.md) or [Nuxt 2.x](/docs/libraries/nuxt-js-2.md).

## Installation

Install the PostHog Nuxt module using your package manager:

PostHog AI

### npm

```bash
npm install @posthog/nuxt
```

### Yarn

```bash
yarn add @posthog/nuxt
```

### pnpm

```bash
pnpm add @posthog/nuxt
```

### Bun

```bash
bun add @posthog/nuxt
```

> **If your site sets a Content-Security-Policy**, it needs to allow PostHog. This applies to the snippet and to package installs alike: the SDK lazy-loads extra bundles (session replay, surveys) from PostHog's CDN, and sends events to the ingestion host. PostHog serves from subdomains of `posthog.com` that change over time, so allow the wildcard:
>
> PostHog AI
>
> ```
> script-src 'self' https://*.posthog.com;
> connect-src 'self' https://*.posthog.com;
> worker-src 'self' blob: data:;
> ```
>
> `script-src` covers the snippet and the lazy-loaded bundles, `connect-src` covers event ingestion and feature flags, and `worker-src` covers session replay. The [toolbar needs a few more](/docs/advanced/content-security-policy.md), or use a [reverse proxy](/docs/advanced/proxy.md) so everything is first-party. Failing to do so causes silent failures where `capture` and `identify` calls never send, so the integration looks complete while zero events arrive. Remember `connect-src` falls back to `default-src`, so `default-src 'self'` blocks event delivery even when the script itself is bundled.

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> Use a stable ID from your auth system when possible, not an email or display name. Send those as person properties instead. If your app has no other stable key, email works as a fallback if they are unique. Never a shared literal like `"anonymous"` or `"user"`, which pools many people onto one person and corrupts their data. When no ID is available at all, skip the identify and retain the anonymous distinct ID that's automatically assigned.
>
> Call `posthog.reset()` on logout, so the next person to use the browser doesn't inherit the last one's identity.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

If your app calls your own backend, `tracing_headers` adds `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` to matching `fetch` and `XMLHttpRequest` requests. This lets server-side SDKs link backend events, errors, and LLM traces back to frontend sessions and replays. Use hostnames only, without protocols or paths.

JavaScript

PostHog AI

```javascript
posthog.init('<ph_project_token>', {
  api_host: 'https://us.i.posthog.com',
  // Optional: send PostHog session/user context to your backend
  tracing_headers: ['api.example.com'],
})
```

This works in local development too, but match on the hostname alone: use `'localhost'`, not `'localhost:3000'`. Ports are never part of a hostname, so a value with one in it never matches anything. `localhost` and `127.0.0.1` are also different hostnames — use whichever your app actually calls.

Tracing headers help you attribute events across front and backend consistently. When this isn't available, use your server-side stable IDs to deduce the matching `distinctId`, and pass it in when capturing the event.

## Configuration

Store your PostHog keys in environment variables rather than hard-coding them. Add them to a `.env` file (and to your hosting provider). You can find these values in [your project settings](https://us.posthog.com/settings/project).

.env

PostHog AI

```shell
NUXT_PUBLIC_POSTHOG_KEY=<ph_project_token>
NUXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

Then reference them when you add the module to your `nuxt.config.ts` file:

nuxt.config.ts

PostHog AI

```typescript
export default defineNuxtConfig({
  modules: ['@posthog/nuxt'],
  posthogConfig: {
    publicKey: process.env.NUXT_PUBLIC_POSTHOG_KEY, // Find it in project settings https://app.posthog.com/settings/project
    host: process.env.NUXT_PUBLIC_POSTHOG_HOST, // Optional: defaults to https://us.i.posthog.com. Use https://eu.i.posthog.com for EU region
    clientConfig: {
      // Optional: PostHog client configuration options
    },
  },
})
```

**Keep your personal API key out of the client bundle**

Anything shipped to the browser – the token you pass to `posthog.init()`, anything under Nuxt's `runtimeConfig.public`, or the `@posthog/nuxt` module's `posthogConfig` – ends up in your client-side JavaScript and is visible to anyone who visits your site. This is fine for your **project token** (`<ph_project_token>`), which is designed to be public.

Your **[personal API key](/docs/api.md#authentication)** is different. It can grant full access to your PostHog account, so it must never reach the browser. If you need it – for example, for [source map uploads](/docs/error-tracking/upload-source-maps/nuxt.md) or [server-side local evaluation](/docs/feature-flags/local-evaluation.md) – read it from a server-only environment variable (or top-level `runtimeConfig`, never `runtimeConfig.public`) and only use it in server code.

Either way, prefer reading keys from environment variables rather than hard-coding them in `nuxt.config`, so you can keep them out of source control and use different values per environment.

## Usage on the client side

The module provides the `usePostHog()` composable which is auto-imported and available in all your Vue components:

app/pages/index.vue

PostHog AI

```html
<script setup>
const posthog = usePostHog()
// Capture a custom event
posthog?.capture('button_clicked', { button_name: 'signup' })
</script>
```

> **Note:** `usePostHog()` returns `undefined` on the server side during SSR, so use optional chaining `?.` when calling methods.

## Usage on the server side

The `@posthog/nuxt` module initializes a server-side client for error tracking only. For general event capture in Nitro routes, create your own `posthog-node` SDK client.

The `@posthog/nuxt` module makes your config available at `runtimeConfig.public.posthog`.

First, create a server utility to reuse the PostHog client across requests:

server/utils/posthog.ts

PostHog AI

```typescript
import { PostHog } from 'posthog-node'
let client: PostHog | null = null
export function useServerPostHog(): PostHog {
  if (!client) {
    const config = useRuntimeConfig()
    client = new PostHog(config.public.posthog.publicKey, {
      host: config.public.posthog.host,
    })
  }
  return client
}
```

Then use it in your server routes:

server/api/example.ts

PostHog AI

```typescript
export default defineEventHandler((event) => {
  const posthog = useServerPostHog()
  posthog.capture({
    distinctId: 'user_123',
    event: 'server_event',
  })
  return { success: true }
})
```

Set up a reverse proxy (recommended)

We recommend [setting up a reverse proxy](/docs/advanced/proxy.md), so that events are less likely to be intercepted by tracking blockers.

We have our [own managed reverse proxy service](/docs/advanced/proxy/managed-reverse-proxy.md), which is free for all PostHog Cloud users, routes through our infrastructure, and makes setting up your proxy easy.

If you don't want to use our managed service then there are several other options for creating a reverse proxy, including using [Cloudflare](/docs/advanced/proxy/cloudflare.md), [AWS Cloudfront](/docs/advanced/proxy/cloudfront.md), and [Vercel](/docs/advanced/proxy/vercel.md).

Grouping products in one project (recommended)

If you have multiple customer-facing products (e.g. a marketing website + mobile app + web app), it's best to install PostHog on them all and [group them in one project](/docs/settings/projects.md).

This makes it possible to track users across their entire journey (e.g. from visiting your marketing website to signing up for your product), or how they use your product across multiple platforms.

Add IPs to Firewall/WAF allowlists (recommended)

For certain features like [heatmaps](/docs/toolbar/heatmaps.md), your Web Application Firewall (WAF) may be blocking PostHog's requests to your site. Add these IP addresses to your WAF allowlist or rules to let PostHog access your site.

**EU**: `3.75.65.221`, `18.197.246.42`, `3.120.223.253`

**US**: `44.205.89.55`, `52.4.194.122`, `44.208.188.173`

These are public, stable IPs used by PostHog services (e.g., Celery tasks for snapshots).

## Feature flags

The module provides auto-imported composables for feature flags. All composables return reactive refs that automatically update when flags are loaded or changed.

Vue

PostHog AI

```html
<script setup>
const isEnabled = useFeatureFlagEnabled('new-feature')
// returns true, false, or undefined
</script>
<template>
  <div v-if="isEnabled">Feature is enabled!</div>
</template>
```

Vue

PostHog AI

```html
<script setup>
const variant = useFeatureFlagVariantKey('experiment')
// returns the variant string, true/false, or undefined
</script>
<template>
  <div v-if="variant === 'control'">Control group</div>
  <div v-else-if="variant === 'test'">Test group</div>
</template>
```

Vue

PostHog AI

```html
<script setup>
const payload = useFeatureFlagPayload('config-flag')
// returns any JSON value or undefined
</script>
<template>
  <div v-if="payload">Config: {{ payload.value }}</div>
</template>
```

## Error Tracking

For a detailed error tracking installation guide, including automatic exception capture and source map configuration, see the [Nuxt error tracking installation docs](/docs/error-tracking/installation/nuxt-3-7.md).

## Troubleshooting

**TypeScript errors in posthog config:** Remove the `.nuxt` directory and rebuild your project to regenerate config types.

**PostHog not capturing events:** Ensure you're using optional chaining (`posthog?.capture()`) since `usePostHog()` returns `undefined` during server-side rendering.

## Next steps

For any technical questions for how to integrate specific PostHog features into Nuxt (such as analytics, feature flags, A/B testing, surveys, etc.), have a look at our [JavaScript Web](/docs/libraries/js.md) and [Node](/docs/libraries/node.md) SDK docs.

Alternatively, the following tutorials can help you get started:

-   [How to set up analytics in Nuxt](/tutorials/nuxt-analytics.md)
-   [How to set up feature flags in Nuxt](/tutorials/nuxt-feature-flags.md)
-   [How to set up A/B tests in Nuxt](/tutorials/nuxtjs-ab-tests.md)
-   [How to set up surveys in Nuxt](/tutorials/nuxt-surveys.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better