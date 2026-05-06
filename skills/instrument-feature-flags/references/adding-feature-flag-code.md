# Adding feature flag code - Docs

Once you've created your feature flag in PostHog, the next step is to add your code:

## Web

### Boolean feature flags

Web

PostHog AI

```javascript
if (posthog.isFeatureEnabled('flag-key') ) {
    // Do something differently for this user
    // Optional: fetch the payload
    const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
}
```

### Multivariate feature flags

Web

PostHog AI

```javascript
if (posthog.getFeatureFlag('flag-key')  == 'variant-key') { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
}
```

### Ensuring flags are loaded before usage

Every time a user loads a page, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in your chosen persistence option (local storage by default).

This means that for most pages, the feature flags are available immediately — **except for the first time a user visits**.

To handle this, you can use the `onFeatureFlags` callback to wait for the feature flag request to finish:

Web

PostHog AI

```javascript
posthog.onFeatureFlags(function (flags, flagVariants, { errorsLoading }) {
    // feature flags are guaranteed to be available at this point
    if (posthog.isFeatureEnabled('flag-key')) {
        // do something
    }
})
```

#### Callback parameters

The `onFeatureFlags` callback receives the following parameters:

-   `flags: string[]`: An object containing the feature flags that apply to the user.

-   `flagVariants: Record<string, string | boolean>`: An object containing the variants that apply to the user.

-   `{ errorsLoading }: { errorsLoading?: boolean }`: An object containing a boolean indicating if an error occurred during the request to load the feature flags. This is `true` if the request timed out or if there was an error. It will be `false` or `undefined` if the request was successful.

You won't usually need to use these, but they are useful if you want to be extra careful about feature flags not being loaded yet because of a network error and/or a network timeout (see `feature_flag_request_timeout_ms`).

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

Web

PostHog AI

```javascript
posthog.reloadFeatureFlags()
```

### Overriding server properties

Sometimes, you might want to evaluate feature flags using properties that haven't been ingested yet, or were set incorrectly earlier. You can do so by setting properties the flag depends on with these calls:

Web

PostHog AI

```javascript
posthog.setPersonPropertiesForFlags({'property1': 'value', property2: 'value2'})
```

> **Note:** These are set for the entire session. Successive calls are additive: all properties you set are combined together and sent for flag evaluation.

Whenever you set these properties, we also trigger a reload of feature flags to ensure we have the latest values. You can disable this by passing in the optional parameter for reloading:

Web

PostHog AI

```javascript
posthog.setPersonPropertiesForFlags({'property1': 'value', property2: 'value2'}, false)
```

At any point, you can reset these properties by calling `resetPersonPropertiesForFlags`:

Web

PostHog AI

```javascript
posthog.resetPersonPropertiesForFlags()
```

The same holds for [group](/manual/group-analytics.md) properties:

Web

PostHog AI

```javascript
// set properties for a group
posthog.setGroupPropertiesForFlags({'company': {'property1': 'value', property2: 'value2'}})
// reset properties for a given group:
posthog.resetGroupPropertiesForFlags('company')
// reset properties for all groups:
posthog.resetGroupPropertiesForFlags()
```

> **Note:** You don't need to add the group names here, since these properties are automatically attached to the current group (set via `posthog.group()`). When you change the group, these properties are reset.

#### Automatic overrides

Whenever you call `posthog.identify` with person properties, we automatically add these properties to flag evaluation calls to help determine the correct flag values. The same is true for when you call `posthog.group()`.

#### Default overridden properties

By default, we always override some properties based on the user IP address.

The list of properties that this overrides:

1.  `$geoip_city_name`
2.  `$geoip_country_name`
3.  `$geoip_country_code`
4.  `$geoip_continent_name`
5.  `$geoip_continent_code`
6.  `$geoip_postal_code`
7.  `$geoip_time_zone`

This enables any geolocation-based flags to work without manually setting these properties.

### Request timeout

You can configure the `feature_flag_request_timeout_ms` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked in the case when PostHog's servers are too slow to respond. By default, this is set at 3 seconds.

JavaScript

PostHog AI

```javascript
posthog.init('<ph_project_token>', {
  api_host: 'https://us.i.posthog.com',
  defaults: '2026-01-30'
  feature_flag_request_timeout_ms: 3000 // Time in milliseconds. Default is 3000 (3 seconds).
})
```

### Feature flag error handling

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

## React

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

## Node.js

There are two steps to implement feature flags in Node:

### Step 1: Evaluate flags once

Call `client.evaluateFlags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Node.js

PostHog AI

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user')
if (flags.isEnabled('flag-key')) {
    // Do something differently for this user
    // Optional: fetch the payload
    const matchedFlagPayload = flags.getFlagPayload('flag-key')
}
```

#### Multivariate feature flags

Node.js

PostHog AI

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user')
const enabledVariant = flags.getFlag('flag-key')
if (enabledVariant === 'variant-key') { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    const matchedFlagPayload = flags.getFlagPayload('flag-key')
}
```

`flags.getFlag()` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `undefined` when the flag wasn't returned by the evaluation.

> **Note:** `client.isFeatureEnabled()`, `client.getFeatureFlag()`, `client.getFeatureFlagPayload()`, and `capture({ sendFeatureFlags: true })` still work during the migration period, but they're deprecated. Prefer `evaluateFlags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Node.js

PostHog AI

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user')
if (flags.isEnabled('flag-key')) {
    // Do something differently for this user
}
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    flags,
})
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

Node.js

PostHog AI

```javascript
// Attach only flags accessed with isEnabled() or getFlag() before this call
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags.onlyAccessed(),
})
// Attach only specific flags
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags.only(['checkout-flow', 'new-dashboard']),
})
```

`onlyAccessed()` is order-dependent. If you call it before accessing any flags with `isEnabled()` or `getFlag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Node.js

PostHog AI

```javascript
client.capture({
    distinctId: 'distinct_id_of_your_user',
    event: 'event_name',
    properties: {
        // Replace feature-flag-key with your flag key and 'variant-key' with the key of your variant
        '$feature/feature-flag-key': 'variant-key',
    },
})
```

### Evaluating only specific flags

By default, `evaluateFlags()` evaluates every flag for the user. If you only need a few flags, pass `flagKeys` to request only those flags:

Node.js

PostHog AI

```javascript
const flags = await client.evaluateFlags('distinct_id_of_your_user', {
    flagKeys: ['checkout-flow', 'new-dashboard'],
})
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `evaluateFlags()`, the SDK sends this event when you call `flags.isEnabled()` or `flags.getFlag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.getFlagPayload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `onlyAccessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Node.js

PostHog AI

```javascript
const flags = await client.evaluateFlags('distinct_id_of_the_user', {
    personProperties: {
        property_name: 'value',
    },
    groups: {
        your_group_type: 'your_group_id',
        another_group_type: 'your_group_id',
    },
    groupProperties: {
        your_group_type: {
            group_property_name: 'value',
        },
        another_group_type: {
            group_property_name: 'value',
        },
    },
})
if (flags.isEnabled('flag-key')) {
    // Do something differently for this user
}
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Request timeout

You can configure the `feature_flag_request_timeout_ms` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked if PostHog's servers are too slow to respond. By default, this is set to 3 seconds.

JavaScript

PostHog AI

```javascript
const client = new PostHog('<ph_project_token>', {
    api_host: 'https://us.i.posthog.com',
    feature_flag_request_timeout_ms: 3000, // Time in milliseconds. Defaults to 3000 (3 seconds).
})
```

## Python

There are two steps to implement feature flags in Python:

### Step 1: Evaluate flags once

Call `posthog.evaluate_flags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Python

PostHog AI

```python
flags = posthog.evaluate_flags("distinct_id_of_your_user")
if flags.is_enabled("flag-key"):
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flags.get_flag_payload("flag-key")
```

#### Multivariate feature flags

Python

PostHog AI

```python
flags = posthog.evaluate_flags("distinct_id_of_your_user")
enabled_variant = flags.get_flag("flag-key")
if enabled_variant == "variant-key":  # replace "variant-key" with the key of your variant
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flags.get_flag_payload("flag-key")
```

`flags.get_flag()` returns the variant string for multivariate flags, `True` for enabled boolean flags, `False` for disabled flags, and `None` when the flag wasn't returned by the evaluation.

> **Note:** `posthog.feature_enabled()`, `posthog.get_feature_flag()`, `posthog.get_feature_flag_payload()`, and `posthog.capture(send_feature_flags=True)` still work during the migration period, but they're deprecated. Prefer `posthog.evaluate_flags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Python

PostHog AI

```python
flags = posthog.evaluate_flags("distinct_id_of_your_user")
if flags.is_enabled("flag-key"):
    # Do something differently for this user
    pass
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_your_user",
    flags=flags,
)
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

Python

PostHog AI

```python
# Attach only flags accessed with is_enabled() or get_flag() before this call
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_your_user",
    flags=flags.only_accessed(),
)
# Attach only specific flags
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_your_user",
    flags=flags.only(["checkout-flow", "new-dashboard"]),
)
```

`only_accessed()` is order-dependent. If you call it before accessing any flags with `is_enabled()` or `get_flag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Python

PostHog AI

```python
posthog.capture(
    "event_name",
    distinct_id="distinct_id_of_the_user",
    properties={
        # Replace feature-flag-key with your flag key and "variant-key" with the key of your variant
        "$feature/feature-flag-key": "variant-key",
    },
)
```

### Evaluating only specific flags

By default, `posthog.evaluate_flags()` evaluates every flag for the user. If you only need a few flags, pass `flag_keys` to request only those flags:

Python

PostHog AI

```python
flags = posthog.evaluate_flags(
    "distinct_id_of_your_user",
    flag_keys=["checkout-flow", "new-dashboard"],
)
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `posthog.evaluate_flags()`, the SDK sends this event when you call `flags.is_enabled()` or `flags.get_flag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.get_flag_payload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `only_accessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Python

PostHog AI

```python
flags = posthog.evaluate_flags(
    "distinct_id_of_the_user",
    person_properties={"property_name": "value"},
    groups={
        "your_group_type": "your_group_id",
        "another_group_type": "your_group_id",
    },
    group_properties={
        "your_group_type": {"group_property_name": "value"},
        "another_group_type": {"group_property_name": "value"},
    },
)
if flags.is_enabled("flag-key"):
    # Do something differently for this user
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Request timeout

You can configure the `feature_flags_request_timeout_seconds` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked if PostHog's servers are too slow to respond. By default, this is set to 3 seconds.

Python

PostHog AI

```python
posthog = Posthog(
    "<ph_project_token>",
    host="https://us.i.posthog.com",
    feature_flags_request_timeout_seconds=3,  # Time in seconds. Defaults to 3.
)
```

## PHP

There are 2 steps to implement feature flags in PHP:

### Step 1: Evaluate the feature flag value

#### Boolean feature flags

PHP

PostHog AI

```php
$isMyFlagEnabledForUser = PostHog::isFeatureEnabled('flag-key', 'distinct_id_of_your_user')
if ($isMyFlagEnabledForUser) {
    // Do something differently for this user
}
```

#### Multivariate feature flags

PHP

PostHog AI

```php
$enabledVariant = PostHog::getFeatureFlag('flag-key', 'distinct_id_of_your_user')
if ($enabledVariant === 'variant-key') { # replace 'variant-key' with the key of your variant
    # Do something differently for this user
}
```

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Include the `$feature/feature_flag_name` property

In the event properties, include `$feature/feature_flag_name: variant_key`:

PHP

PostHog AI

```php
PostHog::capture([
  'distinctId' => 'distinct_id_of_your_user',
  'event' => 'event_name',
  'properties' => [
    '$feature/feature-flag-key' => 'variant-key' // replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
  ]
]);
```

#### Method 2: Set `send_feature_flags` to `true`

The `capture()` method has an optional argument `send_feature_flags`, which is set to `false` by default. By setting this to `true`, feature flag information will automatically be sent with the event.

Note that by doing this, PostHog will make an additional request to fetch feature flag information before capturing the event. So this method is only recommended if you don't mind the extra API call and delay.

PHP

PostHog AI

```php
PostHog::capture([
  'distinctId' => 'distinct_id_of_your_user',
  'event' => 'event_name',
  'send_feature_flags' => true
]);
```

### Fetching all flags for a user

You can fetch all flag values for a single user by calling `getAllFlags()`.

This is useful when you need to fetch multiple flag values and don't want to make multiple requests.

PHP

PostHog AI

```php
PostHog::getAllFlags('distinct_id_of_your_user')
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enable PostHog to know when a flag was accessed by a user and thus provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. By default, we send a these event when:

1.  You call `getFeatureFlag()` or `isFeatureEnabled()`, AND
2.  It's a new user, or the value of the flag has changed.

> *Note:* Tracking whether it's a new user or if a flag value has changed happens in a local cache. This means that if you reinitialize the PostHog client, the cache resets as well – causing `$feature_flag_called` events to be sent again when calling `getFeatureFlag` or `isFeatureEnabled`. PostHog is built to handle this, and so duplicate `$feature_flag_called` events won't affect your analytics.

You can disable automatically capturing `$feature_flag_called` events. For example, when you don't need the analytics, or it's being called at such a high volume that sending events slows things down.

To disable it, set the `sendFeatureFlagEvents` argument in your function call, like so:

PHP

PostHog AI

```php
$isMyFlagEnabledForUser = PostHog::isFeatureEnabled(
    key: 'flag-key',
    distinctId: 'distinct_id_of_your_user',
    sendFeatureFlagEvents: false
)
```

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

PHP

PostHog AI

```php
PostHog::getFeatureFlag(
    'flag-key',
    'distinct_id_of_the_user',
    [
        'your_group_type' => 'your_group_id',
        'another_group_type' => 'your_group_id'
    ], // groups
    ['property_name' => 'value'], // person properties
    [
        'your_group_type' => ['group_property_name' => 'value'],
        'another_group_type' => ['group_property_name' => 'value']
    ], // group properties
    false, // onlyEvaluateLocally, Optional. Defaults to false.
    true // sendFeatureFlagEvents
);
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Request timeout

You can configure the `feature_flag_request_timeout_ms` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked in the case when PostHog's servers are too slow to respond. By default, this is set at 3 seconds.

PHP

PostHog AI

```php
PostHog::init("<ph_project_token>",
  [
    'host' => 'https://us.i.posthog.com',
    'feature_flag_request_timeout_ms' => 3000 // Time in milliseconds. Default is 3000 (3 seconds).
  ]
);
```

### Error handling

When using the PostHog SDK, it's important to handle potential errors that may occur during feature flag operations. Here's an example of how to wrap PostHog SDK methods in an error handler:

PHP

PostHog AI

```php
function handleFeatureFlag($client, $flagKey, $distinctId) {
    try {
        $isEnabled = $client->isFeatureEnabled($flagKey, $distinctId);
        echo "Feature flag '$flagKey' for user '$distinctId' is " . ($isEnabled ? 'enabled' : 'disabled') . "\n";
        return $isEnabled;
    } catch (Exception $e) {
        echo "Error fetching feature flag '$flagKey': " . $e->getMessage() . "\n";
        // Optionally, you can return a default value or throw the error
        // return false; // Default to disabled
        throw $e;
    }
}
// Usage example
try {
    $flagEnabled = handleFeatureFlag($client, 'new-feature', 'user-123');
    if ($flagEnabled) {
        // Implement new feature logic
    } else {
        // Implement old feature logic
    }
} catch (Exception $e) {
    // Handle the error at a higher level
    echo 'Feature flag check failed, using default behavior';
    // Implement fallback logic
}
```

## Ruby

There are 2 steps to implement feature flags in Ruby:

### Step 1: Evaluate the feature flag value

#### Boolean feature flags

Ruby

PostHog AI

```ruby
is_my_flag_enabled = posthog.is_feature_enabled('flag-key', 'distinct_id_of_your_user')
if is_my_flag_enabled
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = posthog.get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
end
```

#### Multivariate feature flags

Ruby

PostHog AI

```ruby
enabled_variant = posthog.get_feature_flag('flag-key', 'distinct_id_of_your_user')
if enabled_variant == 'variant-key' # replace 'variant-key' with the key of your variant
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = posthog.get_feature_flag_payload('variant-key', 'distinct_id_of_your_user')
end
```

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Include the `$feature/feature_flag_name` property

In the event properties, include `$feature/feature_flag_name: variant_key`:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    properties: {
        '$feature/feature-flag-key': 'variant-key', # replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
    }
})
```

#### Method 2: Set `send_feature_flags` to `true`

The `capture()` method has an optional argument `send_feature_flags`, which is set to `false` by default. This parameter controls whether feature flag information is sent with the event.

#### Basic usage

Setting `send_feature_flags` to `true` will include feature flag information with the event:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    send_feature_flags: true,
})
```

## Advanced usage (v3.1.0+)

As of version 3.1.0, `send_feature_flags` can also accept a hash for more granular control:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    send_feature_flags: {
        only_evaluate_locally: true,
        person_properties: { plan: 'premium' },
        group_properties: { org: { tier: 'enterprise' } }
    }
})
```

#### Performance considerations

-   **With local evaluation**: When [local evaluation](/docs/feature-flags/local-evaluation.md) is configured, setting `send_feature_flags: true` will **not** make additional server requests. Instead, it uses the locally cached feature flags, and it provides an interface for including person and/or group properties needed to evaluate the flags in the context of the event, if required.

-   **Without local evaluation**: PostHog will make an additional request to fetch feature flag information before capturing the event, which adds delay.

#### Breaking change in v3.1.0

Prior to version 3.1.0, feature flags were automatically sent with events when using local evaluation, even when `send_feature_flags` was not explicitly set. This behavior has been **removed** in v3.1.0 to be more predictable and explicit.

If you were relying on this automatic behavior, you must now explicitly set `send_feature_flags: true` to continue sending feature flags with your events.

### Fetching all flags for a user

You can fetch all flag values for a single user by calling `get_all_flags()` or `get_all_flags_and_payloads()`.

This is useful when you need to fetch multiple flag values and don't want to make multiple requests.

Ruby

PostHog AI

```ruby
posthog.get_all_flags('distinct_id_of_your_user')
posthog.get_all_flags_and_payloads('distinct_id_of_your_user')
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enable PostHog to know when a flag was accessed by a user and thus provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. By default, we send a these event when:

1.  You call `posthog.get_feature_flag()` or `posthog.is_feature_enabled()`, AND
2.  It's a new user, or the value of the flag has changed.

> *Note:* Tracking whether it's a new user or if a flag value has changed happens in a local cache. This means that if you reinitialize the PostHog client, the cache resets as well – causing `$feature_flag_called` events to be sent again when calling `get_feature_flag` or `is_feature_enabled`. PostHog is built to handle this, and so duplicate `$feature_flag_called` events won't affect your analytics.

You can disable automatically capturing `$feature_flag_called` events. For example, when you don't need the analytics, or it's being called at such a high volume that sending events slows things down.

To disable it, set the `send_feature_flag_events` argument in your function call, like so:

Ruby

PostHog AI

```ruby
is_my_flag_enabled = posthog.is_feature_enabled(
    'flag-key',
    'distinct_id_of_your_user',
    send_feature_flag_events: true)
```

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Ruby

PostHog AI

```ruby
posthog.get_feature_flag(
    'flag-key',
    'distinct_id_of_the_user',
    person_properties: {
        'property_name': 'value'
    },
    groups: {
        'your_group_type': 'your_group_id',
        'another_group_type': 'your_group_id',
    },
    group_properties: {
        'your_group_type': {
            'group_property_name': 'value'
        }
        'another_group_type': {
            'group_property_name': 'value'
        }
    },
)
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Request timeout

You can configure the `feature_flag_request_timeout_seconds` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked in the case when PostHog's servers are too slow to respond. By default, this is set at 3 seconds.

Ruby

PostHog AI

```ruby
posthog = PostHog::Client.new({
   # rest of your configuration...
   feature_flag_request_timeout_seconds: 3 # Time in seconds. Default is 3.
})
```

### Error handling

When using the PostHog SDK, it's important to handle potential errors that may occur during feature flag operations. Here's an example of how to wrap PostHog SDK methods in an error handler:

Ruby

PostHog AI

```ruby
def handle_feature_flag(client, flag_key, distinct_id)
    begin
        is_enabled = client.is_feature_enabled(flag_key, distinct_id)
        puts "Feature flag '#{flag_key}' for user '#{distinct_id}' is #{is_enabled ? 'enabled' : 'disabled'}"
        return is_enabled
    rescue => e
        puts "Error fetching feature flag '#{flag_key}': #{e.message}"
        # Optionally, you can return a default value or throw the error
        # return false # Default to disabled
        raise e
    end
end
# Usage example
try
    flag_enabled = handle_feature_flag(client, 'new-feature', 'user-123')
    if flag_enabled
        # Implement new feature logic
    else
        # Implement old feature logic
    end
rescue => e
    # Handle the error at a higher level
    puts 'Feature flag check failed, using default behavior'
    # Implement fallback logic
end
```

## Go

There are 2 steps to implement feature flags in Go:

### Step 1: Evaluate the feature flag value

#### Boolean feature flags

Go

PostHog AI

```go
isMyFlagEnabled, err := client.IsFeatureEnabled(posthog.FeatureFlagPayload{
    Key:        "flag-key",
    DistinctId: "distinct_id_of_your_user",
})
if err != nil {
    // Handle error (e.g. capture error and fallback to default behavior)
}
if isMyFlagEnabled == true {
    // Do something differently for this user
}
```

#### Multivariate feature flags

Go

PostHog AI

```go
enabledVariant, err := client.GetFeatureFlag(posthog.FeatureFlagPayload{
    Key:        "flag-key",
    DistinctId: "distinct_id_of_your_user",
})
if err != nil {
    // Handle error (e.g. capture error and fallback to default behavior)
}
if enabledVariant == "variant-key" { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
}
```

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Include the `$feature/feature_flag_name` property

In the event properties, include `$feature/feature_flag_name: variant_key`:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
  DistinctId: "distinct_id_of_your_user",
  Event:      "event_name",
  Properties: posthog.NewProperties().
    Set("$feature/feature-flag-key", "variant-key"), // replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
})
```

#### Method 2: Set `SendFeatureFlags` to `true`

The `Capture` struct has an optional field `SendFeatureFlags`, which is set to `false` by default. This parameter controls whether feature flag information is sent with the event.

#### Basic usage

Setting `SendFeatureFlags` to `true` will include feature flag information with the event:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
  DistinctId: "distinct_id_of_your_user",
  Event:      "event_name",
  SendFeatureFlags: true,
})
```

## Advanced usage (v1.6.1+)

As of version 1.6.1, `SendFeatureFlags` can also accept a `SendFeatureFlagsOptions` struct for more granular control:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
  DistinctId: "distinct_id_of_your_user",
  Event:      "event_name",
  SendFeatureFlags: posthog.SendFeatureFlagsOptions{
    OnlyEvaluateLocally: true,
    PersonProperties: map[string]interface{}{
      "plan": "premium",
    },
    GroupProperties: map[string]map[string]interface{}{
      "org": {
        "tier": "enterprise",
      },
    },
  },
})
```

#### Performance considerations

-   **With local evaluation**: When [local evaluation](/docs/feature-flags/local-evaluation.md) is configured, setting `SendFeatureFlags: true` will **not** make additional server requests. Instead, it uses the locally cached feature flags, and it provides an interface for including person and/or group properties needed to evaluate the flags in the context of the event, if required.

-   **Without local evaluation**: PostHog will make an additional request to fetch feature flag information before capturing the event, which adds delay.

#### Breaking change in v1.6.1

Prior to version 1.6.1, feature flags were automatically sent with events when using local evaluation, even when `SendFeatureFlags` was not explicitly set. This behavior has been **removed** in v1.6.1 to be more predictable and explicit.

If you were relying on this automatic behavior, you must now explicitly set `SendFeatureFlags: true` to continue sending feature flags with your events.

### Fetching all flags for a user

You can fetch all flag values for a single user by calling `GetAllFlags()`.

This is useful when you need to fetch multiple flag values and don't want to make multiple requests.

Go

PostHog AI

```go
featureVariants, err := client.GetAllFlags(posthog.FeatureFlagPayloadNoKey{
        DistinctId: "distinct_id_of_your_user",
})
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enable PostHog to know when a flag was accessed by a user and thus provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. By default, we send a these event when:

1.  You call `GetFeatureFlag()` or `IsFeatureEnabled()`, AND
2.  It's a new user, or the value of the flag has changed.

> *Note:* Tracking whether it's a new user or if a flag value has changed happens in a local cache. This means that if you reinitialize the PostHog client, the cache resets as well – causing `$feature_flag_called` events to be sent again when calling `GetFeatureFlag` or `IsFeatureEnabled`. PostHog is built to handle this, and so duplicate `$feature_flag_called` events won't affect your analytics.

You can disable automatically capturing `$feature_flag_called` events. For example, when you don't need the analytics, or it's being called at such a high volume that sending events slows things down.

To disable it (pre v1.6.1), set the `SendFeatureFlagEvents` argument in your function call, like so:

Go

PostHog AI

```go
sendFeatureFlags := false
isMyFlagEnabled, err := client.IsFeatureEnabled(posthog.FeatureFlagPayload{
    Key:                    "flag-key",
    DistinctId:             "distinct_id_of_your_user",
    SendFeatureFlagEvents:  &sendFeatureFlags,
})
```

Versions after v1.6.1 have this feature disabled by default.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Go

PostHog AI

```go
enabledVariant, err := client.GetFeatureFlag(
    FeatureFlagPayload{
        Key:        "flag-key",
        DistinctId: "distinct_id_of_the_user",
        Groups: posthog.NewGroups().
            Set("your_group_type", "your_group_id").
            Set("another_group_type", "your_group_id"),
        PersonProperties: posthog.NewProperties().
            Set("property_name", "value"),
        GroupProperties: map[string]map[string]interface{}{
            "your_group_type": {
                "group_property_name": "value",
            },
            "another_group_type": {
                "group_property_name": "value",
            },
        },
    },
)
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Request timeout

You can configure the `FeatureFlagRequestTimeout` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked in the case when PostHog's servers are too slow to respond. By default, this is set at 3 seconds.

Go

PostHog AI

```go
client, _ := posthog.NewWithConfig(
   os.Getenv("<ph_project_token>"),
   posthog.Config{
      PersonalApiKey:            "your personal API key", // Optional, but much more performant.  If this token is not supplied, then fetching feature flag values will be slower.
      Endpoint:                  "https://us.i.posthog.com",
      FeatureFlagRequestTimeout: 3 // Time in seconds. Default is 3.
   },
)
```

### Error handling

When using the PostHog SDK, it's important to handle potential errors that may occur during feature flag operations. Here's an example of how to wrap PostHog SDK methods in an error handler:

Go

PostHog AI

```go
func handleFeatureFlag(client *posthog.Client, flagKey string, distinctId string) {
    flag, err := client.GetFeatureFlag(posthog.FeatureFlagPayload{
        Key:        flagKey,
        DistinctId: distinctId,
    })
    if err != nil {
        // Handle the error appropriately
        log.Printf("Error fetching feature flag: %v", err)
        return
    }
    // Use the flag value as needed
    fmt.Printf("Feature flag '%s' for user '%s': %s\n", flagKey, distinctId, flag)
}
```

## React Native

There are two ways to implement feature flags in React Native:

1.  Using hooks.
2.  Loading the flag directly.

### Method 1: Using hooks

#### Example 1: Boolean feature flags

React Native

PostHog AI

```jsx
import { useFeatureFlag } from 'posthog-react-native'
const MyComponent = () => {
    const booleanFlag = useFeatureFlag('key-for-your-boolean-flag')
    if (booleanFlag === undefined) {
        // the response is undefined if the flags are being loaded
        return null
    }
    // Optional use the 'useFeatureFlagWithPayload' hook for fetching the feature flag payload
    return booleanFlag ? <Text>Testing feature 😄</Text> : <Text>Not Testing feature 😢</Text>
}
```

#### Example 2: Multivariate feature flags

React Native

PostHog AI

```jsx
import { useFeatureFlag } from 'posthog-react-native'
const MyComponent = () => {
    const multiVariantFeature = useFeatureFlag('key-for-your-multivariate-flag')
    if (multiVariantFeature === undefined) {
        // the response is undefined if the flags are being loaded
        return null
    } else if (multiVariantFeature === 'variant-name') { // replace 'variant-name' with the name of your variant
      // Do something
    }
    // Optional use the 'useFeatureFlagWithPayload' hook for fetching the feature flag payload
    return <div/>
}
```

### Method 2: Loading the flag directly

React Native

PostHog AI

```jsx
// Defaults to undefined if not loaded yet or if there was a problem loading
posthog.isFeatureEnabled('key-for-your-boolean-flag')
// Defaults to undefined if not loaded yet or if there was a problem loading
posthog.getFeatureFlag('key-for-your-boolean-flag')
// Multivariant feature flags are returned as a string
posthog.getFeatureFlag('key-for-your-multivariate-flag')
// Optional fetch the payload returns 'JsonType' or undefined if not loaded yet or if there was a problem loading
posthog.getFeatureFlagPayload('key-for-your-multivariate-flag')
```

### Ensuring flags are loaded before usage

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in the storage.

This means that for most screens, the feature flags are available immediately — **except for the first time a user visits**.

To handle this, you can use the `onFeatureFlags` callback to wait for the feature flag request to finish:

React Native

PostHog AI

```jsx
posthog.onFeatureFlags((flags) => {
  // feature flags are guaranteed to be available at this point
  if (posthog.isFeatureEnabled('flag-key')) {
    // do something
  }
})
```

### Reloading flags

PostHog loads feature flags when instantiated and refreshes whenever methods are called that affect the flag.

If want to manually trigger a refresh, you can call `reloadFeatureFlagsAsync()`:

React Native

PostHog AI

```jsx
posthog.reloadFeatureFlagsAsync().then((refreshedFlags) => console.log(refreshedFlags))
```

Or when you want to trigger the reload, but don't care about the result:

React Native

PostHog AI

```jsx
posthog.reloadFeatureFlags()
```

### Feature flag caching

The React Native SDK caches feature flag values in AsyncStorage. Cached values persist indefinitely with no TTL until updated by a successful API call. This enables offline support and reduces latency, but means **inactive users may see stale flag values** from their last session.

For example, if a user last opened your app when a flag was `false`, that value remains cached even after you roll it out to 100%. When they reopen the app, the SDK returns the cached `false` first, then fetches the fresh `true` value from the API.

To ensure fresh flag values:

React Native

PostHog AI

```jsx
// Force refresh on app start
await posthog.reloadFeatureFlagsAsync()
```

Or clear cached values for inactive users:

React Native

PostHog AI

```jsx
if (lastActiveDate < migrationDate) {
  posthog.reset() // Clears all cached data
}
```

### Request timeout

You can configure the `featureFlagsRequestTimeoutMs` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked in the case when PostHog's servers are too slow to respond. By default, this is set at 10 seconds.

React Native

PostHog AI

```jsx
export const posthog = new PostHog('<ph_project_token>', {
  // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
  host: 'https://us.i.posthog.com',
  featureFlagsRequestTimeoutMs: 10000 // Time in milliseconds. Default is 10000 (10 seconds).
})
```

### Error handling

When using the PostHog SDK, it's important to handle potential errors that may occur during feature flag operations. Here's an example of how to wrap PostHog SDK methods in an error handler:

React Native

PostHog AI

```jsx
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

### Overriding server properties

Sometimes, you might want to evaluate feature flags using properties that haven't been ingested yet, or were set incorrectly earlier. You can do so by setting properties the flag depends on with these calls:

React Native

PostHog AI

```jsx
posthog.setPersonPropertiesForFlags({'property1': 'value', property2: 'value2'})
```

Note that these are set for the entire session. Successive calls are additive: all properties you set are combined together and sent for flag evaluation.

Whenever you set these properties, we also trigger a reload of feature flags to ensure we have the latest values. You can disable this by passing in the optional parameter for reloading:

React Native

PostHog AI

```jsx
posthog.setPersonPropertiesForFlags({'property1': 'value', property2: 'value2'}, false)
```

At any point, you can reset these properties by calling `resetPersonPropertiesForFlags`:

React Native

PostHog AI

```jsx
posthog.resetPersonPropertiesForFlags()
```

The same holds for [group](/docs/product-analytics/group-analytics.md) properties:

React Native

PostHog AI

```jsx
// set properties for a group
posthog.setGroupPropertiesForFlags({'company': {'property1': 'value', property2: 'value2'}})
// reset properties for all groups:
posthog.resetGroupPropertiesForFlags()
```

> **Note:** You don't need to add the group names here, since these properties are automatically attached to the current group (set via `posthog.group()`). When you change the group, these properties are reset.

**Automatic overrides**

Whenever you call `posthog.identify` with person properties, we automatically add these properties to flag evaluation calls to help determine the correct flag values. The same is true for when you call `posthog.group()`.

**Default overridden properties**

By default, we always override some properties based on the user IP address.

The list of properties that this overrides:

1.  $geoip\_city\_name
2.  $geoip\_country\_name
3.  $geoip\_country\_code
4.  $geoip\_continent\_name
5.  $geoip\_continent\_code
6.  $geoip\_postal\_code
7.  $geoip\_time\_zone

This enables any geolocation-based flags to work without manually setting these properties.

## Android

### Boolean feature flags

Kotlin

PostHog AI

```kotlin
import com.posthog.PostHog
if (PostHog.isFeatureEnabled("flag-key")) {
    // Do something differently for this user
    // Optional: fetch the payload
    val matchedFlagPayload = PostHog.getFeatureFlagPayload("flag-key")
}
```

### Multivariate feature flags

Kotlin

PostHog AI

```kotlin
import com.posthog.PostHog
if (PostHog.getFeatureFlag("flag-key") == "variant-key") { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    val matchedFlagPayload = PostHog.getFeatureFlagPayload("flag-key")
}
```

### Ensuring flags are loaded before usage

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in the storage.

This means that for most screens, the feature flags are available immediately – **except for the first time a user visits**.

To handle this, you can use the `onFeatureFlags` callback to wait for the feature flag request to finish:

Kotlin

PostHog AI

```kotlin
import com.posthog.PostHog
import com.posthog.android.PostHogAndroidConfig
import com.posthog.PostHogOnFeatureFlags
// During SDK initialization
val config = PostHogAndroidConfig(apiKey = "<ph_project_token>").apply {
    onFeatureFlags = PostHogOnFeatureFlags {
        if (PostHog.isFeatureEnabled("flag-key")) {
            // do something
        }
    }
}
// And/Or manually the SDK is initialized
PostHog.reloadFeatureFlags {
    if (PostHog.isFeatureEnabled("flag-key")) {
        // do something
    }
}
```

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

Kotlin

PostHog AI

```kotlin
import com.posthog.PostHog
PostHog.reloadFeatureFlags()
```

## iOS

### Boolean feature flags

Swift

PostHog AI

```swift
if (PostHogSDK.shared.isFeatureEnabled("flag-key")) {
    // Do something differently for this user
    // Optional: fetch the payload
    let matchedFlagPayload = PostHogSDK.shared.getFeatureFlagPayload("flag-key")
}
```

### Multivariate feature flags

Swift

PostHog AI

```swift
if (PostHogSDK.shared.getFeatureFlag("flag-key") as? String == "variant-key") { // replace "variant-key" with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    let matchedFlagPayload = PostHogSDK.shared.getFeatureFlagPayload("flag-key")
}
```

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

Swift

PostHog AI

```swift
PostHogSDK.shared.reloadFeatureFlags()
```

### Ensuring flags are loaded before usage

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in the storage.

This means that for most screens, the feature flags are available immediately – **except for the first time a user visits**.

To handle this, you can use the `didReceiveFeatureFlags` notification to wait for the feature flag request to finish:

Swift

PostHog AI

```swift
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        // register for `didReceiveFeatureFlags` notification before SDK initialization
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(receiveFeatureFlags),
            name: PostHogSDK.didReceiveFeatureFlags,
            object: nil
        )
        let POSTHOG_PROJECT_TOKEN = "<ph_project_token>"
        // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
        let POSTHOG_HOST = "https://us.i.posthog.com"
        let config = PostHogConfig(projectToken: POSTHOG_PROJECT_TOKEN, host: POSTHOG_HOST)
        PostHogSDK.shared.setup(config)
        return true
    }
    // The "receiveFeatureFlags" method will be called when the SDK receives the feature flags from the server.
    @objc func receiveFeatureFlags() {
        print("receiveFeatureFlags called")
    }
}
```

Alternatively, you can use the completion block of the `reloadFeatureFlags(_:)` method. This allows you to execute logic immediately after the flags are reloaded:

Swift

PostHog AI

```swift
// Reload feature flags and check if a specific feature is enabled
PostHogSDK.shared.reloadFeatureFlags {
    if PostHogSDK.shared.isFeatureEnabled("flag-key") {
        // do something
    }
}
```

## Flutter

### Boolean feature flags

Dart

PostHog AI

```dart
if (await Posthog().isFeatureEnabled('flag-key')) {
  // Do something differently for this user
  // Optional: fetch the payload
  final matchedFlagPayload = await Posthog().getFeatureFlagPayload('flag-key');
}
```

### Multivariate feature flags

Dart

PostHog AI

```dart
if (await Posthog().getFeatureFlag('flag-key') == 'variant-key') { // replace 'variant-key' with the key of your variant
  // Do something differently for this user
  // Optional: fetch the payload
  final matchedFlagPayload = await Posthog().getFeatureFlagPayload('flag-key');
}
```

### Ensuring flags are loaded before usage

> To use the `onFeatureFlags` callback, you must [set up the SDK manually](#installation) by disabling the `com.posthog.posthog.AUTO_INIT` mode.

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in the storage.

This means that for most screens, the feature flags are available immediately – **except for the first time a user visits**.

To handle this, you can use the `onFeatureFlags` callback in your config to be notified when flags are loaded:

Dart

PostHog AI

```dart
final config = PostHogConfig('<ph_project_token>');
config.host = 'https://us.i.posthog.com';
config.onFeatureFlags = () async {
  if (await Posthog().isFeatureEnabled('flag-key')) {
    // do something
  }
};
await Posthog().setup(config);
```

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

Dart

PostHog AI

```dart
await Posthog().reloadFeatureFlags();
```

## Java

### Boolean feature flags

Java

PostHog AI

```java
if (posthog.isFeatureEnabled("distinct_id_of_your_user", "flag-key")) {
    // Do something differently for this user
    // Optional: fetch the payload
    Object matchedFlagPayload = posthog.getFeatureFlagPayload("distinct_id_of_your_user", "flag-key");
}
```

### Multivariate feature flags

Java

PostHog AI

```java
if ("variant-key".equals(posthog.getFeatureFlag("distinct_id_of_your_user", "flag-key"))) { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    Object matchedFlagPayload = posthog.getFeatureFlagPayload("distinct_id_of_your_user", "flag-key");
}
```

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Java

PostHog AI

```java
import com.posthog.server.PostHogFeatureFlagOptions;
posthog.getFeatureFlag(
    "distinct_id_of_the_user",
    "flag-key",
    PostHogFeatureFlagOptions
        .builder()
        .defaultValue(false)
        .group("your_group_type", "your_group_id")
        .group("another_group_type", "your_group_id")
        .groupProperty("your_group_type", "group_property_name", "value")
        .groupProperty("another_group_type", "group_property_name", "value")
        .personProperty("property_name", "value")
        .build());
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

## Rust

There are 2 steps to implement feature flags in Rust:

### Step 1: Evaluate the feature flag value

#### Boolean feature flags

Rust

PostHog AI

```rust
let is_enabled = client.is_feature_enabled(
    "flag-key".to_string(),
    "distinct_id_of_your_user".to_string(),
    None, // groups
    None, // person_properties
    None, // group_properties
).await.unwrap();
if is_enabled {
    // Do something differently for this user
}
```

#### Multivariate feature flags

Rust

PostHog AI

```rust
use posthog_rs::FlagValue;
match client.get_feature_flag(
    "flag-key".to_string(),
    "distinct_id_of_your_user".to_string(),
    None, // groups
    None, // person_properties
    None, // group_properties
).await.unwrap() {
    Some(FlagValue::String(variant)) => {
        if variant == "variant-key" {
            // Do something for this variant
        }
    }
    Some(FlagValue::Boolean(enabled)) => {
        // Handle boolean flag
    }
    None => {
        // Flag not found or disabled
    }
}
```

### Step 2: Include feature flag information in your events

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Include the `$feature/feature_flag_name` property

In the event properties, include `$feature/feature_flag_name: variant_key`:

Rust

PostHog AI

```rust
let mut event = Event::new("event_name", "distinct_id_of_your_user");
event.insert_prop("$feature/feature-flag-key", "variant-key").unwrap();
client.capture(event).unwrap();
```

#### Method 2: Fetch and include all flags

Rust

PostHog AI

```rust
let (flags, _) = client.get_feature_flags(
    "distinct_id_of_your_user".to_string(),
    None, None, None
).await.unwrap();
let mut event = Event::new("event_name", "distinct_id_of_your_user");
for (key, value) in flags {
    let prop_key = format!("$feature/{}", key);
    match value {
        FlagValue::Boolean(b) => event.insert_prop(&prop_key, b).unwrap(),
        FlagValue::String(s) => event.insert_prop(&prop_key, s).unwrap(),
    };
}
client.capture(event).unwrap();
```

### Fetching all flags for a user

You can fetch all flag values for a single user by calling `get_feature_flags()`.

This is useful when you need to fetch multiple flag values and don't want to make multiple requests.

Rust

PostHog AI

```rust
let (flags, payloads) = client.get_feature_flags(
    "distinct_id_of_your_user".to_string(),
    None, // groups
    None, // person_properties
    None, // group_properties
).await.unwrap();
for (key, value) in flags {
    println!("Flag {}: {:?}", key, value);
}
```

### Feature flag payloads

You can retrieve additional data associated with a feature flag using payloads:

Rust

PostHog AI

```rust
let payload = client.get_feature_flag_payload(
    "flag-key".to_string(),
    "distinct_id_of_your_user".to_string()
).await.unwrap();
if let Some(data) = payload {
    println!("Payload: {}", data);
}
```

### With person properties

You can include person properties for more targeted flag evaluation:

Rust

PostHog AI

```rust
use std::collections::HashMap;
use serde_json::json;
let mut person_props = HashMap::new();
person_props.insert("plan".to_string(), json!("enterprise"));
person_props.insert("country".to_string(), json!("US"));
let flag = client.get_feature_flag(
    "premium-feature".to_string(),
    "distinct_id_of_your_user".to_string(),
    None, // groups
    Some(person_props),
    None, // group_properties
).await.unwrap();
```

### With groups (B2B)

For B2B applications with group-based flags:

Rust

PostHog AI

```rust
use std::collections::HashMap;
use serde_json::json;
let mut groups = HashMap::new();
groups.insert("company".to_string(), "company-123".to_string());
let mut group_props = HashMap::new();
let mut company_props = HashMap::new();
company_props.insert("size".to_string(), json!(500));
group_props.insert("company".to_string(), company_props);
let flag = client.get_feature_flag(
    "b2b-feature".to_string(),
    "distinct_id_of_your_user".to_string(),
    Some(groups),
    None, // person_properties
    Some(group_props),
).await.unwrap();
```

### Blocking client

If you're using the blocking client (with `default-features = false`), the API is the same but without `.await`:

Rust

PostHog AI

```rust
let is_enabled = client.is_feature_enabled(
    "flag-key".to_string(),
    "distinct_id_of_your_user".to_string(),
    None, None, None
).unwrap();
```

### Error handling

When using the PostHog SDK, handle potential errors that may occur during feature flag operations:

Rust

PostHog AI

```rust
match client.get_feature_flag(
    "flag-key".to_string(),
    "distinct_id_of_your_user".to_string(),
    None, None, None
).await {
    Ok(Some(value)) => {
        // Use the flag value
        println!("Flag value: {:?}", value);
    }
    Ok(None) => {
        // Flag not found or disabled
        println!("Flag not found");
    }
    Err(e) => {
        // Handle the error appropriately
        eprintln!("Error fetching feature flag: {}", e);
        // Fall back to default behavior
    }
}
```

## Elixir

There are two steps to implement feature flags in Elixir:

### Step 1: Evaluate flags once

Call `PostHog.FeatureFlags.evaluate_flags/1` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Elixir

PostHog AI

```elixir
{:ok, snapshot} = PostHog.FeatureFlags.evaluate_flags("distinct_id_of_your_user")
if PostHog.FeatureFlags.Evaluations.enabled?(snapshot, "flag-key") do
  # Do something differently for this user
  # Optional: fetch the payload
  payload = PostHog.FeatureFlags.Evaluations.get_flag_payload(snapshot, "flag-key")
end
```

#### Multivariate feature flags

Elixir

PostHog AI

```elixir
{:ok, snapshot} = PostHog.FeatureFlags.evaluate_flags("distinct_id_of_your_user")
enabled_variant = PostHog.FeatureFlags.Evaluations.get_flag(snapshot, "flag-key")
if enabled_variant == "variant-key" do
  # Do something differently for this user
  # Optional: fetch the payload
  payload = PostHog.FeatureFlags.Evaluations.get_flag_payload(snapshot, "flag-key")
end
```

`PostHog.FeatureFlags.Evaluations.get_flag/2` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `nil` when the flag wasn't returned by the evaluation.

> **Note:** `PostHog.FeatureFlags.check/2`, `PostHog.FeatureFlags.check!/2`, `PostHog.FeatureFlags.get_feature_flag_result/2`, and `PostHog.FeatureFlags.get_feature_flag_result!/2` still work during the migration period, but they're deprecated. Prefer `evaluate_flags/1` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Put the evaluated flags snapshot in context

Put the same `snapshot` object that you used for branching into context. Subsequent captures from the same process attach the exact flag values from that evaluation and don't make another `/flags` request.

Elixir

PostHog AI

```elixir
{:ok, snapshot} = PostHog.FeatureFlags.evaluate_flags("distinct_id_of_your_user")
if PostHog.FeatureFlags.Evaluations.enabled?(snapshot, "flag-key") do
  # Do something differently for this user
end
PostHog.FeatureFlags.set_in_context(snapshot)
PostHog.capture("event_name", %{distinct_id: "distinct_id_of_your_user"})
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, put a filtered snapshot in context:

Elixir

PostHog AI

```elixir
{:ok, snapshot} = PostHog.FeatureFlags.evaluate_flags("distinct_id_of_your_user")
# Attach only flags accessed with enabled?/2, get_flag/2, or get_flag_payload/2 before this call
PostHog.FeatureFlags.Evaluations.enabled?(snapshot, "flag-key")
PostHog.FeatureFlags.set_in_context(
  PostHog.FeatureFlags.Evaluations.only_accessed(snapshot)
)
# Or attach only specific flags
PostHog.FeatureFlags.set_in_context(
  PostHog.FeatureFlags.Evaluations.only(snapshot, ["checkout-flow", "new-dashboard"])
)
```

`only_accessed/1` is order-dependent. If you call it before accessing any flags with `enabled?/2`, `get_flag/2`, or `get_flag_payload/2`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Elixir

PostHog AI

```elixir
PostHog.capture("event_name", %{
  "$feature/feature-flag-key" => "variant-key",
  distinct_id: "distinct_id_of_your_user"
})
```

### Evaluating only specific flags

By default, `evaluate_flags/1` evaluates every flag for the user. If you only need a few flags, pass `flag_keys` to request only those flags:

Elixir

PostHog AI

```elixir
{:ok, snapshot} =
  PostHog.FeatureFlags.evaluate_flags(%{
    distinct_id: "distinct_id_of_your_user",
    flag_keys: ["checkout-flow", "new-dashboard"]
  })
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `evaluate_flags/1`, the SDK sends this event when you call `PostHog.FeatureFlags.Evaluations.enabled?/2` or `PostHog.FeatureFlags.Evaluations.get_flag/2` for a flag.

`PostHog.FeatureFlags.Evaluations.get_flag_payload/2` doesn't send `$feature_flag_called` events.

## .NET

There are 2 steps to implement feature flags in .NET:

### Step 1: Evaluate the feature flag value

#### Boolean feature flags

C#

PostHog AI

```csharp
if (await posthog.IsFeatureEnabledAsync(
    "flag-key",
    "distinct_id_of_your_user"))
{
    // Feature is enabled
}
else
{
    // Feature is disabled
}
```

#### Multivariate feature flags

C#

PostHog AI

```csharp
var flag = await posthog.GetFeatureFlagAsync(
    "flag-key",
    "distinct_id_of_your_user"
);
// replace "variant-key" with the key of your variant
if (flag is { VariantKey: "variant-key"} ) {
    // Do something differently for this user
    // Optional: fetch the payload
    var matchedPayload = flag.Payload;
}
```

> **Note:** The `GetFeatureFlagAsync` method returns a nullable `FeatureFlag` object. If the flag is not found or evaluating it is inconclusive, it returns `null`. However, there is an implicit conversion to bool to make comparisons easier.

C#

PostHog AI

```csharp
if (await posthog.GetFeatureFlagAsync(
    "flag-key",
    "distinct_id_of_your_user")
)
{
    // Do something differently for this user
}
```

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Include the `$feature/feature_flag_name` property

In the event properties, include `$feature/feature_flag_name: variant_key`:

C#

PostHog AI

```csharp
posthog.Capture(
    "distinct_id_of_your_user",
    "event_name",
    properties: new() {
        // replace feature-flag-key with your flag key.
        // Replace "variant-key" with the key of your variant
        ["$feature/feature-flag-key"] = "variant-key"
    }
);
```

#### Method 2: Set `send_feature_flags` to `true`

The `Capture()` method has an optional argument `sendFeatureFlags`, which is set to `false` by default. By setting this to `true`, feature flag information will automatically be sent with the event.

Note that by doing this, PostHog will make an additional request to fetch feature flag information before capturing the event. So this method is only recommended if you don't mind the extra API call and delay.

C#

PostHog AI

```csharp
posthog.Capture(
    "distinct_id_of_your_user",
    "event_name",
    properties: null,
    groups: null,
    sendFeatureFlags: true
);
```

### Fetching all flags for a user

You can fetch all flag values for a single user by calling `GetAllFeatureFlagsAsync()`.

This is useful when you need to fetch multiple flag values and don't want to make multiple requests.

C#

PostHog AI

```csharp
var flags = await posthog.GetAllFeatureFlagsAsync(
    "distinct_id_of_your_user"
);
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enable PostHog to know when a flag was accessed by a user and thus provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. By default, we send a these event when:

1.  You call `posthog.GetFeatureFlagAsync()` or `posthog.IsFeatureEnabledAsync()`, AND
2.  It's a new user, or the value of the flag has changed.

> *Note:* Tracking whether it's a new user or if a flag value has changed happens in a local cache. This means that if you reinitialize the PostHog client, the cache resets as well – causing `$feature_flag_called` events to be sent again when calling `GetFeatureFlagAsync` or `IsFeatureEnabledAsync`. PostHog is built to handle this, and so duplicate `$feature_flag_called` events won't affect your analytics.

You can disable automatically the additional request to capture `$feature_flag_called` events. For example, when you don't need the analytics, or it's being called at such a high volume that sending events slows things down.

To disable it, set the `sendFeatureFlagsEvent` option in your function call, like so:

C#

PostHog AI

```csharp
var isMyFlagEnabled = await posthog.IsFeatureEnabledAsync(
    "flag-key",
    "distinct_id_of_your_user",
    options: new FeatureFlagOptions
    {
        SendFeatureFlagEvents = true
    }
);
// will not send `$feature_flag_called` events
```

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

C#

PostHog AI

```csharp
// Overriding Person Properties
var personFlag = await posthog.GetFeatureFlagAsync(
    "flag-key",
    "distinct_id_of_the_user",
    personProperties: new() {["property_name"] = "value"});
// Overriding Group Properties
var groupFlag = await posthog.GetFeatureFlagAsync(
    "flag-key",
    "distinct_id_of_the_user",
    options: new FeatureFlagOptions
    {
        Groups = [
            new Group("your_group_type", "your_group_id")
            {
                ["group_property_name"] = "your group value"
            },
            new Group(
                "another_group_type",
                "another_group_id")
                {
                    ["group_property_name"] = "another group value"
                }
        ]
    });
// Overriding both Person and Group Properties
var bothFlag = await posthog.GetFeatureFlagAsync(
    "flag-key",
    "distinct_id_of_the_user",
    options: new FeatureFlagOptions
    {
        PersonProperties = new() { ["property_name"] = "value" },
        Groups = [
            new Group("your_group_type", "your_group_id")
            {
                ["group_property_name"] = "your group value"
            },
            new Group(
                "another_group_type",
                "another_group_id")
                {
                    ["group_property_name"] = "another group value"
                }
        ]
    });
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

## API

There are 3 steps to implement feature flags using the PostHog API:

### Step 1: Evaluate the feature flag value using `flags`

`flags` is the endpoint used to determine if a given flag is enabled for a certain user or not.

#### Request

PostHog AI

### Terminal

```shell
# Basic request (flags only)
curl -v -L --header "Content-Type: application/json" -d '  {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user",
    "groups" : {
        "group_type": "group_id"
    }
}' "https://us.i.posthog.com/flags?v=2"
# With configuration (flags + PostHog config)
curl -v -L --header "Content-Type: application/json" -d '  {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user",
    "groups" : {
        "group_type": "group_id"
    }
}' "https://us.i.posthog.com/flags?v=2&config=true"
```

### Python

```python
import requests
import json
# Basic request (flags only)
url = "https://us.i.posthog.com/flags?v=2"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "api_key": "<ph_project_token>",
    "distinct_id": "user distinct id",
    "groups": {
        "group_type": "group_id"
    }
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())
# With configuration (flags + PostHog config)
url_with_config = "https://us.i.posthog.com/flags?v=2&config=true"
response_with_config = requests.post(url_with_config, headers=headers, data=json.dumps(payload))
print(response_with_config.json())
```

### Node.js

```javascript
import fetch from "node-fetch";
async function sendFlagsRequest() {
    const headers = {
        "Content-Type": "application/json",
    };
    const payload = {
        api_key: "<ph_project_token>",
        distinct_id: "user distinct id",
        groups: {
            group_type: "group_id",
        },
    };
    // Basic request (flags only)
    const url = "https://us.i.posthog.com/flags?v=2";
    const response = await fetch(url, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(payload),
    });
    const data = await response.json();
    console.log(data);
    // With configuration (flags + PostHog config)
    const urlWithConfig = "https://us.i.posthog.com/flags?v=2&config=true";
    const responseWithConfig = await fetch(urlWithConfig, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(payload),
    });
    const dataWithConfig = await responseWithConfig.json();
    console.log(dataWithConfig);
}
sendFlagsRequest();
```

> **Note:** The `groups` key is only required for group-based feature flags. If you use it, replace `group_type` and `group_id` with the values for your group such as `company: "Twitter"`.

#### Using evaluation context tags and runtime filtering without SDKs

When making direct API calls to the `/flags` endpoint, you can control which flags are evaluated using evaluation context tags and runtime filtering.

##### Evaluation contexts

To filter flags by evaluation context, include the `evaluation_contexts` field in your request body:

> **Note:** The legacy parameter `evaluation_environments` is also supported for backward compatibility.

PostHog AI

### Terminal

```shell
curl -v -L --header "Content-Type: application/json" -d '  {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user",
    "evaluation_contexts": ["production", "web"]
}' "https://us.i.posthog.com/flags?v=2"
```

### Python

```python
import requests
import json
url = "https://us.i.posthog.com/flags?v=2"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "api_key": "<ph_project_token>",
    "distinct_id": "user distinct id",
    "evaluation_contexts": ["production", "web"]
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())
```

### JavaScript

```javascript
const response = await fetch("https://us.i.posthog.com/flags?v=2", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
    },
    body: JSON.stringify({
        api_key: "<ph_project_token>",
        distinct_id: "user-distinct-id",
        evaluation_contexts: ["production", "web"]
    }),
});
const data = await response.json();
```

Only flags where at least one evaluation tag matches (or flags with no tags at all) will be returned. For example:

-   Flag with evaluation context tags `["production", "api", "backend"]` + request with `["production", "web"]` = ✅ Flag evaluates ("production" matches)
-   Flag with evaluation context tags `["staging", "api"]` + request with `["production", "web"]` = ❌ Flag doesn't evaluate (no tags match)
-   Flag with evaluation context tags `["web", "mobile"]` + request with `["production", "web"]` = ✅ Flag evaluates ("web" matches)
-   Flag with no evaluation context tags = ✅ Always evaluates (backward compatibility)

##### Runtime detection

Evaluation runtime (server vs. client) is automatically detected based on your request headers and user-agent. This determines which flags are available based on their runtime setting (server-only, client-only, or all).

**How runtime is detected:**

1.  **User-Agent patterns** - The system analyzes the User-Agent header:

    -   **Client-side patterns**: `Mozilla/`, `Chrome/`, `Safari/`, `Firefox/`, `Edge/` (browsers), or mobile SDKs like `posthog-android/`, `posthog-ios/`, `posthog-react-native/`, `posthog-flutter/`
    -   **Server-side patterns**: `posthog-python/`, `posthog-ruby/`, `posthog-php/`, `posthog-java/`, `posthog-go/`, `posthog-node/`, `posthog-dotnet/`, `posthog-elixir/`, `python-requests/`, `curl/`
2.  **Browser-specific headers** - Presence of these headers indicates client-side:

    -   `Origin` header
    -   `Referer` header
    -   `Sec-Fetch-Mode` header
    -   `Sec-Fetch-Site` header
3.  **Default behavior** - If runtime can't be determined, the system includes flags with no runtime requirement and those set to "all"

**Examples of runtime detection:**

JavaScript

PostHog AI

```javascript
// Browser fetch - Detected as CLIENT runtime
// Will receive: client-only flags + "all" flags
// Won't receive: server-only flags
const response = await fetch("https://us.i.posthog.com/flags?v=2", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        // Browser automatically adds Origin, Referer, Sec-Fetch-* headers
    },
    body: JSON.stringify({
        api_key: "<ph_project_token>",
        distinct_id: "user-id"
    })
});
```

Python

PostHog AI

```python
# Python requests - Detected as SERVER runtime
# Will receive: server-only flags + "all" flags
# Won't receive: client-only flags
import requests
response = requests.post(
    "https://us.i.posthog.com/flags?v=2",
    json={
        "api_key": "<ph_project_token>",
        "distinct_id": "user-id"
    }
    # python-requests/ in User-Agent indicates server-side
)
```

Terminal

PostHog AI

```shell
# curl - Detected as SERVER runtime
# Will receive: server-only flags + "all" flags
# Won't receive: client-only flags
curl -v -L --header "Content-Type: application/json" -d '{
    "api_key": "<ph_project_token>",
    "distinct_id": "user-id"
}' "https://us.i.posthog.com/flags?v=2"
# curl/ in User-Agent indicates server-side
```

JavaScript

PostHog AI

```javascript
// Node.js with custom User-Agent - Control runtime detection
const response = await fetch("https://us.i.posthog.com/flags?v=2", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "User-Agent": "posthog-node/3.0.0"  // Explicitly indicates server-side
    },
    body: JSON.stringify({
        api_key: "<ph_project_token>",
        distinct_id: "user-id"
    })
});
```

##### Combining evaluation context tags and runtime filtering

Both features work together as sequential filters:

JavaScript

PostHog AI

```javascript
// Example: Production web client
const response = await fetch("https://us.i.posthog.com/flags?v=2", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        // Browser headers will trigger client runtime detection
    },
    body: JSON.stringify({
        api_key: "<ph_project_token>",
        distinct_id: "user-id",
        evaluation_contexts: ["production", "web"]
    })
});
// This request will only receive flags that:
// 1. Have runtime set to "client" OR "all" (due to browser headers)
// AND
// 2. Have evaluation context tags matching "production" OR "web" (or no tags)
// Note: You can also use the legacy "evaluation_environments" parameter
```

This allows precise control over which flags are evaluated in different contexts, helping optimize costs and improve security by ensuring flags only evaluate where intended.

#### Response

The response varies depending on whether you include the `config=true` query parameter:

##### Basic response (`/flags?v=2`)

Use this endpoint when you only need to evaluate feature flags. It returns a response with just the flag evaluation results.

> **Note:** If a feature flag is associated with an experiment that has a [holdout group](/docs/experiments/holdouts.md), users in the holdout receive a variant value in the format `holdout-{holdout_id}` (e.g., `holdout-727`). You can detect holdout users by checking if the variant starts with `holdout-`.

JSON

PostHog AI

```json
{
  "flags": {
    "my-awesome-flag": {
      "key": "my-awesome-flag",
      "enabled": true,
      "reason": {
        "code": "condition_match",
        "condition_index": 0,
        "description": "Condition set 1 matched"
      },
      "metadata": {
        "id": 1,
        "version": 1,
        "payload": "{\"example\": \"json\", \"payload\": \"value\"}"
      }
    },
    "my-multivariate-flag" :{
      "key":"my-multivariate-flag",
      "enabled": true,
      "variant": "some-string-value",
      "reason": {
        "code": "condition_match",
        "condition_index": 1,
        "description": "Condition set 2 matched"
      },
      "metadata": {
        "id": 2,
        "version": 42,
      }
    },
    "flag-thats-not-on": {
      "key": "flag-thats-not-on",
      "enabled": false,
      "reason": {
        "code": "no_condition_match",
        "condition_index": 0,
        "description": "No condition sets matched"
      },
      "metadata": {
        "id": 3,
        "version": 1
      }
    }
  },
  "errorsWhileComputingFlags": false,
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

##### Full response with configuration (`/flags?v=2&config=true`)

Use this endpoint when you need both feature flag evaluation and PostHog configuration information (useful for client-side SDKs that need to initialize PostHog):

JSON

PostHog AI

```json
{
  "config": {
    "enable_collect_everything": true
  },
  "toolbarParams": {},
  "errorsWhileComputingFlags": false,
  "isAuthenticated": false,
  "requestId": "550e8400-e29b-41d4-a716-446655440000",
  "supportedCompression": [
    "gzip",
    "lz64"
  ],
  "flags": {
    "my-awesome-flag": {
      "key": "my-awesome-flag",
      "enabled": true,
      "reason": {
        "code": "condition_match",
        "condition_index": 0,
        "description": "Condition set 1 matched"
      },
      "metadata": {
        "id": 1,
        "version": 1,
        "payload": "{\"example\": \"json\", \"payload\": \"value\"}"
      }
    },
    "my-multivariate-flag" :{
      "key":"my-multivariate-flag",
      "enabled": true,
      "variant": "some-string-value",
      "reason": {
        "code": "condition_match",
        "condition_index": 1,
        "description": "Condition set 2 matched"
      },
      "metadata": {
        "id": 2,
        "version": 42,
      }
    },
    "flag-thats-not-on": {
      "key": "flag-thats-not-on",
      "enabled": false,
      "reason": {
        "code": "no_condition_match",
        "condition_index": 0,
        "description": "No condition sets matched"
      },
      "metadata": {
        "id": 3,
        "version": 1
      }
    }
  }
}
```

> **Note:** `errorsWhileComputingFlags` will return `true` if we didn't manage to compute some flags (for example, if there's an [ongoing incident involving flag evaluation](https://status.posthog.com/)).
>
> This enables partial updates to currently active flags in your clients.

#### Quota limiting

If your organization exceeds its feature flag quota, the `/flags` endpoint will return a modified response with `quotaLimited`.

For basic response (`/flags?v=2`):

JSON

PostHog AI

```json
{
  "flags": {},
  "errorsWhileComputingFlags": false,
  "quotaLimited": ["feature_flags"],
  "requestId": "d4d89b14-9619-4627-adf2-01b761691c2e"
}
```

For full response with configuration (`/flags?v=2&config=true`):

JSON

PostHog AI

```json
{
  "config": {
    "enable_collect_everything": true
  },
  "toolbarParams": {},
  "isAuthenticated": false,
  "supportedCompression": [
    "gzip",
    "lz64"
  ],
  "flags": {},
  "errorsWhileComputingFlags": false,
  "quotaLimited": ["feature_flags"],
  "requestId": "d4d89b14-9619-4627-adf2-01b761691c2e"
  // ... other fields, not relevant to feature flags
}
```

When you receive a response with `quotaLimited` containing `"feature_flags"`, it means:

1.  Your feature flag evaluations have been temporarily paused because you've exceeded your feature flag quota
2.  If you want to continue evaluating feature flags, you can increase your quota in [your billing settings](https://us.posthog.com/organization/billing) under **Feature flags & Experiments** or [contact support](https://us.posthog.com/#panel=support%3Asupport%3Abilling%3A%3Atrue)

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

To do this, include the `$feature/feature_flag_name` property in your event:

PostHog AI

### Terminal

```shell
curl -v -L --header "Content-Type: application/json" -d '  {
    "api_key": "<ph_project_token>",
    "event": "your_event_name",
    "distinct_id": "distinct_id_of_your_user",
    "properties": {
      "$feature/feature-flag-key": "variant-key" # Replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
    }
}' https://us.i.posthog.com/i/v0/e/
```

### Python

```python
import requests
import json
url = "https://us.i.posthog.com/i/v0/e/"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "api_key": "<ph_project_token>",
    "event": "your_event_name",
    "distinct_id": "distinct_id_of_your_user,
    "properties": {
      "$feature/feature-flag-key": "variant-key" # Replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
    }
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response)
```

### Step 3: Send a `$feature_flag_called` event

To track usage of your feature flag and view related analytics in PostHog, submit the `$feature_flag_called` event whenever you check a feature flag value in your code.

You need to include two properties with this event:

1.  `$feature_flag_response`: This is the name of the variant the user has been assigned to e.g., "control" or "test"
2.  `$feature_flag`: This is the key of the feature flag in your experiment.

PostHog AI

### Terminal

```shell
curl -v -L --header "Content-Type: application/json" -d '  {
    "api_key": "<ph_project_token>",
    "event": "$feature_flag_called",
    "distinct_id": "distinct_id_of_your_user",
    "properties": {
      "$feature_flag": "feature-flag-key",
      "$feature_flag_response": "variant-name"
    }
}' https://us.i.posthog.com/i/v0/e/
```

### Python

```python
import requests
import json
url = "https://us.i.posthog.com/i/v0/e/"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "api_key": "<ph_project_token>",
    "event": "feature_flag_called",
    "distinct_id": "distinct_id_of_your_user,
    "properties": {
      "$feature_flag": "feature-flag-key",
      "$feature_flag_response": "variant-name"
    }
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response)
```

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

PostHog AI

### Terminal

```shell
curl -v -L --header "Content-Type: application/json" -d '  {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user",
    "groups" : { # Required only for group-based feature flags
      "group_type": "group_id" # Replace "group_type" with the name of your group type. Replace "group_id" with the id of your group.
    },
    "person_properties": {"<personProp1>": "<personVal1>"}, # Optional. Include any properties used to calculate the value of the feature flag.
    "group_properties": {"group type": {"<groupProp1>":"<groupVal1>"}} # Optional. Include any properties used to calculate the value of the feature flag.
}' https://us.i.posthog.com/flags?v=2
```

### Python

```python
import requests
import json
url = "https://us.i.posthog.com/flags?v=2"
headers = {
    "Content-Type": "application/json"
}
payload = {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user",
    "groups" : { # Required only for group-based feature flags
      "group_type": "group_id" # Replace "group_type" with the name of your group type. Replace "group_id" with the id of your group.
    },
    "person_properties": {"<personProp1>": "<personVal1>"}, # Optional. Include any properties used to calculate the value of the feature flag.
    "group_properties": {"group type": {"<groupProp1>":"<groupVal1>"}} # Optional. Include any properties used to calculate the value of the feature flag.
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

To override the GeoIP properties used to evaluate a feature flag, provide an IP address in the `HTTP_X_FORWARDED_FOR` when making your `/flags` request:

PostHog AI

### Terminal

```shell
curl -v -L \
--header "Content-Type: application/json" \
--header "HTTP_X_FORWARDED_FOR: the_client_ip_address_to_use " \
-d '  {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user"
}' https://us.i.posthog.com/flags?v=2
```

### Python

```python
import requests
import json
url = "https://us.i.posthog.com/flags?v=2"
headers = {
    "Content-Type": "application/json",
    "HTTP_X_FORWARDED_FOR": "the_client_ip_address_to_use"
}
payload = {
    "api_key": "<ph_project_token>",
    "distinct_id": "distinct_id_of_your_user"
}
response = requests.post(url, headers=headers, data=json.dumps(payload))
print(response.json())
```

The list of properties that this overrides:

1.  `$geoip_city_name`
2.  `$geoip_country_name`
3.  `$geoip_country_code`
4.  `$geoip_continent_name`
5.  `$geoip_continent_code`
6.  `$geoip_postal_code`
7.  `$geoip_time_zone`

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better