> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Next.js rewrites reverse proxy

Canonical URL: https://posthog.com/docs/advanced/proxy/nextjs

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu-assets.i.posthog.com` instead of `https://us-assets.i.posthog.com` (assets host).

## On this page

- [How it works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Add rewrites to next.config.js](#add-rewrites-to-nextconfigjs)
- [Update your PostHog SDK](#update-your-posthog-sdk)
- [Deploy your changes](#deploy-your-changes)
- [Verify your setup](#verify-your-setup)
- [Troubleshooting](#troubleshooting)

**Before you start**

-   If you use a self-hosted proxy, PostHog can't help troubleshoot. Use [our managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) if you want support.
-   Use domains matching your PostHog region: `us.i.posthog.com` for US, `eu.i.posthog.com` for EU.
-   Don't use obvious path names like `/analytics`, `/tracking`, `/telemetry`, or `/posthog`. Blockers will catch them. Use something unique to your app instead.

**Data transfer costs**

Rewrites route all PostHog traffic – events, session recordings, feature flag polls, and SDK assets – through your Next.js server. On Vercel, this counts toward [Fast Data Transfer and Edge Requests](https://vercel.com/docs/pricing); on other hosts it counts against their bandwidth and compute quotas. Session recordings are the biggest driver (often 1 to 5 MB per session) and can consume a plan quickly on high-traffic sites.

To avoid these costs, use the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) (free for PostHog Cloud users) or a provider without egress fees like [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md).

This guide shows you how to use [Next.js rewrites](https://nextjs.org/docs/app/api-reference/next-config-js/rewrites) as a reverse proxy for PostHog.

## How it works

Next.js rewrites map incoming request paths to different destinations. When you add PostHog rewrites, Next.js fetches content from PostHog's servers and returns it under your domain.

Here's the request flow:

1.  User triggers an event in your app
2.  Request goes to your domain (e.g., `yourdomain.com/yourpath`)
3.  Next.js matches the request against your rewrite rules
4.  Next.js fetches the response from PostHog's servers
5.  Next.js returns PostHog's response under your domain

This works because the rewrite happens server-side, so the browser only sees requests to your domain. Ad blockers that filter by domain won't block these requests.

**Hosting compatibility**

Rewrites work best when self-hosting Next.js or using Vercel. Some hosting platforms modify headers during rewrites, causing `503` or `400` errors.

If you encounter issues, try [Next.js proxy](https://posthog.com/docs/advanced/proxy/nextjs-middleware.md) (formerly middleware) or a platform-specific proxy like [Netlify](https://posthog.com/docs/advanced/proxy/netlify.md).

## Prerequisites

This guide works with any Next.js project using the app router or pages router.

## Setup

1.  1

    ## Add rewrites to next.config.js

    Add a `rewrites()` function and the `skipTrailingSlashRedirect` option to your `next.config.js`:

    ```javascript
    // next.config.js
    const nextConfig = {
      async rewrites() {
        return [
          {
            source: '/yourpath/static/:path*',
            destination: 'https://us-assets.i.posthog.com/static/:path*',
          },
          {
            source: '/yourpath/array/:path*',
            destination: 'https://us-assets.i.posthog.com/array/:path*',
          },
          {
            source: '/yourpath/:path*',
            destination: 'https://us.i.posthog.com/:path*',
          },
        ]
      },
      skipTrailingSlashRedirect: true,
    }
    
    module.exports = nextConfig
    ```

    Replace `us` with `eu` for EU region.

    Here's what each part does:

    -   The first rewrite routes static asset requests to PostHog's asset server. This serves the JavaScript SDK and other static files.
    -   The second rewrite routes remote config requests (`/array/{token}/config.js`) to the asset server. The asset server returns proper `cache-control` headers for these responses, while the main API server strips them.
    -   The third rewrite routes all other requests to PostHog's main API. This handles event capture, Feature flags, and session recordings.
    -   `skipTrailingSlashRedirect` stops Next.js from redirecting URLs that end with a slash. PostHog API paths end with a slash, such as `/e/` and `/flags/`. Without this setting, Next.js answers each of these requests with a `308` redirect. Browsers follow it, so events still arrive, but each request takes an extra round trip.

    The static and array rewrites must come before the catch-all. Next.js evaluates rewrites in order, so if the catch-all rule came first, it would match `/yourpath/static/*` and `/yourpath/array/*` before the specific rules.

    See [Next.js rewrites documentation](https://nextjs.org/docs/app/api-reference/next-config-js/rewrites) for more details.

    **Using middleware? Exclude your proxy path**

    If your app already has a `middleware.ts` (or `proxy.ts` in Next.js 16) – common with [next-intl](https://next-intl.dev), [NextAuth](https://authjs.dev), or your own logic – its `matcher` can grab the proxy path before the rewrite runs and break ingestion.

    A catch-all matcher matches the capture endpoints (`/yourpath/e`, `/yourpath/flags`, `/yourpath/s`) and rewrites or redirects them, so events, feature flags, and recordings never reach PostHog. The static assets at `/yourpath/static/*.js` have a file extension, so a matcher like next-intl's default `'/((?!api|_next|_vercel|.*\\..*).*)'` skips them and they still load, which makes PostHog look connected even though nothing is sending.

    Add your proxy path to the matcher's negative lookahead:

    ```javascript
    export const config = {
      matcher: ['/((?!api|yourpath|_next|_vercel|.*\\..*).*)'],
    }
    ```

2.  2

    ## Update your PostHog SDK

    In your application code, update your PostHog initialization to use your proxy path:

    ### US

    ```javascript
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN, {
      api_host: '/yourpath',
      ui_host: 'https://us.posthog.com'
    })
    ```

    ### EU

    ```javascript
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN, {
      api_host: '/yourpath',
      ui_host: 'https://eu.posthog.com'
    })
    ```

    The `api_host` tells the SDK where to send events. Using a relative path ensures requests go to your domain. The `ui_host` must point to PostHog's actual domain so features like the toolbar link correctly.

3.  3

    ## Deploy your changes

    Commit and push your changes. Restart your dev server if testing locally, as Next.js doesn't hot-reload config changes.

4.  ## Verify your setup

    Checkpoint

    Confirm events are flowing through your proxy:

    1.  Open your browser's developer tools and go to the **Network** tab
    2.  Navigate to your site or trigger an event
    3.  Look for requests to your domain with your proxy path (e.g., `yourdomain.com/yourpath`)
    4.  Verify the response status is `200 OK`
    5.  Check the [PostHog app](https://app.posthog.com) to confirm events appear in your activity feed

    If you see errors, check [troubleshooting](#troubleshooting) below.

**Cookies being forwarded to PostHog**

By default, the proxy forwards all headers including cookies to PostHog. If you don't want to forward authentication cookies and headers, delete them from the request. Keep an `Authorization` header that starts with `Bearer phc_`, `Bearer phs_` or `Bearer phx_`, because PostHog SDKs send their keys there. Keys created before these prefixes need their exact `Bearer <key>` value allowed too:

```javascript
const requestHeaders = new Headers(request.headers)
requestHeaders.set('host', hostname)
requestHeaders.delete('cookie')
// Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
// To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
  requestHeaders.delete('authorization')
}
```

Alternatively, configure PostHog to use `localStorage` instead of cookies:

```javascript
posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN, {
  api_host: '/yourpath',
  persistence: 'localStorage'
})
```

## Troubleshooting

### 503 or 400 errors

Some hosting platforms modify headers during rewrites, breaking the proxy. This commonly happens with Heroku and Netlify.

Solutions:

1.  Use [Next.js proxy](https://posthog.com/docs/advanced/proxy/nextjs-middleware.md) (formerly middleware) for more control over the request
2.  Use a platform-specific proxy like [Netlify redirects](https://posthog.com/docs/advanced/proxy/netlify.md)
3.  Self-host Next.js or use Vercel

### Rewrites not working

If requests to your proxy path return 404:

1.  Verify your `next.config.js` is in the project root
2.  Restart your dev server after changing the config
3.  Check the rewrite order: static and array rules must come before the catch-all
4.  If you have middleware (`middleware.ts` or `proxy.ts`), check its `matcher` doesn't catch your proxy path. A catch-all matcher redirects the capture endpoints – you'll see something like `POST /yourpath/s` become a 307 to `/en/yourpath/s` that 404s, while `/yourpath/static/*.js` still loads. Add your proxy path to the matcher: `matcher: ['/((?!api|yourpath|_next|_vercel|.*\\..*).*)']`

### Trailing slash conflicts with SEO

The `skipTrailingSlashRedirect` setting removes a redirect from each PostHog API request, but it can cause SEO issues if pages become accessible at both `/page` and `/page/`.

Solutions:

1.  Handle trailing slash redirects in [Next.js middleware](https://nextjs.org/docs/app/building-your-application/routing/middleware) for non-PostHog routes
2.  Use `<link rel="canonical">` to specify the preferred URL for search engines
3.  Ensure your sitemap only includes one URL format
4.  Leave `skipTrailingSlashRedirect` out. PostHog requests still work, with one extra redirect each

### 401 errors or "No project token provided"

If you see authentication errors and have verified your project token is correct, this usually indicates a region mismatch. Ensure the domains in your rewrites match your PostHog project's region (`us` or `eu`).

Some hosting platforms also strip the request body during rewrites, losing the project token. If this happens, use [Next.js proxy](https://posthog.com/docs/advanced/proxy/nextjs-middleware.md) instead.
