# iOS Feature Flags installation - Docs

1.  1

    ## Install dependency

    Required

    Install via Swift Package Manager:

    Package.swift

    PostHog AI

    ```swift
    dependencies: [
      .package(url: "https://github.com/PostHog/posthog-ios.git", from: "3.0.0")
    ]
    ```

    Or add PostHog to your Podfile:

    Podfile

    PostHog AI

    ```ruby
    pod "PostHog", "~> 3.0"
    ```

2.  2

    ## Configure PostHog

    Required

    Initialize PostHog in your AppDelegate:

    AppDelegate.swift

    PostHog AI

    ```swift
    import Foundation
    import PostHog
    import UIKit
    class AppDelegate: NSObject, UIApplicationDelegate {
        func application(_: UIApplication, didFinishLaunchingWithOptions _: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
            let POSTHOG_PROJECT_TOKEN = "<ph_project_token>"
            let POSTHOG_HOST = "https://us.i.posthog.com"
            let config = PostHogConfig(apiKey: POSTHOG_PROJECT_TOKEN, host: POSTHOG_HOST)
            PostHogSDK.shared.setup(config)
            return true
        }
    }
    ```

3.  3

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events to test your integration:

    Swift

    PostHog AI

    ```swift
    PostHogSDK.shared.capture("button_clicked", properties: ["button_name": "signup"])
    ```

4.  4

    ## Evaluate boolean feature flags

    Required

    Check if a feature flag is enabled:

    Swift

    PostHog AI

    ```swift
    let isMyFlagEnabled = PostHogSDK.shared.isFeatureEnabled("flag-key")
    if isMyFlagEnabled {
        // Do something differently for this user
        // Optional: fetch the payload
        let matchedFlagPayload = PostHogSDK.shared.getFeatureFlagPayload("flag-key")
    }
    ```

5.  5

    ## Evaluate multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    Swift

    PostHog AI

    ```swift
    let enabledVariant = PostHogSDK.shared.getFeatureFlag("flag-key")
    if enabledVariant == "variant-key" { // replace 'variant-key' with the key of your variant
        // Do something differently for this user
        // Optional: fetch the payload
        let matchedFlagPayload = PostHogSDK.shared.getFeatureFlagPayload("flag-key")
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