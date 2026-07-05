# Svelte - Docs

PostHog makes it easy to get data about traffic and usage of your [Svelte](https://svelte.dev/) app. Integrating PostHog into your site enables analytics about user behavior, custom events capture, session recordings, feature flags, and more.

This guide walks you through integrating PostHog into your SvelteKit app using the [JavaScript Web](/docs/libraries/js.md) and [Node.js](/docs/libraries/node.md) SDKs.

## Beta: integration via LLM

Install PostHog for Svelte in seconds with our wizard by running this prompt with [LLM coding agents](/blog/envoy-wizard-llm-agent.md) like Cursor and Bolt, or by running it in your terminal.

`npx @posthog/wizard`

[Learn more](/wizard.md)

Or, to integrate manually, continue with the rest of this guide.

## Client-side setup

Install `posthog-js` using your package manager:

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

Then, if you haven't created a root [layout](https://kit.svelte.dev/docs/routing#layout) already, create a new file called `+layout.js` in your `src/routes` folder In this file, check the environment is the browser, and initialize PostHog if so. You can get both your API key and instance address in your [project settings](https://us.posthog.com/project/settings).

routes/+layout.js

PostHog AI

```javascript
import posthog from 'posthog-js'
import { browser } from '$app/environment';
export const load = async () => {
  if (browser) {
    posthog.init('<ph_project_token>', {
      api_host: 'https://us.i.posthog.com',
      defaults: '2026-05-30',
    })
  }
  return
};
```

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

> ❗️ If you intend on using session replays with a server-side rendered Svelte app ensure that your [asset URLs are configured to be relative](/docs/session-replay/troubleshooting.md#ensure-assets-are-imported-from-the-base-URL-in-Svelte).

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

## Server-side setup

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

Then, initialize the PostHog Node client where you'd like to use it on the server side. For example, in a [load function](https://kit.svelte.dev/docs/load#page-data):

routes/+page.server.js

PostHog AI

```javascript
import { PostHog } from 'posthog-node';
export async function load() {
  const posthog = new PostHog('<ph_project_token>', { host: 'https://us.i.posthog.com' });
  posthog.capture({
    distinctId: 'distinct_id_of_the_user',
    event: 'event_name',
  })
  await posthog.shutdown()
}
```

> **Note:** Make sure to always call `posthog.shutdown()` after capturing events from the server-side. PostHog queues events into larger batches, and this call forces all batched events to be flushed immediately.

## Feature flags

To use client-side feature flags, import PostHog into your Svelte component and check if the feature is enabled (while ensuring the code only runs in the browser).

routes/+page.svelte

PostHog AI

```javascript
<script>
  import posthog from 'posthog-js'
  import { browser } from '$app/environment'
  import { onMount } from 'svelte'
  let coolFeature = $state(false)
  onMount(() => {
    if (browser) {
      coolFeature = posthog.isFeatureEnabled('cool-feature')
    }
  })
</script>
{#if coolFeature}
  <p>Welcome to the cool feature!</p>
{/if}
```

To use server-side feature flags, import PostHog into your SvelteKit `load` function and check if the feature is enabled.

routes/+page.server.js

PostHog AI

```javascript
import { PostHog } from 'posthog-node';
const client = new PostHog(
  '<ph_project_token>',
  { host: 'https://us.i.posthog.com' }
);
export async function load() {
  const distinctId = 'distinct_id_of_the_user';
  const megaFeature = await client.isFeatureEnabled(
    'mega-feature',
    distinctId
  );
  return {
    megaFeature
  };
}
```

See our [JavaScript Web](/docs/libraries/js/features.md#feature-flags) and [Node](/docs/libraries/node.md#feature-flags) docs for more details.

## Configuring session replay for server-side rendered apps

By default, [Svelte uses relative asset paths](https://kit.svelte.dev/docs/configuration) during server-side rending. This causes issues with PostHog's ability to record sessions.

To fix this, set the config to not use relative paths in `svelte.config.js`:

JavaScript

PostHog AI

```javascript
kit: {
     paths: {
         relative: false,
     },
 },
```

## Next steps

For any technical questions for how to integrate specific PostHog features into Svelte (such as analytics, feature flags, A/B testing, surveys, etc.), have a look at our [JavaScript Web](/docs/libraries/js/features.md) and [Node](/docs/libraries/node.md) SDK docs.

Alternatively, the following tutorials can help you get started:

-   [How to set up Svelte analytics, feature flags, and more](/tutorials/svelte-analytics.md)
-   [How to set up A/B tests in Svelte](/tutorials/svelte-ab-tests.md)
-   [How to set up surveys in Svelte](/tutorials/svelte-surveys.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better