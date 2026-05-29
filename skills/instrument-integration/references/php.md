# PHP - Docs

This is an optional library you can install if you're working with PHP. It uses an internal queue to batch requests, flushes at the end of the request, and optionally does so in an async manner.

## Installation

Install the package with Composer:

Terminal

PostHog AI

```bash
composer require posthog/posthog-php
```

In your app, set your project token before making any calls.

PHP

PostHog AI

```php
PostHog\PostHog::init("<ph_project_token>",
  ['host' => 'https://us.i.posthog.com']
);
```

> **Note:** As a rule of thumb, we do not recommend having API keys or tokens in plaintext. Setting them as environment variables is best. The PHP SDK reads `POSTHOG_API_KEY` and `POSTHOG_HOST` when you omit the project token or host.

You can find your project token and instance address in the [project settings](https://app.posthog.com/project/settings) page in PostHog.

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Capturing events

You can send custom events using `capture`:

PHP

PostHog AI

```php
PostHog::capture([
  'distinctId' => 'distinct_id_of_the_user',
  'event' => 'user_signed_up'
]);
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

PHP

PostHog AI

```php
PostHog::capture([
  'distinctId' => 'distinct_id_of_the_user',
  'event' => 'user_signed_up',
  'properties' => [
    'login_type' => 'email',
    'is_free_trial' => 'true'
  ]
]);
```

### Sending page views

If you're aiming for a backend-only implementation of PostHog and won't be capturing events from your frontend, you can send `pageviews` from your backend like so:

PHP

PostHog AI

```php
PostHog::capture([
  'distinctId' => 'distinct_id_of_the_user',
  'event' => '$pageview',
  'properties' => [
    '$current_url' => 'https://example.com'
  ]
]);
```

## Person profiles and properties

The PHP SDK captures identified events by default. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/data/user-properties.md), call `identify` with the user's distinct ID and properties:

PHP

PostHog AI

```php
PostHog::identify([
    'distinctId' => 'distinct_id',
    'properties' => [
        'email' => 'max@example.com',
        'name' => 'Max Hedgehog',
    ],
]);
```

You can also include person properties when capturing an event:

PHP

PostHog AI

```php
PostHog::capture([
    'distinctId' => 'distinct_id',
    'event' => 'event_name',
    'properties' => [
        '$set' => [
            'name' => 'Max Hedgehog'
        ],
        '$set_once' => [
            'initial_url' => '/blog'
        ]
    ]
]);
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/data/user-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

PHP

PostHog AI

```php
PostHog::capture([
    'distinctId' => 'distinct_id',
    'event' => 'event_name',
    'properties' => [
        '$process_person_profile' => false
    ]
]);
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

PHP

PostHog AI

```php
PostHog::alias([
  'distinctId' => 'distinct_id',
  'alias' => 'alias_id'
]);
```

We strongly recommend reading our docs on [alias](/docs/data/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in PHP:

### Step 1: Evaluate flags once

Call `PostHog::evaluateFlags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags('distinct_id_of_your_user');
if ($flags->isEnabled('flag-key')) {
    // Do something differently for this user
    // Optional: fetch the payload
    $matchedFlagPayload = $flags->getFlagPayload('flag-key');
}
```

#### Multivariate feature flags

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags('distinct_id_of_your_user');
$enabledVariant = $flags->getFlag('flag-key');
if ($enabledVariant === 'variant-key') { // replace 'variant-key' with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    $matchedFlagPayload = $flags->getFlagPayload('flag-key');
}
```

`$flags->getFlag()` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `null` when the flag wasn't returned by the evaluation.

You can also call `$flags->getKeys()` to list the evaluated flag keys, or `$flags->getEventProperties()` to get the `$feature/<flag-key>` and `$active_feature_flags` properties that would be attached to a captured event.

> **Note:** `PostHog::isFeatureEnabled()`, `PostHog::getFeatureFlag()`, `PostHog::getFeatureFlagPayload()`, and `capture(['send_feature_flags' => true])` still work during the migration period, but they're deprecated. Prefer `evaluateFlags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags('distinct_id_of_your_user');
if ($flags->isEnabled('flag-key')) {
    // Do something differently for this user
}
PostHog::capture([
    'distinctId' => 'distinct_id_of_your_user',
    'event' => 'event_name',
    'flags' => $flags,
]);
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

PHP

PostHog AI

```php
// Attach only flags accessed with isEnabled() or getFlag() before this call
PostHog::capture([
    'distinctId' => 'distinct_id_of_your_user',
    'event' => 'event_name',
    'flags' => $flags->onlyAccessed(),
]);
// Attach only specific flags
PostHog::capture([
    'distinctId' => 'distinct_id_of_your_user',
    'event' => 'event_name',
    'flags' => $flags->only(['checkout-flow', 'new-dashboard']),
]);
```

`onlyAccessed()` is order-dependent. If you call it before accessing any flags with `isEnabled()` or `getFlag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

PHP

PostHog AI

```php
PostHog::capture([
    'distinctId' => 'distinct_id_of_your_user',
    'event' => 'event_name',
    'properties' => [
        // Replace feature-flag-key with your flag key and 'variant-key' with the key of your variant
        '$feature/feature-flag-key' => 'variant-key',
    ],
]);
```

### Evaluating only specific flags

By default, `evaluateFlags()` evaluates every flag for the user. If you only need a few flags, pass `flagKeys` to request only those flags:

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags(
    distinctId: 'distinct_id_of_your_user',
    flagKeys: ['checkout-flow', 'new-dashboard'],
);
```

### Optional evaluation parameters

`evaluateFlags()` also accepts optional parameters for local evaluation and GeoIP behavior:

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags(
    distinctId: 'distinct_id_of_your_user',
    groups: ['company' => 'company_id_in_your_db'],
    personProperties: ['plan' => 'pro'],
    groupProperties: ['company' => ['employees' => 11]],
    onlyEvaluateLocally: false, // Defaults to false. Set to true to avoid a remote fallback.
    disableGeoip: false, // Defaults to false. Set to true to disable GeoIP enrichment during remote evaluation.
    flagKeys: ['checkout-flow', 'new-dashboard'],
);
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `evaluateFlags()`, the SDK sends this event when you call `$flags->isEnabled()` or `$flags->getFlag()` for a flag.

The SDK deduplicates these events per `(flag key, distinct_id)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`$flags->getFlagPayload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `onlyAccessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags(
    distinctId: 'distinct_id_of_the_user',
    groups: [
        'your_group_type' => 'your_group_id',
        'another_group_type' => 'your_group_id',
    ],
    personProperties: ['property_name' => 'value'],
    groupProperties: [
        'your_group_type' => ['group_property_name' => 'value'],
        'another_group_type' => ['group_property_name' => 'value'],
    ],
);
if ($flags->isEnabled('flag-key')) {
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

PHP

PostHog AI

```php
PostHog::init("<ph_project_token>",
    [
        'host' => 'https://us.i.posthog.com',
        'feature_flag_request_timeout_ms' => 3000, // Time in milliseconds. Defaults to 3000 (3 seconds).
    ]
);
```

### Local Evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

To load feature flag definitions for local evaluation, initialize the SDK with your feature flags secure API key as `personalAPIKey`:

PHP

PostHog AI

```php
PostHog::init(
    '<ph_project_token>',
    ['host' => 'https://us.i.posthog.com'],
    personalAPIKey: 'your feature flags secure API key'
);
```

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

### Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

PHP

PostHog AI

```php
$flags = PostHog::evaluateFlags('user_distinct_id');
$variant = $flags->getFlag('experiment-feature-flag-key');
if ($variant === 'variant-name') {
    // Do something differently for this user
}
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

### Group analytics

Group analytics allows you to associate an event with a group (e.g. teams, organizations, etc.). This feature requires version `2.1.0` or above of the PHP SDK. Read the [group analytics guide](/docs/product-analytics/group-analytics.md) for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](/pricing.md).

To create a group or update its properties, use `groupIdentify`:

PHP

PostHog AI

```php
PostHog::groupIdentify([
    'groupType' => 'company',
    'groupKey' => 'company_id_in_your_db',
    'properties' => [
        'name' => 'Awesome Inc.',
        'employees' => 11,
    ],
    // Optional distinct ID to associate this event with an existing person.
    // Requires posthog-php 4.4.0 or later.
    'distinctId' => 'user_distinct_id'
]);
```

`name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID is used instead.

If the optional `distinctId` parameter is not provided in the group identify call, it defaults to `${groupType}_${groupKey}` (e.g., `$company_company_id_in_your_db` in the example above). This default behavior results in each group appearing as a separate person in PostHog. To avoid this, use a consistent `distinctId`, such as `group_identifier`, or a real user distinct ID.

Once a group is created, you can use the `capture` method and pass in the `groups` parameter to capture an event with group analytics.

PHP

PostHog AI

```php
PostHog::capture([
    'distinctId' => 'user_distinct_id',
    'event' => 'some_event',
    'groups' => ['company' => 'company_id_in_your_db']
]);
```

## Request context

Use request context to apply a distinct ID, session ID, and common properties to all captures inside a callback. This is useful when connecting frontend activity to backend events, session replay, and error tracking.

PHP

PostHog AI

```php
PostHog::withContext([
    'distinctId' => 'user_distinct_id',
    'sessionId' => 'session_id_from_frontend',
    'properties' => [
        '$current_url' => 'https://example.com/account',
    ],
], function () {
    PostHog::capture([
        'event' => 'backend_event',
    ]);
});
```

You can extract PostHog context from frontend tracing headers with `contextFromHeaders()`:

PHP

PostHog AI

```php
$context = PostHog::contextFromHeaders($_SERVER);
PostHog::withContext($context, function () {
    PostHog::capture([
        'event' => 'backend_event',
    ]);
});
```

Call `PostHog::getContext()` to read the currently active context. Pass `['fresh' => true]` as the third argument to `withContext()` if you don't want to inherit any existing context.

## Error tracking

The PHP SDK supports both manual exception capture and opt-in automatic error tracking.

To automatically capture uncaught exceptions, PHP errors, and fatal shutdown errors, enable `error_tracking` when initializing the client:

PHP

PostHog AI

```php
PostHog::init(
    '<ph_project_token>',
    [
        'host' => 'https://us.i.posthog.com',
        'error_tracking' => [
            'enabled' => true,
        ],
    ],
);
```

You can also call `PostHog::captureException()` directly for manual capture. When source files are readable at runtime, PostHog includes surrounding source lines for in-app stack frames automatically.

For the full setup guide, including `context_provider`, excluded exceptions, and verification steps, see the [PHP error tracking installation docs](/docs/error-tracking/installation/php.md).

## Config options

When calling `PostHog::init`, there are various configuration options you can set apart from the host. Pass them into your client initialisation like so:

PHP

PostHog AI

```php
PostHog::init(
    '<ph_project_token>',
    [
        'host' => 'https://us.i.posthog.com',
        'debug' => true,
        'ssl' => false,
        // all options go here
    ],
);
```

All possible options below:

| Attribute | Description |
| --- | --- |
| hostType: StringDefault: us.i.posthog.com | URL of your PostHog instance. |
| sslType: BooleanDefault: true | Whether to use SSL for API requests or not. If host includes http:// or https://, the SDK infers this option unless you set it explicitly. |
| timeoutType: IntegerDefault: 10000 | Request timeout in milliseconds. |
| verify_batch_events_requestType: BooleanDefault: true | Whether to verify successful delivery of batch events (true, synchronous) or fire and forget (false, asynchronous) with the lib_curl consumer. |
| feature_flag_request_timeout_msType: IntegerDefault: 3000 | Request timeout for feature flags in milliseconds. |
| maximum_backoff_durationType: IntegerDefault: 10000 | Request retry backoff. Retries stop after this duration is hit. |
| consumerType: StringDefault: lib_curl | One of socket, file, lib_curl, and fork_curl. Determines what transport option to use for analytics capture. |
| debugType: BooleanDefault: false | Output debug logs or not. |
| max_queue_sizeType: IntegerDefault: 1000 | Maximum number of events to queue before rejecting new events. Applies to queued consumers. |
| batch_sizeType: IntegerDefault: 100 | Number of queued events to send in each batch. Applies to queued consumers. |
| compress_requestType: Boolean/StringDefault: false | Whether to gzip batch request payloads. |
| error_handlerType: CallableDefault: null | Callback invoked for SDK transport errors. |
| filenameType: StringDefault: sys_get_temp_dir() . '/posthog.log' | File path used when consumer is set to file. |
| error_trackingType: ArrayDefault: [] | Enables automatic error tracking. See the options below or the [PHP error tracking setup guide](/docs/error-tracking/installation/php.md). |

### Error tracking options

| Attribute | Description |
| --- | --- |
| enabledType: BooleanDefault: false | Enables automatic error tracking handlers. Manual captureException works regardless. |
| capture_errorsType: BooleanDefault: true | When enabled, captures PHP errors and fatal shutdown errors in addition to uncaught exceptions. |
| excluded_exceptionsType: Array of class stringsDefault: [] | Throwable classes to skip during automatic capture. |
| max_framesType: IntegerDefault: 20 | Maximum number of stack frames included in $exception_list. |
| context_providerType: Callable or nullDefault: null | Callback that returns distinctId and extra event properties for automatic captures. |

## Debug mode

PHP

PostHog AI

```php
PostHog::init(
    '<ph_project_token>',
    [
        'host' => 'https://us.i.posthog.com',
        'debug' => true,
    ],
);
```

## Thank you

This library is largely based on the `analytics-php` package.

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better