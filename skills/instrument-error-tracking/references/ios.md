# iOS error tracking installation - Docs

1.  1

    ## Install dependency

    Required

    Install via Swift Package Manager:

    Package.swift

    PostHog AI

    ```swift
    dependencies: [
      .package(url: "https://github.com/PostHog/posthog-ios.git", from: "3.56.0")
    ]
    ```

    Or add PostHog to your Podfile:

    Podfile

    PostHog AI

    ```ruby
    pod "PostHog", "~> 3.56"
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
            let config = PostHogConfig(projectToken: POSTHOG_PROJECT_TOKEN, host: POSTHOG_HOST)
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

    ## Set up exception autocapture

    Recommended

    **Remote configuration**

    Exception autocapture can also be managed remotely via the [error tracking settings](https://app.posthog.com/settings/project-error-tracking#exception-autocapture).

    **Platform support**

    Exception autocapture is available on **iOS, macOS, and tvOS** only. It is not available on watchOS or visionOS due to platform limitations.

    You can still capture events manually on all platforms, including visionOS.

    You can autocapture exceptions by setting the `errorTrackingConfig.autoCapture` argument to `true` when initializing the PostHog SDK.

    Swift

    PostHog AI

    ```swift
    import PostHog
    let config = PostHogConfig(
        projectToken: "<ph_project_token>",
        host: "https://us.i.posthog.com"
    )
    config.errorTrackingConfig.autoCapture = true
    PostHogSDK.shared.setup(config)
    ```

    When enabled, this automatically captures `$exception` events for:

    -   **Mach exceptions** (e.g., `EXC_BAD_ACCESS`, `EXC_CRASH`)
    -   **POSIX signals** (e.g., `SIGSEGV`, `SIGABRT`, `SIGBUS`)
    -   **Uncaught NSExceptions**

    Crashes are persisted to disk and sent as `$exception` events with level "fatal" on the next app launch.

5.  5

    ## Manually capture exceptions

    Optional

    ### Swift Error handling

    You can manually capture exceptions using the `captureException` method:

    Swift

    PostHog AI

    ```swift
    import PostHog
    do {
        try FileManager.default.removeItem(at: badFileUrl)
    } catch {
        PostHogSDK.shared.captureException(error)
    }
    ```

    ### Objective-C NSException handling

    For Objective-C code that uses NSException:

    Objective-C

    PostHog AI

    ```objc
    @import PostHog;
    @try {
        [self riskyOperation];
    } @catch (NSException *exception) {
        [[PostHogSDK shared] captureExceptionWithNSException:exception properties:nil];
    }
    ```

    ### Adding custom properties

    You can add custom properties to help with debugging, grouping, and analysis:

    Swift

    PostHog AI

    ```swift
    do {
        try performNetworkRequest()
    } catch {
        PostHogSDK.shared.captureException(error, properties: [
            "endpoint": "/api/users",
            "retry_count": 3
        ])
    }
    ```

    This is helpful if you've built your own error handling logic or want to capture exceptions that are handled by your application code.

6.  6

    ## Configure in-app frames

    Optional

    By default, PostHog automatically marks your app's code as "in-app" in stack traces to help you focus on your code rather than system frameworks.

    You can customize this behavior with `errorTrackingConfig`:

    Swift

    PostHog AI

    ```swift
    import PostHog
    let config = PostHogConfig(
        projectToken: "<ph_project_token>",
        host: "https://us.i.posthog.com"
    )
    // Mark additional packages as in-app
    config.errorTrackingConfig.inAppIncludes = [
        "MySharedFramework",
        "MyUtilityLib"
    ]
    // Exclude specific packages from being marked as in-app
    config.errorTrackingConfig.inAppExcludes = [
        "Alamofire",
        "SDWebImage"
    ]
    // Control default behavior for unknown packages
    config.errorTrackingConfig.inAppByDefault = true // default
    PostHogSDK.shared.setup(config)
    ```

    **Configuration options:**

    | Option | Description |
    | --- | --- |
    | inAppIncludes | List of package/bundle identifiers to mark as in-app (takes precedence over excludes) |
    | inAppExcludes | List of package/bundle identifiers to exclude from in-app |
    | inAppByDefault | Whether frames are considered in-app by default when origin cannot be determined |

    **Default behavior:**

    -   Your app's bundle identifier and executable name are automatically included
    -   System frameworks (Foundation, UIKit, etc.) are automatically excluded

7.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

8.  7

    ## Upload dSYMs

    Required

    Great, you're capturing exceptions! The next step is to upload dSYM files so PostHog can symbolicate your crash reports and generate accurate stack traces.

    Let's continue to the next section.

    [Upload dSYMs](/docs/error-tracking/upload-source-maps/ios.md)

## Limitations:

-   System symbols and frames are not symbolicated (UIKit, Foundation, etc.) ([issue](https://github.com/PostHog/posthog/issues/50614)).
-   Swift crashes appear as `SIGTRAP` without the actual error message ([issue](https://github.com/PostHog/posthog-ios/issues/522)).

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better