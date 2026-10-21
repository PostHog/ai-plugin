> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Android Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/android

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install the dependency](#install-the-dependency)
- [Configure PostHog](#configure-posthog)
- [Send events](#send-events)
- [Set up exception autocapture](#set-up-exception-autocapture)
- [Manually capture exceptions](#manually-capture-exceptions)
- [Verify error tracking](#verify-error-tracking)
- [Upload mapping files](#upload-mapping-files)

1.  1

    ## Install the dependency

    Required

    Add the PostHog Android SDK to your `build.gradle` dependencies:

    build.gradle

    ```kotlin
    dependencies {
        implementation("com.posthog:posthog-android:3.+")
    }
    ```

2.  2

    ## Configure PostHog

    Required

    Initialize PostHog in your Application class:

    SampleApp.kt

    ```kotlin
    class SampleApp : Application() {
    
        companion object {
            const val POSTHOG_PROJECT_TOKEN = "<ph_project_token>"
            const val POSTHOG_HOST = "https://us.i.posthog.com"
        }
    
        override fun onCreate() {
            super.onCreate()
    
            // Create a PostHog Config with the given project token and host
            val config = PostHogAndroidConfig(
                apiKey = POSTHOG_PROJECT_TOKEN,
                host = POSTHOG_HOST
            )
    
            // Setup PostHog with the given Context and Config
            PostHogAndroid.setup(this, config)
        }
    }
    ```

3.  3

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events to test your integration:

    Kotlin

    ```kotlin
    import com.posthog.PostHog
    
    PostHog.capture(
        event = "button_clicked",
        properties = mapOf(
            "button_name" to "signup"
        )
    )
    ```

4.  4

    ## Set up exception autocapture

    Recommended

    **Client-side configuration only**

    Support for remote configuration in the [error tracking settings](https://app.posthog.com/settings/project-error-tracking#exception-autocapture) requires SDK version 3.32.0 or higher.

    You can autocapture exceptions by setting the `errorTrackingConfig.autoCapture` argument to `true` when initializing the PostHog SDK.

    Kotlin

    ```kotlin
    import com.posthog.android.PostHogAndroidConfig
    val config = PostHogAndroidConfig(
        apiKey = POSTHOG_PROJECT_TOKEN,
        host = POSTHOG_HOST
    ).apply {
        ...
        errorTrackingConfig.autoCapture = true
    }
    ...
    ```

    When enabled, this automatically captures `$exception` events when errors are thrown by wrapping the `Thread.UncaughtExceptionHandler` listener.

    **Planned features**

    We currently don't support [source code context](https://posthog.com/docs/error-tracking/stack-traces.md) associated with an exception.

    These features will be added in a future release.

5.  5

    ## Manually capture exceptions

    Optional

    It is also possible to manually capture exceptions using the `captureException` method:

    Kotlin

    ```kotlin
    PostHog.captureException(
        exception,
        properties = additionalProperties
    )
    ```

    This is helpful if you've built your own error handling logic or want to capture exceptions that are handled by your application code.

6.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

7.  6

    ## Upload mapping files

    Required

    Great, you're capturing exceptions! The next step is to upload ProGuard/R8 mapping files so PostHog can deobfuscate your stack traces.

    Let's continue to the next section.

    [Upload mapping files](https://posthog.com/docs/error-tracking/upload-mappings/android.md)
