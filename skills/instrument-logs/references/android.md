# Android Logs installation - Docs

The PostHog Android SDK has built-in support for capturing structured Logs from Android apps. The SDK handles the OTLP encoding, batching, on-disk persistence across app restarts, and lifecycle integration. You just call `PostHog.logger.{trace,debug,info,warn,error,fatal}(...)`.

> **Manual capture only.** Logs are emitted by your code. The SDK does not autocapture system log streams (`Log.d`, `Logcat`, `Timber`).

> **Minimum version:** `com.posthog:posthog-android@3.46.0` or later. Bump the dependency in your `build.gradle` (or `build.gradle.kts`) and re-sync.

1.  1

    ## Install posthog-android

    Required

    If you haven't installed `posthog-android` yet, follow the steps below. For full details, see the [Android SDK guide](/docs/libraries/android.md).

    The best way to install the PostHog Android library is with a build system like [Gradle](https://gradle.org/). This ensures you can easily upgrade to the latest versions.

    All you need to do is add the `posthog-android` module to your App's `build.gradle` or `build.gradle.kts`:

    PostHog AI

    ### app/build.gradle

    ```gradle
    dependencies {
      implementation 'com.posthog:posthog-android:3.+'
    }
    ```

    ### app/build.gradle.kts

    ```kotlin
    dependencies {
      implementation("com.posthog:posthog-android:3.+")
    }
    ```

    ### Configuration

    The best place to initialize the client is in your `Application` subclass.

    Kotlin

    PostHog AI

    ```kotlin
    import android.app.Application
    import com.posthog.android.PostHogAndroid
    import com.posthog.android.PostHogAndroidConfig
    class SampleApp : Application() {
        companion object {
            const val POSTHOG_API_KEY = "<ph_project_token>"
            // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
            const val POSTHOG_HOST = "https://us.i.posthog.com"
        }
        override fun onCreate() {
            super.onCreate()
            val config = PostHogAndroidConfig(
                apiKey = POSTHOG_API_KEY,
                host = POSTHOG_HOST
            )
            PostHogAndroid.setup(this, config)
        }
    }
    ```

2.  2

    ## Configure logs in your PostHogAndroidConfig

    Required

    Configure Logs through `config.logs` before calling `PostHogAndroid.setup(...)`. All fields are optional; defaults are tuned for mobile (cellular bandwidth, battery, app lifecycle).

    Kotlin

    PostHog AI

    ```kotlin
    import com.posthog.android.PostHogAndroid
    import com.posthog.android.PostHogAndroidConfig
    class SampleApp : Application() {
        override fun onCreate() {
            super.onCreate()
            val config = PostHogAndroidConfig(
                apiKey = "<ph_project_token>",
                host = "https://us.i.posthog.com",
            ).apply {
                logs.serviceName = "my-app"        // OTLP service.name – shown in the Logs UI
                logs.environment = "production"    // OTLP deployment.environment
                logs.serviceVersion = "1.2.3"      // OTLP service.version
            }
            PostHogAndroid.setup(this, config)
        }
    }
    ```

    These resource attributes are captured at `setup(...)` and apply to every batch. Mutating `config.logs.serviceName`, `environment`, `serviceVersion`, or `resourceAttributes` after setup has no effect.

3.  3

    ## Capture logs

    Required

    Use `PostHog.logger` for the per-level convenience API.

    Kotlin

    PostHog AI

    ```kotlin
    import com.posthog.PostHog
    import com.posthog.logs.PostHogLogSeverity
    // Per-level convenience methods
    PostHog.logger.info("checkout completed", mapOf("order_id" to "ord_789", "amount_cents" to 4999))
    PostHog.logger.warn("payment retry", mapOf("attempt" to 2))
    PostHog.logger.error("payment failed", mapOf("code" to "E001"))
    // Generic entry point for a runtime severity (e.g. mapping a Timber priority)
    PostHog.logger.log("rendered cart", severity = PostHogLogSeverity.DEBUG)
    ```

    Available severity levels: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`.

    Records are buffered, batched, persisted to disk, and flushed automatically – every 30 seconds, when the buffer hits the threshold, when the app moves to the background, or on `PostHog.flush()`. `flush()` drains events, Session Replay, and Logs together.

    Each record is automatically tagged with the current distinct ID, session ID, current screen, app foreground/background state, and active Feature Flags at the moment of capture.

    From Java:

    Java

    PostHog AI

    ```java
    import com.posthog.PostHog;
    import com.posthog.logs.PostHogLogSeverity;
    import java.util.Map;
    PostHog.Companion.getLogger().info("checkout opened", null);
    PostHog.Companion.getLogger().error(
        "payment failed",
        Map.of("amount_cents", 1999, "currency", "USD")
    );
    ```

4.  4

    ## Test your setup

    Recommended

    1.  Capture a test log from your app:

        Kotlin

        PostHog AI

        ```kotlin
        PostHog.logger.info("hello from Android")
        PostHog.flush()
        ```

    2.  Open the [PostHog Logs UI](https://app.posthog.com/logs).
    3.  Filter by `service.name = 'my-app'` (or whatever value you set above).

    You should see your record arrive within a few seconds.

    [View your Logs in PostHog](https://app.posthog.com/logs)

5.  5

    ## Tune buffering, rate cap, and resource attributes

    Optional

    The `logs` config has knobs for high-volume apps:

    Kotlin

    PostHog AI

    ```kotlin
    val config = PostHogAndroidConfig(apiKey = "<ph_project_token>").apply {
        logs.serviceName = "my-app"
        logs.flushIntervalSeconds = 5            // default 30
        logs.maxBufferSize = 200                 // default 1000
        logs.maxBatchSize = 50                   // default 50
        logs.flushAt = 20                        // default 20
        logs.rateCapMaxLogs = 5000               // default 500
        logs.rateCapWindowSeconds = 60           // default 10
        logs.resourceAttributes = mapOf("host.name" to "device-01")
    }
    PostHogAndroid.setup(this, config)
    ```

    Full configuration reference:

    | Field | Default | What it does |
    | --- | --- | --- |
    | serviceName | app package id | OTLP service.name resource attribute |
    | serviceVersion | BuildConfig.VERSION_NAME | OTLP service.version resource attribute |
    | environment | null | OTLP deployment.environment resource attribute |
    | resourceAttributes | {} | Extra OTLP resource attributes (SDK keys win on collision) |
    | flushIntervalSeconds | 30 | Periodic flush interval |
    | flushAt | 20 | Buffer threshold that triggers an automatic flush |
    | maxBatchSize | 50 | Max records per outbound POST (halved on 413) |
    | maxBufferSize | 1000 | Max records held on disk before FIFO eviction |
    | rateCapMaxLogs | 500 | Max records per rateCapWindowSeconds window. Set to 0 to disable. |
    | rateCapWindowSeconds | 10 | Rate-cap tumbling window length |

    `serviceName`, `serviceVersion`, `environment`, `resourceAttributes`, `flushAt`, and `maxBatchSize` are captured at `setup(...)`; mutating them later has no effect. `flushIntervalSeconds`, `maxBufferSize`, and rate-cap fields are re-read at runtime. Defaults are tuned for cellular-aware mobile apps. Raise `rateCapMaxLogs` and `maxBufferSize` for high-volume scenarios.

6.  6

    ## Filter or redact with beforeSend

    Optional

    `beforeSend` runs synchronously before the rate cap, so dropped records don't consume the per-window budget. Use it for redaction, sampling, or filtering by level. Each hook receives an immutable `PostHogLogRecord` and returns either a (possibly modified) record or `null` to drop it.

    Kotlin

    PostHog AI

    ```kotlin
    config.logs.addBeforeSend { record ->
        // Drop debug logs in production
        if (record.level == PostHogLogSeverity.DEBUG) return@addBeforeSend null
        // Redact secrets in the body
        record.copy(body = record.body.replace(Regex("api_key=\\S+"), "api_key=[REDACTED]"))
    }
    ```

    Call `addBeforeSend` multiple times to compose a chain – hooks are evaluated left-to-right (registration order). Returning `null` from any hook short-circuits and drops the record. A hook that throws is treated the same as returning `null` (the record is dropped, the exception is logged via the SDK's internal debug logger). Returning a record with a blank body also drops the record.

    `addBeforeSend` and `removeBeforeSend` are live – added or removed hooks take effect on the next `captureLog` call.

    From Java, register a `PostHogBeforeSendLog` SAM:

    Java

    PostHog AI

    ```java
    config.getLogs().addBeforeSend(record ->
        record.getBody().contains("secret") ? null : record
    );
    ```

8.  ## Next steps

    Checkpoint

    *What you can do with your logs*

    | Action | Description |
    | --- | --- |
    | [Why you need logs](/docs/logs/basics.md) | What logs show you that nothing else does |
    | [Search logs](/docs/logs/search.md) | Use the search interface to find specific log entries |
    | Filter by level | Filter by INFO, WARN, ERROR, etc. |
    | [Link session replay](/docs/logs/link-session-replay.md) | Connect logs to users and session replays by passing posthogDistinctId and sessionId |
    | [Link logs to a person](/docs/logs/link-person.md) | Surface every log emitted on behalf of a user on their PostHog person profile |
    | [Logging best practices](/docs/logs/best-practices.md) | Learn what to log, how to structure logs, and patterns that make logs useful in production |

    [Troubleshoot common issues](/docs/logs/troubleshooting.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better