# Ruby - Docs

The `posthog-ruby` library provides tracking functionality on the server-side for applications built in Ruby.

It uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your web app or other server-side application that needs performance.

> **Use a single client instance (singleton)** — Create the PostHog client once and reuse it throughout your application. Multiple client instances with the same API key can cause dropped events and inconsistent behavior. The SDK logs a warning if it detects multiple instances.

## Installation

Add this to your `Gemfile`:

Terminal

PostHog AI

```bash
gem "posthog-ruby"
```

In your app, set your API key **before** making any calls. If setting a custom `host`, make sure to include the protocol (e.g. `https://`).

Ruby

PostHog AI

```ruby
require 'posthog'
posthog = PostHog::Client.new({
  api_key: "<ph_project_token>",
  host: "https://us.i.posthog.com",
  on_error: Proc.new { |status, msg| print msg }
})
```

You can find your project token and instance address in the [project settings](https://app.posthog.com/project/settings) page in PostHog.

## Configuration

Initialize the client with your project token before making any calls:

Ruby

PostHog AI

```ruby
require 'posthog'
posthog = PostHog::Client.new({
  api_key: '<ph_project_token>',
  host: 'https://us.i.posthog.com',
  on_error: Proc.new { |status, msg| print msg }
})
```

Available client options:

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| api_key | String | required | Your PostHog project token. |
| host | String | https://us.i.posthog.com | Fully qualified PostHog API host. Include the protocol, for example https://us.i.posthog.com or https://eu.i.posthog.com. |
| personal_api_key | String | nil | Personal API key. Required for local feature flag evaluation and remote config payloads. |
| max_queue_size | Integer | 10000 | Maximum number of events to keep in the async queue before dropping new events. |
| batch_size | Integer | 100 | Maximum number of events to send in one async batch. |
| test_mode | Boolean | false | Keep events queued and do not send them. Useful for tests. |
| sync_mode | Boolean | false | Send events synchronously on the calling thread. Useful in forking environments like Sidekiq and Resque. |
| on_error | Proc | no-op | Callback called as on_error.call(status, error) for API or serialization errors. |
| feature_flags_polling_interval | Integer | 30 | Seconds between local feature flag definition polls. |
| feature_flag_request_timeout_seconds | Integer | 3 | Timeout, in seconds, for feature flag requests. |
| before_send | Proc | nil | Callback that receives the event hash before it is queued or sent. Return a modified event hash, or nil to drop the event. |
| disable_singleton_warning | Boolean | false | Suppress warnings about multiple clients with the same API key. Use only when you intentionally need multiple clients. |
| skip_ssl_verification | Boolean | false | Disable SSL certificate verification. Intended only for local development or custom deployments. |
| flag_definition_cache_provider | Object | nil | Provider for distributed feature flag definition caching. See [distributed flag definition caching](#distributed-flag-definition-caching). |

### Filtering or modifying events before sending

Use `before_send` to add, modify, or drop events immediately before the SDK queues or sends them:

Ruby

PostHog AI

```ruby
posthog = PostHog::Client.new({
  api_key: '<ph_project_token>',
  before_send: Proc.new do |event|
    event[:properties] ||= {}
    event[:properties]['environment'] = ENV['RACK_ENV']
    # Return nil to drop the event
    event[:properties]['internal_user'] == true ? nil : event
  end
})
```

### Flushing and shutting down

For short-lived scripts, call `flush` before the process exits. Call `shutdown` when your application is stopping to flush pending events and stop background resources.

Ruby

PostHog AI

```ruby
posthog.capture({ distinct_id: 'user_123', event: 'script_finished' })
posthog.flush
posthog.shutdown
```

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

Identify a user and set their person properties with `identify`:

Ruby

PostHog AI

```ruby
posthog.identify({
  distinct_id: 'distinct_id_of_your_user',
  properties: {
    email: 'john@doe.com',
    pro_user: false
  }
})
```

## Capturing events

You can send custom events using `capture`:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_the_user',
    event: 'user_signed_up'
})
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_the_user',
    event: 'user_signed_up',
    properties: {
        login_type: 'email',
        is_free_trial: true
    }
})
```

### Sending pageviews

If you're aiming for a backend-only implementation of PostHog and won't be capturing events from your frontend, you can send `pageviews` from your backend like so:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_the_user',
    event: '$pageview',
    properties: {
        '$current_url': 'https://example.com'
    }
})
```

`capture` accepts these fields:

| Field | Type | Description |
| --- | --- | --- |
| distinct_id | String | The user ID. If omitted, framework integrations can provide request context; otherwise the SDK generates a UUID and marks the event as personless. |
| event | String | Event name. Required. |
| properties | Hash | Event properties. |
| groups | Hash | Group analytics mapping from group type to group key. |
| timestamp | Time | When the event occurred. Defaults to the current time. |
| message_id | String | Optional message ID. |
| uuid | String | Optional event UUID used for deduplication. Must be a valid UUID. |
| flags | PostHog::FeatureFlagEvaluations | Snapshot returned by evaluate_flags. Adds $feature/<key> and $active_feature_flags properties without another /flags request. |
| send_feature_flags | Boolean, Hash, or PostHog::SendFeatureFlagsOptions | Deprecated. Prefer passing flags: from evaluate_flags. |

## Person profiles and properties

The Ruby SDK captures identified events by default. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/data/user-properties.md) in these profiles, include them when capturing an event:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id',
    event: 'event_name',
    properties: {
        '$set': { name: 'Max Hedgehog' },
        '$set_once': { initial_url: '/blog' }
    }
})
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/data/user-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id',
    event: 'event_name',
    properties: {
        '$process_person_profile': false
    }
})
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Ruby

PostHog AI

```ruby
posthog.alias({
  distinct_id: 'distinct_id',
  alias: 'alias_id'
})
```

We strongly recommend reading our docs on [alias](/docs/data/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in Ruby:

### Step 1: Evaluate flags once

Call `posthog.evaluate_flags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags('distinct_id_of_your_user')
if flags.enabled?('flag-key')
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flags.get_flag_payload('flag-key')
end
```

#### Multivariate feature flags

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags('distinct_id_of_your_user')
enabled_variant = flags.get_flag('flag-key')
if enabled_variant == 'variant-key' # replace 'variant-key' with the key of your variant
    # Do something differently for this user
    # Optional: fetch the payload
    matched_flag_payload = flags.get_flag_payload('flag-key')
end
```

`flags.get_flag()` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `nil` when the flag wasn't returned by the evaluation.

> **Note:** `posthog.is_feature_enabled()`, `posthog.get_feature_flag()`, `posthog.get_feature_flag_result()`, `posthog.get_feature_flag_payload()`, and `capture({ ..., send_feature_flags: true })` still work during the migration period, but they're deprecated. Prefer `evaluate_flags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags('distinct_id_of_your_user')
if flags.enabled?('flag-key')
    # Do something differently for this user
end
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags,
})
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

Ruby

PostHog AI

```ruby
# Attach only flags accessed with enabled?() or get_flag() before this call
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags.only_accessed,
})
# Attach only specific flags
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    flags: flags.only(['checkout-flow', 'new-dashboard']),
})
```

`only_accessed` is order-dependent. If you call it before accessing any flags with `enabled?()` or `get_flag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_your_user',
    event: 'event_name',
    properties: {
        # Replace feature-flag-key with your flag key and 'variant-key' with the key of your variant
        '$feature/feature-flag-key': 'variant-key',
    },
})
```

### Evaluating only specific flags

By default, `evaluate_flags()` evaluates every flag for the user. If you only need a few flags, pass `flag_keys` to request only those flags:

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags(
    'distinct_id_of_your_user',
    flag_keys: ['checkout-flow', 'new-dashboard'],
)
```

### Evaluating locally only

If you want to skip the remote `/flags` request and only use locally cached definitions, pass `only_evaluate_locally: true`:

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags(
    'distinct_id_of_your_user',
    only_evaluate_locally: true,
)
```

### Disabling GeoIP for flag evaluation

Pass `disable_geoip: true` to disable GeoIP lookup for remote flag evaluation:

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags(
    'distinct_id_of_your_user',
    disable_geoip: true,
)
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `evaluate_flags()`, the SDK sends this event when you call `flags.enabled?()` or `flags.get_flag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.get_flag_payload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `only_accessed`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags(
    'distinct_id_of_the_user',
    person_properties: {
        property_name: 'value'
    },
    groups: {
        your_group_type: 'your_group_id',
        another_group_type: 'your_group_id',
    },
    group_properties: {
        your_group_type: {
            group_property_name: 'value'
        },
        another_group_type: {
            group_property_name: 'value'
        },
    },
)
if flags.enabled?('flag-key')
    # Do something differently for this user
end
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

You can configure the `feature_flag_request_timeout_seconds` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked if PostHog's servers are too slow to respond. By default, this is set to 3 seconds.

Ruby

PostHog AI

```ruby
posthog = PostHog::Client.new({
    # rest of your configuration...
    feature_flag_request_timeout_seconds: 3 # Time in seconds. Defaults to 3.
})
```

### Legacy single-flag methods

The following methods are still available during the migration period, but are deprecated. Prefer `evaluate_flags` for new code.

| Method | Replacement |
| --- | --- |
| posthog.is_feature_enabled(flag_key, distinct_id, ...) | posthog.evaluate_flags(distinct_id, ...).enabled?(flag_key) |
| posthog.get_feature_flag(flag_key, distinct_id, ...) | posthog.evaluate_flags(distinct_id, ...).get_flag(flag_key) |
| posthog.get_feature_flag_payload(flag_key, distinct_id, ...) | posthog.evaluate_flags(distinct_id, ...).get_flag_payload(flag_key) |
| posthog.get_feature_flag_result(flag_key, distinct_id, ...) | posthog.evaluate_flags(distinct_id, ...) and read get_flag / get_flag_payload |
| posthog.capture({ ..., send_feature_flags: true }) | posthog.capture({ ..., flags: flags }) |

### Local Evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

#### Evaluating feature flags locally in unicorn server

If you have `preload_app true` in your unicorn config, you can use the [`after_fork`](https://www.rubydoc.info/gems/unicorn/Unicorn%2FConfigurator:after_fork) hook (which is part of the unicorn's configuration) to enable the feature flag cache to receive the updates from PostHog.

Ruby

PostHog AI

```ruby
after_fork do |_server, _worker|
  $posthog = PostHog::Client.new({
    api_key: '<ph_project_token>',
    personal_api_key: '<ph_personal_api_key>',
    host: 'https://us.i.posthog.com',
    on_error: Proc.new { |status, msg| print msg }
  })
end
```

#### Evaluating feature flags locally in a Puma server

If you use Puma with multiple workers, you can use the `on_worker_boot` hook (which is part of Puma's configuration) to enable the feature flag cache to receive updates from PostHog.

Ruby

PostHog AI

```ruby
on_worker_boot do
  $posthog = PostHog::Client.new({
    api_key: '<ph_project_token>',
    personal_api_key: '<ph_personal_api_key>',
    host: 'https://us.i.posthog.com',
    on_error: Proc.new { |status, msg| print msg }
  })
end
```

### Distributed flag definition caching

`flag_definition_cache_provider` shares locally evaluated feature flag definitions across multiple workers or processes. The provider object must implement:

-   `flag_definitions` – returns cached definitions as a hash with `:flags`, `:group_type_mapping`, and `:cohorts`, or `nil` if empty.
-   `should_fetch_flag_definitions?` – returns `true` if this process should fetch fresh definitions from PostHog.
-   `on_flag_definitions_received(data)` – stores freshly fetched definitions.
-   `shutdown` – releases locks or other resources.

Ruby

PostHog AI

```ruby
posthog = PostHog::Client.new({
  api_key: '<ph_project_token>',
  personal_api_key: '<ph_personal_api_key>',
  flag_definition_cache_provider: my_cache_provider
})
```

### Remote config payloads

Use `get_remote_config_payload` to fetch the decrypted remote config payload for a flag. This requires `personal_api_key`.

Ruby

PostHog AI

```ruby
payload = posthog.get_remote_config_payload('flag-key')
```

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

Ruby

PostHog AI

```ruby
flags = posthog.evaluate_flags('user_distinct_id')
variant = flags.get_flag('experiment-feature-flag-key')
if variant == 'variant-name'
    # Do something
end
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## Group analytics

Group analytics allows you to associate an event with a group (e.g. teams, organizations, etc.). Read the [Group Analytics](/docs/user-guides/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](/pricing.md).

Capture an event and associate it with a group:

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_the_user',
    event: 'movie_played',
    properties: {
        movie_id: '123',
        category: 'romcom'
    },
    groups: {
        'company': 'company_id_in_your_db'
    }
})
```

Update properties on a group:

Ruby

PostHog AI

```ruby
posthog.group_identify({
  group_type: 'company',
  group_key: 'company_id_in_your_db',
  properties: {
    name: 'Awesome Inc.'
  }
})
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

If the optional `distinct_id` is not provided in the group identify call, it defaults to `$#{group_type}_#{group_key}` (e.g., `$company_company_id_in_your_db` in the example above). This default behavior will result in each group appearing as a separate person in PostHog. To avoid this, it's often more practical to use a consistent `distinct_id`, such as `group_identifier`.

## Exception capture

You can capture exceptions using the `posthog-ruby` library. This enables you to see stack traces and debug errors in your application. Learn more in our [error tracking docs](/docs/error-tracking/installation/ruby.md).

**Using Rails?**

The [posthog-rails](/docs/libraries/ruby-on-rails.md) gem provides automatic exception capture, ActiveJob instrumentation, and user context out of the box. See our [Rails error tracking guide](/docs/error-tracking/installation/ruby-on-rails.md) for details.

For non-Rails Ruby applications, you can manually capture exceptions with `capture_exception`:

Ruby

PostHog AI

```ruby
begin
  # Code that might raise an exception
  raise StandardError, 'Something went wrong'
rescue => e
  posthog.capture_exception(
    e,
    'user_distinct_id',
    {
      custom_property: 'custom_value'
    }
  )
end
```

The `capture_exception` method accepts the following parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| exception | Exception, String, or exception-like object | The exception to capture. Required. |
| distinct_id | String | The distinct ID of the user. Optional; request context can provide a default, otherwise the SDK generates a UUID. |
| additional_properties | Hash | Additional properties to attach to the exception event. Optional. |
| flags | PostHog::FeatureFlagEvaluations | Optional keyword argument. Adds the same feature flag properties as capture({ flags: flags }). |

You can also override the [fingerprint](/docs/error-tracking/fingerprints.md) to customize how exceptions are grouped into issues:

Ruby

PostHog AI

```ruby
posthog.capture_exception(
  e,
  'user_distinct_id',
  {
    '$exception_fingerprint': 'CustomExceptionGroup'
  }
)
```

## Debug mode

The Ruby SDK logs warnings by default. You can change the log level to `DEBUG` to debug the client:

Ruby

PostHog AI

```ruby
posthog.logger.level = Logger::DEBUG
```

You can also replace the SDK logger globally:

Ruby

PostHog AI

```ruby
PostHog::Logging.logger = Rails.logger
```

## Test helpers

When `test_mode: true`, events remain queued. You can inspect and clear the queue in tests:

Ruby

PostHog AI

```ruby
posthog = PostHog::Client.new({ api_key: '<ph_project_token>', test_mode: true })
posthog.capture({ distinct_id: 'user_123', event: 'test_event' })
posthog.queued_messages
posthog.dequeue_last_message
posthog.clear
```

## Thank you

This library is largely based on the `analytics-ruby` package.

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better