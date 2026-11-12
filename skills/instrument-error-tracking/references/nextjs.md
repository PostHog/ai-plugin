> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Next.js Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/nextjs

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Install the package](#install-the-package)
- [Add environment variables](#add-environment-variables)
- [Initialize PostHog](#initialize-posthog)
- [Accessing PostHog on the client](#accessing-posthog-on-the-client)
- [Capture client-side exceptions](#capture-client-side-exceptions)
- [Installing PostHog SDK for server-side](#installing-posthog-sdk-for-server-side)
- [Verify server-side exceptions](#verify-server-side-exceptions)
- [Capturing server-side exceptions](#capturing-server-side-exceptions)
- [Verify error tracking](#verify-error-tracking)
- [Upload source maps](#upload-source-maps)

## Install with the wizard

Run this command in your project directory to add PostHog to your Next.js project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

1.  1

    ## Install the package

    Required

    Install the PostHog JavaScript library using your package manager:

    ### npm

    ```bash
    npm install posthog-js@1
    ```

    ### yarn

    ```bash
    yarn add posthog-js@1
    ```

    ### pnpm

    ```bash
    pnpm add posthog-js@1
    ```

    ### bun

    ```bash
    bun add posthog-js@1
    ```

2.  2

    ## Add environment variables

    Required

    Add your PostHog project token and host to your `.env.local` file and to your hosting provider (e.g. Vercel, Netlify). These values need to start with `NEXT_PUBLIC_` to be accessible on the client-side.

    .env.local

    ```bash
    NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN=<ph_project_token>
    NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
    ```

3.  3

    ## Initialize PostHog

    Required

    Choose the integration method based on your Next.js version and router type.

    ## Next.js 15.3+

    If you're using Next.js 15.3+, you can use `instrumentation-client.ts` for a lightweight, fast integration:

    instrumentation-client.ts

    ```typescript
    import posthog from 'posthog-js'
    
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN!, {
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
        defaults: '2026-08-30'
    })
    ```

    ## App router

    For the App router, create a `providers.tsx` file in your `app` folder. The `posthog-js` library needs to be initialized on the client-side using the `'use client'` directive:

    app/providers.tsx

    ```typescript
    'use client'
    
    import { usePathname, useSearchParams } from "next/navigation"
    import { useEffect } from "react"
    
    import posthog from 'posthog-js'
    import { PostHogProvider as PHProvider } from '@posthog/react'
    
    export function PostHogProvider({ children }: { children: React.ReactNode }) {
      useEffect(() => {
        posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN as string, {
          api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
          defaults: '2026-08-30'
        })
      }, [])
    
      return (
        <PHProvider client={posthog}>
          {children}
        </PHProvider>
      )
    }
    ```

    Then import the `PostHogProvider` component in your `app/layout.tsx` and wrap your app with it:

    app/layout.tsx

    ```typescript
    import './globals.css'
    import { PostHogProvider } from './providers'
    
    export default function RootLayout({ children }: { children: React.ReactNode }) {
      return (
        <html lang="en">
          <body>
            <PostHogProvider>
              {children}
            </PostHogProvider>
          </body>
        </html>
      )
    }
    ```

    ## Pages router

    For the Pages router, integrate PostHog at the root of your app in `pages/_app.tsx`:

    pages/\_app.tsx

    ```typescript
    import { useEffect } from 'react'
    import { Router } from 'next/router'
    import posthog from 'posthog-js'
    import { PostHogProvider } from '@posthog/react'
    import type { AppProps } from 'next/app'
    
    export default function App({ Component, pageProps }: AppProps) {
    
      useEffect(() => {
        posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN as string, {
          api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
          defaults: '2026-08-30',
          loaded: (posthog) => {
            if (process.env.NODE_ENV === 'development') posthog.debug()
          }
        })
      }, [])
    
      return (
        <PostHogProvider client={posthog}>
          <Component {...pageProps} />
        </PostHogProvider>
      )
    }
    ```

    **Defaults option**

    The `defaults` option automatically configures PostHog with recommended settings for new projects. See [SDK defaults](https://posthog.com/docs/libraries/js.md#sdk-defaults) for details.

4.  4

    ## Accessing PostHog on the client

    Recommended

    ## Next.js 15.3+

    Once initialized in `instrumentation-client.ts`, import `posthog` from `posthog-js` anywhere and call the methods you need:

    app/checkout/page.tsx

    ```typescript
    'use client'
    
    import posthog from 'posthog-js'
    
    export default function CheckoutPage() {
        function handlePurchase() {
            posthog.capture('purchase_completed', { amount: 99 })
        }
    
        return <button onClick={handlePurchase}>Complete purchase</button>
    }
    ```

    ## App/Pages router

    Use the `usePostHog` hook to access PostHog in client components:

    app/checkout/page.tsx

    ```typescript
    'use client'
    
    import { usePostHog } from '@posthog/react'
    
    export default function CheckoutPage() {
        const posthog = usePostHog()
    
        function handlePurchase() {
            posthog.capture('purchase_completed', { amount: 99 })
        }
    
        return <button onClick={handlePurchase}>Complete purchase</button>
    }
    ```

5.  5

    ## Capture client-side exceptions

    Required

    PostHog can automatically capture unhandled exceptions in your Next.js app using the JavaScript Web SDK. Turn it on with `capture_exceptions: true` in your `posthog.init` call:

    instrumentation-client.js

    ```javascript
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN, {
      api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      capture_exceptions: true,
    })
    ```

    It is also possible to manually capture exceptions using the `captureException` method:

    JavaScript

    ```javascript
    posthog.captureException(error, additionalProperties)
    ```

    Manual capture is very useful if you already use error boundaries to handle errors in your app:

    ## App router

    Next.js uses [error boundaries](https://nextjs.org/docs/app/building-your-application/routing/error-handling#using-error-boundaries) to handle uncaught exceptions by rendering a fallback UI instead of the crashing components. To set one up, create a `error.tsx` file in any of your route directories. This triggers when there is an error rendering your component. An error boundary catches the error before autocapture sees it, so add the capture to **every** `error.tsx` your app has. It should look like this:

    error.tsx

    ```typescript
    "use client"
    import posthog from "posthog-js"
    import { useEffect } from "react"
    
    export default function Error({
      error,
      reset,
    }: {
      error: Error & { digest?: string }
      reset: () => void
    }) {
      useEffect(() => {
        posthog.captureException(error)
      }, [error])
      return (
        ...
      )
    }
    ```

    Also add the capture to a [Global Error component](https://nextjs.org/docs/app/building-your-application/routing/error-handling#handling-global-errors) at `app/global-error.tsx`, and create one if your app has none: it catches errors in the root layout and in the first render, before autocapture loads.

    app/global-error.tsx

    ```typescript
    'use client'
    import posthog from "posthog-js"
    import NextError from "next/error"
    import { useEffect } from "react"
    
    export default function GlobalError({
      error,
      reset,
    }: {
      error: Error & { digest?: string }
      reset: () => void
    }) {
      useEffect(() => {
        posthog.captureException(error)
      }, [error])
      return (
        // global-error must include html and body tags
        <html>
          <body>
            {/* `NextError` is the default Next.js error page component */}
            <NextError statusCode={0} />
          </body>
        </html>
      )
    }
    ```

    ## Pages router

    For Pages Router, you can use React's [Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary) to catch JavaScript errors anywhere in the component tree. Create a custom error boundary component and report errors to PostHog in the `componentDidCatch` method:

    components/ErrorBoundary.tsx

    ```typescript
    componentDidCatch(error, errorInfo) {
      posthog.captureException(error)
    }
    ```

    Then wrap your app or specific components with the error boundary:

    pages/\_app.tsx

    ```typescript
    import type { AppProps } from 'next/app'
    import ErrorBoundary from '../components/ErrorBoundary'
    
    export default function App({ Component, pageProps }: AppProps) {
      return (
        <ErrorBoundary>
          <Component {...pageProps} />
        </ErrorBoundary>
      )
    }
    ```

6.  6

    ## Installing PostHog SDK for server-side

    Required

    Next.js enables you to both server-side render pages and add server-side functionality. To capture server-side exceptions, use [`@posthog/next`](https://posthog.com/docs/libraries/next-js/posthog-next.md) for the errors Next.js reports and the [Node SDK](https://posthog.com/docs/libraries/node.md) for everything else.

    First, install `@posthog/next` 0.11.0+ and `posthog-node` 5.61.1+, and upgrade `posthog-js` to 1.445.1+ if yours is older:

    ### npm

    ```bash
    npm install @posthog/next@0.11 posthog-node@5
    ```

    ### yarn

    ```bash
    yarn add @posthog/next@0.11 posthog-node@5
    ```

    ### pnpm

    ```bash
    pnpm add @posthog/next@0.11 posthog-node@5
    ```

    ### bun

    ```bash
    bun add @posthog/next@0.11 posthog-node@5
    ```

    Then create a `lib/posthog-server.js` file that initializes PostHog from `posthog-node`. With `enableExceptionAutocapture`, it captures uncaught exceptions and unhandled promise rejections. Turn it on for the Node.js runtime only: the edge runtime cannot register process listeners, so the client would fail to start there.

    This looks like this:

    lib/posthog-server.js

    ```javascript
    import { PostHog } from 'posthog-node'
    
    let posthogServer = null
    
    export function getPostHogServer() {
      posthogServer ??= new PostHog(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN, {
        host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
        flushAt: 1,
        flushInterval: 0,
        // Uncaught exceptions and unhandled promise rejections, on the Node.js runtime only
        enableExceptionAutocapture: process.env.NEXT_RUNTIME === 'nodejs',
      })
      return posthogServer
    }
    ```

    You can now use the `getPostHogServer` function to capture exceptions your server-side code handles itself. Pass the user's distinct ID when you know it:

    JavaScript

    ```javascript
    const posthog = getPostHogServer()
    try {
      throw new Error('This is a test exception for error tracking')
    } catch (error) {
      posthog.captureException(error, 'user_distinct_id', { source: 'test' })
    }
    ```

7.  ## Verify server-side exceptions

    Recommended

    You should also see events and exceptions in PostHog coming from your server-side code in the activity feed.

    [Check for server events in PostHog](https://app.posthog.com/activity/events)

8.  7

    ## Capturing server-side exceptions

    Required

    To capture errors that occur in your server-side code, set up an [`instrumentation.ts`](https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation) file at the root of your project (or in `src/`). Next.js calls its `onRequestError` hook when a Server Component, Route Handler, or Server Action throws. [`createOnRequestError`](https://posthog.com/docs/libraries/next-js/posthog-next.md) returns that hook, and links each error to the user and session. `register()` starts the `posthog-node` client when the server starts.

    This looks like this:

    instrumentation.js

    ```javascript
    import { createOnRequestError } from '@posthog/next'
    import { getPostHogServer } from './lib/posthog-server'
    
    export function register() {
      if (process.env.NEXT_RUNTIME === 'nodejs') {
        getPostHogServer()
      }
    }
    
    export const onRequestError = createOnRequestError({
      apiKey: process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN,
      host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
    })
    ```

    `onRequestError` misses errors thrown in `proxy.ts` and in Node.js middleware. If your app has either, wrap it with `withPostHogProxy`:

    proxy.ts

    ```typescript
    import { NextResponse } from 'next/server'
    import type { NextRequest } from 'next/server'
    import { withPostHogProxy } from '@posthog/next'
    
    // On Next.js 15 and earlier, this is middleware.ts with `export const middleware`
    export const proxy = withPostHogProxy(
      async (request: NextRequest) => {
        // Your existing proxy code
        return NextResponse.next()
      },
      {
        apiKey: process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN,
        host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
      }
    )
    ```

    Errors thrown in `after()` callbacks do not reach `onRequestError` either. If your app imports `after` from `next/server`, capture inside each callback:

    app/api/orders/route.ts

    ```typescript
    import { after } from 'next/server'
    import { getPostHogServer } from '@/lib/posthog-server'
    
    after(async () => {
      try {
        await sendReceipt(order)
      } catch (error) {
        await getPostHogServer().captureExceptionImmediate(error)
        throw error
      }
    })
    ```

    **Next.js 14 and earlier** run `instrumentation.js` only with the `instrumentationHook` flag. They never call `onRequestError`, so leave it out, and upgrade to capture Server Component, Route Handler and Server Action errors:

    next.config.js

    ```javascript
    module.exports = {
      // Only on Next.js 14 and earlier: later versions run instrumentation.js without it
      experimental: { instrumentationHook: true },
    }
    ```

    You can find a full example of both this and client-side error tracking in our [Next.js error monitoring tutorial](https://posthog.com/tutorials/nextjs-error-monitoring.md).

9.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

10.  8

     ## Upload source maps

     Required

     Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

     Let's continue to the next section.

     [Upload source maps](https://posthog.com/docs/error-tracking/upload-source-maps/nextjs.md)
