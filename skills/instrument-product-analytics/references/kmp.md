> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Kotlin Multiplatform

Canonical URL: https://posthog.com/docs/libraries/kmp

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.posthog.com` instead of `https://us.posthog.com` or `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Installation](#installation)
- [Capturing events](#capturing-events)
- [Filter events before sending](#filter-events-before-sending)
- [Identifying users](#identifying-users)
- [Anonymous and identified events](#anonymous-and-identified-events)
- [Get the current user's distinct ID](#get-the-current-users-distinct-id)
- [Alias](#alias)
- [Setting person properties](#setting-person-properties)
- [Super properties](#super-properties)
- [Feature flags](#feature-flags)
- [Experiments (A/B tests)](#experiments-ab-tests)
- [Group analytics](#group-analytics)
- [Screen views](#screen-views)
- [Error tracking](#error-tracking)
- [Session replay](#session-replay)
- [Opt out of data capture](#opt-out-of-data-capture)
- [Session management](#session-management)
- [Flush](#flush)
- [Reset after logout](#reset-after-logout)
- [Close](#close)
- [Debug mode](#debug-mode)
- [All configuration options](#all-configuration-options)
- [Platform support](#platform-support)
- [FAQ](#faq)

The PostHog Kotlin Multiplatform (KMP) SDK lets you capture analytics from shared Kotlin code that runs on Android, iOS, the web, and JVM desktop apps. It's a thin wrapper that delegates to the official PostHog SDKs on each target – [Android](https://posthog.com/docs/libraries/android.md), [iOS](https://posthog.com/docs/libraries/ios.md), [JavaScript](https://posthog.com/docs/libraries/js.md), and the [JVM core library](https://posthog.com/docs/libraries/java.md) on desktop – so you get native batching, queueing, and session replay behind a single common API.

> **Early access:** This SDK is currently in a `0.x` pre-release. The API may change between minor versions until it stabilizes. We'd love your feedback on [GitHub](https://github.com/PostHog/posthog-kmp/issues).

## Install with the wizard

Run this command in your project directory to add PostHog to your Kotlin Multiplatform project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

## Installation

Add the dependency to your shared module's `commonMain` source set:

shared/build.gradle.kts

```kotlin
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("com.posthog:posthog-kmp:<version>")
        }
    }
}
```

If you use a [Gradle version catalog](https://docs.gradle.org/current/userguide/version_catalogs.html), declare it there instead:

gradle/libs.versions.toml

```toml
[versions]
posthog-kmp = "<version>"

[libraries]
posthog-kmp = { group = "com.posthog", name = "posthog-kmp", version.ref = "posthog-kmp" }
```

You can find the latest version on [Maven Central](https://central.sonatype.com/artifact/com.posthog/posthog-kmp).

### Link the iOS Swift package

> **Note:** This setup applies to `posthog-kmp` 0.5.0 and later and requires Kotlin 2.4.0 or later.

On iOS, the SDK uses Kotlin's [Swift Package Manager (SwiftPM) integration](https://kotlinlang.org/docs/multiplatform/multiplatform-spm-import.html) to link the native `posthog-ios` package and copy its resources, including privacy manifests, into your app.

`posthog-kmp` 0.7.0 and later requires iOS 15 or later.

After adding the dependency, run the linkage task once from your project root:

```bash
XCODEPROJ_PATH="$PWD/iosApp/iosApp.xcodeproj" \
./gradlew :shared:integrateLinkagePackage
```

Replace `iosApp/iosApp.xcodeproj` with the path to your Xcode project and `:shared` with the Gradle module that builds your iOS framework.

The task generates a `KotlinMultiplatformLinkedPackage` directory and adds it to the Xcode project. Commit the generated package and Xcode project changes. The package is updated automatically when SwiftPM dependencies change. If the first build after a dependency change stops with `Synthetic project state updated`, run the same build again. You don't need to add `posthog-ios` to Xcode separately.

### Configure the SDK

Initialize PostHog once, early in your app's lifecycle, by calling `PostHog.setup()` with a `PostHogConfig` and a platform `PostHogContext`:

```kotlin
import com.posthog.kmp.PostHog
import com.posthog.kmp.PostHogConfig
import com.posthog.kmp.PostHogContext

PostHog.setup(
    config = PostHogConfig(
        projectToken = "<ph_project_token>",
        host = "https://us.i.posthog.com",
    ),
    context = PostHogContext(), // platform-specific, see below
)
```

You can find your project token and host in [your project settings](https://us.posthog.com/settings/project). For convenience, `PostHogConfig.HOST_US` and `PostHogConfig.HOST_EU` are provided as constants for the two PostHog Cloud hosts.

### Platform-specific setup

The only platform difference is how you build `PostHogContext`. Everything else – event capture, feature flags, config – is shared code.

#### Android

Android requires the `Application` instance, so call `setup` from your `Application` class – not from an Activity, whose `onCreate` re-runs on every recreation (for example, on rotation):

```kotlin
import android.app.Application

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        PostHog.setup(
            config = PostHogConfig(projectToken = "<ph_project_token>"),
            context = PostHogContext(this),
        )
    }
}
```

Register the class in your `AndroidManifest.xml`:

```xml
<application android:name=".MyApplication" ...>
```

#### iOS

On iOS, use the no-argument `PostHogContext()`:

```kotlin
// MainViewController.kt
fun MainViewController() = ComposeUIViewController {
    LaunchedEffect(Unit) {
        PostHog.setup(
            config = PostHogConfig(projectToken = "<ph_project_token>"),
            context = PostHogContext(),
        )
    }
    App()
}
```

#### Web

On the web, use the no-argument `PostHogContext()`:

```kotlin
// main.kt
fun main() {
    PostHog.setup(
        config = PostHogConfig(projectToken = "<ph_project_token>"),
        context = PostHogContext(),
    )
}
```

#### JVM (desktop)

On the JVM – for example, a Compose Multiplatform desktop app – use the no-argument `PostHogContext()`:

```kotlin
// main.kt
fun main() = application {
    PostHog.setup(
        config = PostHogConfig(projectToken = "<ph_project_token>"),
        context = PostHogContext(),
    )
    Window(onCloseRequest = ::exitApplication) { App() }
}
```

##### Configure Compose Desktop release builds

If you package your app with Compose Desktop, add `jdk.unsupported` and a ProGuard configuration file to the `compose.desktop.application` block in your app module's `build.gradle.kts`:

composeApp/build.gradle.kts

```kotlin
compose.desktop {
    application {
        buildTypes.release.proguard {
            configurationFiles.from(project.file("compose-desktop.pro"))
        }

        nativeDistributions {
            modules("jdk.unsupported")
        }
    }
}
```

If you already configure `nativeDistributions.modules`, add `jdk.unsupported` to the existing list.

Create `compose-desktop.pro` next to the module's `build.gradle.kts`:

composeApp/compose-desktop.pro

```text
# PostHog uses Gson reflection for its queue and API payloads.
-keepattributes Signature,*Annotation*
-keep class com.posthog.** { *; }
-keep class com.google.gson.** { *; }

# Compose Desktop's ProGuard optimizer can produce invalid Okio bridge return types.
-keep class okio.** { *; }

# OkHttp probes optional platform and TLS provider classes at runtime.
-dontwarn android.**
-dontwarn dalvik.**
-dontwarn javax.annotation.**
-dontwarn org.bouncycastle.**
-dontwarn org.conscrypt.**
-dontwarn org.openjsse.**
-dontwarn org.codehaus.mojo.animal_sniffer.**
-dontwarn com.jetbrains.SharedTextures

-adaptresourcefilenames okhttp3/internal/publicsuffix/PublicSuffixDatabase.gz
```

Compose Desktop creates release distributions with ProGuard and a custom Java runtime built by `jlink`. The custom runtime doesn't include `jdk.unsupported` automatically, but Gson uses APIs from this module when it deserializes PostHog's queued events and API models. The ProGuard rules preserve reflection-based PostHog and Gson models, prevent invalid Okio bytecode optimization, and retain the OkHttp resources required at runtime.

You must configure both settings in your application because Compose Desktop owns the application's ProGuard and `jlink` configuration. Dependencies such as the PostHog KMP SDK can't modify this release packaging configuration.

On the JVM, the SDK persists its offline event queue and identity cache to disk under `~/.posthog-kmp`. If `user.home` isn't set (for example, in some containers), it falls back to the temp directory and logs a warning.

## Capturing events

You can send custom events using `capture`:

```kotlin
PostHog.capture("user_signed_up")
```

You can add properties to any event by passing a `properties` map:

```kotlin
PostHog.capture(
    event = "purchase_completed",
    properties = mapOf(
        "product_id" to "SKU123",
        "price" to 29.99,
        "currency" to "USD",
    ),
)
```

To attach [group](https://posthog.com/docs/product-analytics/group-analytics.md) context or a custom timestamp to a single event, pass `CaptureOptions`:

```kotlin
import com.posthog.kmp.CaptureOptions

PostHog.capture(
    event = "feature_used",
    properties = mapOf("feature_name" to "export"),
    options = CaptureOptions(groups = mapOf("company" to "acme_corp")),
)
```

> **Note:** Properties with `null` values are dropped before the event is sent, so every platform receives the same event shape.

## Filter events before sending

`beforeSend` is available in PostHog KMP 0.3.0 and later on Android, iOS, JVM, Kotlin/JS, and Kotlin/Wasm. Use version 0.4.2 or later for the exception behavior described below.

Add one or more `PostHogBeforeSend` callbacks to `PostHogConfig.beforeSend`. Return a copied event to modify its name or distinct ID, or to redact properties. Return `null` to drop the event before the SDK queues it:

```kotlin
import com.posthog.kmp.PostHog
import com.posthog.kmp.PostHogBeforeSend
import com.posthog.kmp.PostHogConfig
import com.posthog.kmp.PostHogContext

val config = PostHogConfig(
    projectToken = "<ph_project_token>",
    beforeSend = listOf(
        PostHogBeforeSend { event ->
            event.copy(properties = event.properties - "email")
        },
        PostHogBeforeSend { event ->
            if (event.event == "internal_debug_event") null else event
        },
    ),
)

PostHog.setup(
    config = config,
    context = PostHogContext(),
)
```

Callbacks run synchronously in list order. Each callback receives the event returned by the previous callback. Returning `null` skips the remaining callbacks. If a callback throws, the SDK drops the event and skips the remaining callbacks.

Versions 0.3.0 through 0.4.1 ignore a callback exception and continue with the last valid event.

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](https://posthog.com/docs/session-replay.md), [LLM traces](https://posthog.com/docs/ai-engineering.md), and [error tracking](https://posthog.com/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> Use a stable ID from your auth system when possible, not an email or display name. Send those as person properties instead. If your app has no other stable key, email works as a fallback if they are unique. Never a shared literal like `"anonymous"` or `"user"`, which pools many people onto one person and corrupts their data. When no ID is available at all, skip the identify and retain the anonymous distinct ID that's automatically assigned.
>
> Call `posthog.reset()` on logout, so the next person to use the browser doesn't inherit the last one's identity.
>
> See our guide on [identifying users](https://posthog.com/docs/getting-started/identify-users.md) for how to set this up.

Use `identify` to associate events with a specific user and, optionally, set [person properties](https://posthog.com/docs/product-analytics/person-properties.md):

```kotlin
PostHog.identify(
    distinctId = "user_123",
    userProperties = mapOf(
        "email" to "user@example.com",
        "plan" to "premium",
    ),
)
```

`userPropertiesSetOnce` works just like `userProperties`, except it only sets a property if the user doesn't already have it:

```kotlin
PostHog.identify(
    distinctId = "user_123",
    userPropertiesSetOnce = mapOf(
        "first_seen" to "2025-01-01",
        "signup_source" to "organic",
    ),
)
```

## Anonymous and identified events

PostHog captures two types of events: [**anonymous** and **identified**](https://posthog.com/docs/data/anonymous-vs-identified-events.md)

**Identified events** enable you to attribute events to specific users, and attach [person properties](https://posthog.com/docs/product-analytics/person-properties.md). They're best suited for logged-in users.

Scenarios where you want to capture identified events are:

-   Tracking logged-in users in B2B and B2C SaaS apps
-   Doing user segmented product analysis
-   Growth and marketing teams wanting to analyze the *complete* conversion lifecycle

**Anonymous events** are events without individually identifiable data. They're best suited for [web analytics](https://posthog.com/docs/web-analytics.md) or apps where users aren't logged in.

Scenarios where you want to capture anonymous events are:

-   Tracking a marketing website
-   Content-focused sites
-   B2C apps where users don't sign up or log in

Under the hood, the key difference between identified and anonymous events is that for identified events we create a [person profile](https://posthog.com/docs/data/persons.md) for the user, whereas for anonymous events we do not.

> **Important:** Due to the reduced cost of processing them, anonymous events can be up to 4x cheaper than identified ones, so we recommended you only capture identified events when needed.

## Get the current user's distinct ID

You may find it helpful to get the current user's distinct ID – for example, to check whether you've already called `identify` for a user. Call `getDistinctId()`, which returns either the ID automatically generated by PostHog or the one passed to `identify()`:

```kotlin
val distinctId = PostHog.getDistinctId()
```

## Alias

Sometimes you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible – for example, if a distinct ID used on the frontend isn't available in your backend. Use `alias` to assign another distinct ID to the same user:

```kotlin
PostHog.alias("distinct_id")
```

We strongly recommend reading our docs on [alias](https://posthog.com/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Setting person properties

Besides setting properties during `identify`, you can set person properties directly with `setPersonProperties`:

```kotlin
PostHog.setPersonProperties(
    userProperties = mapOf("plan" to "premium"),
    userPropertiesSetOnce = mapOf("first_seen" to "2025-01-01"),
)
```

## Super properties

Super properties are properties you set once and then send with every subsequent `capture` call. They're set with `PostHog.register`, which takes a key and value, and they persist across sessions:

```kotlin
PostHog.register("team_id", 22)
```

The call above ensures every event sent by the user includes `"team_id": 22`.

> **Note:** This stores properties against the user's events, not against the user profile itself. To store properties against the person, use `identify` or `setPersonProperties`.

To stop sending a super property with events, use `unregister`:

```kotlin
PostHog.unregister("team_id")
```

If you're doing this as part of a user logging out, you can instead call `PostHog.reset()`, which clears all stored super properties and more.

## Feature flags

PostHog's [feature flags](https://posthog.com/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

By default, flags are preloaded on setup (`preloadFeatureFlags = true`). Check whether a flag is enabled:

```kotlin
if (PostHog.isFeatureEnabled("new_dashboard")) {
    showNewDashboard()
}
```

Get the value of a [multivariate flag](https://posthog.com/docs/feature-flags/creating-feature-flags.md#step-3-choose-a-feature-flag-type-required):

```kotlin
when (PostHog.getFeatureFlag("pricing_experiment")) {
    "control" -> showOriginalPricing()
    "variant_a" -> showNewPricing()
    "variant_b" -> showPremiumPricing()
}
```

Get a detailed result, including the flag's [payload](https://posthog.com/docs/feature-flags/payloads.md):

```kotlin
val result = PostHog.getFeatureFlagResult("new_feature")
if (result != null) {
    println("Enabled: ${result.enabled}")
    println("Variant: ${result.variant}")
    println("Value: ${result.value}") // variant if present, otherwise enabled

    // Cast the payload to an expected type
    val payload = result.getPayloadAs<Map<String, Any>>()
}
```

Get every evaluated flag at once as a map of `FeatureFlagResult`:

```kotlin
val allFlags = PostHog.getAllFeatureFlags()
```

Feature flags are fetched on setup and cached. If a user's properties change (for example, after `identify`), reload them so they reflect the latest state:

```kotlin
PostHog.reloadFeatureFlags {
    // flags are now up to date
}
```

## Experiments (A/B tests)

Since [experiments](https://posthog.com/docs/experiments/start-here.md) use feature flags, running one is very similar to the feature flag code above:

```kotlin
if (PostHog.getFeatureFlag("experiment-feature-flag-key") == "variant-name") {
    // do something
}
```

It's also possible to [run experiments without using feature flags](https://posthog.com/docs/experiments/running-experiments-without-feature-flags.md).

## Group analytics

Group analytics lets you associate a user's events with a group (for example, a company, team, or organization). Read the [group analytics](https://posthog.com/docs/product-analytics/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the free plan. Learn more on the [pricing page](https://posthog.com/pricing.md).

Associate the current user's events with a group:

```kotlin
// "company" is the group type, "acme_corp" is the group key
PostHog.group(type = "company", key = "acme_corp")
```

Associate with a group and update that group's properties at the same time:

```kotlin
PostHog.group(
    type = "company",
    key = "acme_corp",
    groupProperties = mapOf(
        "name" to "Acme Corporation",
        "plan" to "enterprise",
    ),
)
```

The `name` is a special property used in the PostHog UI for the group's name. If you don't specify it, the group key is used instead.

## Screen views

Capture a [screen view](https://posthog.com/docs/product-analytics/capture-events.md#capturing-screen-views) with `screen`:

```kotlin
PostHog.screen("Home")
```

You can add properties too:

```kotlin
PostHog.screen(
    screenName = "Product Details",
    properties = mapOf(
        "product_id" to "SKU123",
        "category" to "Electronics",
    ),
)
```

To automatically capture screen views on Android, set `captureScreenViews = true` in your config.

## Error tracking

The PostHog Kotlin Multiplatform SDK 0.4.0 and higher can automatically capture unhandled exceptions. First, turn on **Enable exception autocapture** in your project's [Error Tracking settings](https://app.posthog.com/settings/project-error-tracking#error-tracking-exception-autocapture). This server-side option acts as a kill switch, so the SDK does not automatically capture exceptions when it is disabled.

Then, pass an `ErrorTrackingConfig` when you initialize PostHog:

```kotlin
import com.posthog.kmp.ErrorTrackingConfig

val config = PostHogConfig(
    projectToken = "<ph_project_token>",
    errorTracking = ErrorTrackingConfig(
        autoCapture = true,
        inAppIncludes = listOf("com.example"),
    ),
)
```

On Android, iOS, and JVM, this captures unhandled exceptions. On Kotlin/JS and Kotlin/Wasm, it captures unhandled errors and unhandled promise rejections. It does not capture browser console errors.

Capture handled exceptions with their stack traces by calling `captureException`:

```kotlin
try {
    riskyOperation()
} catch (error: Exception) {
    PostHog.captureException(
        throwable = error,
        additionalProperties = mapOf("context" to "checkout_flow"),
    )
}
```

Follow the [Kotlin Multiplatform Error Tracking guide](https://posthog.com/docs/error-tracking/installation/kmp.md) for setup and verification. Upload [target-specific debug symbols](https://posthog.com/docs/error-tracking/upload-debug-symbols/kmp.md) to get readable stack traces from minified and native builds.

## Session replay

[Session replay](https://posthog.com/docs/session-replay/mobile.md) is available on Android and iOS. To enable it, turn on "Record user sessions" in [your project settings](https://us.posthog.com/settings/project-replay) and pass a `SessionRecordingConfig`:

```kotlin
import com.posthog.kmp.SessionRecordingConfig

PostHog.setup(
    config = PostHogConfig(
        projectToken = "<ph_project_token>",
        sessionRecording = SessionRecordingConfig(
            enabled = true,
            maskAllTextInputs = true, // mask sensitive text (default)
            maskAllImages = true,     // mask images (default)
        ),
    ),
    context = PostHogContext(),
)
```

You can also enable experimental screenshot mode instead of the default wireframe recording:

```kotlin
sessionRecording = SessionRecordingConfig(
    enabled = true,
    screenshot = true,   // capture screenshots instead of wireframes
    maskAllImages = true, // recommended when using screenshots
)
```

> **Warning:** Screenshots may contain sensitive information. Make sure masking is configured appropriately before enabling screenshot mode.

On Android, enable experimental mask-alignment verification to help preserve screenshot captures during pixel-only redraws, such as continuously animated content:

```kotlin
sessionRecording = SessionRecordingConfig(
    enabled = true,
    screenshot = true,
    verifyScreenshotMaskAlignment = true,
)
```

`verifyScreenshotMaskAlignment` defaults to `false` and only affects Android screenshot mode. It adds view-hierarchy walks during capture, so evaluate its performance in your app. Windows with a Compose root already use verification regardless of this flag; setting it to `false` doesn't disable verification for those windows. Other platforms ignore this option.

## Opt out of data capture

You can opt users out of data capture in two ways.

Opt users out by default by setting `optOut` to `true` in your config:

```kotlin
PostHog.setup(
    config = PostHogConfig(projectToken = "<ph_project_token>", optOut = true),
    context = PostHogContext(),
)
```

Or opt a user out (and back in) at runtime:

```kotlin
PostHog.optOut()
PostHog.optIn()
```

Check whether a user is currently opted out:

```kotlin
if (PostHog.isOptedOut()) {
    showConsentBanner()
}
```

## Session management

Access the identifiers PostHog uses for the current session:

```kotlin
val anonymousId = PostHog.getAnonymousId() // before identification
val sessionId = PostHog.getSessionId()
val distinctId = PostHog.getDistinctId()
```

## Flush

You can configure how many events queue before flushing with `flushAt`. Setting this to `1` will send events immediately and will use more battery. The default is `20`.

You can also manually flush the queue to start sending events immediately instead of waiting for the next batch:

```kotlin
PostHog.flush()
```

Flushing is best-effort and asynchronous – it starts sending queued events in the background but doesn't wait for the request to finish, so it isn't a delivery guarantee.

## Reset after logout

To reset the user's ID and anonymous ID, call `reset`. Usually you'd do this right after the user logs out:

```kotlin
PostHog.reset()
```

## Close

To flush queued events and release resources during a clean shutdown, call `close`:

```kotlin
PostHog.close()
```

## Debug mode

If you're not seeing the events, feature flags, or session replay behavior you expect, enable debug mode to see verbose logs about what the SDK is doing:

```kotlin
PostHog.setup(
    config = PostHogConfig(projectToken = "<ph_project_token>", debug = true),
    context = PostHogContext(),
)

// or at runtime
PostHog.setDebug(true)
```

## All configuration options

Pass these to `PostHogConfig` when calling `setup`.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `projectToken` | `String` | **Required** | Your PostHog project token. |
| `host` | `String` | `HOST_US` | PostHog instance URL. Use `PostHogConfig.HOST_US` (`https://us.i.posthog.com`) or `PostHogConfig.HOST_EU` (`https://eu.i.posthog.com`). |
| `debug` | `Boolean` | `false` | Enables verbose SDK logging. |
| `captureApplicationLifecycleEvents` | `Boolean` | `true` | Captures app open/close lifecycle events (mobile). |
| `captureScreenViews` | `Boolean` | `false` | Automatically captures `$screen` events (Android). |
| `captureDeepLinks` | `Boolean` | `true` | Captures deep link opens (Android). |
| `sendFeatureFlagEvent` | `Boolean` | `true` | Sends `$feature_flag_called` when a flag is evaluated. |
| `preloadFeatureFlags` | `Boolean` | `true` | Fetches feature flags automatically during setup. |
| `flushAt` | `Int` | `20` | Number of queued events that triggers a flush. |
| `flushIntervalSeconds` | `Int` | `30` | Maximum delay before queued events are flushed. |
| `maxQueueSize` | `Int` | `1000` | Maximum number of events kept in the queue. |
| `maxBatchSize` | `Int` | `50` | Maximum number of events sent in one batch. |
| `optOut` | `Boolean` | `false` | Starts with analytics opted out. |
| `personProfiles` | `PersonProfiles` | `IDENTIFIED_ONLY` | When person profiles are created: `IDENTIFIED_ONLY`, `ALWAYS`, or `NEVER`. |
| `sessionRecording` | `SessionRecordingConfig?` | `null` | Enables and configures session replay (Android and iOS). |
| `autocapture` | `Boolean` | `false` | Enables automatic event capture where the native platform supports it. |
| `beforeSend` | `List<PostHogBeforeSend>` | `emptyList()` | Modifies or drops events before the SDK queues them. |
| `errorTracking` | `ErrorTrackingConfig?` | `null` | Enables and configures Error Tracking. |

### Error Tracking options

Pass an `ErrorTrackingConfig` to `PostHogConfig.errorTracking`.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `autoCapture` | `Boolean` | `false` | Automatically captures unhandled exceptions. |
| `inAppIncludes` | `List<String>` | `emptyList()` | Package or bundle prefixes to mark as in-app frames (Android, JVM, and iOS). |
| `ignoredExceptionTypes` | `List<KClass<out Throwable>>` | `emptyList()` | Exception types that the SDK should not capture (Android, JVM, and iOS). |
| `inAppExcludes` | `List<String>` | `emptyList()` | Package or bundle prefixes to mark as external frames (iOS only). |
| `inAppByDefault` | `Boolean` | `true` | Marks unmatched stack frames as in-app frames (iOS only). |

### Session recording options

Pass a `SessionRecordingConfig` to `PostHogConfig.sessionRecording`. Defaults match the native Android and iOS SDKs.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `enabled` | `Boolean` | `true` | Enables session recording. |
| `maskAllTextInputs` | `Boolean` | `true` | Masks all text input values. |
| `maskAllImages` | `Boolean` | `true` | Masks all images. |
| `captureNetworkTelemetry` | `Boolean` | `true` | Includes network requests in the recording. |
| `captureLogs` | `Boolean` | `false` | Captures console and system logs (iOS and web). |
| `screenshot` | `Boolean` | `false` | Uses screenshots instead of wireframes (experimental, Android and iOS). |
| `captureLogcat` | `Boolean` | `true` | Captures Android logcat output (Android only). |
| `debouncerDelayMs` | `Long` | `1000` | Touch event debounce delay in milliseconds (Android only). |
| `verifyScreenshotMaskAlignment` | `Boolean` | `false` | Experimental mask-alignment verification for Android screenshot mode. Adds view-hierarchy walks during capture. Compose-rooted windows always use verification. Ignored on other platforms. |

## Platform support

| Platform | Status | Backed by |
| --- | --- | --- |
| Android | ✅ | [PostHog Android](https://posthog.com/docs/libraries/android.md) (native) |
| iOS | ✅ | [PostHog iOS](https://posthog.com/docs/libraries/ios.md) (native, via SwiftPM) |
| Web | ✅ | [PostHog.js](https://posthog.com/docs/libraries/js.md) |
| JVM (desktop) | ✅ | `com.posthog:posthog`, the [JVM core library](https://posthog.com/docs/libraries/java.md) the Android SDK is built on |

Because the SDK delegates to the native library on each platform, feature availability and behavior follow the underlying SDK. Session replay is available on Android and iOS; the web target inherits PostHog.js behavior.

On the JVM, event capture, identification, feature flags, groups, error tracking, and super properties are all supported. Mobile and browser-only concepts don't apply, so `sessionRecording`, `captureApplicationLifecycleEvents`, `captureScreenViews`, `captureDeepLinks`, and `autocapture` are ignored. The JVM also has no standard app-manifest source, so `$app_version`, `$app_build`, and `$app_namespace` person properties aren't set – feature flags targeting those won't match desktop users.

## FAQ

### Which platforms does the KMP SDK support?

Android, iOS, web, and JVM (desktop). The SDK is designed for Kotlin Multiplatform projects – including Compose Multiplatform – that share business logic across these targets.

### Is this different from the Android SDK?

Yes. The [Android SDK](https://posthog.com/docs/libraries/android.md) is for native Android apps. The KMP SDK is for shared Kotlin code targeting multiple platforms, and it wraps the native Android, iOS, and web SDKs so you can call one common API from `commonMain`.

### Why don't I see surveys or logs?

The KMP wrapper currently exposes event capture, identification, feature flags, group analytics, screen tracking, session replay, and error tracking. Surveys and logs aren't wrapped yet. If you'd like [logs](https://posthog.com/docs/logs.md) support, upvote the [logs feature request on GitHub](https://github.com/PostHog/posthog-kmp/issues/30) – subscribing to the issue is the best way to follow along.
