> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# SvelteKit reverse proxy

Canonical URL: https://posthog.com/docs/advanced/proxy/sveltekit

## On this page

- [How it works](#how-it-works)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Create the server hook](#create-the-server-hook)
- [Update your PostHog SDK](#update-your-posthog-sdk)
- [Deploy your changes](#deploy-your-changes)
- [Verify your setup](#verify-your-setup)
- [Troubleshooting](#troubleshooting)
- [Deployment notes](#deployment-notes)

**Before you start**

-   If you use a self-hosted proxy, PostHog can't help troubleshoot. Use [our managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) if you want support.
-   Use domains matching your PostHog region: `us.i.posthog.com` for US, `eu.i.posthog.com` for EU.
-   Don't use obvious path names like `/analytics`, `/tracking`, `/telemetry`, or `/posthog`. Blockers will catch them. Use something unique to your app instead.

**Data transfer costs**

The `handle` hook runs on every request, so all PostHog traffic – events, session recordings, feature flag polls, and SDK assets – passes through your SvelteKit deployment. Costs depend on where it's hosted: serverless platforms like Vercel or Netlify bill this as bandwidth and function invocations, which can add up on high-traffic sites, especially because session recordings are often 1–5 MB each.

To avoid these costs, use the [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md) (free for PostHog Cloud users) or a provider without egress fees like [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md).

This guide shows you how to use [SvelteKit server hooks](https://kit.svelte.dev/docs/hooks#server-hooks) as a reverse proxy for PostHog.

## How it works

SvelteKit's `handle` hook runs on every request before it reaches your routes. When a request matches your proxy path, the hook fetches the response from PostHog and returns it under your domain.

Here's the request flow:

1.  User triggers an event in your app
2.  Request goes to your domain (e.g., `yourdomain.com/yourpath/e`)
3.  SvelteKit's server hook intercepts the request
4.  The hook fetches the response from PostHog's servers
5.  PostHog's response is returned to the user under your domain

This works because the hook runs server-side, so the browser only sees requests to your domain. Ad blockers that filter by domain won't block these requests.

**SSR required**

This method only works with server-side rendering enabled. If you're using `adapter-static` for static site generation, SvelteKit ignores `hooks.server.ts`. Use a CDN-level proxy like [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md) or [Netlify redirects](https://posthog.com/docs/advanced/proxy/netlify.md) instead.

## Prerequisites

This guide requires a SvelteKit project with SSR enabled (the default).

## Setup

1.  1

    ## Create the server hook

    Create a file at `src/hooks.server.ts`:

    ### US

    ```typescript
    import type { Handle } from '@sveltejs/kit'
    
    export const handle: Handle = async ({ event, resolve }) => {
      const { pathname } = event.url
    
      if (pathname.startsWith('/yourpath')) {
        const useAssetHost = pathname.startsWith('/yourpath/static/') || pathname.startsWith('/yourpath/array/')
        const hostname = useAssetHost
          ? 'us-assets.i.posthog.com'
          : 'us.i.posthog.com'
    
        const url = new URL(event.request.url)
        url.protocol = 'https:'
        url.hostname = hostname
        url.port = '443'
        url.pathname = pathname.replace(/^\/yourpath/, '')
    
        const headers = new Headers(event.request.headers)
        headers.set('host', hostname)
        // Remove cookies before forwarding to PostHog
        headers.delete('cookie')
        // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
        // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
        if (!/^Bearer ph[csx]_/.test(headers.get('authorization') ?? '')) {
          headers.delete('authorization')
        }
        headers.set('accept-encoding', '')
    
        // Forward client IP for geolocation
        const clientIp = event.request.headers.get('x-forwarded-for') || event.getClientAddress()
        if (clientIp) {
          headers.set('x-forwarded-for', clientIp)
        }
    
        const response = await fetch(url.toString(), {
          method: event.request.method,
          headers,
          body: event.request.body,
          // @ts-ignore - duplex is required for streaming request bodies
          duplex: 'half'
        })
    
        return response
      }
    
      return resolve(event)
    }
    ```

    ### EU

    ```typescript
    import type { Handle } from '@sveltejs/kit'
    
    export const handle: Handle = async ({ event, resolve }) => {
      const { pathname } = event.url
    
      if (pathname.startsWith('/yourpath')) {
        const useAssetHost = pathname.startsWith('/yourpath/static/') || pathname.startsWith('/yourpath/array/')
        const hostname = useAssetHost
          ? 'eu-assets.i.posthog.com'
          : 'eu.i.posthog.com'
    
        const url = new URL(event.request.url)
        url.protocol = 'https:'
        url.hostname = hostname
        url.port = '443'
        url.pathname = pathname.replace(/^\/yourpath/, '')
    
        const headers = new Headers(event.request.headers)
        headers.set('host', hostname)
        // Remove cookies before forwarding to PostHog
        headers.delete('cookie')
        // Forward PostHog keys (Bearer phc_, phs_ or phx_), which the SDKs need. Strip any other credentials.
        // To allow an older key without one of these prefixes, also match its exact 'Bearer <key>' value.
        if (!/^Bearer ph[csx]_/.test(headers.get('authorization') ?? '')) {
          headers.delete('authorization')
        }
        headers.set('accept-encoding', '')
    
        // Forward client IP for geolocation
        const clientIp = event.request.headers.get('x-forwarded-for') || event.getClientAddress()
        if (clientIp) {
          headers.set('x-forwarded-for', clientIp)
        }
    
        const response = await fetch(url.toString(), {
          method: event.request.method,
          headers,
          body: event.request.body,
          // @ts-ignore - duplex is required for streaming request bodies
          duplex: 'half'
        })
    
        return response
      }
    
      return resolve(event)
    }
    ```

    Here's what the code does:

    -   Intercepts requests starting with `/yourpath`
    -   Routes `/static/*` and `/array/*` requests to PostHog's asset server and everything else to the main API
    -   Sets the `host` header so PostHog can route the request correctly
    -   Forwards the client's IP address for accurate geolocation
    -   Passes non-matching requests to the normal SvelteKit request handler

    See [SvelteKit's hooks documentation](https://kit.svelte.dev/docs/hooks#server-hooks) for more details.

2.  2

    ## Update your PostHog SDK

    In your SvelteKit app, initialize PostHog with your proxy path. Create or update your PostHog setup:

    ### US

    ```typescript
    // src/lib/posthog.ts
    import posthog from 'posthog-js'
    import { browser } from '$app/environment'
    
    export function initPostHog() {
      if (!browser) return
    
      posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN, {
        api_host: '/yourpath',
        ui_host: 'https://us.posthog.com',
        persistence: 'localStorage'
      })
    }
    ```

    ### EU

    ```typescript
    // src/lib/posthog.ts
    import posthog from 'posthog-js'
    import { browser } from '$app/environment'
    
    export function initPostHog() {
      if (!browser) return
    
      posthog.init(import.meta.env.VITE_POSTHOG_PROJECT_TOKEN, {
        api_host: '/yourpath',
        ui_host: 'https://eu.posthog.com',
        persistence: 'localStorage'
      })
    }
    ```

    Then call it from your root layout:

    ```html
    <!-- src/routes/+layout.svelte -->
    <script>
      import { onMount } from 'svelte'
      import { initPostHog } from '$lib/posthog'
    
      onMount(() => {
        initPostHog()
      })
    </script>
    
    <slot />
    ```

    The `api_host` tells the SDK where to send events. Using a relative path ensures requests go to your domain. The `ui_host` must point to PostHog's actual domain so features like the toolbar link correctly.

3.  3

    ## Deploy your changes

    Commit and push your changes. The server hook will be active once deployed.

    In development, restart your dev server after creating the hook file.

4.  ## Verify your setup

    Checkpoint

    Confirm events are flowing through your proxy:

    1.  Open your browser's developer tools and go to the **Network** tab
    2.  Navigate to your site or trigger an event
    3.  Look for requests to your domain with your proxy path (e.g., `yourdomain.com/yourpath`)
    4.  Verify the response status is `200 OK`
    5.  Check the [PostHog app](https://app.posthog.com) to confirm events appear in your activity feed

    If you see errors, check [troubleshooting](#troubleshooting) below.

## Troubleshooting

### Hook not running

If requests to your proxy path return 404 or aren't being proxied:

1.  Verify your file is at `src/hooks.server.ts` (not `src/routes/hooks.server.ts`)
2.  Check the file extension is `.ts` for TypeScript projects
3.  Restart your dev server after creating the file

### Static site generation

SvelteKit server hooks don't run for statically generated sites. If you're using `adapter-static`, use a different proxy method:

-   [Cloudflare Workers](https://posthog.com/docs/advanced/proxy/cloudflare.md) for sites on Cloudflare Pages
-   [Netlify redirects](https://posthog.com/docs/advanced/proxy/netlify.md) for sites on Netlify
-   [Vercel rewrites](https://posthog.com/docs/advanced/proxy/vercel.md) for sites on Vercel

### All users show same location

If geolocation data is wrong or all users appear in the same location:

1.  Verify the `x-forwarded-for` header is being set in your hook
2.  If you're behind multiple proxies (like Cloudflare or a load balancer), the original client IP may be in a different header. Try using the incoming `x-forwarded-for` header first.

The code above handles this by checking both `x-forwarded-for` from the incoming request and `event.getClientAddress()` as a fallback.

## Deployment notes

This proxy works with these SvelteKit adapters:

-   **adapter-node:** Works out of the box
-   **adapter-vercel:** Works with SSR enabled
-   **adapter-netlify:** Works with SSR enabled
-   **adapter-cloudflare:** Works with SSR enabled

For `adapter-static`, use a CDN-level proxy instead.
