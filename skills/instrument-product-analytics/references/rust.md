> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Rust

Canonical URL: https://posthog.com/docs/libraries/rust

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Installation](#installation)
- [Identifying users](#identifying-users)
- [Capturing events](#capturing-events)
- [Flushing on shutdown](#flushing-on-shutdown)
- [Person profiles and properties](#person-profiles-and-properties)
- [Alias](#alias)
- [Feature flags](#feature-flags)
- [Local evaluation](#local-evaluation)
- [Error tracking](#error-tracking)
- [Observability](#observability)

## Install with the wizard

Run this command in your project directory to add PostHog to your Rust project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

## Installation

Install the `posthog-rs` crate by adding it to your `Cargo.toml`.

Cargo.toml

```toml
[dependencies]
posthog-rs = "0.14"
```

Next, set up the client with your PostHog project key.

```rust
let client = posthog_rs::client("<ph_project_token>").await;
```

### Blocking client

Our Rust SDK supports both blocking and async clients. The async client is the default and is recommended for most use cases.

If you need to use a synchronous client instead – like we do in our [CLI](https://github.com/PostHog/posthog/tree/master/cli) –, you can opt into it by disabling the asynchronous feature on your `Cargo.toml` file.

```toml
[dependencies]
posthog-rs = { version = "0.14", default-features = false }
```

With the blocking client, the same methods are available without `.await`. Either way, `capture` is non-blocking: it hands the event to a background worker that batches and sends it, so it returns immediately instead of waiting on the network. Because delivery happens in the background, call `flush()` or `shutdown()` before your program exits, or buffered events may be lost.

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](https://posthog.com/docs/session-replay.md), [LLM traces](https://posthog.com/docs/ai-engineering.md), or [error tracking](https://posthog.com/docs/error-tracking.md).
>
> See our guide on [identifying users](https://posthog.com/docs/getting-started/identify-users.md) for how to set this up.

## Capturing events

You can send custom events using `capture`:

```rust
let mut event = Event::new("user_signed_up", "distinct_id_of_the_user");
client.capture(event);
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](https://posthog.com/docs/data/events.md#event-properties) object:

```rust
let mut event = Event::new("user_signed_up", "distinct_id_of_the_user");

event.insert_prop("login_type", "email").unwrap();
event.insert_prop("is_free_trial", true).unwrap();

client.capture(event);
```

### Batching events

To capture multiple events at once, use `capture_batch()`:

```rust
let event1 = posthog_rs::Event::new("event 1", "distinct_id_of_user_A");
let event2 = posthog_rs::Event::new("event 2", "distinct_id_of_user_B");

client.capture_batch(vec![event1, event2], false);
```

### Flushing events

`capture` and `capture_batch` return as soon as the event is queued. A background worker batches and sends events for you, so capturing never blocks on the network. Because delivery happens in the background, flush before your program exits or buffered events may be lost:

```rust
// Send queued events now (one delivery attempt per pending batch)
client.flush().await;

// Or flush, stop the background worker, and wait for it to finish (for example, on shutdown)
client.shutdown().await;
```

With the blocking client (`default-features = false`), call `flush()` and `shutdown()` without `.await`.

## Flushing on shutdown

`capture` is fire-and-forget – it queues the event and returns, and a background worker delivers it. Events still queued when the process exits are lost.

Call `flush` and then `shutdown` before your process ends, where your server future resolves – after `run().await` in an actix or axum `main`. If your app has no shutdown path today, that line is still the place – add the calls rather than skipping the flush.

```rust
server.run().await?;
client.flush().await;
client.shutdown().await;
```

## Person profiles and properties

The Rust SDK captures identified events when you pass a `distinct_id` to `Event::new`. These create [person profiles](https://posthog.com/docs/data/persons.md). To set [person properties](https://posthog.com/docs/product-analytics/person-properties.md), include `$set` and `$set_once` properties when capturing an event.

To capture [anonymous events](https://posthog.com/docs/data/anonymous-vs-identified-events.md) without person profiles, use `Event::new_anon`.

## Alias

The Rust SDK doesn't currently expose an `alias` helper. If you need to assign multiple distinct IDs to the same user from Rust, see the [Rust example in the alias docs](https://posthog.com/docs/product-analytics/identify?tab=Rust.md#alias-assigning-multiple-distinct-ids-to-the-same-user).

## Feature flags

PostHog's [feature flags](https://posthog.com/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in Rust:

### Step 1: Evaluate flags once

Call `client.evaluate_flags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

```rust
use posthog_rs::EvaluateFlagsOptions;

let flags = client.evaluate_flags(
    "distinct_id_of_your_user",
    EvaluateFlagsOptions::default(),
).await.unwrap();

if flags.is_enabled("flag-key") {
    // Do something differently for this user
    // Optional: fetch the payload
    let matched_flag_payload = flags.get_flag_payload("flag-key");
}
```

#### Multivariate feature flags

```rust
use posthog_rs::{EvaluateFlagsOptions, FlagValue};

let flags = client.evaluate_flags(
    "distinct_id_of_your_user",
    EvaluateFlagsOptions::default(),
).await.unwrap();

match flags.get_flag("flag-key") {
    Some(FlagValue::String(variant)) if variant == "variant-key" => {
        // Do something differently for this user
        // Optional: fetch the payload
        let matched_flag_payload = flags.get_flag_payload("flag-key");
    }
    _ => {}
}
```

`flags.get_flag()` returns `Some(FlagValue::String(...))` for multivariate flags, `Some(FlagValue::Boolean(true))` for enabled boolean flags, `Some(FlagValue::Boolean(false))` for disabled flags, and `None` when the flag wasn't returned by the evaluation.

> **Note:** `client.is_feature_enabled()`, `client.get_feature_flag()`, `client.get_feature_flag_payload()`, and `client.get_feature_flags()` still work during the migration period, but they're deprecated. Prefer `evaluate_flags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](https://posthog.com/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](https://posthog.com/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to the event

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

```rust
use posthog_rs::{EvaluateFlagsOptions, Event};

let flags = client.evaluate_flags(
    "distinct_id_of_your_user",
    EvaluateFlagsOptions::default(),
).await.unwrap();

if flags.is_enabled("flag-key") {
    // Do something differently for this user
}

let mut event = Event::new("event_name", "distinct_id_of_your_user");
event.with_flags(&flags);
client.capture(event);
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

```rust
// Attach only flags accessed with is_enabled() or get_flag() before this call
let mut event = Event::new("event_name", "distinct_id_of_your_user");
event.with_flags(&flags.only_accessed());
client.capture(event);

// Attach only specific flags
let mut event = Event::new("event_name", "distinct_id_of_your_user");
event.with_flags(&flags.only(&["checkout-flow", "new-dashboard"]));
client.capture(event);
```

`only_accessed()` is order-dependent. If you call it before accessing any flags with `is_enabled()` or `get_flag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

```rust
use posthog_rs::Event;

let mut event = Event::new("event_name", "distinct_id_of_your_user");
event.insert_prop("$feature/feature-flag-key", "variant-key").unwrap();
client.capture(event);
```

### Evaluating only specific flags

By default, `evaluate_flags()` evaluates every flag for the user. If you only need a few flags, pass `flag_keys` to request only those flags:

```rust
use posthog_rs::EvaluateFlagsOptions;

let flags = client.evaluate_flags(
    "distinct_id_of_your_user",
    EvaluateFlagsOptions {
        flag_keys: Some(vec!["checkout-flow".to_string(), "new-dashboard".to_string()]),
        ..Default::default()
    },
).await.unwrap();
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](https://posthog.com/docs/product-analytics/insights.md) on the flag. With `evaluate_flags()`, the SDK sends this event when you call `flags.is_enabled()` or `flags.get_flag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.get_flag_payload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `only_accessed()`.

### Blocking client

If you're using the blocking client (with `default-features = false`), the API is the same but without `.await`:

```rust
use posthog_rs::EvaluateFlagsOptions;

let flags = client.evaluate_flags(
    "distinct_id_of_your_user",
    EvaluateFlagsOptions::default(),
).unwrap();

if flags.is_enabled("flag-key") {
    // Do something differently for this user
}
```

## Local evaluation

For improved performance, you can evaluate feature flags locally by enabling local evaluation. This caches flag definitions and evaluates them without making API requests for each flag check.

To enable local evaluation, you need a [personal API key](https://posthog.com/docs/api/personal-api-keys.md) and to configure the client:

```rust
use posthog_rs::ClientOptionsBuilder;

let options = ClientOptionsBuilder::default()
    .api_key("your-project-api-key")
    .personal_api_key("your-personal-api-key")
    .enable_local_evaluation(true)
    .poll_interval_seconds(30) // Optional, defaults to 30
    .build()
    .unwrap();

let client = posthog_rs::client(options).await;
```

When local evaluation is enabled, flag definitions are fetched on initialization and periodically refreshed in the background. Flag evaluation then happens locally without network requests, providing 100-1000x faster performance.

> **Note:** Local evaluation requires providing any person properties, groups, or group properties needed to evaluate the flag's release conditions, since PostHog can't fetch these automatically without a server request.

## Error tracking

You can capture exceptions with the Rust SDK. `capture_exception` accepts any `std::error::Error` and records a stack trace at the call site; `capture_exception_with` additionally links a person and attaches context:

```rust
use posthog_rs::CaptureExceptionOptions;

let error = std::io::Error::new(std::io::ErrorKind::Other, "connection refused");

// Captured personlessly
client.capture_exception(&error).await.unwrap();

// Associated with a person, with optional context
client.capture_exception_with(
    &error,
    CaptureExceptionOptions::new()
        .distinct_id("user_distinct_id")
        .property("route", "/checkout").unwrap(),
).await.unwrap();
```

To also capture unhandled panics, enable `capture_panics` and initialize the global client with `init_global`. For that and the full setup guide, see the [Rust error tracking installation docs](https://posthog.com/docs/error-tracking/installation/rust.md).

## Observability

The Rust SDK uses [`tracing`](https://docs.rs/tracing) for structured logging. Add a tracing subscriber to your application to see SDK logs:

```rust
use tracing_subscriber::{fmt, EnvFilter};

tracing_subscriber::fmt()
    .with_env_filter(EnvFilter::from_default_env())
    .init();
```

Set `RUST_LOG` to control the log level:

```bash
RUST_LOG=posthog_rs=debug cargo run
```

Use `posthog_rs=warn` for warnings and errors only, or `posthog_rs=trace` for detailed local-evaluation and cache logs.
