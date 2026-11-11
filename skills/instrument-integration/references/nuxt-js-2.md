> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Nuxt.js (v2.16 and below)

Canonical URL: https://posthog.com/docs/libraries/nuxt-js-2

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host).

## On this page

- [Installation](#installation)
- [Usage](#usage)
- [Next steps](#next-steps)

PostHog makes it easy to get data about usage of your [Nuxt.js](https://nuxt.com/) app. Integrating PostHog into your app enables analytics about user behavior, custom events capture, session replays, feature flags, and more.

These docs are for Nuxt v2.16 and below.

We are going to implement PostHog as a [Nuxt.js integration](https://nuxtjs.org/docs/2.x/directory-structure/plugins) which gives us the possibility to inject the `posthog` object and make it available across our application.

## Installation

The first thing you want to do is to install the [posthog-js library](https://posthog.com/docs/libraries/js.md) in your project - so add it using your package manager:

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

> **If your site sets a Content-Security-Policy**, it needs to allow PostHog. This applies to the snippet and to package installs alike: the SDK lazy-loads extra bundles (session replay, surveys) from PostHog's CDN, and sends events to the ingestion host. PostHog serves from subdomains of `posthog.com` that change over time, so allow the wildcard:
>
> ```
> script-src 'self' https://*.posthog.com;
> connect-src 'self' https://*.posthog.com;
> worker-src 'self' blob: data:;
> ```
>
> `script-src` covers the snippet and the lazy-loaded bundles, `connect-src` covers event ingestion and feature flags, and `worker-src` covers session replay. The [toolbar needs a few more](https://posthog.com/docs/advanced/content-security-policy.md), or use a [reverse proxy](https://posthog.com/docs/advanced/proxy.md) so everything is first-party. Failing to do so causes silent failures where `capture` and `identify` calls never send, so the integration looks complete while zero events arrive. Remember `connect-src` falls back to `default-src`, so `default-src 'self'` blocks event delivery even when the script itself is bundled.

After that we want to create an app in `plugins/posthog/index.js`

```javascript
import posthog from 'posthog-js'
import Vue from 'vue'

export default function({ app: { router } }, inject) {
  // Init PostHog
  posthog.init('<ph_project_token>', {
    api_host: 'https://us.i.posthog.com',
    defaults: '2026-08-30',
    capture_pageview: false,
    loaded: () => posthog.identify('unique_id') // If you can already identify your user
  })

  // Inject PostHog into the application and make it available via this.$posthog (or app.$posthog)
  inject('posthog', posthog)

  // Make sure that pageviews are captured with each route change
  router.afterEach(to => {
    Vue.nextTick(() => {
      /* Note: this might also be a good place to call posthog.register(...) in order to update your properties
      on each page view
      */
      posthog.capture('$pageview', {
        $current_url: to.fullPath
      })
    })
  })
}
```

**Keep your personal API key out of the client bundle**

Anything shipped to the browser – the token you pass to `posthog.init()`, anything under Nuxt's `runtimeConfig.public`, or the `@posthog/nuxt` module's `posthogConfig` – ends up in your client-side JavaScript and is visible to anyone who visits your site. This is fine for your **project token** (`<ph_project_token>`), which is designed to be public.

Your **[personal API key](https://posthog.com/docs/api.md#authentication)** is different. It can grant full access to your PostHog account, so it must never reach the browser. If you need it – for example, for [source map uploads](https://posthog.com/docs/error-tracking/upload-source-maps/nuxt.md) or [server-side local evaluation](https://posthog.com/docs/feature-flags/local-evaluation.md) – read it from a server-only environment variable (or top-level `runtimeConfig`, never `runtimeConfig.public`) and only use it in server code.

Either way, prefer reading keys from environment variables rather than hard-coding them in `nuxt.config`, so you can keep them out of source control and use different values per environment.

Finally, we need to activate it on the client side in our `nuxt.config.js`

```javascript
plugins: [
    ...
    { src: './plugins/posthog', mode: 'client' }
  ],
```

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

## Usage

By using the example code above you can now use PostHog across your app with `this.$posthog` or `app.$posthog` - depending on the context. Compare with the [Nuxt.js docs](https://nuxtjs.org/docs/2.x/directory-structure/plugins#inject-in-root--context) on further details when to use `app.$posthog` or `this.$posthog`.

Let's say for example the user makes a purchase you could track an event like that:

```javascript
<template>
  <button @click="purchase">Buy</button>
</template>

<script>
...
  methods: {
     purchase() {
       this.$posthog.capture('purchase')
     }
  }
...
</script>
```

## Next steps

For any technical questions for how to integrate specific PostHog features into Nuxt (such as analytics, feature flags, A/B testing, surveys, etc.), have a look at our [JavaScript Web](https://posthog.com/docs/libraries/js.md) and [Node](https://posthog.com/docs/libraries/node.md) SDK docs.

Alternatively, the following tutorials can help you get started:

-   [How to set up analytics in Nuxt](https://posthog.com/tutorials/nuxt-analytics.md)
-   [How to set up feature flags in Nuxt](https://posthog.com/tutorials/nuxt-feature-flags.md)
-   [How to set up A/B tests in Nuxt](https://posthog.com/tutorials/nuxtjs-ab-tests.md)
-   [How to set up surveys in Nuxt](https://posthog.com/tutorials/nuxt-surveys.md)
