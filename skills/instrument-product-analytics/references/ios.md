> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# iOS

Canonical URL: https://posthog.com/docs/libraries/ios

## On this page

- [Installation](#installation)
- [Identifying users](#identifying-users)
- [Offline behavior](#offline-behavior)
- [Using PostHog with application extensions](#using-posthog-with-application-extensions)
- [Method swizzling](#method-swizzling)
- [Push notifications](#push-notifications)
- [Next steps](#next-steps)

The PostHog iOS SDK is a library that you can use to track events, identify users, record session replays, evaluate feature flags, run experiments, build surveys, and more.

This page shows you how to install the SDK and get started with it. If you've already installed the SDK, you can skip ahead to learn about [using the features](https://posthog.com/docs/libraries/ios/usage.md) and [configuring the SDK](https://posthog.com/docs/libraries/ios/configuration.md).

## Installation

PostHog is available through [CocoaPods](http://cocoapods.org) or you can add it as a Swift Package Manager based dependency.

### CocoaPods

Podfile

```ruby
pod "PostHog", "~> 3.59.3"
```

### Swift Package Manager

Add PostHog as a dependency in your Xcode project "Package Dependencies" and select the project target for your app, as appropriate.

For a Swift Package Manager based project, add PostHog as a dependency in your `Package.swift` file's Package dependencies section:

Package.swift

```swift
dependencies: [
  .package(url: "https://github.com/PostHog/posthog-ios.git", from: "3.59.3")
],
```

and then as a dependency for the Package target utilizing PostHog:

Package.swift

```swift
.target(
    name: "myApp",
    dependencies: [.product(name: "PostHog", package: "posthog-ios")]),
```

### Configuration

Configuration is done through the `PostHogConfig` object. Here's a basic configuration example to get you started.

You can find more advanced configuration options in the [configuration page](https://posthog.com/docs/libraries/ios/configuration.md).

## UIKit

```swift
import Foundation
import PostHog
import UIKit

class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_: UIApplication, didFinishLaunchingWithOptions _: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool {
        let POSTHOG_PROJECT_TOKEN = "<ph_project_token>"
        // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
        let POSTHOG_HOST = "https://us.i.posthog.com"

        let config = PostHogConfig(projectToken: POSTHOG_PROJECT_TOKEN, host: POSTHOG_HOST)
        PostHogSDK.shared.setup(config)

        return true
    }
}
```

## SwiftUI

```swift
import SwiftUI
import PostHog

@main
struct YourGreatApp: App {

    // Add PostHog to your app's initializer.
    // If using UIApplicationDelegateAdaptor, see the UIKit tab.

    init() {

        let POSTHOG_PROJECT_TOKEN = "<ph_project_token>"
        // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
        let POSTHOG_HOST = "https://us.i.posthog.com"

        let config = PostHogConfig(projectToken: POSTHOG_PROJECT_TOKEN, host: POSTHOG_HOST)
        PostHogSDK.shared.setup(config)

    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## Identifying users

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](https://posthog.com/docs/session-replay.md), [LLM traces](https://posthog.com/docs/ai-engineering.md), and [error tracking](https://posthog.com/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> Use a stable ID from your auth system when possible, not an email or display name. Send those as person properties instead. If your app has no other stable key, email works as a fallback if they are unique. Never a shared literal like `"anonymous"` or `"user"`, which pools many people onto one person and corrupts their data. When no ID is available at all, skip the identify and retain the anonymous distinct ID that's automatically assigned.
>
> Call `posthog.reset()` on logout, so the next person to use the browser doesn't inherit the last one's identity.
>
> See our guide on [identifying users](https://posthog.com/docs/getting-started/identify-users.md) for how to set this up.

## Offline behavior

The PostHog iOS SDK will continue to capture events when the device is offline. The events are stored in a queue in the device's file storage and are flushed when the device is online.

-   The queue has a maximum size defined by `maxQueueSize` in the configuration.
-   When the queue is full, the oldest event is deleted first.
-   The queue is flushed only when the device is online.

You can find the options for configuring the offline behavior in the [configuration page](https://posthog.com/docs/libraries/ios/configuration.md#all-configuration-options).

## Using PostHog with application extensions

PostHog supports sharing analytics data between your main app and application extensions (such as widgets, app clips, share extensions, and custom keyboards) through App Groups. This ensures that users maintain the same identity across all parts of your app ecosystem.

By default, each iOS app target stores its data in its own sandboxed directory. This means that if a user interacts with your main app and then uses a widget or extension, PostHog would treat them as two different anonymous users. This can lead to:

-   Inflated user counts in your analytics
-   Fragmented user journeys
-   Difficulty tracking feature adoption across your app ecosystem

[Learn more about setting up app groups](https://posthog.com/docs/libraries/ios/configuration.md#setting-up-app-groups).

## Method swizzling

The PostHog iOS SDK uses method swizzling to intercept and modify method calls at runtime to provide advanced features like screen view tracking, element interactions, session replay, surveys, and more.

Method swizzling is particularly important for accurate session metrics tracking. When disabled, the SDK cannot capture optimal session metrics.

You can learn more about configuring method swizzling in the [configuration page](https://posthog.com/docs/libraries/ios/configuration.md#method-swizzling).

## Push notifications

The iOS SDK can register a device for [Workflows](https://posthog.com/docs/workflows.md) push notifications and capture when a user opens one. For setup, including automatic and manual registration, capturing opens, and identity verification, see [Push notifications](https://posthog.com/docs/workflows/push-notifications.md).

## Next steps

Now that you've installed the SDK, explore the configuration and usage options:

-   [Learn about using all of the features of PostHog with iOS SDK](https://posthog.com/docs/libraries/ios/usage.md)
-   [Learn about configuration options for the iOS SDK](https://posthog.com/docs/libraries/ios/configuration.md)
