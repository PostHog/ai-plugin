# iOS SDK usage - Docs

## Capturing events

You can send custom events using `capture`:

Swift

PostHog AI

```swift
PostHogSDK.shared.capture("user_signed_up")
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

Swift

PostHog AI

```swift
PostHogSDK.shared.capture("user_signed_up", properties: ["login_type": "email"], userProperties: ["is_free_trial": true])
```

## Autocapture

PostHog autocapture automatically tracks the following events for you:

-   **Application Opened** - when the app is opened from a closed state or when the app comes to the foreground (e.g. from the app switcher)
-   **Application Backgrounded** - when the app is sent to the background by the user
-   **Application Installed** - when the app is installed
-   **Application Updated** - when the app is updated
-   **$screen** - when the user navigates (if using `UIViewController`)
-   **$autocapture** - when the user interacts with elements in a screen (`UIKit based`)
-   **$rageclick** - when the user rapidly taps in the same area (iOS/macCatalyst, `UIKit based`)

> 🚧 **Note:** `$autocapture` and `$rageclick` are captured from UIKit interactions. Some SwiftUI views use UIKit under the hood (for example, `TextField` → `UITextField` and `Toggle` → `UISwitch`), so those interactions may also be autocaptured. In other SwiftUI cases, interactions might still be captured, but element metadata (such as `$elements_chain`) may be incomplete.

### Capturing screen views

With [`configuration.captureScreenViews`](/docs/libraries/ios/configuration.md#all-configuration-options) set as `true`, PostHog will try to record all screen changes automatically.

If you want to manually send a new screen capture event, use the `screen` function.

Swift

PostHog AI

```swift
PostHogSDK.shared.screen("Dashboard", properties: ["fromIcon": "bottom"])
```

> **Important:** While `captureScreenViews` works with both `UIKit` and `SwiftUI`, the screen names captured in `SwiftUI` may not be very meaningful as they are based on internal SwiftUI view identifiers. For `SwiftUI` applications, we recommend turning this option off and instead using the `.postHogScreenView()` view modifier (see next section) to capture screen views with meaningful names.

> **Note:** You can use the `BeforeSendBlock` to filter or drop any undesired screen events, giving you control over which screen views are sent to PostHog. See [Amending, dropping or sampling events](/docs/libraries/ios.md#amending-dropping-or-sampling-events) for implementation examples.

### Capturing screen views in SwiftUI

To track a screen view in `SwiftUI`, apply the `postHogScreenView` modifier to your full-screen views. PostHog will send a `$screen` event when the `onAppear` action is executed and will infer a screen name based on the view’s type. You can provide a custom name and event properties if needed.

HomeView.swift

PostHog AI

```swift
// This will trigger a screen view event with $screen_name: "HomeViewContent"
struct HomeView: View {
    var body: some View {
        HomeViewContent()
            .postHogScreenView()
    }
}
// This will trigger a screen view event with $screen_name: "My Home View" and an additional event property from_button: "start"
struct HomeView: View {
    var body: some View {
        HomeViewContent()
            .postHogScreenView("My Home View", ["from_button": "start"])
    }
}
```

In SwiftUI, views can range from entire screens to small UI components. Unlike UIKit, SwiftUI doesn’t clearly distinguish between these levels, which makes automatic tracking of full-screen views harder.

### Adding a custom label on autocaptured elements

PostHog automatically captures interactions with various UI elements in your app, but these interactions are often identified by element type names (e.g., UIButton, UITextField, UILabel).

While this provides basic tracking, it can be challenging to pinpoint specific interactions with particular elements in your analytics. To make your data more meaningful and actionable, you can assign custom labels to any autocaptured element. These labels act as descriptive identifiers, making it easier to identify, filter, and analyze events in your reports.

**Adding a custom label in UIKit**

To assign a custom label to a UIView, use the `postHogLabel` property:

Swift

PostHog AI

```swift
let view = UIView()
view.postHogLabel = "usernameTextField"
```

In this example, interactions with the UITextField will be captured with an additional identifier "usernameTextField".

**Adding a custom label in SwiftUI**

In SwiftUI, use the `.postHogLabel(_:)` modifier instead:

Swift

PostHog AI

```swift
var body: some View {
    ...
    TextField("username", text: $username)
        .postHogLabel("usernameTextField")
}
```

Since SwiftUI's `TextField` uses `UITextField` under the hood, interactions with it will be autocaptured with the additional identifier "usernameTextField".

**Example of generated analytics data**

The generated analytics element in the examples above will have the following form:

Swift

PostHog AI

```swift
<UITextField id="usernameTextField">text value</UITextField>
```

**Filtering for labeled autocaptured elements in reports**

To locate and filter interactions with specific elements in PostHog reports, you can use Autocapture element filters, such as:

-   Tag Name (`UITextField` in this example)
-   Text (`text value` in this example)
-   CSS Selector (the generated `id` attribute in this example)

In the examples above, we can filter for the specific text field using the CSS Selector `#usernameTextField`

### Interaction autocapture

Interaction autocapture records when users interact with UI elements in your app. This includes:

-   User interactions like `touch`, `swipe`, `pan`, `pinch`, `rotation`, `long_press`, `scroll`
-   Control types `value_changed`, `submit`, `toggle`, `primary_action`, `menu_action`, `change`

Interaction autocapture is **not enabled by default**. You can enable it by setting `captureElementInteractions` to `true` in the config.

Swift

PostHog AI

```swift
let config = PostHogConfig(projectToken: <ph_project_token>, host: https://us.i.posthog.com)
config.captureElementInteractions = true // Disabled by default
PostHogSDK.shared.setup(config)
```

### Rage click autocapture

> **Note:** Rage click autocapture for iOS/macCatalyst is available in version 3.51.0+.

A rage click is when a user taps an area multiple times in quick succession (e.g more than 3 taps in 1 second).

This is captured as a `$rageclick` event. You can use this event to identify opportunities to improve your UI, since it's a good indication that users may be frustrated with your product.

It is enabled by default (`rageClickConfig.enabled = true`).

Swift

PostHog AI

```swift
let config = PostHogConfig(projectToken: <ph_project_token>, host: https://us.i.posthog.com)
config.rageClickConfig.enabled = true // Enabled by default
config.rageClickConfig.minimumTapCount = 3 // Optional, default is 3
config.rageClickConfig.thresholdPoints = 30 // Optional, default is 30
config.rageClickConfig.timeoutInterval = 1.0 // Optional, default is 1.0s
PostHogSDK.shared.setup(config)
```

### Autocapture configuration

You can enable or disable autocapture through the `PostHogConfig` object. Find more details about autocapture configuration in the [configuration page](/docs/libraries/ios/configuration.md#autocapture-configuration).

## Preventing sensitive data capture

To exclude specific UI elements from autocapture or session replay, add `ph-no-capture` as either an `accessibilityLabel` or `accessibilityIdentifier`. When PostHog detects this label or identifier anywhere in the view hierarchy, the element will be either ignored or masked:

Swift

PostHog AI

```swift
// This view will be excluded from autocapture
let view = UIView()
view.accessibilityLabel = "ph-no-capture"
```

> **Important:** By default, PostHog will make a best effort to automatically exclude fields detected as sensitive, even without the `ph-no-capture` tag. These include password fields, credit card fields, OTP fields, and any other fields related to Personally Identifiable Information (PII).

For more details on how to setup masking for session replay, please refer to our [privacy controls](/docs/session-replay/privacy?tab=iOS.md) documentation.

## Identifying users

> We highly recommend reading our section on [Identifying users](/docs/integrate/identifying-users.md) to better understand how to correctly use this method.

Using `identify`, you can associate events with specific users. This enables you to gain full insights as to how they're using your product across different sessions, devices, and platforms.

An `identify` call has the following arguments:

-   `distinct_id` which uniquely identifies your user in your database

-   **userProperties:** Optional. A dictionary with key:value pairs to set the [person properties](/docs/product-analytics/person-properties.md)
-   **userPropertiesSetOnce:** Optional. Similar to `userProperties`. [See the difference between `userProperties` and `userPropertiesSetOnce`](/docs/product-analytics/person-properties.md#what-is-the-difference-between-set-and-set_once)

Swift

PostHog AI

```swift
PostHogSDK.shared.identify("user_id_from_your_database",
                            userProperties: ["name": "Peter Griffin", "email": "peter@familyguy.com"],
                            userPropertiesSetOnce: ["date_of_first_log_in": "2024-03-01"])
```

You should call `identify` as soon as you're able to. Typically, this is after your user logs in. This ensures that events sent during your user's sessions are correctly associated with them.

When you call `identify`, all previously tracked anonymous events will be linked to the user.

## Get the current user's distinct ID

You may find it helpful to get the current user's distinct ID. For example, to check whether you've already called `identify` for a user or not.

To do this, call `getDistinctId()`. This returns either the ID automatically generated by PostHog or the ID that has been passed by a call to `identify()`.

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Swift

PostHog AI

```swift
PostHogSDK.shared.alias("alias_id")
```

We strongly recommend reading our docs on [alias](/docs/data/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Anonymous vs identified events

PostHog captures two types of events: [**anonymous** and **identified**](/docs/data/anonymous-vs-identified-events.md)

**Identified events** enable you to attribute events to specific users, and attach [person properties](/docs/product-analytics/person-properties.md). They're best suited for logged-in users.

Scenarios where you want to capture identified events are:

-   Tracking logged-in users in B2B and B2C SaaS apps
-   Doing user segmented product analysis
-   Growth and marketing teams wanting to analyze the *complete* conversion lifecycle

**Anonymous events** are events without individually identifiable data. They're best suited for [web analytics](/docs/web-analytics.md) or apps where users aren't logged in.

Scenarios where you want to capture anonymous events are:

-   Tracking a marketing website
-   Content-focused sites
-   B2C apps where users don't sign up or log in

Under the hood, the key difference between identified and anonymous events is that for identified events we create a [person profile](/docs/data/persons.md) for the user, whereas for anonymous events we do not.

> **Important:** Due to the reduced cost of processing them, anonymous events can be up to 4x cheaper than identified ones, so we recommended you only capture identified events when needed.

### How to capture anonymous events

The iOS SDK captures anonymous events by default. However, this may change depending on your `personProfiles` [config](/docs/libraries/ios/configuration.md#all-configuration-options) when initializing PostHog:

1.  `personProfiles: .identifiedOnly` *(recommended)* *(default)* - Anonymous events are captured by default. PostHog only captures identified events for users where [person profiles](/docs/data/persons.md) have already been created.

2.  `personProfiles: .always` - Capture identified events for all events.

3.  `personProfiles: .never` - Capture anonymous events for all events.

For example:

iOS

PostHog AI

```swift
let config = PostHogConfig(
    projectToken: POSTHOG_PROJECT_TOKEN,
    host: POSTHOG_HOST
)
config.personProfiles = .identifiedOnly
PostHogSDK.shared.setup(config)
```

### How to capture identified events

If you've set the [`personProfiles` config](/docs/libraries/ios/configuration.md#all-configuration-options) to `IDENTIFIED_ONLY` (the default option), anonymous events are captured by default. Then, to capture identified events, call any of the following functions:

-   [`identify()`](/docs/product-analytics/identify.md)
-   [`alias()`](/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user)
-   [`group()`](/docs/product-analytics/group-analytics.md)

When you call any of these functions, it creates a [person profile](/docs/data/persons.md) for the user. Once this profile is created, all subsequent events for this user will be captured as identified events.

Alternatively, you can set `personProfiles` to `ALWAYS` to capture identified events by default.

## Setting person properties

To set [properties](/docs/data/user-properties.md) on your users via an event, you can leverage the event properties `userProperties` and `userPropertiesSetOnce`.

When capturing an event, you can pass a property called `$set` as an event property, and specify its value to be an object with properties to be set on the user that will be associated with the user who triggered the event.

Swift

PostHog AI

```swift
PostHogSDK.shared.capture("signed_up", properties: ["plan": "Pro++"], userProperties: ["user_property_name": "your_value"])
```

`userPropertiesSetOnce` works just like `userProperties`, except that it will **only set the property if the user doesn't already have that property set**.

Swift

PostHog AI

```swift
PostHogSDK.shared.capture("signed_up", properties: ["plan": "Pro++"], userPropertiesSetOnce: ["user_property_name": "your_value"])
```

## Super properties

Super properties are properties associated with events that are set once and then sent with every `capture` call, be it a `$screen`, or anything else.

They are set using `PostHogSDK.shared.register`, which takes a properties object as a parameter, and they persist across sessions.

For example, take a look at the following call:

Swift

PostHog AI

```swift
PostHogSDK.shared.register(["team_id": 22])
```

The call above ensures that every event sent by the user will include `"team_id": 22`. This way, if you filtered events by property using `team_id = 22`, it would display all events captured on that user after the `PostHogSDK.shared.register` call, since they all include the specified Super Property.

However, please note that this does not store properties against the User, only against their events. To store properties against the User object, you should use `PostHogSDK.shared.identify`. More information on this can be found on the [Sending User Information section](#sending-user-information).

### Removing stored super properties

Super properties persist across sessions so you have to explicitly remove them if they are no longer relevant. To stop sending a super property with events, you can use `PostHogSDK.shared.unregister`, like so:

Swift

PostHog AI

```swift
PostHogSDK.shared.unregister("team_id")
```

This removes the super property and subsequent events will not include it.

If you are doing this as part of a user logging out, you can instead simply use `PostHogSDK.shared.reset` which clears all super properties and more.

## Reset after logout

To reset the user's ID and anonymous ID, call `reset`. Usually you would do this right after the user logs out.

Swift

PostHog AI

```swift
PostHogSDK.shared.reset()
```

## Group analytics

Group analytics allows you to associate the events for that person's session with a group (e.g. teams, organizations, etc.). Read the [Group Analytics](/docs/user-guides/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](/pricing.md).

-   Associate the events for this session with a group

Swift

PostHog AI

```swift
PostHogSDK.shared.group(type: "company", key: "company_id_in_your_db")
```

-   Associate the events for this session with a group AND update the properties of that group

Swift

PostHog AI

```swift
PostHogSDK.shared.group(type: "company", key: "company_id_in_your_db", groupProperties: [
    "name": "ACME Corp"
])
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

## Opt out of data capture

You can completely opt-out users from data capture. To do this, there are two options:

1.  Opt users out by default by setting `optOut` to `true` in your PostHog config:

Swift

PostHog AI

```swift
let config = PostHogConfig(projectToken: "<ph_project_token>", host: "https://us.i.posthog.com")
config.optOut = true
PostHogSDK.shared.setup(config)
```

2.  Opt users out on a per-person basis by calling `optOut()`:

Swift

PostHog AI

```swift
PostHogSDK.shared.optOut()
```

Similarly, you can opt users in:

Swift

PostHog AI

```swift
PostHogSDK.shared.optIn()
```

To check if a user is opted out:

Swift

PostHog AI

```swift
PostHogSDK.shared.isOptOut()
```

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

### Boolean feature flags

Swift

PostHog AI

```swift
if (PostHogSDK.shared.isFeatureEnabled("flag-key")) {
    // Do something differently for this user
    // Optional: fetch the payload
    let matchedFlagPayload = PostHogSDK.shared.getFeatureFlagPayload("flag-key")
}
```

### Multivariate feature flags

Swift

PostHog AI

```swift
if (PostHogSDK.shared.getFeatureFlag("flag-key") as? String == "variant-key") { // replace "variant-key" with the key of your variant
    // Do something differently for this user
    // Optional: fetch the payload
    let matchedFlagPayload = PostHogSDK.shared.getFeatureFlagPayload("flag-key")
}
```

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

Swift

PostHog AI

```swift
PostHogSDK.shared.reloadFeatureFlags()
```

### Ensuring flags are loaded before usage

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in the storage.

This means that for most screens, the feature flags are available immediately – **except for the first time a user visits**.

To handle this, you can use the `didReceiveFeatureFlags` notification to wait for the feature flag request to finish:

Swift

PostHog AI

```swift
class AppDelegate: NSObject, UIApplicationDelegate {
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey : Any]? = nil) -> Bool {
        // register for `didReceiveFeatureFlags` notification before SDK initialization
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(receiveFeatureFlags),
            name: PostHogSDK.didReceiveFeatureFlags,
            object: nil
        )
        let POSTHOG_PROJECT_TOKEN = "<ph_project_token>"
        // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
        let POSTHOG_HOST = "https://us.i.posthog.com"
        let config = PostHogConfig(projectToken: POSTHOG_PROJECT_TOKEN, host: POSTHOG_HOST)
        PostHogSDK.shared.setup(config)
        return true
    }
    // The "receiveFeatureFlags" method will be called when the SDK receives the feature flags from the server.
    @objc func receiveFeatureFlags() {
        print("receiveFeatureFlags called")
    }
}
```

Alternatively, you can use the completion block of the `reloadFeatureFlags(_:)` method. This allows you to execute logic immediately after the flags are reloaded:

Swift

PostHog AI

```swift
// Reload feature flags and check if a specific feature is enabled
PostHogSDK.shared.reloadFeatureFlags {
    if PostHogSDK.shared.isFeatureEnabled("flag-key") {
        // do something
    }
}
```

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

Swift

PostHog AI

```swift
if (PostHogSDK.shared.getFeatureFlag("experiment-feature-flag-key") as? String == "variant-name") {
    // do something
}
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## A note about IDFA (identifier for advertisers) collection in iOS 14

Starting with iOS 14, Apple will further restrict apps that track users. Any references to Apple's AdSupport framework, even in strings, [will trip](https://github.com/PostHog/posthog-ios/issues/6) the App Store's static analysis.

Hence **starting with posthog-ios version 1.2.0** we have removed all references to Apple's AdSupport framework.

## Session replay

> **Note:** Session replay is currently only available on iOS. For future macOS support, please follow and upvote [this GitHub issue](https://github.com/PostHog/posthog-ios/issues/200).

To set up [session replay](/docs/session-replay/mobile.md) in your project, all you need to do is install the iOS SDK, enable "Record user sessions" in [your project settings](https://us.posthog.com/settings/project-replay) and enable the `sessionReplay` option.

## Surveys

[Surveys](/docs/surveys.md) launched with [popover presentation](/docs/surveys/creating-surveys.md#presentation) are automatically shown to users matching the [display conditions](/docs/surveys/creating-surveys.md#display-conditions) you set up.

## Debug mode

If you're not seeing the expected events being captured, the feature flags being evaluated, or the surveys being shown, you can enable debug mode to see what's happening.

You can enable debug mode by setting the `debug` option to `true` in the `PostHogConfig` object. A common pattern is to set this to `true` in development environments only for local development.

Swift

PostHog AI

```swift
let config = PostHogConfig(projectToken: "<ph_project_token>", host: "https://us.i.posthog.com")
config.debug = true
PostHogSDK.shared.setup(config)
```

This will enable verbose logs about the inner workings of the SDK.

You can also toggle debug by calling the `PostHogSDK.shared.debug()` method in your code.

Swift

PostHog AI

```swift
// Enable debug mode
PostHogSDK.shared.debug(true)
// Disable debug mode
PostHogSDK.shared.debug(false)
```

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better