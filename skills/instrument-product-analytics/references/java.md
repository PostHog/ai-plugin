> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Java

Canonical URL: https://posthog.com/docs/libraries/java

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Installation](#installation)
- [Integrating with Spring](#integrating-with-spring)
- [Debug mode](#debug-mode)
- [Identifying users](#identifying-users)
- [Capturing events](#capturing-events)
- [Person profiles and properties](#person-profiles-and-properties)
- [Alias](#alias)
- [Group analytics](#group-analytics)
- [Request context](#request-context)
- [Feature flags](#feature-flags)
- [Experiments (A/B tests)](#experiments-ab-tests)
- [GeoIP properties](#geoip-properties)
- [Serverless environments](#serverless-environments)
- [Shutdown](#shutdown)

This is an optional library you can install if you're working with server-side Java applications. It uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your web app or other server side application that needs performance.

## Install with the wizard

Run this command in your project directory to add PostHog to your Java project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

## Installation

The best way to install the PostHog Java SDK is with a build system like Gradle or Maven. This ensures you can easily upgrade to the latest versions.

Look up the latest version of [`com.posthog.posthog-server`](https://central.sonatype.com/artifact/com.posthog/posthog-server).

#### Gradle

All you need to do is add the `posthog-server` module to your `build.gradle`:

build.gradle

```kotlin
dependencies {
  implementation 'com.posthog:posthog-server:2.+'
}
```

#### Maven

All you need to do is add the `posthog-server` module to your `pom.xml`:

pom.xml

```xml
<dependency>
  <groupId>com.posthog</groupId>
  <artifactId>posthog-server</artifactId>
  <version>LATEST</version>
</dependency>
```

#### Other

See [`com.posthog.posthog-server`](https://central.sonatype.com/artifact/com.posthog/posthog-server) in the Maven Central Repository. Clicking on the latest version shows you options for adding dependencies for other build systems.

### Setup

```java
import com.posthog.server.PostHog;
import com.posthog.server.PostHogConfig;
import com.posthog.server.PostHogInterface;

class Sample {
  private static final String POSTHOG_API_KEY = "<ph_project_token>";
  private static final String POSTHOG_HOST = "https://us.i.posthog.com";

  public static void main(String args[]) {
    PostHogConfig config = PostHogConfig
            .builder(POSTHOG_API_KEY)
            .host(POSTHOG_HOST)
            .build();

    PostHogInterface posthog = PostHog.with(config);

    posthog.flush(); // send any remaining events
    posthog.close(); // shut down the client
  }
}
```

## Integrating with Spring

To see how to integrate the PostHog SDK with Spring, check out this [sample project](https://github.com/PostHog/posthog-android/tree/main/posthog-samples/posthog-spring-sample).

## Debug mode

If you're not seeing the expected events being captured, or the feature flags being evaluated, you can enable debug mode to see what's happening.

To see detailed logging, set the debug configuration option to true.

```java
PostHogConfig config = PostHogConfig
          .builder(POSTHOG_API_KEY)
          .host(POSTHOG_HOST)
          .debug(true)
          .build();
```

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](https://posthog.com/docs/session-replay.md), [LLM traces](https://posthog.com/docs/ai-engineering.md), or [error tracking](https://posthog.com/docs/error-tracking.md).
>
> See our guide on [identifying users](https://posthog.com/docs/getting-started/identify-users.md) for how to set this up.

## Capturing events

You can send custom events using `capture`:

```java
posthog.capture("distinct_id_of_the_user", "user_signed_up");
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](https://posthog.com/docs/data/events.md#event-properties) object:

```java
posthog.capture(
    "distinct_id_of_the_user",
    "user_signed_up",
    PostHogCaptureOptions
        .builder()
        .property("login_type", "email")
        .property("is_free_trial", true)
        .build());
```

## Person profiles and properties

The Java SDK captures identified events by default. These create [person profiles](https://posthog.com/docs/data/persons.md). To set [person properties](https://posthog.com/docs/product-analytics/person-properties.md) in these profiles, include them when capturing an event:

```java
posthog.capture(
    "distinct_id_of_the_user",
    "event_name",
    PostHogCaptureOptions
        .builder()
        .userProperty("name", "Max Hedgehog")
        .userPropertySetOnce("initial_url", "/blog")
        .build()
);
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](https://posthog.com/docs/product-analytics/person-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](https://posthog.com/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

```java
posthog.capture(
    "distinct_id_of_the_user",
    "event_name",
    PostHogCaptureOptions
        .builder()
        .property("$process_person_profile", false)
        .build()
);
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

```java
posthog.alias("distinct_id", "alias_id");
```

We strongly recommend reading our docs on [alias](https://posthog.com/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Group analytics

Group analytics allows you to associate an event with a group (e.g. teams, organizations, etc.). Read the [group analytics](https://posthog.com/docs/product-analytics/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on our [pricing page](https://posthog.com/pricing.md).

To create a group, use the `group` method. This associates a user with a group and optionally sets properties on the group:

```java
posthog.group(
    "user_distinct_id",
    "company",
    "company_id_in_your_db",
    Map.of(
        "name", "Acme Corporation",
        "industry", "Technology",
        "employee_count", 500
    )
);
```

You can also create a group without setting properties:

```java
posthog.group("user_distinct_id", "organization", "org_123");
```

To associate an event with a group, include the group information when capturing the event:

```java
posthog.capture(
    "user_distinct_id",
    "some_event",
    PostHogCaptureOptions
        .builder()
        .group("company", "company_id_in_your_db")
        .build()
);
```

## Request context

Use request context to apply a distinct ID, session ID, and common properties to all captures inside a request scope. This allows you to associate frontend user activity with backend events, session replay, error tracking, and feature flag evaluation.

If you're using [PostHog JS](https://posthog.com/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) for your Java backend hostname so browser requests include the session and distinct ID headers.

Then read the incoming headers in your Java request scope:

```java
Map<String, Object> headers = new HashMap<>();
headers.put(
    PostHogRequestContext.DISTINCT_ID_HEADER,
    request.getHeader(PostHogRequestContext.DISTINCT_ID_HEADER)
);
headers.put(
    PostHogRequestContext.SESSION_ID_HEADER,
    request.getHeader(PostHogRequestContext.SESSION_ID_HEADER)
);

Map<String, Object> properties = new HashMap<>();
properties.put("$current_url", request.getRequestURL().toString());
properties.put("$request_method", request.getMethod());
properties.put("$request_path", request.getRequestURI());
properties.put("$user_agent", request.getHeader("User-Agent"));
properties.put("$ip", request.getRemoteAddr());

PostHogRequestContextData context = PostHogRequestContext.fromHeaders(
    headers,
    true,
    properties
);

try (PostHogRequestContext.Scope ignored = PostHogRequestContext.beginScope(context, true)) {
    posthog.capture("backend_event");
    posthog.captureException(error);

    PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags();
    if (flags.isEnabled("new-checkout")) {
        // Do something differently for this request
    }
}
```

`fromHeaders()` reads `X-PostHog-Distinct-Id` and `X-PostHog-Session-Id`. Captures inside the scope use the context distinct ID when you don't pass one explicitly. If no distinct ID is available, captures are sent as [personless events](https://posthog.com/docs/data/anonymous-vs-identified-events.md) with an auto-generated UUID. `evaluateFlags()` returns an empty snapshot when no distinct ID is available.

Pass `false` as the second argument to `fromHeaders()` to ignore client-supplied tracing headers while still attaching request metadata:

```java
PostHogRequestContextData context = PostHogRequestContext.fromHeaders(
    headers,
    false,
    properties
);
```

Tracing headers are client-controlled analytics context, not authentication or authorization context. If an event should be server-authoritative, pass an authenticated distinct ID explicitly.

Request context is stored in a `ThreadLocal`. It applies to work on the same thread while the scope is active. If your framework moves work across threads, propagate the context explicitly in your framework integration.

## Feature flags

PostHog's [feature flags](https://posthog.com/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in Java:

### Step 1: Evaluate flags once

Call `posthog.evaluateFlags()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags("distinct_id_of_your_user");

if (flags.isEnabled("flag-key")) {
    // Do something differently for this user

    // Optional: fetch the payload
    String matchedFlagPayload = flags.getFlagPayload("flag-key");
}
```

#### Multivariate feature flags

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags("distinct_id_of_your_user");

Object flagValue = flags.getFlag("flag-key");
String enabledVariant = flagValue instanceof String ? (String) flagValue : null;

if ("variant-key".equals(enabledVariant)) { // replace "variant-key" with the key of your variant
    // Do something differently for this user

    // Optional: fetch the payload
    String matchedFlagPayload = flags.getFlagPayload("flag-key");
}
```

`flags.getFlag()` returns the variant string for multivariate flags, `true` for enabled boolean flags, `false` for disabled flags, and `null` when the flag wasn't returned by the evaluation.

> **Note:** `posthog.isFeatureEnabled()`, `posthog.getFeatureFlag()`, `posthog.getFeatureFlagPayload()`, and `PostHogCaptureOptions.builder().appendFeatureFlags(true)` still work during the migration period, but they're deprecated. Prefer `evaluateFlags()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](https://posthog.com/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](https://posthog.com/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags("distinct_id_of_your_user");

if (flags.isEnabled("flag-key")) {
    // Do something differently for this user
}

posthog.capture(
    "distinct_id_of_your_user",
    "event_name",
    PostHogCaptureOptions.builder()
        .flags(flags)
        .build()
);
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

```java
// Attach only flags accessed with isEnabled() or getFlag() before this call
posthog.capture(
    "distinct_id_of_your_user",
    "event_name",
    PostHogCaptureOptions.builder()
        .flags(flags.onlyAccessed())
        .build()
);

// Attach only specific flags
posthog.capture(
    "distinct_id_of_your_user",
    "event_name",
    PostHogCaptureOptions.builder()
        .flags(flags.only("checkout-flow", "new-dashboard"))
        .build()
);
```

`onlyAccessed()` is order-dependent. If you call it before accessing any flags with `isEnabled()` or `getFlag()`, no feature flag properties are attached.

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

```java
posthog.capture(
    "distinct_id_of_your_user",
    "event_name",
    PostHogCaptureOptions.builder()
        .property("$feature/feature-flag-key", "variant-key") // replace feature-flag-key with your flag key. Replace "variant-key" with the key of your variant
        .build()
);
```

### Evaluating only specific flags

By default, `evaluateFlags()` evaluates every flag for the user. If you only need a few flags, pass `flagKeys` to request only those flags:

```java
import java.util.Arrays;

PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(
    "distinct_id_of_your_user",
    PostHogEvaluateFlagsOptions.builder()
        .flagKeys(Arrays.asList("checkout-flow", "new-dashboard"))
        .build()
);
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](https://posthog.com/docs/product-analytics/insights.md) on the flag. With `evaluateFlags()`, the SDK sends this event when you call `flags.isEnabled()` or `flags.getFlag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.getFlagPayload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `onlyAccessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](https://posthog.com/docs/product-analytics/person-properties.md), [groups](https://posthog.com/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

```java
import com.posthog.server.PostHogEvaluateFlagsOptions;

PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(
    "distinct_id_of_the_user",
    PostHogEvaluateFlagsOptions.builder()
        .group("your_group_type", "your_group_id")
        .group("another_group_type", "your_group_id")
        .groupProperty("your_group_type", "group_property_name", "value")
        .groupProperty("another_group_type", "group_property_name", "value")
        .personProperty("property_name", "value")
        .build()
);

if (flags.isEnabled("flag-key")) {
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

### Local evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

Local evaluation improves performance by fetching flag definitions once and evaluating them locally, rather than making API calls for each flag check.

#### Configuration

To enable local evaluation, you need:

1.  A **personal API key** (not your project token)
    -   Generate one at: PostHog → Settings → Account → [Personal API Keys](https://app.posthog.com/settings/user-api-keys)
2.  Enable `localEvaluation` in your config

```java
PostHogConfig config = PostHogConfig
    .builder(POSTHOG_API_KEY) // This is your project token
    .host(POSTHOG_HOST)
    .personalApiKey("phx_your_personal_api_key_here") // This is your personal API key, required for local evaluation
    .localEvaluation(true)
    .pollIntervalSeconds(30)  // Optional: customize the rate which flag definitions are polled (default: 30s)
    .build();
```

> **Note:** Setting the `personalApiKey` automatically enables `localEvaluation` unless explicitly set to `false`.

#### Usage with person and group properties

For local evaluation to work, you must provide person properties, groups, or group properties that are used in your flag's [release conditions](https://posthog.com/docs/feature-flags/creating-feature-flags.md#release-conditions).

Use `PostHogEvaluateFlagsOptions` to provide these properties:

**Basic flag evaluation:**

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags("distinct-id");
boolean isEnabled = flags.isEnabled("flag-key");
```

**With person properties:**

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(
    "distinct-id",
    PostHogEvaluateFlagsOptions.builder()
        .personProperty("plan", "premium")
        .personProperty("email", "my-user@example.com")
        .build()
);

boolean isEnabled = flags.isEnabled("flag-key");
```

**With groups:**

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(
    "distinct-id",
    PostHogEvaluateFlagsOptions.builder()
        .group("company", "company_id_in_your_db")
        .build()
);

boolean isEnabled = flags.isEnabled("flag-key");
```

**With group properties:**

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(
    "distinct-id",
    PostHogEvaluateFlagsOptions.builder()
        .group("company", "company_id_in_your_db")
        .groupProperty("company", "industry", "technology")
        .groupProperty("company", "employees", 500)
        .build()
);

boolean isEnabled = flags.isEnabled("flag-key");
```

**Multivariate flags:**

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags(
    "distinct-id",
    PostHogEvaluateFlagsOptions.builder()
        .personProperty("plan", "premium")
        .group("company", "company_id_in_your_db")
        .groupProperty("company", "industry", "technology")
        .build()
);

Object flagValue = flags.getFlag("algorithm");
String algorithm = flagValue instanceof String ? (String) flagValue : "control";

switch (algorithm) {
    case "neural_network":
        useNeuralNetwork();
        break;
    case "collaborative_filtering":
        useCollaborativeFiltering();
        break;
    default:
        useControlAlgorithm();
}
```

#### Limitations

Local evaluation is **not possible** for flags that:

1.  Have **experience continuity** enabled (set when you check "persist flag across authentication steps")
2.  Are linked to an **early access feature**
3.  Depend on **static cohorts**

For these flags, PostHog automatically falls back to remote evaluation via the API.

For more details, see our [local evaluation guide](https://posthog.com/docs/feature-flags/local-evaluation.md).

### Feature flag caching

To improve performance and reduce API calls, the Java SDK caches feature flag results in memory. You can configure the cache behavior when initializing PostHog:

```java
PostHogConfig config = PostHogConfig
    .builder(POSTHOG_API_KEY)
    .featureFlagCacheSize(1000)        // Maximum number of cached flag results (default: 1000)
    .featureFlagCacheMaxAgeMs(300000)  // Cache expiry in milliseconds (default: 300000 = 5 minutes)
    .build();
```

**Configuration options:**

-   `featureFlagCacheSize`: The maximum number of feature flag results to cache in memory (default: `1000`)
-   `featureFlagCacheMaxAgeMs`: The maximum age of a cached feature flag result in milliseconds (default: `300000` or 5 minutes)

Cached results are stored per distinct ID and flag key combination. When a cached result expires or the cache is full, the SDK will fetch fresh results from the PostHog API.

## Experiments (A/B tests)

Since [experiments](https://posthog.com/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

```java
PostHogFeatureFlagEvaluations flags = posthog.evaluateFlags("user_distinct_id");
Object flagValue = flags.getFlag("recommendation_algorithm");
String variant = flagValue instanceof String ? (String) flagValue : "control";

if ("neural_network".equals(variant)) {
    // Do something differently for this user
}
```

It's also possible to [run experiments without using feature flags](https://posthog.com/docs/experiments/running-experiments-without-feature-flags.md).

## GeoIP properties

The `posthog-server` library disregards the server IP, does not add the GeoIP properties, and does not use the values for feature flag evaluations.

## Serverless environments

By default, the library buffers events before sending them to the `/batch` endpoint for better performance. This can lead to lost events in serverless environments if the Java process is terminated by the platform before the buffer is fully flushed.

To avoid this, call `posthog.flush()` after processing every request. This allows `posthog.capture()` to remain asynchronous for better performance.

```java
posthog.flush();
```

## Shutdown

When you're done using PostHog, make sure to call `close()` to ensure all events are flushed before your application exits:

```java
posthog.close();
```
