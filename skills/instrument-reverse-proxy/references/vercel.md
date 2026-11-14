> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Vercel reverse proxy

Canonical URL: https://posthog.com/docs/advanced/proxy/vercel

## On this page

- [How it works](#how-it-works)
- [Using Next.js on Vercel?](#using-nextjs-on-vercel)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Create vercel.json](#create-verceljson)
- [Update your PostHog SDK](#update-your-posthog-sdk)
- [Deploy to Vercel](#deploy-to-vercel)
- [Verify your setup](#verify-your-setup)
- [Troubleshooting](#troubleshooting)

**Before you start**

-   If you use a self-hosted proxy, PostHog can't help troubleshoot. Use [our managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) if you want support.
-   Use domains matching your PostHog region: `us.i.posthog.com` for US, `eu.i.posthog.com` for EU.
-   Don't use obvious path names like `/analytics`, `/tracking`, `/telemetry`, or `/posthog`. Blockers will catch them. Use something unique to your app instead.

**Data transfer costs**

Proxying routes all PostHog traffic – events, session recordings, feature flag polls, and SDK assets – through Vercel, which bills it as [Fast Data Transfer and Edge Requests](https://vercel.com/docs/pricing). Session recordings are the biggest driver (often 1–5 MB per session) and can consume a plan quickly on high-traffic sites.

To avoid these costs, use the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) (free for PostHog Cloud users) or a provider without egress fees like [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md).

This guide shows you how to use [Vercel rewrites](https://vercel.com/docs/projects/project-configuration#rewrites) as a reverse proxy for PostHog.

## How it works

Vercel rewrites map incoming request paths to different destinations. When you add PostHog rewrites to `vercel.json`, Vercel fetches content from PostHog's servers and returns it under your domain.

Here's the request flow:

1.  User triggers an event in your app
2.  Request goes to your Vercel domain (e.g., `yourdomain.com/yourpath`)
3.  Vercel matches the request against your rewrite rules
4.  Vercel fetches the response from PostHog's servers
5.  Vercel returns PostHog's response under your domain

This works because the rewrite happens server-side, so the browser only sees requests to your domain. Ad blockers that filter by domain won't block these requests.

## Using Next.js on Vercel?

If you're using Next.js, you can configure rewrites in either `vercel.json` or `next.config.js`. Both work identically on Vercel.

-   Use this guide (`vercel.json`) if you want all Vercel-specific settings in one file
-   Use [Next.js rewrites](https://posthog.com/docs/advanced/proxy/nextjs.md) if you prefer keeping config in `next.config.js`

Don't use both at the same time as they may conflict.

## Prerequisites

This guide requires a project deployed on Vercel.

## Setup

1.  1

    ## Create vercel.json

    In your project root, create or update `vercel.json`:

    ### US

    ```json
    {
      "rewrites": [
        {
          "source": "/yourpath/static/:path(.*)",
          "destination": "https://us-assets.i.posthog.com/static/:path"
        },
        {
          "source": "/yourpath/array/:path(.*)",
          "destination": "https://us-assets.i.posthog.com/array/:path"
        },
        {
          "source": "/yourpath/:path(.*)",
          "destination": "https://us.i.posthog.com/:path"
        }
      ]
    }
    ```

    ### EU

    ```json
    {
      "rewrites": [
        {
          "source": "/yourpath/static/:path(.*)",
          "destination": "https://eu-assets.i.posthog.com/static/:path"
        },
        {
          "source": "/yourpath/array/:path(.*)",
          "destination": "https://eu-assets.i.posthog.com/array/:path"
        },
        {
          "source": "/yourpath/:path(.*)",
          "destination": "https://eu.i.posthog.com/:path"
        }
      ]
    }
    ```

    Here's what each part does:

    -   The first rewrite routes `/yourpath/static/*` requests to PostHog's asset server. This serves the JavaScript SDK and other static files.
    -   The second rewrite routes `/yourpath/array/*` requests to PostHog's asset server. This serves the remote config (e.g., `/array/<token>/config.js`) with proper `cache-control` headers. Without this rule, remote config requests fall through to the main API, which strips cache headers and can cause browsers to use stale SDK config.
    -   The third rewrite routes all other `/yourpath/*` requests to PostHog's main API. This handles event capture, Feature flags, and session recordings.
    -   The `:path(.*)` syntax captures everything after the matched prefix and passes it to the destination URL.

    The specific path rewrites must come before the catch-all. Vercel evaluates rewrites in order, so if the catch-all rule came first, it would match `/yourpath/static/*` and `/yourpath/array/*` before the path-specific rules.

    See [Vercel's rewrites documentation](https://vercel.com/docs/projects/project-configuration#rewrites) for more details.

2.  2

    ## Update your PostHog SDK

    In your application code, update your PostHog initialization:

    ### US

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: '/yourpath',
      ui_host: 'https://us.posthog.com'
    })
    ```

    ### EU

    ```javascript
    posthog.init('<ph_project_token>', {
      api_host: '/yourpath',
      ui_host: 'https://eu.posthog.com'
    })
    ```

    The `api_host` tells the SDK where to send events. Using a relative path ensures requests go to your domain. The `ui_host` must point to PostHog's actual domain so features like the toolbar link correctly.

3.  3

    ## Deploy to Vercel

    Commit and push your changes. The rewrites become active once deployed.

    You can verify the configuration in your Vercel dashboard under **Project Settings** → **Functions** → **Rewrites**.

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

### Rewrites not working

If requests to your proxy path return 404:

1.  Verify `vercel.json` is in your project root (same level as `package.json`)
2.  Check the file is valid JSON with no syntax errors
3.  Ensure the rewrites are in the correct order: static assets first, then array, then catch-all
4.  Check the Vercel dashboard to confirm the config was deployed

### 401 errors after deployment

If events work locally but return 401 errors on Vercel, this usually indicates a region mismatch. Verify your rewrite destinations match your PostHog project's region:

-   US region: `us.i.posthog.com` and `us-assets.i.posthog.com`
-   EU region: `eu.i.posthog.com` and `eu-assets.i.posthog.com`

### Conflicts with Next.js rewrites

If you're using both `vercel.json` rewrites and Next.js `next.config.js` rewrites, they may conflict. Choose one method:

-   Use `vercel.json` for all Vercel-specific config
-   Or use `next.config.js` for framework-level config

Remove the PostHog rewrites from whichever file you're not using.

### Rewrite pattern not matching

If your rewrites aren't matching correctly, ensure you're using Vercel's named parameter syntax:

### US

```json
{
  "source": "/yourpath/:path(.*)",
  "destination": "https://us.i.posthog.com/:path"
}
```

### EU

```json
{
  "source": "/yourpath/:path(.*)",
  "destination": "https://eu.i.posthog.com/:path"
}
```

The `:path(.*)` captures the path and `:path` in the destination references it. Don't use `(.*)` without the named parameter.
