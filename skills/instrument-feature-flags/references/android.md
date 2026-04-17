# Android Feature Flags installation - Docs

1.  1

    ## Install the dependency

    Required

    Add the PostHog Android SDK to your `build.gradle` dependencies:

    build.gradle

    PostHog AI

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

    PostHog AI

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

    PostHog AI

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

    ## Evaluate boolean feature flags

    Required

    Check if a feature flag is enabled:

    Kotlin

    PostHog AI

    ```kotlin
    val isMyFlagEnabled = PostHog.isFeatureEnabled("flag-key")
    if (isMyFlagEnabled) {
        // Do something differently for this user
        // Optional: fetch the payload
        val matchedFlagPayload = PostHog.getFeatureFlagPayload("flag-key")
    }
    ```

5.  5

    ## Evaluate multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    Kotlin

    PostHog AI

    ```kotlin
    val enabledVariant = PostHog.getFeatureFlag("flag-key")
    if (enabledVariant == "variant-key") { // replace 'variant-key' with the key of your variant
        // Do something differently for this user
        // Optional: fetch the payload
        val matchedFlagPayload = PostHog.getFeatureFlagPayload("flag-key")
    }
    ```

6.  6

    ## Running experiments

    Optional

    Experiments run on top of our feature flags. Once you've implemented the flag in your code, you run an experiment by creating a new experiment in the PostHog dashboard.

7.  7

    ## Next steps

    Recommended

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