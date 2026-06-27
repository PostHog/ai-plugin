# Rust Feature Flags installation - Docs

Install the `posthog-rs` crate by adding it to your `Cargo.toml`.

Cargo.toml

PostHog AI

```toml
[dependencies]
posthog-rs = "0.14"
```

Next, set up the client with your PostHog project key.

Rust

PostHog AI

```rust
let client = posthog_rs::client("<ph_project_token>").await;
```

### Blocking client

Our Rust SDK supports both blocking and async clients. The async client is the default and is recommended for most use cases.

If you need to use a synchronous client instead – like we do in our [CLI](https://github.com/PostHog/posthog/tree/master/cli) –, you can opt into it by disabling the asynchronous feature on your `Cargo.toml` file.

toml

PostHog AI

```toml
[dependencies]
posthog-rs = { version = "0.14", default-features = false }
```

With the blocking client, the same methods are available without `.await`. Either way, `capture` is non-blocking: it hands the event to a background worker that batches and sends it, so it returns immediately instead of waiting on the network. Because delivery happens in the background, call `flush()` or `shutdown()` before your program exits, or buffered events may be lost.

## Using feature flags

There are two steps to implement feature flags in Rust:

### Step 1: Evaluate flags once

Call `client.evaluate_flags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

Rust

PostHog AI

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

Rust

PostHog AI

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

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to the event

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

Rust

PostHog AI

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

Rust

PostHog AI

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

Rust

PostHog AI

```rust
use posthog_rs::Event;
let mut event = Event::new("event_name", "distinct_id_of_your_user");
event.insert_prop("$feature/feature-flag-key", "variant-key").unwrap();
client.capture(event);
```

### Evaluating only specific flags

By default, `evaluate_flags()` evaluates every flag for the user. If you only need a few flags, pass `flag_keys` to request only those flags:

Rust

PostHog AI

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

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `evaluate_flags()`, the SDK sends this event when you call `flags.is_enabled()` or `flags.get_flag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.get_flag_payload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `only_accessed()`.

### Blocking client

If you're using the blocking client (with `default-features = false`), the API is the same but without `.await`:

Rust

PostHog AI

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