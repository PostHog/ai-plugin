# Vue.js - Docs

PostHog makes it easy to get data about usage of your [Vue.js](https://vuejs.org/) app. Integrating PostHog into your app enables analytics about user behavior, custom events capture, session replays, feature flags, and more.

This guide walks you through integrating PostHog into your app for both Vue 2 and Vue 3. We'll use the [JavaScript Web SDK](/docs/libraries/js.md) for this.

For integrating PostHog into a [Nuxt.js](https://nuxt.com/) app, see our [Nuxt guide](/docs/libraries/nuxt-js.md).

## Prerequisites

To follow this guide along, you need:

1.  A [PostHog account](https://app.posthog.com/signup)
2.  A running Vue.js app

## Setting up PostHog

Start by installing `posthog-js` using your package manager:

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

Next, depending on your Vue version, we recommend initializing PostHog using the composition API or as a plugin.

## Vue 3: Composition API

We use the Composition API as it provides better accessibility, maintainability, and type safety.

PostHog initializes as a singleton, so you can initialize it in your `main.ts` file **before** you mount your app. This ensures PostHog is initialized before any other code runs.

src/main.ts

PostHog AI

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import posthog from "posthog-js";
const app = createApp(App);
posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN || '<ph_project_token>', {
  api_host: import.meta.env.VITE_POSTHOG_HOST || 'https://us.i.posthog.com',
  defaults: '2026-05-30',
});
app.use(createPinia())
app.use(router)
app.config.errorHandler = (err, instance, info) => {
  posthog.captureException(err)
}
app.mount('#app')
```

Then, you can access PostHog throughout your app just by importing it from `posthog-js`.

TypeScript

PostHog AI

```typescript
// src/App.vue
<script setup>
import posthog from 'posthog-js'
const handleClick = () => {
  posthog.capture('button_clicked')
}
</script>
```

Once done, PostHog will begin [autocapturing](/docs/product-analytics/autocapture.md) events and pageviews (if enabled) and is ready to use throughout your app.

## Vue 2: Plugins

Start by creating a `plugins` folder and adding a `posthog.js` file to that folder. In `posthog.js`, initialize PostHog using the `install` method with your project token and host. You can find these in your [project settings](https://us.posthog.com/project/settings).

JavaScript

PostHog AI

```javascript
// src/plugins/posthog.js
import posthog from 'posthog-js'
export default {
  install(Vue) {
    posthog.init('<ph_project_token>', {
      api_host: 'https://us.i.posthog.com',
      defaults: '2026-05-30'
    })
    Vue.prototype.$posthog = posthog
  }
}
```

Next, in `main.js`, import and use the plugin.

JavaScript

PostHog AI

```javascript
// src/main.js
import Vue from 'vue'
import App from './App.vue'
import PosthogPlugin from './plugins/posthog'
Vue.config.productionTip = false
Vue.use(PosthogPlugin)
new Vue({
  render: h => h(App),
}).$mount('#app')
```

This makes PostHog available as `this.$posthog` in any Vue component.

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Capturing custom events, using feature flags, and more

Once you have PostHog initialized, there is a lot more you can do with it beyond autocapture, pageviews, and pageleaves. You can find the full details in our [JavaScript SDK docs](/docs/libraries/js/features.md), but we'll cover a few examples here.

## Vue 3: Composition API

To capture custom events, evaluate feature flags, and use any of the other PostHog features, you can use the `posthog` object returned from the `usePostHog` composable like this:

JavaScript

PostHog AI

```javascript
// src/App.vue
<script setup>
import { RouterView } from 'vue-router'
import { usePostHog } from './composables/usePostHog'
const { posthog } = usePostHog()
const handleClick = () => {
  posthog.capture('button_clicked', { location: 'homepage' })
}
</script>
<template>
  <div>
    <button @click="handleClick">Click me!</button>
  </div>
  <RouterView />
</template>
```

### Feature flags with reactive updates

When using feature flags on pages that users navigate to directly, the flags may not be loaded when the component first renders. To ensure your UI updates reactively when flags load, create a composable that returns a reactive ref:

JavaScript

PostHog AI

```javascript
// src/composables/usePostHogFeatureFlag.ts
import { ref, type Ref } from 'vue'
import { usePostHog } from './usePostHog'
export function usePostHogFeatureFlag(
  feature: string,
): Ref<string | boolean | undefined> {
  const { posthog } = usePostHog()
  const flag = ref(posthog.getFeatureFlag(feature))
  posthog.onFeatureFlags(() => {
    flag.value = posthog.getFeatureFlag(feature)
  })
  return flag
}
```

Then use it in your components:

JavaScript

PostHog AI

```javascript
// src/App.vue
<script setup>
import { RouterView } from 'vue-router'
import { usePostHog } from './composables/usePostHog'
import { usePostHogFeatureFlag } from './composables/usePostHogFeatureFlag'
const { posthog } = usePostHog()
const isFeatureEnabled = usePostHogFeatureFlag('test-flag')
const handleClick = () => {
  posthog.capture('button_clicked', { location: 'homepage' })
}
</script>
<template>
  <div>
    <button @click="handleClick">Click me!</button>
    <p>Is feature flag enabled? {{ isFeatureEnabled ? 'Yes' : 'No' }}</p>
  </div>
  <RouterView />
</template>
```

This ensures your component will automatically update when feature flags load, even if the page is accessed directly.

## Vue 2: Plugins

To capture custom events, evaluate feature flags, and use any of the other PostHog features, you can use the `$posthog` object returned from the plugin like this:

JavaScript

PostHog AI

```javascript
// src/components/AboutPage.vue
<template>
  <div class="about">
    <h1>About Page</h1>
    <button @click="handleClick">Test PostHog</button>
    <router-link to="/">Go to Home</router-link>
    <p>Feature enabled? {{ isFeatureEnabled ? 'Yes' : 'No' }}</p>
  </div>
</template>
<script>
export default {
  name: 'AboutPage',
  data() {
    return {
      isFeatureEnabled: false
    }
  },
  created() {
    this.isFeatureEnabled = this.$posthog.isFeatureEnabled('test-flag')
  },
  methods: {
    handleClick() {
      this.$posthog.capture('button_clicked')
    }
  }
}
</script>
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

## Next steps

For any technical questions for how to integrate specific PostHog features into Vue (such as analytics, feature flags, A/B testing, or surveys), have a look at our [JavaScript Web](/docs/libraries/js/features.md) SDK docs.

Alternatively, the following tutorials can help you get started:

-   [How to set up analytics in Vue](/tutorials/vue-analytics.md)
-   [How to set up feature flags in Vue](/tutorials/vue-feature-flags.md)
-   [How to set up A/B tests in Vue](/tutorials/vue-ab-tests.md)
-   [How to set up surveys in Vue](/tutorials/vue-surveys.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better