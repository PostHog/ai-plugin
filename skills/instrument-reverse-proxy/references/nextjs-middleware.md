> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Next.js proxy file reverse proxy

Canonical URL: https://posthog.com/docs/advanced/proxy/nextjs-middleware

## On this page

- [How it works](#how-it-works)
- [When to use proxy vs rewrites](#when-to-use-proxy-vs-rewrites)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Create the proxy file](#create-the-proxy-file)
- [Configure trailing slash handling](#configure-trailing-slash-handling)
- [Update your PostHog SDK](#update-your-posthog-sdk)
- [Deploy your changes](#deploy-your-changes)
- [Verify your setup](#verify-your-setup)
- [Troubleshooting](#troubleshooting)

**Before you start**

-   If you use a self-hosted proxy, PostHog can't help troubleshoot. Use [our managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) if you want support.
-   Use domains matching your PostHog region: `us.i.posthog.com` for US, `eu.i.posthog.com` for EU.
-   Don't use obvious path names like `/analytics`, `/tracking`, `/telemetry`, or `/posthog`. Blockers will catch them. Use something unique to your app instead.

**Data transfer costs**

The proxy file runs on every matching request, so all PostHog traffic – events, session recordings, feature flag polls, and SDK assets – passes through it. On Vercel, each invocation counts as an [Edge Request](https://vercel.com/docs/pricing) in addition to the data transfer; other hosts bill it against their compute and bandwidth quotas. Session recordings amplify this (often 1–5 MB per session) and can quickly push a plan over its limits on high-traffic sites.

To avoid these costs, use the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) (free for PostHog Cloud users) or a provider without egress fees like [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md).

This guide shows you how to use [Next.js proxy](https://nextjs.org/docs/app/api-reference/file-conventions/proxy) (formerly middleware) as a reverse proxy for PostHog.

**Next.js 16 renamed middleware to proxy**

In Next.js 16, `middleware.js` was renamed to `proxy.js`. The functionality is identical, but the file and export names changed. If you're on Next.js 15 or earlier, use `middleware.js` and export `middleware` instead of `proxy`.

You can migrate existing middleware using: `npx @next/codemod@canary middleware-to-proxy .`

## How it works

Next.js proxy runs on the edge before a request reaches your pages. When a request matches your proxy path, it rewrites the request to PostHog's servers and returns the response under your domain.

Here's the request flow:

1.  User triggers an event in your app
2.  Request goes to your domain (e.g., `yourdomain.com/yourpath`)
3.  Next.js proxy intercepts the request before it reaches your pages
4.  Proxy rewrites the request URL to PostHog's servers
5.  PostHog processes the request and returns a response
6.  Proxy returns the response to the user under your domain

This works because the proxy runs server-side, so the browser only sees requests to your domain. Ad blockers that filter by domain won't block these requests.

## When to use proxy vs rewrites

Next.js offers two ways to proxy PostHog: [rewrites](https://posthog.com/docs/advanced/proxy/nextjs.md) and proxy. Both work with the app router and pages router.

-   [**Rewrites:**](https://posthog.com/docs/advanced/proxy/nextjs.md) Simpler configuration in `next.config.js`. Use this for most cases, especially on Vercel or self-hosted Next.js.
-   **Proxy:** More control over request handling. Use this when rewrites return `503` or `400` errors on your hosting platform, or when you need custom logic like header modification.

Try rewrites first. Use proxy if you encounter issues.

## Prerequisites

This guide works with any Next.js project using the app router or pages router. Requires Next.js 12.2 or later (use `middleware.js` for versions before 16, `proxy.js` for 16+).

## Setup

1.  1

    ## Create the proxy file

    Create a file named `proxy.js` (or `proxy.ts` for TypeScript) in your project root, at the same level as your `app` or `pages` folder:

    ### US

    ```javascript
    import { NextResponse } from 'next/server'
    
    export function proxy(request) {
      const url = request.nextUrl.clone()
      const hostname = url.pathname.startsWith('/yourpath/static/') || url.pathname.startsWith('/yourpath/array/')
        ? 'us-assets.i.posthog.com'
        : 'us.i.posthog.com'
    
      const requestHeaders = new Headers(request.headers)
      requestHeaders.set('host', hostname)
      // Remove cookies before forwarding to PostHog
      requestHeaders.delete('cookie')
      // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
      // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
      if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
        requestHeaders.delete('authorization')
      }
    
      url.protocol = 'https'
      url.hostname = hostname
      url.port = '443'
      url.pathname = url.pathname.replace(/^\/yourpath/, '')
    
      return NextResponse.rewrite(url, {
        request: { headers: requestHeaders },
      })
    }
    
    export const config = {
      matcher: '/yourpath/:path*',
    }
    ```

    ### EU

    ```javascript
    import { NextResponse } from 'next/server'
    
    export function proxy(request) {
      const url = request.nextUrl.clone()
      const hostname = url.pathname.startsWith('/yourpath/static/') || url.pathname.startsWith('/yourpath/array/')
        ? 'eu-assets.i.posthog.com'
        : 'eu.i.posthog.com'
    
      const requestHeaders = new Headers(request.headers)
      requestHeaders.set('host', hostname)
      // Remove cookies before forwarding to PostHog
      requestHeaders.delete('cookie')
      // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
      // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
      if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
        requestHeaders.delete('authorization')
      }
    
      url.protocol = 'https'
      url.hostname = hostname
      url.port = '443'
      url.pathname = url.pathname.replace(/^\/yourpath/, '')
    
      return NextResponse.rewrite(url, {
        request: { headers: requestHeaders },
      })
    }
    
    export const config = {
      matcher: '/yourpath/:path*',
    }
    ```

    **Using Next.js 15 or earlier? Use middleware.js instead**

    ### US

    ```javascript
    import { NextResponse } from 'next/server'
    
    export function middleware(request) {
      const url = request.nextUrl.clone()
      const hostname = url.pathname.startsWith('/yourpath/static/') || url.pathname.startsWith('/yourpath/array/')
        ? 'us-assets.i.posthog.com'
        : 'us.i.posthog.com'
    
      const requestHeaders = new Headers(request.headers)
      requestHeaders.set('host', hostname)
      // Remove cookies before forwarding to PostHog
      requestHeaders.delete('cookie')
      // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
      // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
      if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
        requestHeaders.delete('authorization')
      }
    
      url.protocol = 'https'
      url.hostname = hostname
      url.port = '443'
      url.pathname = url.pathname.replace(/^\/yourpath/, '')
    
      return NextResponse.rewrite(url, {
        request: { headers: requestHeaders },
      })
    }
    
    export const config = {
      matcher: '/yourpath/:path*',
    }
    ```

    ### EU

    ```javascript
    import { NextResponse } from 'next/server'
    
    export function middleware(request) {
      const url = request.nextUrl.clone()
      const hostname = url.pathname.startsWith('/yourpath/static/') || url.pathname.startsWith('/yourpath/array/')
        ? 'eu-assets.i.posthog.com'
        : 'eu.i.posthog.com'
    
      const requestHeaders = new Headers(request.headers)
      requestHeaders.set('host', hostname)
      // Remove cookies before forwarding to PostHog
      requestHeaders.delete('cookie')
      // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
      // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
      if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
        requestHeaders.delete('authorization')
      }
    
      url.protocol = 'https'
      url.hostname = hostname
      url.port = '443'
      url.pathname = url.pathname.replace(/^\/yourpath/, '')
    
      return NextResponse.rewrite(url, {
        request: { headers: requestHeaders },
      })
    }
    
    export const config = {
      matcher: '/yourpath/:path*',
    }
    ```

    The only differences are the filename (`middleware.js`) and the exported function name (`middleware` instead of `proxy`).

    The proxy does the following:

    -   The `matcher` config tells Next.js to only run this proxy for requests starting with `/yourpath`
    -   It determines which PostHog host to use: the assets host for `/static/*` and `/array/*` requests (so that cache headers are preserved), the main host for everything else
    -   It sets the `host` header so PostHog knows how to route the request. Without this, you'll get 401 errors.
    -   It rewrites the URL to PostHog's domain and strips the `/yourpath` prefix
    -   It removes cookies and any `Authorization` header that isn't a PostHog key (`Bearer phc_`, `phs_` or `phx_`). Capture v1 SDKs send the project token as `Authorization: Bearer <token>`, so the proxy forwards that header. Keys created before these prefixes need their exact `Bearer <key>` value allowed too.
    -   It passes the headers as `request: { headers }`, so Next.js applies them to the request it forwards to PostHog

    See [Next.js proxy documentation](https://nextjs.org/docs/app/api-reference/file-conventions/proxy) for more details.

2.  2

    ## Configure trailing slash handling

    Add `skipTrailingSlashRedirect` to your `next.config.js`:

    ```javascript
    // next.config.js
    const nextConfig = {
      skipTrailingSlashRedirect: true,
    }
    
    module.exports = nextConfig
    ```

    PostHog API paths end with a slash, such as `/e/` and `/flags/`. Without this setting, Next.js answers these requests with a `308` redirect to the same path without the slash. Browsers follow the redirect, so events still arrive, but each request takes an extra round trip.

3.  3

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

4.  4

    ## Deploy your changes

    Commit and push your changes. The proxy activates once deployed.

    In development, restart your dev server after creating the proxy file. Next.js doesn't hot-reload proxy changes.

5.  ## Verify your setup

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

### Proxy not running

If requests to your proxy path return 404 or don't get proxied:

1.  Verify your `proxy.js` (or `middleware.js` for Next.js <16) file is in the project root (same level as `app` or `pages`), not inside those folders
2.  Check that the `matcher` pattern matches your proxy path
3.  Restart your dev server after creating or modifying the proxy file

### Using with Clerk or other auth solutions

If you use Clerk or a similar auth middleware, send PostHog requests to the proxy before the auth middleware runs. PostHog requests then work for logged-out users, and the auth middleware never sees them. This example uses Clerk's `clerkMiddleware`:

### US

```javascript
import { clerkMiddleware } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

function posthogProxy(request) {
  const url = request.nextUrl.clone()
  const hostname = url.pathname.startsWith('/yourpath/static/') || url.pathname.startsWith('/yourpath/array/')
    ? 'us-assets.i.posthog.com'
    : 'us.i.posthog.com'

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('host', hostname)
  // Remove cookies before forwarding to PostHog
  requestHeaders.delete('cookie')
  // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
  // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
  if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
    requestHeaders.delete('authorization')
  }

  url.protocol = 'https'
  url.hostname = hostname
  url.port = '443'
  url.pathname = url.pathname.replace(/^\/yourpath/, '')

  return NextResponse.rewrite(url, {
    request: { headers: requestHeaders },
  })
}

const clerk = clerkMiddleware()

export function proxy(request, event) {
  if (request.nextUrl.pathname.startsWith('/yourpath')) {
    return posthogProxy(request)
  }
  return clerk(request, event)
}

export const config = {
  matcher: [
    // Clerk's default matcher: skip Next.js internals and static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
    // The PostHog path, including the .js files that the pattern above skips
    '/yourpath/:path*',
  ],
}
```

### EU

```javascript
import { clerkMiddleware } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

function posthogProxy(request) {
  const url = request.nextUrl.clone()
  const hostname = url.pathname.startsWith('/yourpath/static/') || url.pathname.startsWith('/yourpath/array/')
    ? 'eu-assets.i.posthog.com'
    : 'eu.i.posthog.com'

  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('host', hostname)
  // Remove cookies before forwarding to PostHog
  requestHeaders.delete('cookie')
  // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
  // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
  if (!/^Bearer ph[csx]_/.test(requestHeaders.get('authorization') ?? '')) {
    requestHeaders.delete('authorization')
  }

  url.protocol = 'https'
  url.hostname = hostname
  url.port = '443'
  url.pathname = url.pathname.replace(/^\/yourpath/, '')

  return NextResponse.rewrite(url, {
    request: { headers: requestHeaders },
  })
}

const clerk = clerkMiddleware()

export function proxy(request, event) {
  if (request.nextUrl.pathname.startsWith('/yourpath')) {
    return posthogProxy(request)
  }
  return clerk(request, event)
}

export const config = {
  matcher: [
    // Clerk's default matcher: skip Next.js internals and static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    '/(api|trpc)(.*)',
    // The PostHog path, including the .js files that the pattern above skips
    '/yourpath/:path*',
  ],
}
```

Keep the `/yourpath/:path*` entry in the `matcher`. Clerk's default matcher skips paths that end in `.js`, such as `/yourpath/static/array.js`, so without this entry the PostHog SDK files never reach the proxy. On Next.js 15 or earlier, put this code in `middleware.js` and name the function `middleware`.

### 503 or 400 errors persist

If proxy doesn't resolve the errors, your hosting platform may be incompatible with Next.js proxying. Try:

1.  A platform-specific proxy like [Netlify redirects](https://posthog.com/docs/advanced/proxy/netlify.md) or [Vercel rewrites](https://posthog.com/docs/advanced/proxy/vercel.md)
2.  [PostHog's managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md)
3.  Self-hosting Next.js where you control the infrastructure
