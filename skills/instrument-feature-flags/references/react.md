# React Feature Flags installation - Docs

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

    ## Use feature flags

    Required

    ## Using hooks

    PostHog provides several hooks to make it easy to use feature flags in your React app. Use `useFeatureFlagEnabled` for boolean flags:

    ```jsx
    import { useFeatureFlagEnabled } from '@posthog/react'
    function App() {
        const showWelcomeMessage = useFeatureFlagEnabled('flag-key')
        const payload = useFeatureFlagPayload('flag-key')
        return (
            <div className="App">
                {showWelcomeMessage ? (
                    <div>
                        <h1>Welcome!</h1>
                        <p>Thanks for trying out our feature flags.</p>
                    </div>
                ) : (
                    <div>
                        <h2>No welcome message</h2>
                        <p>Because the feature flag evaluated to false.</p>
                    </div>
                )}
            </div>
        )
    }
    ```

    ### Multivariate flags

    For multivariate flags, use `useFeatureFlagVariantKey`:

    ```jsx
    import { useFeatureFlagVariantKey } from '@posthog/react'
    function App() {
        const variantKey = useFeatureFlagVariantKey('show-welcome-message')
        let welcomeMessage = ''
        if (variantKey === 'variant-a') {
            welcomeMessage = 'Welcome to the Alpha!'
        } else if (variantKey === 'variant-b') {
            welcomeMessage = 'Welcome to the Beta!'
        }
        return (
            <div className="App">
                {welcomeMessage ? (
                    <div>
                        <h1>{welcomeMessage}</h1>
                        <p>Thanks for trying out our feature flags.</p>
                    </div>
                ) : (
                    <div>
                        <h2>No welcome message</h2>
                        <p>Because the feature flag evaluated to false.</p>
                    </div>
                )}
            </div>
        )
    }
    ```

    ### Flag payloads

    The `useFeatureFlagPayload` hook does *not* send a `$feature_flag_called` event, which is required for experiments. Always use it with `useFeatureFlagEnabled` or `useFeatureFlagVariantKey`:

    ```jsx
    import { useFeatureFlagPayload, useFeatureFlagEnabled } from '@posthog/react'
    function App() {
        const variant = useFeatureFlagEnabled('show-welcome-message')
        const payload = useFeatureFlagPayload('show-welcome-message')
        return (
            <>
                {variant ? (
                    <div className="welcome-message">
                        <h2>{payload?.welcomeTitle}</h2>
                        <p>{payload?.welcomeMessage}</p>
                    </div>
                ) : (
                    <div>
                        <h2>No custom welcome message</h2>
                        <p>Because the feature flag evaluated to false.</p>
                    </div>
                )}
            </>
        )
    }
    ```

    ## Using PostHogFeature component

    The `PostHogFeature` component simplifies code by handling feature flag related logic:

    App.tsx

    PostHog AI

    ```jsx
    import { PostHogFeature } from '@posthog/react'
    function App() {
        return (
            <PostHogFeature flag='show-welcome-message' match={true}>
                <div>
                    <h1>Hello</h1>
                    <p>Thanks for trying out our feature flags.</p>
                </div>
            </PostHogFeature>
        )
    }
    ```

    The `match` prop can be either `true`, or the variant key, to match on a specific variant. If you also want to show a default message, you can pass these in the `fallback` prop.

    If your flag has a payload, you can pass a function to children whose first argument is the payload:

    App.tsx

    PostHog AI

    ```jsx
    <PostHogFeature flag='show-welcome-message' match={true}>
        {(payload) => {
            return (
                <div>
                    <h1>{payload.welcomeMessage}</h1>
                    <p>Thanks for trying out our feature flags.</p>
                </div>
            )
        }}
    </PostHogFeature>
    ```

7.  7

    ## Running experiments

    Optional

    Experiments run on top of our feature flags. Once you've implemented the flag in your code, you run an experiment by creating a new experiment in the PostHog dashboard.

8.  8

    ## Next steps

    Recommended

    Now that you're evaluating flags, continue with the resources below to learn what else Feature Flags enables within the PostHog platform.

    | Resource | Description |
    | --- | --- |
    | [Creating a feature flag](/docs/feature-flags/creating-feature-flags.md) | How to create a feature flag in PostHog |
    | [Adding feature flag code](/docs/feature-flags/adding-feature-flag-code.md) | How to check flags in your code for all platforms |
    | [Framework-specific guides](/docs/feature-flags/tutorials.md#framework-guides) | Setup guides for React Native, Next.js, Flutter, and other frameworks |
    | [How to do a phased rollout](/tutorials/phased-rollout.md) | Gradually roll out features to minimize risk |
    | [More tutorials](/docs/feature-flags/tutorials.md) | Other real-world examples and use cases |

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better