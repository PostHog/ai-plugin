# iOS Logs installation - Docs

The PostHog iOS SDK has built-in support for capturing structured Logs from iOS, macOS, tvOS, watchOS, and visionOS apps. The SDK handles OTLP encoding, batching, on-disk persistence across app restarts, and lifecycle integration. You just call `PostHogSDK.shared.captureLog(...)` or `PostHogSDK.shared.logger?.{trace,debug,info,warn,error,fatal}(...)`.

> **Manual capture only.** Logs are emitted by your code. The SDK does not autocapture system log streams (`os_log`, `Logger`, `print`).

> **Minimum version:** `posthog-ios@3.58.0` or later. Run `pod update PostHog` (CocoaPods) or update the package version in Xcode (Swift Package Manager).

1.  1

    ## Install posthog-ios

    Required

    If you haven't installed `posthog-ios` yet, follow the steps below. For full details, see the [iOS SDK guide](/docs/libraries/ios.md).

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

2.  2

    ## Configure logs in your PostHogConfig

    Required

    Configure Logs through `config.logs` before calling `setup(_:)`. All fields are optional; defaults are tuned for mobile (cellular bandwidth, battery, OS lifecycle).

    Swift

    PostHog AI

    ```swift
    import PostHog
    let config = PostHogConfig(projectToken: "<ph_project_token>", host: "https://us.i.posthog.com")
    config.logs.serviceName = "my-app"        // OTLP service.name – shown in the Logs UI
    config.logs.environment = "production"    // OTLP deployment.environment
    config.logs.serviceVersion = "1.2.3"      // OTLP service.version
    PostHogSDK.shared.setup(config)
    ```

    These resource attributes are captured at `setup(_:)` and apply to every batch. Mutating `config.logs` after `setup` has no effect.

3.  3

    ## Capture logs

    Required

    Use `PostHogSDK.shared.logger` for the per-level convenience API, or `PostHogSDK.shared.captureLog` for full control over level, attributes, and trace context.

    Swift

    PostHog AI

    ```swift
    // Per-level convenience methods – Optional, since logger is created at setup
    PostHogSDK.shared.logger?.info("checkout completed", attributes: ["order_id": "ord_789", "amount_cents": 4999])
    PostHogSDK.shared.logger?.warn("payment retry", attributes: ["attempt": 2])
    PostHogSDK.shared.logger?.error("payment failed", attributes: ["code": "E001"])
    // Lower-level API for custom severity / trace context
    PostHogSDK.shared.captureLog(
        "checkout failed",
        level: .error,
        attributes: ["order_id": "ord_789", "step": "auth"],
        traceId: "4bf92f3577b34da6a3ce929d0e0e4736",  // optional W3C trace context (32 hex chars)
        spanId: "00f067aa0ba902b7"                    // optional W3C span (16 hex chars)
    )
    ```

    Available severity levels: `.trace`, `.debug`, `.info`, `.warn`, `.error`, `.fatal`.

    Records are buffered, batched, persisted to disk, and flushed automatically – every 30 seconds, when the buffer hits the threshold, when the app moves to the background, or on `PostHogSDK.shared.flush()`. `flush()` drains events, Session Replay, and Logs together.

    Each record is automatically tagged with the current distinct ID, session ID, current screen, app foreground/background state, and active Feature Flags at the moment of capture.

4.  4

    ## Test your setup

    Recommended

    1.  Capture a test log from your app:

        Swift

        PostHog AI

        ```swift
        PostHogSDK.shared.logger?.info("hello from iOS")
        PostHogSDK.shared.flush()
        ```

    2.  Open the [PostHog Logs UI](https://app.posthog.com/logs).
    3.  Filter by `service.name = 'my-app'` (or whatever value you set above).

    You should see your record arrive within a few seconds.

    [View your Logs in PostHog](https://app.posthog.com/logs)

5.  5

    ## Tune buffering, rate cap, and resource attributes

    Optional

    The `logs` config has knobs for high-volume apps:

    Swift

    PostHog AI

    ```swift
    let config = PostHogConfig(projectToken: "<ph_project_token>")
    config.logs.serviceName = "my-app"
    config.logs.flushIntervalSeconds = 5            // default 30
    config.logs.maxBufferSize = 200                 // default 1000
    config.logs.maxBatchSize = 50                   // default 50
    config.logs.flushAt = 20                        // default 20
    config.logs.rateCapMaxLogs = 5000               // default 500
    config.logs.rateCapWindowSeconds = 60           // default 10
    config.logs.resourceAttributes = ["host.name": "device-01"]
    PostHogSDK.shared.setup(config)
    ```

    Full configuration reference:

    | Field | Default | What it does |
    | --- | --- | --- |
    | serviceName | bundle identifier | OTLP service.name resource attribute |
    | serviceVersion | CFBundleShortVersionString | OTLP service.version resource attribute |
    | environment | nil | OTLP deployment.environment resource attribute |
    | resourceAttributes | [:] | Extra OTLP resource attributes (SDK keys win on collision) |
    | flushIntervalSeconds | 30 | Periodic flush interval |
    | flushAt | 20 | Buffer threshold that triggers an automatic flush |
    | maxBatchSize | 50 | Max records per outbound POST (halved on 413) |
    | maxBufferSize | 1000 | Max records held on disk before FIFO eviction |
    | rateCapMaxLogs | 500 | Max records per rateCapWindowSeconds window. Set to 0 to disable. |
    | rateCapWindowSeconds | 10 | Rate-cap tumbling window length |

    All of the above are captured at `setup(_:)`; mutating them later has no effect. Defaults are tuned for cellular-aware mobile apps. Raise `rateCapMaxLogs` and `maxBufferSize` for high-volume scenarios.

6.  6

    ## Filter or redact with beforeSend

    Optional

    `beforeSend` runs synchronously before the rate cap, so dropped records don't consume the per-window budget. Use it for redaction, sampling, or filtering by level. Each block receives a mutable `PostHogLogRecord` and returns either the (possibly mutated) record or `nil` to drop it.

    Swift

    PostHog AI

    ```swift
    config.logs.setBeforeSend({ record in
        // Drop debug logs in production
        if record.level == .debug { return nil }
        // Redact secrets in the body
        record.body = record.body.replacingOccurrences(
            of: #"api_key=\S+"#,
            with: "api_key=[REDACTED]",
            options: .regularExpression
        )
        return record
    })
    ```

    Pass an array (or a comma-separated list) of blocks to compose a chain – evaluated left-to-right. Returning `nil` from any block short-circuits and drops the record. Setting `record.body` to an empty string also drops the record.

    From Objective-C, wrap each closure in a `BoxedBeforeSendLogBlock`:

    objc

    PostHog AI

    ```objc
    [posthogConfig.logs setBeforeSend:@[
        [[BoxedBeforeSendLogBlock alloc] initWithBlock:^PostHogLogRecord * _Nullable(PostHogLogRecord * record) {
            return [record.body containsString:@"secret"] ? nil : record;
        }]
    ]];
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