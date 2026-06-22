# Go - Docs

This library uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your web app or other server-side application that needs performance.

## Installation

Terminal

PostHog AI

```bash
go get github.com/posthog/posthog-go
```

Go

PostHog AI

```go
package main
import (
    "os"
    "github.com/posthog/posthog-go"
)
func main() {
    client, _ := posthog.NewWithConfig(
        os.Getenv("POSTHOG_API_KEY"),
        posthog.Config{
            PersonalApiKey: "your personal API key", // Optional, but much more performant.  If this token is not supplied, then fetching feature flag values will be slower.
            Endpoint:       "https://us.i.posthog.com",
        },
    )
    defer client.Close()
    // run commands
}
```

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Capturing events

You can send custom events using `capture`:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
  DistinctId: "distinct_id_of_the_user",
  Event: "user_signed_up",
})
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

> **Tip:** You can define event schemas with typed properties and generate type-safe code using [schema management](/docs/product-analytics/schema-management.md).

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id_of_the_user",
    Event:      "user_signed_up",
    Properties: posthog.NewProperties().
      Set("login_type", "email").
      Set("is_free_trial", true),
  })
```

### Capturing pageviews

If you're aiming for a backend-only implementation of PostHog and won't be capturing events from your frontend, you can send `pageviews` from your backend like so:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
  DistinctId: "distinct_id_of_the_user",
  Event:      "$pageview",
  Properties: posthog.NewProperties().
    Set("$current_url", "https://example.com"),
})
```

## Person profiles and properties

For backward compatibility, the Go SDK captures identified events by default. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/data/user-properties.md) in these profiles, include them when capturing an event:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id",
    Event:      "event_name",
    Properties: map[string]interface{}{
        "$set": map[string]interface{}{
            "name": "Max Hedgehog",
        },
        "$set_once": map[string]interface{}{
            "initial_url": "/blog",
        },
    },
})
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/data/user-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id",
    Event:      "event_name",
    Properties: map[string]interface{}{
        "$process_person_profile": false,
    },
})
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Go

PostHog AI

```go
client.Enqueue(posthog.Alias{
  DistinctId: "distinct_id",
  Alias: "alias_id",
})
```

We strongly recommend reading our docs on [alias](/docs/data/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Request context

Use request context to apply a distinct ID, session ID, and common request properties to capture and exception events inside a `net/http` request. This is useful when connecting frontend activity to backend events, session replay, error tracking, and feature flag evaluation.

If you're using [PostHog JS](/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](/docs/libraries/js/config.md#tracing-headers) for your Go backend hostname so browser requests include the session and distinct ID headers. Then wrap your handler with `NewRequestContextMiddleware` and use the context-aware helpers:

Go

PostHog AI

```go
handler := posthog.NewRequestContextMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
    flags, err := posthog.EvaluateFlagsWithContext(r.Context(), client, posthog.EvaluateFlagsPayload{})
    if err != nil {
        // If neither the request context nor payload has a distinct ID,
        // err is posthog.ErrNoDistinctID.
    }
    _ = posthog.EnqueueWithContext(r.Context(), client, posthog.Capture{
        Event: "checkout started",
        Flags: flags,
    })
}))
```

The middleware adds `$current_url`, `$request_method`, `$request_path`, `$user_agent`, and `$ip` properties. By default, it also reads `X-PostHog-Distinct-Id` and `X-PostHog-Session-Id` as request-scoped defaults. Explicit `DistinctId` values and `$session_id` properties passed to captures take precedence over request context.

If request context is attached but no distinct ID is available, capture and exception events are sent as [personless events](/docs/data/anonymous-vs-identified-events.md) with an auto-generated UUID and `$process_person_profile: false`. Calls to `Enqueue` without request context still require `DistinctId`. `EvaluateFlagsWithContext` uses the request-scoped distinct ID when `EvaluateFlagsPayload.DistinctId` is empty, but it never generates personless IDs and returns `ErrNoDistinctID` when no distinct ID is available.

Tracing headers are client-controlled analytics context, not authentication or authorization. For security-sensitive server-side decisions, pass an authenticated `DistinctId` explicitly or attach one to the request context:

Go

PostHog AI

```go
ctx := posthog.WithRequestContext(r.Context(), posthog.RequestContext{
    DistinctId: user.ID,
})
```

To ignore tracing headers while keeping request metadata, disable tracing header capture:

Go

PostHog AI

```go
handler := posthog.NewRequestContextMiddleware(
    next,
    posthog.WithCaptureTracingHeaders(false),
)
```

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in Go:

### Step 1: Evaluate flags once

Call `client.EvaluateFlags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Go

PostHog AI

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: "distinct_id_of_your_user",
})
if err != nil {
    // Handle error (e.g. capture error and fallback to default behavior)
}
if flags.IsEnabled("flag-key") {
    // Do something differently for this user
    // Optional: fetch the payload
    matchedFlagPayload := flags.GetFlagPayload("flag-key")
}
```

#### Multivariate feature flags

Go

PostHog AI

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: "distinct_id_of_your_user",
})
if err != nil {
    // Handle error (e.g. capture error and fallback to default behavior)
}
enabledVariant := flags.GetFlag("flag-key")
if enabledVariant == "variant-key" { // replace "variant-key" with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    matchedFlagPayload := flags.GetFlagPayload("flag-key")
}
```

`flags.GetFlag()` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `nil` when the flag wasn't returned by the evaluation.

> **Note:** `client.IsFeatureEnabled()`, `client.GetFeatureFlag()`, `client.GetFeatureFlagPayload()`, and `Capture.SendFeatureFlags` still work during the migration period, but they're deprecated. Prefer `EvaluateFlags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `Capture`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Go

PostHog AI

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: "distinct_id_of_your_user",
})
if err != nil {
    // Handle error
}
if flags.IsEnabled("flag-key") {
    // Do something differently for this user
}
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id_of_your_user",
    Event:      "event_name",
    Flags:      flags,
})
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

Go

PostHog AI

```go
// Attach only flags accessed with IsEnabled() or GetFlag() before this call
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id_of_your_user",
    Event:      "event_name",
    Flags:      flags.OnlyAccessed(),
})
// Attach only specific flags
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id_of_your_user",
    Event:      "event_name",
    Flags:      flags.Only([]string{"checkout-flow", "new-dashboard"}),
})
```

`OnlyAccessed()` is order-dependent. If you call it before accessing any flags with `IsEnabled()` or `GetFlag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
    DistinctId: "distinct_id_of_your_user",
    Event:      "event_name",
    Properties: posthog.NewProperties().
        Set("$feature/feature-flag-key", "variant-key"), // replace feature-flag-key with your flag key. Replace "variant-key" with the key of your variant
})
```

### Evaluating only specific flags

By default, `EvaluateFlags()` evaluates every flag for the user. If you only need a few flags, pass `FlagKeys` to request only those flags:

Go

PostHog AI

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: "distinct_id_of_your_user",
    FlagKeys:   []string{"checkout-flow", "new-dashboard"},
})
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `EvaluateFlags()`, the SDK sends this event when you call `flags.IsEnabled()` or `flags.GetFlag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.GetFlagPayload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `OnlyAccessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

Go

PostHog AI

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: "distinct_id_of_the_user",
    Groups: posthog.NewGroups().
        Set("your_group_type", "your_group_id").
        Set("another_group_type", "your_group_id"),
    PersonProperties: posthog.NewProperties().
        Set("property_name", "value"),
    GroupProperties: map[string]posthog.Properties{
        "your_group_type": posthog.NewProperties().
            Set("group_property_name", "value"),
        "another_group_type": posthog.NewProperties().
            Set("group_property_name", "value"),
    },
})
if err != nil {
    // Handle error
}
if flags.IsEnabled("flag-key") {
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

You can configure the `FeatureFlagRequestTimeout` parameter when initializing your PostHog client to set a flag request timeout. This helps prevent your code from being blocked if PostHog's servers are too slow to respond. By default, this is set to 3 seconds.

Go

PostHog AI

```go
// import "time"
client, _ := posthog.NewWithConfig(
    os.Getenv("<ph_project_token>"),
    posthog.Config{
        PersonalApiKey:            "your personal API key", // Optional, but much more performant. If this token is not supplied, then fetching feature flag values will be slower.
        Endpoint:                  "https://us.i.posthog.com",
        FeatureFlagRequestTimeout: 3 * time.Second, // Defaults to 3 seconds.
    },
)
```

### Local Evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

Go

PostHog AI

```go
flags, err := client.EvaluateFlags(posthog.EvaluateFlagsPayload{
    DistinctId: "user_distinct_id",
})
if err != nil {
    // Handle error (e.g. capture error and fallback to default behavior)
}
variant := flags.GetFlag("experiment-feature-flag-key")
if variant == "variant-name" {
    // Do something
}
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## Error tracking

You can capture exceptions and errors using the Go SDK. There are two approaches:

**Direct capture** using `NewDefaultException`, which automatically generates a stack trace:

Go

PostHog AI

```go
exception := posthog.NewDefaultException(
    time.Now(),
    "user_distinct_id",
    "DatabaseError",      // type - rendered as title in the UI
    "connection refused",  // value - rendered as description in the UI
)
client.Enqueue(exception)
```

**Automatic capture** using the `SlogCaptureHandler`, which wraps Go's `log/slog` and sends log records at warning level and above as exceptions:

Go

PostHog AI

```go
baseHandler := slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{
    Level: slog.LevelInfo,
})
logger := slog.New(posthog.NewSlogCaptureHandler(baseHandler, client,
    posthog.WithDistinctIDFn(func(ctx context.Context, r slog.Record) string {
        return "user_distinct_id"
    }),
))
// Automatically captured as an exception in PostHog
logger.Warn("Something broke", "error", fmt.Errorf("connection refused"))
```

For the full setup guide, see the [Go error tracking installation docs](/docs/error-tracking/installation/go.md).

## Group analytics

Group analytics allows you to associate an event with a group (e.g. teams, organizations, etc.). Read the [Group Analytics](/docs/user-guides/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](/pricing.md).

-   Send an event associated with a group

Go

PostHog AI

```go
client.Enqueue(posthog.Capture{
    DistinctId: "user_distinct_id",
    Event:      "some_event",
    Groups: posthog.NewGroups().
        Set("company", "company_id_in_your_db"),
})
```

-   Update properties on a group

Go

PostHog AI

```go
client.Enqueue(posthog.GroupIdentify{
    Type: "company",
    Key:  "company_id_in_your_db",
    Properties: posthog.NewProperties().
        Set("name", "Awesome Inc.").
        Set("employees", 11),
})
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

## Thank you

This library is largely based on the `analytics-go` package.

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better