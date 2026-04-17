# Rust Feature Flags installation - Docs

Install the `posthog-rs` crate by adding it to your `Cargo.toml`.

Cargo.toml

PostHog AI

```toml
[dependencies]
posthog-rs = "0.3.5"
```

Next, set up the client with your PostHog project key.

Rust

PostHog AI

```rust
let client = posthog_rs::client(env!("<ph_project_token>"));
```

### Blocking client

Our Rust SDK supports both blocking and async clients. The async client is the default and is recommended for most use cases.

If you need to use a synchronous client instead – like we do in our [CLI](https://github.com/PostHog/posthog/tree/master/cli) –, you can opt into it by disabling the asynchronous feature on your `Cargo.toml` file.

toml

PostHog AI

```toml
[dependencies]
posthog-rs = { version = "0.3.5", default-features = false }
```

In blocking mode, calls to `capture` and related methods will block until the PostHog event capture API returns – generally this is on the order of tens of milliseconds, but you may want to `thread::spawn` a background thread when you send an event.

## Using feature flags

### Boolean feature flags

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

### Multivariate feature flags

Rust

PostHog AI

```rust
use posthog_rs::FlagValue;
match client.get_feature_flag(
    "flag-key".to_string(),
    "distinct_id_of_your_user".to_string(),
    None, None, None
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

### Fetching all flags

Rust

PostHog AI

```rust
let (flags, payloads) = client.get_feature_flags(
    "distinct_id_of_your_user".to_string(),
    None, None, None
).await.unwrap();
for (key, value) in flags {
    println!("Flag {}: {:?}", key, value);
}
```

### Feature flag payloads

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
    None,
    Some(person_props),
    None
).await.unwrap();
```

### With groups

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
    None,
    Some(group_props)
).await.unwrap();
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