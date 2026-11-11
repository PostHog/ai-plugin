> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Docusaurus

Canonical URL: https://posthog.com/docs/libraries/docusaurus

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://us.posthog.com` (app host for links).

To easily track your Docusaurus site, you can install the [PostHog plugin](https://github.com/PostHog/posthog-docusaurus). This enables you to autocapture pageviews, clicks, session replays, as well as use the other features of PostHog such as [surveys](https://posthog.com/docs/surveys.md).

## Install

Once you have your Docusaurus site set up, install the PostHog plugin:

```bash
npm install --save posthog-docusaurus
```

or

```bash
yarn add posthog-docusaurus
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

Next, add it to your Docusaurus config with your project token and instance address, both of which you can find in [your project settings](https://us.posthog.com/settings/project).

```javascript
// docusaurus.config.js
module.exports = {
  plugins: [
    [
      "posthog-docusaurus",
      {
        apiKey: "<ph_project_token>",
        appUrl: "https://us.i.posthog.com", // optional, defaults to "https://us.i.posthog.com"
        enableInDevelopment: false, // optional
      },
    ],
  ],
};
```

Run your site again to see events autocaptured by PostHog.

> **Note:**You can pass additional PostHog [config options](https://posthog.com/docs/libraries/js/config.md) to the plugin, but they are passed through `JSON.stringify()`, so functions (such as `before_send`) are not supported.

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](https://posthog.com/docs/session-replay.md), [LLM traces](https://posthog.com/docs/ai-engineering.md), and [error tracking](https://posthog.com/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> Use a stable ID from your auth system when possible, not an email or display name. Send those as person properties instead. If your app has no other stable key, email works as a fallback if they are unique. Never a shared literal like `"anonymous"` or `"user"`, which pools many people onto one person and corrupts their data. When no ID is available at all, skip the identify and retain the anonymous distinct ID that's automatically assigned.
>
> Call `posthog.reset()` on logout, so the next person to use the browser doesn't inherit the last one's identity.
>
> See our guide on [identifying users](https://posthog.com/docs/getting-started/identify-users.md) for how to set this up.

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
