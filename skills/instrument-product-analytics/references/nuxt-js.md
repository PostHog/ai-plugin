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

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Configuration

Add the module to your `nuxt.config.ts` file:

nuxt.config.ts

PostHog AI

```typescript
export default defineNuxtConfig({
  modules: ['@posthog/nuxt'],
  posthogConfig: {
    publicKey: '<ph_project_token>', // Find it in project settings https://app.posthog.com/settings/project
    host: 'https://us.i.posthog.com', // Optional: defaults to https://us.i.posthog.com. Use https://eu.i.posthog.com for EU region
    clientConfig: {
      // Optional: PostHog client configuration options
    },
  },
})
```

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

For certain features like [heatmaps](/docs/toolbar/heatmaps.md), your Web Application Firewall (WAF) may be blocking PostHog’s requests to your site. Add these IP addresses to your WAF allowlist or rules to let PostHog access your site.

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