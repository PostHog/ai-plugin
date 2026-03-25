# React error tracking installation - Docs

1.  1

    ## Install the package

    Required

    Install [`posthog-js`](https://github.com/posthog/posthog-js) and `@posthog/react` using your package manager:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-js @posthog/react
    ```

    ### yarn

    ```bash
    yarn add posthog-js @posthog/react
    ```

    ### pnpm

    ```bash
    pnpm add posthog-js @posthog/react
    ```

2.  2

    ## Add environment variables

    Required

    Add your PostHog project token and host to your environment variables. For Vite-based React apps, use the `VITE_PUBLIC_` prefix:

    .env

    PostHog AI

    ```bash
    VITE_PUBLIC_POSTHOG_PROJECT_TOKEN=<ph_project_token>
    VITE_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
    ```

3.  3

    ## Initialize PostHog

    Required

    Wrap your app with the `PostHogProvider` component at the root of your application (such as `main.tsx` if you're using Vite):

    main.tsx

    PostHog AI

    ```jsx
    import { StrictMode } from 'react'
    import { createRoot } from 'react-dom/client'
    import './index.css'
    import App from './App.jsx'
    import { PostHogProvider } from '@posthog/react'
    const options = {
      api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
      defaults: '2026-01-30',
    } as const
    createRoot(document.getElementById('root')).render(
      <StrictMode>
        <PostHogProvider apiKey={import.meta.env.VITE_PUBLIC_POSTHOG_PROJECT_TOKEN} options={options}>
          <App />
        </PostHogProvider>
      </StrictMode>
    )
    ```

    **defaults option**

    The `defaults` option automatically configures PostHog with recommended settings for new projects. See [SDK defaults](/docs/libraries/js.md#sdk-defaults) for details.

4.  4

    ## Accessing PostHog in your code

    Recommended

    Use the `usePostHog` hook to access the PostHog instance in any component wrapped by `PostHogProvider`:

    MyComponent.tsx

    PostHog AI

    ```jsx
    import { usePostHog } from '@posthog/react'
    function MyComponent() {
        const posthog = usePostHog()
        function handleClick() {
            posthog.capture('button_clicked', { button_name: 'signup' })
        }
        return <button onClick={handleClick}>Sign up</button>
    }
    ```

    You can also import `posthog` directly for non-React code or utility functions:

    utils/analytics.ts

    PostHog AI

    ```jsx
    import posthog from 'posthog-js'
    export function trackPurchase(amount: number) {
        posthog.capture('purchase_completed', { amount })
    }
    ```

5.  5

    ## Send events

    Recommended

    Click around and view a couple pages to generate some events. PostHog automatically captures pageviews, clicks, and other interactions for you.

    If you'd like, you can also manually capture custom events:

    JavaScript

    PostHog AI

    ```javascript
    posthog.capture('my_custom_event', { property: 'value' })
    ```

6.  6

    ## Set up exception autocapture

    Recommended

    You can enable exception autocapture for the JavaScript Web SDK in the **Error tracking** section of [your project settings](https://app.posthog.com/settings/project-error-tracking#exception-autocapture).

    When enabled, this automatically captures `$exception` events when errors are thrown by wrapping the `window.onerror` and `window.onunhandledrejection` listeners.

7.  7

    ## Set up error boundaries

    Optional

    You can use the `PostHogErrorBoundary` component to capture rendering errors thrown by components:

    JavaScript

    PostHog AI

    ```javascript
    import { PostHogProvider, PostHogErrorBoundary } from '@posthog/react'
    const Layout = () => {
      return (
        <PostHogProvider apiKey="<ph_project_token>">
          <PostHogErrorBoundary
            fallback={<YourFallbackComponent />} // (Optional) Add a fallback component that's shown when an error happens.
          >
            <YourApp />
          </PostHogErrorBoundary>
        </PostHogProvider>
      )
    }
    const YourFallbackComponent = ({ error, componentStack, exceptionEvent }) => {
      return <div>Something went wrong. Please try again later.</div>
    }
    ```

8.  8

    ## Manually capture exceptions

    Optional

    It is also possible to manually capture exceptions using the `captureException` method:

    JavaScript

    PostHog AI

    ```javascript
    posthog.captureException(error, additionalProperties)
    ```

9.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

10.  9

     ## Upload source maps

     Required

     Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

     Let's continue to the next section.

     [Upload source maps](/docs/error-tracking/upload-source-maps/react.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better