# Ruby - Docs

The `posthog-ruby` library provides tracking functionality on the server-side for applications built in Ruby.

It uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your web app or other server-side application that needs performance.

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

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

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

## Person profiles and properties

The Ruby SDK captures identified events by default. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/data/user-properties.md) in these profiles, include them when capturing an event:

Ruby

PostHog AI

```ruby
posthog.capture(
    distinct_id: 'distinct_id',
    event: 'event_name',
    properties: {
        '$set': { name: 'Max Hedgehog' },
        '$set_once': { initial_url: '/blog' }
    }
)
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/data/user-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

Ruby

PostHog AI

```ruby
posthog.capture(
    distinct_id: 'distinct_id',
    event: 'event_name',
    properties: {
        '$process_person_profile': false
    }
)
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Ruby

PostHog AI

```ruby
posthog.alias(
  distinct_id: "distinct_id",
  alias: "alias_id"
)
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

> **Note:** `posthog.is_feature_enabled()`, `posthog.get_feature_flag()`, `posthog.get_feature_flag_payload()`, and `capture(send_feature_flags: true)` still work during the migration period, but they're deprecated. Prefer `evaluate_flags()` for new code.

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

### Local Evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

#### Evaluating feature flags locally in unicorn server

If you have `preload_app true` in your unicorn config, you can use the [`after_fork`](https://www.rubydoc.info/gems/unicorn/Unicorn%2FConfigurator:after_fork) hook (which is part of the unicorn's configuration) to enable the feature flag cache to receive the updates from posthog dashboard.

Ruby

PostHog AI

```ruby
after_fork do |server, worker|
  $posthog = PostHog::Client.new(
    api_key: '<ph_project_token>',
    personal_api_key: '<ph_personal_api_key>'
    host: 'https://us.i.posthog.com',
    on_error: Proc.new { |status, msg| print msg }
  )
end
```

#### Evaluating feature flags locally in a Puma server

If you use Puma with multiple workers, you can use the `on_worker_boot` hook (which is part of the Puma's configuration) to enable the feature flag cache to receive the updates from PostHog.

Ruby

PostHog AI

```ruby
on_worker_boot do
  $posthog = PostHog::Client.new(
    api_key: '<ph_project_token>',
    personal_api_key: '<ph_personal_api_key>'
    host: 'https://us.i.posthog.com',
    on_error: Proc.new { |status, msg| print msg }
  )
end
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

-   Capture an event and associate it with a group

Ruby

PostHog AI

```ruby
posthog.capture({
    distinct_id: 'distinct_id_of_the_user',
    event: 'movie_played',
    properties: {
        movie_id: '123',
        category: 'romcom'
    }
    groups: {
        'company': 'company_id_in_your_db'
    }
})
```

-   Update properties on a group

Ruby

PostHog AI

```ruby
posthog.group_identify(
  {
    group_type: "company",
    group_key: "company_id_in_your_db",
    properties: {
      name: "Awesome Inc."
    }
  }
)
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

If the optional `distinct_id` is not provided in the group identify call, it defaults to `${groupType}_${groupKey}` (e.g., `$company_company_id_in_your_db` in the example above). This default behavior will result in each group appearing as a separate person in PostHog. To avoid this, it's often more practical to use a consistent `distinct_id`, such as `group_identifier`.

## Exception capture

You can capture exceptions using the `posthog-ruby` library. This enables you to see stack traces and debug errors in your application. Learn more in our [error tracking docs](/docs/error-tracking/installation/ruby.md).

**Using Rails?**

The [posthog-rails](/docs/libraries/ruby-on-rails.md) gem provides automatic exception capture, ActiveJob instrumentation, and user context out of the box. See our [Rails error tracking guide](/docs/error-tracking/installation/ruby-on-rails.md) for details.

For non-Rails Ruby applications, you can manually capture exceptions:

To capture exceptions, use the `capture_exception` method:

Ruby

PostHog AI

```ruby
begin
  # Code that might raise an exception
  raise StandardError, "Something went wrong"
rescue => e
  posthog.capture_exception(
    e,
    distinct_id: 'user_distinct_id',
    properties: {
      custom_property: 'custom_value'
    }
  )
end
```

The `capture_exception` method accepts the following parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| exception | Exception | The exception object to capture (required) |
| distinct_id | String | The distinct ID of the user (optional) |
| properties | Hash | Additional properties to attach to the exception event (optional) |

You can also override the [fingerprint](/docs/error-tracking/fingerprints.md) to customize how exceptions are grouped into issues:

Ruby

PostHog AI

```ruby
posthog.capture_exception(
  e,
  distinct_id: 'user_distinct_id',
  properties: {
    '$exception_fingerprint': 'CustomExceptionGroup'
  }
)
```

## Debug mode

The Ruby SDK debug logs by default. The log level by default is set to `WARN`. You can change it to `DEBUG` if you want to debug the client by running `posthog.logger.level = Logger::DEBUG`, where `posthog` is your initialized `PostHog::Client` instance.

## Thank you

This library is largely based on the `analytics-ruby` package.

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better