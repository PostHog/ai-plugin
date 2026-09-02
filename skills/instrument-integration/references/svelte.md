> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Svelte - Docs

Copy page

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

These are public, stable IPs used by PostHog services.

PostHog captures heatmap screenshots using [Browserless](https://www.browserless.io), which has its own IP addresses. Browserless [publishes the current list here](https://docs.browserless.io/baas/troubleshooting/whitelisting-ips).

An allowlist does not help when your app has a private address. For apps on an internal network, see [internal and intranet applications](/docs/session-replay/troubleshooting.md#internal-and-intranet-applications).

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

See our [JavaScript Web](/docs/libraries/js/usage.md#feature-flags) and [Node](/docs/libraries/node.md#feature-flags) docs for more details.

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

For any technical questions for how to integrate specific PostHog features into Svelte (such as analytics, feature flags, A/B testing, surveys, etc.), have a look at our [JavaScript Web](/docs/libraries/js/usage.md) and [Node](/docs/libraries/node.md) SDK docs.

Alternatively, the following tutorials can help you get started:

-   [How to set up Svelte analytics, feature flags, and more](/tutorials/svelte-analytics.md)
-   [How to set up A/B tests in Svelte](/tutorials/svelte-ab-tests.md)
-   [How to set up surveys in Svelte](/tutorials/svelte-surveys.md)

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better