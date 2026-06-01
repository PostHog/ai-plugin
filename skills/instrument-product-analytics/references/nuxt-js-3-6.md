# Nuxt.js (v3.0 to v3.6) - Docs

PostHog makes it easy to get data about usage of your [Nuxt.js](https://nuxt.com/) app. Integrating PostHog into your app enables analytics about user behavior, custom events capture, session replays, feature flags, and more.

These docs are for Nuxt v3.0 to v3.6. You can see a working example of the Nuxt v3.0 integration in our [Nuxt.js demo app](https://github.com/PostHog/posthog-js/tree/master/playground/nuxtjs)

## Setting up PostHog on the client side

1.  Install `posthog-js` using your package manager:

PostHog AI

### npm

```bash
npm install --save posthog-js
```

### Yarn

```bash
yarn add posthog-js
```

### pnpm

```bash
pnpm add posthog-js
```

### Bun

```bash
bun add posthog-js
```

2.  Add your PostHog API key and host to your `nuxt.config.js` file. You can find these in [your project settings](https://us.posthog.com/settings/project).

nuxt.config.js

PostHog AI

```javascript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      posthogToken: process.env.NUXT_PUBLIC_POSTHOG_PROJECT_TOKEN || '<ph_project_token>',
      posthogHost: process.env.NUXT_PUBLIC_POSTHOG_HOST || 'https://us.i.posthog.com',
      posthogDefaults: '2026-01-30',
    },
  }
})
```

3.  Create a new plugin by creating a new file `posthog.client.js` in your [plugins directory](https://nuxt.com/docs/guide/directory-structure/plugins).

plugins/posthog.client.js

PostHog AI

```javascript
import { defineNuxtPlugin, useRuntimeConfig } from '#imports'
import posthog from 'posthog-js'
export default defineNuxtPlugin(() => {
  const runtimeConfig = useRuntimeConfig()
  const posthogClient = posthog.init(runtimeConfig.public.posthogToken, {
    api_host: runtimeConfig.public.posthogHost,
    defaults: runtimeConfig.public.posthogDefaults,
    loaded: (posthog) => {
      if (import.meta.env.MODE === 'development') posthog.debug()
    },
  })
  return {
    provide: {
      posthog: () => posthogClient,
    },
  }
})
```

PostHog can then be accessed throughout your Nuxt.js using the provider accessor, for example:

Vue

PostHog AI

```html
<script setup>
   const { $posthog } = useNuxtApp()
   if ($posthog) {
      const posthog = $posthog()
      posthog.capture('<event_name>')
   }
</script>
```

See the [JavaScript SDK docs](/docs/libraries/js/features.md) for all usable functions, such as:

-   [Capture custom event capture, identify users, and more.](/docs/libraries/js/features.md#capturing-events)
-   [Feature flags including variants and payloads.](/docs/libraries/js/features.md#feature-flags)

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

## Setting up PostHog on the server side

Install `posthog-node` using your package manager:

PostHog AI

### npm

```bash
npm install posthog-node --save
```

### Yarn

```bash
yarn add posthog-node
```

### pnpm

```bash
pnpm add posthog-node
```

### Bun

```bash
bun add posthog-node
```

Add your PostHog API key and host to your `nuxt.config.js` file. If you've already done this when adding PostHog to the client side, you can skip this step.

nuxt.config.js

PostHog AI

```javascript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      posthogToken: '<ph_project_token>',
      posthogHost: 'https://us.i.posthog.com',
      posthogDefaults: '2026-01-30',
    }
  }
})
```

Initialize the PostHog Node client where you'd like to use it on the server side. For example, in a [server route](https://nuxt.com/docs/guide/directory-structure/server#server-routes):

server/api/example.js

PostHog AI

```javascript
const runtimeConfig = useRuntimeConfig()
  const posthog = new PostHog(
    runtimeConfig.public.posthogToken,
    {
      host: runtimeConfig.public.posthogHost,
    }
  );
  posthog.capture({
    event: 'api_call',
    distinctId: distinctId,
    properties: {
      $current_url: url,
      query: query
    }
  })
  posthog.shutdown()
  return {
    message: "example response"
```

> **Note**: Make sure to *always* call `posthog.shutdown()` after capturing events from the server-side. PostHog queues events into larger batches, and this call forces all batched events to be flushed immediately.

See the [Node SDK docs](/docs/libraries/node.md) for all usable functions, such as:

-   [Capture custom event capture, identify users, and more.](/docs/libraries/node.md#capturing-events)
-   [Feature flags including variants and payloads.](/docs/libraries/node.md#feature-flags)

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