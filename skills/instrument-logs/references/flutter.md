# Flutter Logs installation - Docs

The PostHog Flutter SDK has built-in support for capturing structured Logs from your Flutter app across mobile and web. The SDK handles the OTLP encoding, batching, and flushing — and on mobile, on-disk persistence across app restarts and app-lifecycle integration (web buffers in memory via `posthog-js`). You just call `Posthog().captureLog(...)` or `Posthog().logger.{trace,debug,info,warn,error,fatal}(...)`.

> **Manual capture only.** Logs are emitted by your code. The SDK does not autocapture system log streams (`print`, `debugPrint`, or `dart:developer`'s `log`).

> **Minimum version:** `posthog_flutter` `5.27.0` or later (the release that adds Logs support). On mobile it pulls in `posthog-android` `3.48.0` or later automatically.

1.  1

    ## Install posthog\_flutter

    Required

    If you haven't installed `posthog_flutter` yet, follow the steps below. For full details, see the [Flutter SDK guide](/docs/libraries/flutter.md).

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

2.  2

    ## Configure logs in your PostHogConfig

    Required

    Configure Logs through `config.logsConfig` before calling `Posthog().setup(...)`. All fields are optional; unset fields fall back to the native defaults, which are tuned for mobile (cellular bandwidth, battery, app lifecycle).

    Dart

    PostHog AI

    ```dart
    final config = PostHogConfig('<ph_project_token>');
    config.host = 'https://us.i.posthog.com';
    config.logsConfig.serviceName = 'my-app';        // OTLP service.name – shown in the Logs UI
    config.logsConfig.environment = 'production';    // OTLP deployment.environment
    config.logsConfig.serviceVersion = '1.2.3';      // OTLP service.version
    await Posthog().setup(config);
    ```

    These resource attributes are captured at `setup(...)` and apply to every batch.

    > **Web behavior.** On Flutter Web, the SDK attaches to an already-initialized [`posthog-js`](/docs/libraries/js.md) instance, so `config.logsConfig` is **not** applied on web. Configure your log options in the `posthog.init({...})` call in your `web/index.html` instead. `captureLog` and `logger` still work on web (they are forwarded to `posthog-js`), and `beforeSend` still runs (in Dart) on web. Web also requires a recent `posthog-js` build that exposes `captureLog`.

    For example, set the same service identity on the `posthog-js` snippet in `web/index.html`:

    HTML

    PostHog AI

    ```html
    <script>
      posthog.init('<ph_project_token>', {
        api_host: 'https://us.i.posthog.com',
        logs: {
          serviceName: 'my-app',
          environment: 'production',
          serviceVersion: '1.2.3',
        },
      })
    </script>
    ```

    See the [JavaScript Logs installation guide](/docs/logs/installation/javascript.md) for the full `posthog-js` logs config.

3.  3

    ## Capture logs

    Required

    Use `Posthog().logger` for the per-level convenience API, or `Posthog().captureLog` for full control over level, attributes, and trace context.

    Dart

    PostHog AI

    ```dart
    import 'package:posthog_flutter/posthog_flutter.dart';
    // Per-level convenience methods
    Posthog().logger.info('checkout completed', {'order_id': 'ord_789', 'amount_cents': 4999});
    Posthog().logger.warn('payment retry', {'attempt': 2});
    Posthog().logger.error('payment failed', {'code': 'E001'});
    // Lower-level API for custom severity / trace context
    Posthog().captureLog(
      body: 'checkout failed',
      level: PostHogLogSeverity.error,
      attributes: {'order_id': 'ord_789', 'step': 'auth'},
      traceId: '4bf92f3577b34da6a3ce929d0e0e4736',  // optional W3C trace context (32 hex chars)
      spanId: '00f067aa0ba902b7',                   // optional W3C span (16 hex chars)
      traceFlags: 1,
    );
    ```

    The per-level facade methods are `trace`, `debug`, `info`, `warn`, `error`, and `fatal`, each taking a `String body` and an optional `Map<String, Object>` of attributes. Available severity levels for `captureLog` are `PostHogLogSeverity.trace`, `.debug`, `.info`, `.warn`, `.error`, and `.fatal`.

    The optional W3C trace fields (`traceId`, `spanId`, `traceFlags`) are available on `captureLog` only, not on the `logger` facade.

    Records are buffered, batched, persisted to disk, and flushed automatically – every 30 seconds, when the buffer hits the threshold, when the app moves to the background, or on `Posthog().flush()`. `flush()` drains events, Session Replay, and Logs together.

    Each record is automatically tagged with the current distinct ID, session ID, active feature flags, and (on mobile) the current screen and app foreground/background state at the moment of capture. On web, `url.full` is tagged instead of screen name and app state.

4.  4

    ## Test your setup

    Recommended

    1.  Capture a test log from your app:

        Dart

        PostHog AI

        ```dart
        Posthog().logger.info('hello from Flutter');
        Posthog().flush();
        ```

    2.  Open the [PostHog Logs UI](https://app.posthog.com/logs).
    3.  Filter by `service.name = 'my-app'` (or whatever value you set above).

    You should see your record arrive within a few seconds.

    [View your Logs in PostHog](https://app.posthog.com/logs)

5.  5

    ## Tune buffering, rate cap, and resource attributes

    Optional

    The `logsConfig` has knobs for high-volume apps:

    Dart

    PostHog AI

    ```dart
    final config = PostHogConfig('<ph_project_token>');
    config.logsConfig.serviceName = 'my-app';
    config.logsConfig.flushInterval = Duration(seconds: 5);      // default 30s
    config.logsConfig.maxBufferSize = 200;                       // default 1000
    config.logsConfig.maxBatchSize = 50;                         // default 50
    config.logsConfig.flushAt = 20;                              // default 20
    config.logsConfig.rateCapMaxLogs = 5000;                     // default 500
    config.logsConfig.rateCapWindow = Duration(seconds: 60);     // default 10s
    config.logsConfig.resourceAttributes = {'host.name': 'device-01'};
    await Posthog().setup(config);
    ```

    Full configuration reference:

    | Field | Default | What it does |
    | --- | --- | --- |
    | serviceName | app bundle id (iOS) / app namespace (Android) | OTLP service.name resource attribute |
    | serviceVersion | app version | OTLP service.version resource attribute |
    | environment | none | OTLP deployment.environment resource attribute |
    | resourceAttributes | {} | Extra OTLP resource attributes |
    | flushInterval | 30s | Periodic flush interval |
    | flushAt | 20 | Buffer threshold that triggers an automatic flush |
    | maxBatchSize | 50 | Max records per outbound POST |
    | maxBufferSize | 1000 | Max records held on disk before FIFO eviction |
    | rateCapMaxLogs | 500 | Max records per rateCapWindow. Set to 0 to disable. |
    | rateCapWindow | 10s | Rate-cap window length |

    Defaults are tuned for cellular-aware mobile apps. Raise `rateCapMaxLogs` and `maxBufferSize` for high-volume scenarios.

    > On web, these fields are not applied – configure them in your `posthog.init({...})` call in `web/index.html` instead.

6.  6

    ## Filter or redact with beforeSend

    Optional

    Use `config.logsConfig.beforeSend` for redaction, sampling, or filtering by level. It is a `List<BeforeSendLogCallback>`, where each callback is a `FutureOr<PostHogLogRecord?> Function(PostHogLogRecord)`. Callbacks run **in Dart on all platforms (including web)**, evaluated left-to-right. Each callback receives a mutable `PostHogLogRecord` (with mutable `body`, `level`, and `attributes`) and returns either the (possibly mutated) record or `null` to drop it. Callbacks can be synchronous or asynchronous.

    Dart

    PostHog AI

    ```dart
    config.logsConfig.beforeSend = [
      (record) {
        // Drop debug logs in production
        if (record.level == PostHogLogSeverity.debug) return null;
        // Redact a sensitive attribute
        record.attributes?.remove('password');
        return record;
      },
      // Compose a chain – callbacks run left-to-right
      (record) => record.body.contains('secret') ? null : record,
    ];
    ```

    Returning `null` from any callback short-circuits and drops the record. Setting `record.body` to an empty or whitespace-only string also drops the record. A callback that throws is logged and the record is dropped (fail-closed).

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