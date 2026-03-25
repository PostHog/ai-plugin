# React - Docs

PostHog makes it easy to get data about traffic and usage of your React app. Integrating PostHog into your site enables analytics about user behavior, custom events capture, session recordings, feature flags, and more.

This guide walks you through an example integration of PostHog using vanilla React and the [posthog-js library](/docs/integrate/client/js.md).

## Using a framework?

Using React with a framework like Next.js, Remix, or React Router requires additional setup. Follow their respective guides instead:

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/posthog.com/contents/images/docs/integrate/frameworks/nextjs.svg)Next.js](/docs/libraries/next-js.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/remix_letter_glowing_49183adce2.svg)Remix](/docs/libraries/remix.md)

-   [![](https://res.cloudinary.com/dmukukwp6/image/upload/rr_logo_light_970950178e.svg)React Router](/docs/libraries/react-router.md)

## Beta: integration via LLM

Install PostHog for React in seconds with our wizard by running this prompt with [LLM coding agents](/blog/envoy-wizard-llm-agent.md) like Cursor and Bolt, or by running it in your terminal.

`npx @posthog/wizard@latest`

[Learn more](/wizard.md)

Or, to integrate manually, continue with the rest of this guide.

## Installation

> For React-based frameworks, we recommend the [Next.js integration guide](/docs/libraries/next-js.md) and [Next.js integration guide](/docs/libraries/remix.md) instead.

1.  Install [`posthog-js`](https://github.com/posthog/posthog-js) and `@posthog/react` using your package manager:

PostHog AI

### npm

```bash
npm install --save posthog-js @posthog/react
```

### Yarn

```bash
yarn add posthog-js @posthog/react
```

### pnpm

```bash
pnpm add posthog-js @posthog/react
```

### Bun

```bash
bun add posthog-js @posthog/react
```

2.  Add your environment variables to your `.env.local` file and to your hosting provider (e.g. Vercel, Netlify, AWS). You can find your project token and host in [your project settings](https://us.posthog.com/settings/project). If you're using Vite, include `VITE_PUBLIC_` in their names ensures they are accessible in the frontend.

.env.local

PostHog AI

```shell
VITE_PUBLIC_POSTHOG_TOKEN=<ph_project_token>
VITE_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

3.  Integrate PostHog at the root of your app (such as `main.jsx` for Vite apps and `root.tsx` for React Router V7).

React

PostHog AI

```jsx
// src/main.jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import posthog from 'posthog-js';
import { PostHogProvider } from '@posthog/react'
posthog.init(import.meta.env.VITE_PUBLIC_POSTHOG_TOKEN, {
  api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
});
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PostHogProvider client={posthog}>
      <App />
    </PostHogProvider>
  </StrictMode>,
)
```

**Don't directly import PostHog**

Do not directly import `posthog` apart from installation as shown above. This will likely cause errors as the library might not be initialized yet. Initialization is handled automatically when you use the `PostHogProvider` and `usePostHog` hook.

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Usage

### PostHog provider

The React context provider makes it easy to access the `posthog-js` library in your app.

The provider takes an initialized and configured client instance like this:

React

PostHog AI

```jsx
// src/index.js
import posthog from 'posthog-js';
import { PostHogProvider} from '@posthog/react'
posthog.init(process.env.REACT_APP_PUBLIC_POSTHOG_TOKEN, {
  api_host: process.env.REACT_APP_PUBLIC_POSTHOG_HOST,
  defaults: '2026-01-30',
});
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <PostHogProvider client={posthog}>
      <App />
    </PostHogProvider>
  </React.StrictMode>
);
```

### Calling PostHog methods

By default, the `posthog-js` library automatically captures pageviews, element clicks, inputs, and more. Autocapture can be tuned in with [the configuration options](/docs/product-analytics/autocapture.md#configuring-autocapture).

To call PostHog methods for actions like identifying users, capturing events, using feature flags, or using other features, you can access the initialized `posthog-js` library using the `usePostHog` hook.

**Don't directly import PostHog**

Always use the `usePostHog` hook to access the PostHog library. Directly importing `posthog` will likely cause errors as the library might not be initialized yet. Initialization is handled automatically when you use the `PostHogProvider` and hook.

All the methods of the library are available and can be used as described in the [posthog-js documentation](/docs/libraries/js.md).

React

PostHog AI

```jsx
import { usePostHog } from '@posthog/react'
import { useEffect } from 'react'
import { useUser, useLogin } from '../lib/user'
function App() {
    // `usePostHog`, like other React contexts, must be called at the top level of your component
    const posthog = usePostHog()
    const login = useLogin()
    const user = useUser()
    useEffect(() => {
        if (user) {
            // Identify sends an event, so you may want to limit how often you call it
            posthog?.identify(user.id, {
                email: user.email,
            })
            posthog?.group('company', user.company_id)
        }
    }, [posthog, user.id, user.email, user.company_id])
    const loginClicked = () => {
        posthog?.capture('clicked_log_in')
        login()
    }
    return (
        <div className="App">
            {/* Fire a custom event when the button is clicked */}
            <button onClick={() => posthog?.capture('button_clicked')}>Click me</button>
            {/* This button click event is autocaptured by default */}
            <button data-attr="autocapture-button">Autocapture buttons</button>
            {/* This button click event is not autocaptured */}
            <button className="ph-no-capture">Ignore certain elements</button>
            <button onClick={loginClicked}>Login</button>
        </div>
    )
}
export default App
```

### TypeError: Cannot read properties of undefined

If you see the error `TypeError: Cannot read properties of undefined (reading '...')` this is likely because you tried to call a posthog function when posthog was not initialized (such as during the initial render). On purpose, we still render the children even if PostHog is not initialized so that your app still loads even if PostHog can't load.

To fix this error, add a check that posthog has been initialized such as:

React

PostHog AI

```jsx
useEffect(() => {
  posthog?.capture('test') // using optional chaining (recommended)
  if (posthog) {
    posthog.capture('test') // using an if statement
  }
}, [posthog])
```

Typescript helps protect against these errors.

### Tracking element visibility

The `PostHogCaptureOnViewed` component enables you to automatically capture events when elements scroll into view in the browser. This is useful for tracking impressions of important content, monitoring user engagement with specific sections, or understanding which parts of your page users are actually seeing.

The component wraps your content and sends a `$element_viewed` event to PostHog when the wrapped element becomes visible in the viewport. It only fires once per component instance.

**Basic usage:**

React

PostHog AI

```jsx
import { PostHogCaptureOnViewed } from '@posthog/react'
function App() {
    return (
        <PostHogCaptureOnViewed name="hero-banner">
            <div>Your important content here</div>
        </PostHogCaptureOnViewed>
    )
}
```

**With custom properties:**

You can include additional properties with the event to provide more context:

React

PostHog AI

```jsx
<PostHogCaptureOnViewed
    name="product-card"
    properties={{
        product_id: '123',
        category: 'electronics',
        price: 299.99
    }}
>
    <ProductCard />
</PostHogCaptureOnViewed>
```

**Tracking multiple children:**

Use `trackAllChildren` to track each child element separately. This is useful for galleries or lists where you want to know which specific items were viewed:

React

PostHog AI

```jsx
<PostHogCaptureOnViewed
    name="product-gallery"
    properties={{ gallery_type: 'featured' }}
    trackAllChildren
>
    <ProductCard id="1" />
    <ProductCard id="2" />
    <ProductCard id="3" />
</PostHogCaptureOnViewed>
```

When `trackAllChildren` is enabled, each child element sends its own event with a `child_index` property indicating its position.

**Custom intersection observer options:**

You can customize when elements are considered "viewed" by passing options to the `IntersectionObserver`:

React

PostHog AI

```jsx
<PostHogCaptureOnViewed
    name="footer"
    observerOptions={{
        threshold: 0.5,  // Element is 50% visible
        rootMargin: '0px'
    }}
>
    <Footer />
</PostHogCaptureOnViewed>
```

The component passes all other props to the wrapper `div`, so you can add styling, classes, or other HTML attributes as needed.

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two ways to implement feature flags in React:

1.  Using hooks.
2.  Using the `<PostHogFeature>` component.

### Method 1: Using hooks

PostHog provides several hooks to make it easy to use feature flags in your React app.

| Hook | Description |
| --- | --- |
| useFeatureFlagEnabled | Returns a boolean indicating whether the feature flag is enabled. This sends a $feature_flag_called event. |
| useFeatureFlagVariantKey | Returns the variant key of the feature flag. This sends a $feature_flag_called event. |
| useActiveFeatureFlags | Returns an array of active feature flags. This does not send a $feature_flag_called event. |
| useFeatureFlagPayload | Returns the payload of the feature flag. This does not send a $feature_flag_called event. Always use this with useFeatureFlagEnabled or useFeatureFlagVariantKey. |

#### Example 1: Using a boolean feature flag

React

PostHog AI

```jsx
import { useFeatureFlagEnabled } from '@posthog/react'
function App() {
  const showWelcomeMessage = useFeatureFlagEnabled('flag-key')
  const payload = useFeatureFlagPayload('flag-key')
  return (
    <div className="App">
      {
        showWelcomeMessage ? (
          <div>
            <h1>Welcome!</h1>
            <p>Thanks for trying out our feature flags.</p>
          </div>
        ) : (
          <div>
            <h2>No welcome message</h2>
            <p>Because the feature flag evaluated to false.</p>
          </div>
        )
      }
    </div>
  );
}
export default App;
```

#### Example 2: Using a multivariate feature flag

React

PostHog AI

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
      {
        welcomeMessage ? (
          <div>
            <h1>{welcomeMessage}</h1>
            <p>Thanks for trying out our feature flags.</p>
          </div>
        ) : (
          <div>
            <h2>No welcome message</h2>
            <p>Because the feature flag evaluated to false.</p>
          </div>
        )
      }
    </div>
  );
}
export default App;
```

#### Example 3: Using a flag payload

**Payload hook**

The `useFeatureFlagPayload` hook does *not* send a [`$feature_flag_called`](https://posthog.com/docs/experiments/new-experimentation-engine#experiment-exposure) event, which is required for the experiment to be tracked. To ensure the exposure event is sent, you should **always** use the `useFeatureFlagPayload` hook with either the `useFeatureFlagEnabled` or `useFeatureFlagVariantKey` hook.

React

PostHog AI

```jsx
import { useFeatureFlagPayload } from '@posthog/react'
function App() {
  const variant = useFeatureFlagEnabled('show-welcome-message')
  const payload = useFeatureFlagPayload('show-welcome-message')
    return (
                <>
                {
                    variant ? (
                        <div className="welcome-message">
                            <h2>{payload?.welcomeTitle}</h2>
                            <p>{payload?.welcomeMessage}</p>
                        </div>
                    ) : <div>
                        <h2>No custom welcome message</h2>
                        <p>Because the feature flag evaluated to false.</p>
                    </div>
                }
        </>
    )
}
```

### Method 2: Using the PostHogFeature component

The `PostHogFeature` component simplifies code by handling feature flag related logic.

It also automatically captures metrics, like how many times a user interacts with this feature.

> **Note:** You still need the [`PostHogProvider`](/docs/libraries/react.md#installation) at the top level for this to work.

Here is an example:

React

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

-   The `match` on the component can be either `true`, or the variant key, to match on a specific variant.

-   If you also want to show a default message, you can pass these in the `fallback` attribute.

If you wish to customise logic around when the component is considered visible, you can pass in `visibilityObserverOptions` to the feature. These take the same options as the [IntersectionObserver API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API). By default, we use a threshold of 0.1.

#### Payloads

If your flag has a payload, you can pass a function to children whose first argument is the payload. For example:

React

PostHog AI

```jsx
import { PostHogFeature } from '@posthog/react'
function App() {
    return (
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
    )
}
```

### Request timeout

You can configure the `feature_flag_request_timeout_ms` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked in the case when PostHog's servers are too slow to respond. By default, this is set at 3 seconds.

JavaScript

PostHog AI

```javascript
posthog.init('<ph_project_token>', {
  api_host: 'https://us.i.posthog.com',
  defaults: '2026-01-30'
  feature_flag_request_timeout_ms: 3000 // Time in milliseconds. Default is 3000 (3 seconds).
}
)
```

### Error handling

When using the PostHog SDK, it's important to handle potential errors that may occur during feature flag operations. Here's an example of how to wrap PostHog SDK methods in an error handler:

JavaScript

PostHog AI

```javascript
function handleFeatureFlag(client, flagKey, distinctId) {
    try {
        const isEnabled = client.isFeatureEnabled(flagKey, distinctId);
        console.log(`Feature flag '${flagKey}' for user '${distinctId}' is ${isEnabled ? 'enabled' : 'disabled'}`);
        return isEnabled;
    } catch (error) {
        console.error(`Error fetching feature flag '${flagKey}': ${error.message}`);
        // Optionally, you can return a default value or throw the error
        // return false; // Default to disabled
        throw error;
    }
}
// Usage example
try {
    const flagEnabled = handleFeatureFlag(client, 'new-feature', 'user-123');
    if (flagEnabled) {
        // Implement new feature logic
    } else {
        // Implement old feature logic
    }
} catch (error) {
    // Handle the error at a higher level
    console.error('Feature flag check failed, using default behavior');
    // Implement fallback logic
}
```

### Bootstrapping flags

Since there is a delay between initializing PostHog and fetching feature flags, feature flags are not always available immediately. This makes them unusable if you want to do something like redirecting a user to a different page based on a feature flag.

To have your feature flags available immediately, you can initialize PostHog with precomputed values until it has had a chance to fetch them. This is called bootstrapping. After the SDK fetches feature flags from PostHog, it will use those flag values instead of bootstrapped ones.

For details on how to implement bootstrapping, see our [bootstrapping guide](/docs/feature-flags/bootstrapping.md).

## Experiments (A/B tests)

Since [experiments](/docs/experiments/manual.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

React

PostHog AI

```jsx
// You can either use the `useFeatureFlagVariantKey` hook,
// or you can use the feature flags component - /docs/libraries/react#feature-flags-react-component
// Method one: using the useFeatureFlagVariantKey hook
import { useFeatureFlagVariantKey } from '@posthog/react'
function App() {
    const variant = useFeatureFlagVariantKey('experiment-feature-flag-key')
    if (variant == 'variant-name') {
        // do something
    }
}
// Method two: using the feature flags component
import { PostHogFeature } from '@posthog/react'
function App() {
    return (
        <PostHogFeature flag='experiment-feature-flag-key' match={'variant-name'}>
            <!-- the component to show -->
        </PostHogFeature>
    )
}
// You can also test your code by overriding the feature flag:
// e.g., posthog.featureFlags.overrideFeatureFlags({ flags: {'experiment-feature-flag-key': 'test'}})
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better