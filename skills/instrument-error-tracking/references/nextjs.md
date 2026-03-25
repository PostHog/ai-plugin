# Next.js error tracking installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog JavaScript library using your package manager:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-js
    ```

    ### yarn

    ```bash
    yarn add posthog-js
    ```

    ### pnpm

    ```bash
    pnpm add posthog-js
    ```

2.  2

    ## Add environment variables

    Required

    Add your PostHog project token and host to your `.env.local` file and to your hosting provider (e.g. Vercel, Netlify). These values need to start with `NEXT_PUBLIC_` to be accessible on the client-side.

    .env.local

    PostHog AI

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

    PostHog AI

    ```typescript
    import posthog from 'posthog-js'
    posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN!, {
        api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
        defaults: '2026-01-30'
    })
    ```

    ## App router

    For the App router, create a `providers.tsx` file in your `app` folder. The `posthog-js` library needs to be initialized on the client-side using the `'use client'` directive:

    app/providers.tsx

    PostHog AI

    ```typescript
    'use client'
    import { usePathname, useSearchParams } from "next/navigation"
    import { useEffect } from "react"
    import posthog from 'posthog-js'
    import { PostHogProvider as PHProvider } from 'posthog-js/react'
    export function PostHogProvider({ children }: { children: React.ReactNode }) {
      useEffect(() => {
        posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN as string, {
          api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
          defaults: '2026-01-30'
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

    PostHog AI

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

    PostHog AI

    ```typescript
    import { useEffect } from 'react'
    import { Router } from 'next/router'
    import posthog from 'posthog-js'
    import { PostHogProvider } from 'posthog-js/react'
    import type { AppProps } from 'next/app'
    export default function App({ Component, pageProps }: AppProps) {
      useEffect(() => {
        posthog.init(process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN as string, {
          api_host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
          defaults: '2026-01-30',
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

    The `defaults` option automatically configures PostHog with recommended settings for new projects. See [SDK defaults](/docs/libraries/js.md#sdk-defaults) for details.

4.  4

    ## Accessing PostHog on the client

    Recommended

    ## Next.js 15.3+

    Once initialized in `instrumentation-client.ts`, import `posthog` from `posthog-js` anywhere and call the methods you need:

    app/checkout/page.tsx

    PostHog AI

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

    PostHog AI

    ```typescript
    'use client'
    import { usePostHog } from 'posthog-js/react'
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

    PostHog can automatically capture unhandled exceptions in your Next.js app using the JavaScript Web SDK.

    You can enable exception autocapture for the JavaScript Web SDK in the **Error tracking** section of [your project settings](https://us.posthog.com/settings/project-error-tracking#exception-autocapture).

    It is also possible to manually capture exceptions using the `captureException` method:

    JavaScript

    PostHog AI

    ```javascript
    posthog.captureException(error, additionalProperties)
    ```

    Manual capture is very useful if you already use error boundaries to handle errors in your app:

    ## App router

    Next.js uses [error boundaries](https://nextjs.org/docs/app/building-your-application/routing/error-handling#using-error-boundaries) to handle uncaught exceptions by rendering a fallback UI instead of the crashing components. To set one up, create a `error.tsx` file in any of your route directories. This triggers when there is an error rendering your component and should look like this:

    error.tsx

    PostHog AI

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

    You can also create a [Global Error component](https://nextjs.org/docs/app/building-your-application/routing/error-handling#handling-global-errors) in your root layout to capture unhandled exceptions in your root layout.

    app/global-error.tsx

    PostHog AI

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

    PostHog AI

    ```typescript
    componentDidCatch(error, errorInfo) {
      posthog.captureException(error)
    }
    ```

    Then wrap your app or specific components with the error boundary:

    pages/\_app.tsx

    PostHog AI

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

    Next.js enables you to both server-side render pages and add server-side functionality. To integrate PostHog into your Next.js app on the server-side, you can use the [Node SDK](/docs/libraries/node.md).

    First, install the `posthog-node` library:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-node --save
    ```

    ### yarn

    ```bash
    yarn add posthog-node
    ```

    ### pnpm

    ```bash
    pnpm add posthog-node
    ```

    ### bun

    ```bash
    bun add posthog-node
    ```

    For the backend, we can create a `lib/posthog-server.js` file. In it, initialize PostHog from `posthog-node` as a singleton with your project token and host from [your project settings](https://app.posthog.com/settings/project).

    This looks like this:

    lib/posthog-server.js

    PostHog AI

    ```javascript
    import { PostHog } from 'posthog-node'
    let posthogInstance = null
    export function getPostHogServer() {
      if (!posthogInstance) {
        posthogInstance = new PostHog(
          process.env.NEXT_PUBLIC_POSTHOG_PROJECT_TOKEN,
          {
            host: process.env.NEXT_PUBLIC_POSTHOG_HOST,
            flushAt: 1,
            flushInterval: 0,
          }
        )
      }
      return posthogInstance
    }
    ```

    You can now use the `getPostHogServer` function to capture exceptions in server-side code.

    JavaScript

    PostHog AI

    ```javascript
    const posthog = getPostHogServer()
    try {
        throw new Error("This is a test exception for error tracking")
    } catch (error) {
        posthog.captureException(error, {
            source: 'test',
            user_id: 'test-user-123',
        })
    }
    ```

7.  ## Verify server-side exceptions

    Recommended

    You should also see events and exceptions in PostHog coming from your server-side code in the activity feed.

    [Check for server events in PostHog](https://app.posthog.com/activity/explore)

8.  7

    ## Capturing server-side exceptions

    Required

    To capture errors that occur in your server-side code, you can set up an [`instrumentation.ts`](https://nextjs.org/docs/app/building-your-application/optimizing/instrumentation) file at the root of your project. This provides a `onRequestError` hook that you can use to capture errors.

    Importantly, you need to:

    1.  Set up a `posthog-node` client in your server-side code. See our doc on [setting up Next.js server-side analytics](/docs/libraries/next-js.md#server-side-analytics.md) for more.
    2.  Check the request is running in the `nodejs` runtime to ensure PostHog works. You can call `posthog.debug()` to get verbose logging.
    3.  Get the `distinct_id` from the cookie to connect the error to a specific user.

    This looks like this:

    JavaScript

    PostHog AI

    ```javascript
    // instrumentation.js
    export function register() {
      // No-op for initialization
    }
    export const onRequestError = async (err, request, context) => {
      if (process.env.NEXT_RUNTIME === 'nodejs') {
        const { getPostHogServer } = require('./lib/posthog-server')
        const posthog = getPostHogServer()
        let distinctId = null
        if (request.headers.cookie) {
          // Normalize multiple cookie arrays to string
          const cookieString = Array.isArray(request.headers.cookie)
            ? request.headers.cookie.join('; ')
            : request.headers.cookie
          const postHogCookieMatch = cookieString.match(/ph_phc_.*?_posthog=([^;]+)/)
          if (postHogCookieMatch && postHogCookieMatch[1]) {
            try {
              const decodedCookie = decodeURIComponent(postHogCookieMatch[1])
              const postHogData = JSON.parse(decodedCookie)
              distinctId = postHogData.distinct_id
            } catch (e) {
              console.error('Error parsing PostHog cookie:', e)
            }
          }
        }
        await posthog.captureException(err, distinctId || undefined)
      }
    }
    ```

    You can find a full example of both this and client-side error tracking in our [Next.js error monitoring tutorial](/tutorials/nextjs-error-monitoring.md).

9.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

10.  8

     ## Upload source maps

     Required

     Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

     Let's continue to the next section.

     [Upload source maps](/docs/error-tracking/upload-source-maps/nextjs.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better