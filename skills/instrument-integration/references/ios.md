# iOS - Docs

The PostHog iOS SDK is a library that you can use to track events, identify users, record session replays, evaluate feature flags, run experiments, build surveys, and more.

This page shows you how to install the SDK and get started with it. If you've already installed the SDK, you can skip ahead to learn about [using the features](/docs/libraries/ios/usage.md) and [configuring the SDK](/docs/libraries/ios/configuration.md).

## Installation

PostHog is available through [CocoaPods](http://cocoapods.org) or you can add it as a Swift Package Manager based dependency.

### CocoaPods

Podfile

PostHog AI

```ruby
pod "PostHog", "~> 3.58.0"
```

### Swift Package Manager

Add PostHog as a dependency in your Xcode project "Package Dependencies" and select the project target for your app, as appropriate.

For a Swift Package Manager based project, add PostHog as a dependency in your `Package.swift` file's Package dependencies section:

Package.swift

PostHog AI

```swift
dependencies: [
  .package(url: "https://github.com/PostHog/posthog-ios.git", from: "3.58.0")
],
```

and then as a dependency for the Package target utilizing PostHog:

Package.swift

PostHog AI

```swift
.target(
    name: "myApp",
    dependencies: [.product(name: "PostHog", package: "posthog-ios")]),
```

### Configuration

Configuration is done through the `PostHogConfig` object. Here's a basic configuration example to get you started.

You can find more advanced configuration options in the [configuration page](/docs/libraries/ios/configuration.md).

## UIKit

Swift

PostHog AI

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

Swift

PostHog AI

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

> **Identifying users is required.** Call `posthog.identify('your-user-id')` after login to link events to a known user. This is what connects frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), and [error tracking](/docs/error-tracking.md) to the same person — and lets backend events link back too.
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Offline behavior

The PostHog iOS SDK will continue to capture events when the device is offline. The events are stored in a queue in the device's file storage and are flushed when the device is online.

-   The queue has a maximum size defined by `maxQueueSize` in the configuration.
-   When the queue is full, the oldest event is deleted first.
-   The queue is flushed only when the device is online.

You can find the options for configuring the offline behavior in the [configuration page](/docs/libraries/ios/configuration.md#all-configuration-options).

## Using PostHog with application extensions

PostHog supports sharing analytics data between your main app and application extensions (such as widgets, app clips, share extensions, and custom keyboards) through App Groups. This ensures that users maintain the same identity across all parts of your app ecosystem.

By default, each iOS app target stores its data in its own sandboxed directory. This means that if a user interacts with your main app and then uses a widget or extension, PostHog would treat them as two different anonymous users. This can lead to:

-   Inflated user counts in your analytics
-   Fragmented user journeys
-   Difficulty tracking feature adoption across your app ecosystem

[Learn more about setting up app groups](/docs/libraries/ios/configuration.md#setting-up-app-groups).

## Method swizzling

The PostHog iOS SDK uses method swizzling to intercept and modify method calls at runtime to provide advanced features like screen view tracking, element interactions, session replay, surveys, and more.

Method swizzling is particularly important for accurate session metrics tracking. When disabled, the SDK cannot capture optimal session metrics.

You can learn more about configuring method swizzling in the [configuration page](/docs/libraries/ios/configuration.md#method-swizzling).

## Next steps

Now that you've installed the SDK, explore the configuration and usage options:

-   [Learn about using all of the features of PostHog with iOS SDK](/docs/libraries/ios/usage.md)
-   [Learn about configuration options for the iOS SDK](/docs/libraries/ios/configuration.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better