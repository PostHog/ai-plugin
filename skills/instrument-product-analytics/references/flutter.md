# Flutter - Docs

This is an optional library you can install if you're working with Flutter. It uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your mobile app.

PostHog supports the iOS, macOS, Android, and Web platforms.

## Installation

PostHog is available for install via [Pub](https://pub.dev/packages/posthog_flutter).

### Configuration

Set your PostHog project token and enable automatic event tracking if you want the library to capture lifecycle events for you.

Remember that the application lifecycle events won't have any special context set for you by the time it is initialized. If you are using a self-hosted instance of PostHog you will need to have the public hostname or IP for your instance as well.

To start, add `posthog_flutter` to your `pubspec.yaml`:

pubspec.yaml

PostHog AI

```yaml
# rest of your code
dependencies:
  flutter:
    sdk: flutter
  posthog_flutter: ^5.26.0
# rest of your code
```

Then complete the setup for each platform:

> For Session Replay and Surveys, you must set up the SDK manually by disabling the `com.posthog.posthog.AUTO_INIT` mode.

#### Android setup

There are 2 ways of initializing the SDK, automatically and manually.

Automatically:

Add your PostHog configuration to your `AndroidManifest.xml` file located in the `android/app/src/main`:

android/app/src/main/AndroidManifest.xml

PostHog AI

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="your.package.name">
    <application>
        <!-- ... other configuration ... -->
        <meta-data android:name="com.posthog.posthog.PROJECT_TOKEN" android:value="<ph_project_token>" />
        <meta-data android:name="com.posthog.posthog.POSTHOG_HOST" android:value="https://us.i.posthog.com" />  <!-- usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com' -->
        <!-- com.posthog.posthog.CAPTURE_APPLICATION_LIFECYCLE_EVENTS is enabled by default since version 5.23.0 (previously named TRACK_APPLICATION_LIFECYCLE_EVENTS, which still works as an alias) -->
        <meta-data android:name="com.posthog.posthog.DEBUG" android:value="true" />
    </application>
</manifest>
```

Or manually (more control and more configurations available):

Add your PostHog configuration to your `AndroidManifest.xml` file located in the `android/app/src/main`:

android/app/src/main/AndroidManifest.xml

PostHog AI

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="your.package.name">
    <application>
        <!-- ... other configuration ... -->
        <meta-data android:name="com.posthog.posthog.AUTO_INIT" android:value="false" />
    </application>
</manifest>
```

In both cases, you'll also need to update the minimum Android SDK version to `23` in `android/app/build.gradle`:

android/app/build.gradle

PostHog AI

```kotlin
// rest of your config
    defaultConfig {
        minSdkVersion 23
        // rest of your config
    }
// rest of your config
```

#### iOS setup

There are 2 ways of initializing the SDK, automatically and manually.

You'll need to have [Cocoapods](https://guides.cocoapods.org/using/getting-started.html) installed.

Automatically:

Add your PostHog configuration to the `Info.plist` file located in the `ios/Runner` directory:

ios/Runner/Info.plist

PostHog AI

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- rest of your configuration -->
    <key>com.posthog.posthog.PROJECT_TOKEN</key>
    <string><ph_project_token></string>
    <key>com.posthog.posthog.POSTHOG_HOST</key>
    <string>https://us.i.posthog.com</string>
    <!-- com.posthog.posthog.CAPTURE_APPLICATION_LIFECYCLE_EVENTS is enabled by default since version 5.23.0 -->
    <key>com.posthog.posthog.DEBUG</key>
    <true/>
</dict>
</plist>
```

Or manually (more control and more configurations available):

Add your PostHog configuration to the `Info.plist` file located in the `ios/Runner` directory:

ios/Runner/Info.plist

PostHog AI

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- rest of your configuration -->
    <key>com.posthog.posthog.AUTO_INIT</key>
    <false/>
</dict>
</plist>
```

In both cases, you'll need to set the minimum platform version to iOS 13.0 in your Podfile:

ios/Podfile

PostHog AI

```yaml
platform :ios, '13.0'
# rest of your config
```

#### Dart setup (For manual step only)

If you followed the automatic SDK setup, then there's no more configuration needed in Dart.

If you followed the manual SDK setup:

Dart

PostHog AI

```dart
import 'package:flutter/material.dart';
import 'package:posthog_flutter/posthog_flutter.dart';
Future<void> main() async {
  // init WidgetsFlutterBinding if not yet
  WidgetsFlutterBinding.ensureInitialized();
  final config = PostHogConfig('<ph_project_token>');
  config.debug = true;
  // captureApplicationLifecycleEvents is enabled by default since version 5.23.0
  config.host = 'https://us.i.posthog.com';
  await Posthog().setup(config);
  runApp(MyApp());
}
```

#### Web setup

For Web, add your `Web snippet` (which you can find in [your project settings](https://us.posthog.com/settings/project#snippet)) in the `<header>` of your `web/index.html` file:

web/index.html

PostHog AI

```html
<!DOCTYPE html>
<html>
  <head>
    <!-- ... other head elements ... -->
    <script async>
      !(function (t, e) {
        var o, n, p, r;
        e.__SV ||
          ((window.posthog = e),
          (e._i = []),
          (e.init = function (i, s, a) {
            function g(t, e) {
              var o = e.split(".");
              (2 == o.length && ((t = t[o[0]]), (e = o[1])),
                (t[e] = function () {
                  t.push([e].concat(Array.prototype.slice.call(arguments, 0)));
                }));
            }
            (((p = t.createElement("script")).type = "text/javascript"),
              (p.crossOrigin = "anonymous"),
              (p.async = !0),
              (p.src = s.api_host + "/static/array.js"),
              (r = t.getElementsByTagName("script")[0]).parentNode.insertBefore(p, r));
            var u = e;
            for (
              void 0 !== a ? (u = e[a] = []) : (a = "posthog"),
                u.people = u.people || [],
                u.toString = function (t) {
                  var e = "posthog";
                  return ("posthog" !== a && (e += "." + a), t || (e += " (stub)"), e);
                },
                u.people.toString = function () {
                  return u.toString(1) + ".people (stub)";
                },
                o =
                  "capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagResult reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep onSessionId".split(
                    " ",
                  ),
                n = 0;
              n < o.length;
              n++
            )
              g(u, o[n]);
            e._i.push([i, s, a]);
          }),
          (e.__SV = 1));
      })(document, window.posthog || []);
      posthog.init("<ph_project_token>", {
        api_host: "https://us.i.posthog.com", // 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
        defaults: "2026-05-30",
      });
    </script>
  </head>
  <!-- other elements -->
</html>
```

For more information please check: /docs/libraries/js

## Capturing events

You can send custom events using `capture`:

Dart

PostHog AI

```dart
await Posthog().capture(
  eventName: 'user_signed_up',
);
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

Dart

PostHog AI

```dart
await Posthog().capture(
  eventName: 'user_signed_up',
  properties: {
    'login_type': 'email',
    'is_free_trial': true
  }
);
```

### Autocapture

PostHog autocapture automatically tracks the following events for you:

-   **Application Opened** - when the app is opened from a closed state or when the app comes to the foreground (e.g. from the app switcher)
-   **Application Backgrounded** - when the app is sent to the background by the user
-   **Application Installed** - when the app is installed.
-   **Application Updated** - when the app is updated.
-   **$screen** - when the user navigates (if using [navigatorObservers](https://docs.flutter.dev/ui/navigation) or [go\_router](https://pub.dev/packages/go_router). You'd need to set up the `PosthogObserver` manually.)
-   **$exception** - when the app throws exceptions.

### Capturing screen views

> Note: Your routes should be named. Otherwise, they won't be recorded.

#### Using `navigatorObservers`

Add the `PosthogObserver` to record screen views automatically:

Dart

PostHog AI

```dart
import 'package:flutter/material.dart';
import 'package:posthog_flutter/posthog_flutter.dart';
void main() => runApp(MyApp());
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // If you're using session replay, `PostHogWidget` has to be the root, and `MaterialApp` must be the child.
    return MaterialApp(
      navigatorObservers: [
        // The PosthogObserver records screen views automatically
        PosthogObserver(),
      ],
      ...
    );
  }
}
```

Name your routes:

Dart

PostHog AI

```dart
...
MaterialPageRoute(builder: (context) => const HomeScreenRoute(),
  settings: const RouteSettings(name: 'Home Screen'),
),
...
```

#### Using `go_router`

Add the `PosthogObserver` to record screen views automatically:

Dart

PostHog AI

```dart
import 'package:flutter/material.dart';
import 'package:posthog_flutter/posthog_flutter.dart';
import 'package:go_router/go_router.dart';
// GoRouter configuration
final _router = GoRouter(
  routes: [
    ...
  ],
  // The PosthogObserver records screen views automatically
  observers: [PosthogObserver()],
);
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // If you're using session replay, `PostHogWidget` has to be the root, and `MaterialApp` must be the child.
    return MaterialApp.router(
      routerConfig: _router,
    );
  }
}
```

Name your routes:

Dart

PostHog AI

```dart
...
GoRoute(
  name: 'Home Screen',
  ...
),
...
```

## Identifying users

> We highly recommend reading our section on [Identifying users](/docs/integrate/identifying-users.md) to better understand how to correctly use this method.

Using `identify`, you can associate events with specific users. This enables you to gain full insights as to how they're using your product across different sessions, devices, and platforms.

An `identify` call has the following arguments:

-   **userId:** Required. A unique identifier for your user. Typically either their email or database ID.
-   **userProperties:** Optional. A dictionary with key:value pairs to set the [person properties](/docs/product-analytics/person-properties.md)
-   **userPropertiesSetOnce:** Optional. Similar to `userProperties`. [See the difference between `userProperties` and `userPropertiesSetOnce`](/docs/product-analytics/person-properties.md#what-is-the-difference-between-set-and-set_once)

Dart

PostHog AI

```dart
await Posthog().identify(
  userId: emailController.text,
  userProperties: {"name": "Peter Griffin", "email": "peter@familyguy.com"},
  userPropertiesSetOnce: {"date_of_first_log_in": "2024-03-01"}
);
```

You should call `identify` as soon as you're able to. Typically, this is after your user logs in. This ensures that events sent during your user's sessions are correctly associated with them.

When you call `identify`, all previously tracked anonymous events will be linked to the user.

## Get the current user's distinct ID

You may find it helpful to get the current user's distinct ID. For example, to check whether you've already called `identify` for a user or not.

To do this, call `Posthog().getDistinctId()`. This returns either the ID automatically generated by PostHog or the ID that has been passed by a call to `identify()`.

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

Dart

PostHog AI

```dart
await Posthog().alias(
  alias: 'distinct_id',
);
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

The Flutter SDK captures anonymous events by default. However, this may change depending on your `personProfiles` [config](/docs/libraries/flutter.md#person-profiles-anonymous-vs-identified-persons) when initializing PostHog:

1.  `personProfiles: PostHogPersonProfiles.identifiedOnly` *(recommended)* *(default)* - Anonymous events are captured by default. PostHog only captures identified events for users where [person profiles](/docs/data/persons.md) have already been created.

2.  `personProfiles: PostHogPersonProfiles.always` - Capture identified events for all events.

3.  `personProfiles: PostHogPersonProfiles.never` - Capture anonymous events for all events.

For example:

Dart

PostHog AI

```dart
final config = PostHogConfig('<ph_project_token>');
config.host = 'https://us.i.posthog.com';
config.personProfiles = PostHogPersonProfiles.identifiedOnly;
```

### How to capture identified events

If you've set the [`personProfiles` config](/docs/libraries/flutter.md#person-profiles-anonymous-vs-identified-persons) to `PostHogPersonProfiles.identifiedOnly` (the default option), anonymous events are captured by default. Then, to capture identified events, call any of the following functions:

-   [`identify()`](/docs/product-analytics/identify.md)
-   [`alias()`](/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user)
-   [`group()`](/docs/product-analytics/group-analytics.md)

When you call any of these functions, it creates a [person profile](/docs/data/persons.md) for the user. Once this profile is created, all subsequent events for this user will be captured as identified events.

Alternatively, you can set `personProfiles` to `PostHogPersonProfiles.always` to capture identified events by default.

## Super properties

Super properties are properties associated with events that are set once and then sent with every `capture` call, be it a `$screen`, or anything else.

They are set using `Posthog().register`, which takes a key and value, and they persist across sessions.

For example, take a look at the following call:

Dart

PostHog AI

```dart
import 'package:posthog_flutter/posthog_flutter.dart';
await Posthog().register("team_id", 22);
```

The call above ensures that every event sent by the user will include `"team_id": 22`. This way, if you filtered events by property using `team_id = 22`, it would display all events captured on that user after the `Posthog().register` call, since they all include the specified super property.

However, please note that this does not store properties against the User, only against their events. To store properties against the User object, you should use `Posthog().identify`. More information on this can be found on the [Sending User Information section](#sending-user-information).

### Removing stored super properties

Super properties are persisted across sessions so you have to explicitly remove them if they are no longer relevant. In order to stop sending a super property with events, you can use `Posthog().unregister`, like so:

Dart

PostHog AI

```dart
import 'package:posthog_flutter/posthog_flutter.dart';
await Posthog().unregister("team_id");
```

This will remove the super property and subsequent events will not include it.

If you are doing this as part of a user logging out you can instead simply use `Posthog().reset()` which takes care of clearing all stored super properties and more.

## Group analytics

Group analytics allows you to associate the events for that person's session with a group (e.g. teams, organizations, etc.). See [Group Analytics](/docs/product-analytics/group-analytics.md) for Flutter examples and implementation details.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](/pricing.md).

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

### Boolean feature flags

Dart

PostHog AI

```dart
final result = await Posthog().getFeatureFlagResult('flag-key');
if (result != null && result.enabled) {
  // Do something differently for this user
  // Optional: fetch the payload from the same evaluation result
  final matchedFlagPayload = result.payload;
}
```

### Multivariate feature flags

Dart

PostHog AI

```dart
final result = await Posthog().getFeatureFlagResult('flag-key');
if (result != null && result.variant == 'variant-key') { // replace 'variant-key' with the key of your variant
  // Do something differently for this user
  // Optional: fetch the payload from the same evaluation result
  final matchedFlagPayload = result.payload;
}
```

### Ensuring flags are loaded before usage

> To use the `onFeatureFlags` callback, you must [set up the SDK manually](#installation). On Android and iOS, disable `com.posthog.posthog.AUTO_INIT` first.

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in the storage.

This means that for most screens, the feature flags are available immediately – **except for the first time a user visits**.

To handle this, you can use the `onFeatureFlags` callback in your config to be notified when flags are loaded:

Dart

PostHog AI

```dart
final config = PostHogConfig('<ph_project_token>');
config.host = 'https://us.i.posthog.com';
config.onFeatureFlags = () async {
  if (await Posthog().isFeatureEnabled('flag-key')) {
    // do something
  }
};
await Posthog().setup(config);
```

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

Dart

PostHog AI

```dart
await Posthog().reloadFeatureFlags();
```

### Setting properties for flag evaluation

If a flag targets person or group properties, you can send those properties inline with the next flag evaluation request instead of waiting for a `$set` event to be ingested. This avoids the race where a flag returns a stale value right after you set a property.

Dart

PostHog AI

```dart
// Person properties — included in the next flag evaluation request
await Posthog().setPersonPropertiesForFlags({
  'storefront_country': 'US',
  'is_beta_user': true,
});
// Group properties
await Posthog().setGroupPropertiesForFlags('company', {'plan': 'enterprise'});
```

By default these reload feature flags, and the returned `Future` completes once the reload finishes, so the next `getFeatureFlag` reflects the new properties. Pass `reloadFeatureFlags: false` to set several properties before reloading. Use `resetPersonPropertiesForFlags()` and `resetGroupPropertiesForFlags()` to clear them. See [property overrides for flag evaluation](/docs/feature-flags/property-overrides.md) for details.

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code. See [feature flag code examples](/docs/feature-flags/adding-feature-flag-code?tab=Flutter.md) for Flutter implementation details.

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## Error tracking

To set up error tracking in your project, see the [error tracking docs](/docs/error-tracking.md).

## Logs

To set up [logs](/docs/logs.md) in your Flutter app, follow the [Flutter logs installation guide](/docs/logs/installation/flutter.md). The SDK exposes `Posthog().logger.{trace,debug,info,warn,error,fatal}` (and `Posthog().captureLog` for full control) for sending structured records to PostHog Logs, with batching, offline persistence, and a rate cap built in.

## Session replay

> **Note:** Session replay is supported on Flutter Web, Android, and iOS.

To set up [session replay web](/docs/session-replay.md) or [mobile session replay](/docs/session-replay/mobile.md) in your project, all you need to do is install the Flutter SDK, follow the [additional installation instructions](/docs/session-replay/installation/flutter.md), and enable "Record user sessions" in [your project settings](https://us.posthog.com/settings/project-replay) and enable the `sessionReplay` option.

If you're using Flutter Web, also enable the [Canvas capture](/docs/session-replay/canvas-recording.md) in [your project settings](https://us.posthog.com/settings/project-replay). This is needed as Flutter renders your app using a browser canvas element.

## Surveys

> **Note:** Surveys are supported in Flutter for **Web**, **iOS**, and **Android** platforms.

[Surveys](/docs/surveys.md) launched with [popover presentation](/docs/surveys/creating-surveys.md#presentation) are automatically shown to users matching the [display conditions](/docs/surveys/creating-surveys.md#display-conditions) you set up.

## Flush

You can configure how many events queue before flushing with `flushAt`. Setting this to `1` will send events immediately and will use more battery. The default is `20`.

You can also configure the flush interval with `flushInterval` (default 30 seconds), after which queued events are sent regardless of how many have been gathered:

Dart

PostHog AI

```dart
final config = PostHogConfig('<ph_project_token>');
config.flushAt = 20;
config.flushInterval = const Duration(seconds: 30);
```

You can also manually flush the queue to start sending events immediately instead of waiting for the next batch:

Dart

PostHog AI

```dart
await Posthog().flush();
```

Flushing is best-effort and asynchronous – it starts sending queued events in the background but doesn't wait for the request to finish, so it isn't a delivery guarantee.

## Offline behavior

The PostHog Flutter SDK will continue to capture events when the device is offline for Android and Apple platforms. The events are stored in a queue in the device's file storage and are flushed when the device is online.

-   The queue has a maximum size defined by `maxQueueSize` in the configuration.
-   When the queue is full, the oldest event is deleted first.
-   The queue is flushed when the app is restarted and the device is online.

## Opt out of data capture

You can disable data collection for a user at any time using the `disable()` method:

Dart

PostHog AI

```dart
await Posthog().disable();
```

This prevents any future events from being sent. It doesn't remove events already captured for the user. To opt the user back in:

Dart

PostHog AI

```dart
await Posthog().enable();
```

To check if a user is opted out:

Dart

PostHog AI

```dart
await Posthog().isOptOut();
```

## Amending or dropping events

Since version 5.13.0, you can provide `beforeSend` callbacks when initializing the SDK to amend or drop events before they are sent to PostHog.

### Redacting information in events

`beforeSend` gives you one place to edit or redact information before it is sent to PostHog. For example:

Dart

PostHog AI

```dart
final config = PostHogConfig('<ph_project_token>');
config.host = 'https://us.i.posthog.com';
config.beforeSend = [
  (event) {
    // Redact email from properties
    if (event.properties?['email'] != null) {
      event.properties?['email'] = '***@***.***';
    }
    return event;
  },
];
await Posthog().setup(config);
```

### Dropping events

Return `null` from the callback to drop the event:

Dart

PostHog AI

```dart
config.beforeSend = [
  (event) {
    // Drop events you don't want to send
    if (event.event == 'ignored_event') {
      return null;
    }
    return event;
  },
];
```

### Filtering autocaptured screens

You can stop specific screens from being autocaptured by filtering them in your before-send hook. Return `null` for any `$screen` event whose `$screen_name` matches a screen you don't want to track, and it's dropped before being sent – keeping unwanted screen views out of your event log.

Because it's just a function, you can filter however you like – an **ignorelist** (drop the screens you name), an **allowlist** (invert the check to capture only the screens you name), or any custom rule such as a name prefix, a regex, or a check against the event's properties.

Dart

PostHog AI

```dart
const ignoredScreens = {'Splash', 'Debug'};
config.beforeSend = [
  (event) {
    final screenName = event.properties?['$screen_name'];
    if (event.event == '$screen' && ignoredScreens.contains(screenName)) {
      return null;
    }
    return event;
  },
];
```

### Limitations

The `beforeSend` callbacks only apply to events captured via Dart APIs:

-   `Posthog().capture()` - custom events
-   `Posthog().screen()` - screen events (event name is `$screen`)
-   `Posthog().captureException()` - exception events (event name is `$exception`)

They do **not** intercept native-initiated events such as:

-   Session replay events (`$snapshot`)
-   Application lifecycle events (`Application Opened`, etc.)

Additionally, only user-provided properties are available in the callback. System properties (like `$device_type`, `$session_id`) are added by the native SDK at a later stage.

## Debug mode

If you're not seeing the expected events being captured, the feature flags being evaluated, or the surveys being shown, you can enable debug mode to see what's happening.

You can enable debug mode during initialization by setting the `debug` option to `true` in the `PostHogConfig` object. A common pattern is to set this to `true` in development environments only using environment variables.

Dart

PostHog AI

```dart
final config = PostHogConfig('<ph_project_token>');
config.host = 'https://us.i.posthog.com';
config.debug = true;
await Posthog().setup(config);
```

This will enable verbose logs about the inner workings of the SDK.

You can also enable debug by calling the `Posthog().debug()` method in your code.

Dart

PostHog AI

```dart
await Posthog().debug(true);
await Posthog().debug(false);
```

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better