> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Flutter Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/flutter

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install with the wizard](#install-with-the-wizard)
- [Install the package](#install-the-package)
- [Platform setup](#platform-setup)
- [Send events](#send-events)
- [Set up exception autocapture](#set-up-exception-autocapture)
- [Manually capture exceptions](#manually-capture-exceptions)
- [Upload Dart debug symbols](#upload-dart-debug-symbols)
- [Future features](#future-features)
- [Verify error tracking](#verify-error-tracking)
- [Upload source maps](#upload-source-maps)
- [iOS and macOS dependency resolution](#ios-and-macos-dependency-resolution)

## Install with the wizard

Run this command in your project directory to add PostHog to your Flutter project. The wizard detects your framework, installs the SDK, and sets up your first events.

`npx @posthog/wizard`

Or set it up manually by following the rest of this guide.

1.  1

    ## Install the package

    Required

    Add the PostHog Flutter SDK to your `pubspec.yaml`:

    pubspec.yaml

    ```yaml
    posthog_flutter: ^5.58.0
    ```

2.  2

    ## Platform setup

    Required

    ## Tab

    Add these values to your `AndroidManifest.xml`:

    android/app/src/main/AndroidManifest.xml

    ```xml
    <application>
      <activity>
        [...]
      </activity>
      <meta-data android:name="com.posthog.posthog.PROJECT_TOKEN" android:value="<ph_project_token>" />
      <meta-data android:name="com.posthog.posthog.POSTHOG_HOST" android:value="https://us.i.posthog.com" />
      <meta-data android:name="com.posthog.posthog.TRACK_APPLICATION_LIFECYCLE_EVENTS" android:value="true" />
      <meta-data android:name="com.posthog.posthog.DEBUG" android:value="true" />
    </application>
    ```

    Update the minimum Android SDK version to **21** in `android/app/build.gradle`:

    android/app/build.gradle

    ```groovy
    defaultConfig {
      minSdkVersion 23
      // rest of your config
    }
    ```

    ## Tab

    Add these values to your `Info.plist`:

    ios/Runner/Info.plist

    ```xml
    <dict>
      [...]
      <key>com.posthog.posthog.PROJECT_TOKEN</key>
      <string><ph_project_token></string>
      <key>com.posthog.posthog.POSTHOG_HOST</key>
      <string>https://us.i.posthog.com</string>
      <key>com.posthog.posthog.CAPTURE_APPLICATION_LIFECYCLE_EVENTS</key>
      <true/>
      <key>com.posthog.posthog.DEBUG</key>
      <true/>
    </dict>
    ```

    Update the minimum platform version to iOS 13.0 in your `Podfile`:

    Podfile

    ```ruby
    platform :ios, '13.0'
    # rest of your config
    ```

    ## Tab

    Add these values in `index.html`:

    web/index.html

    ```html
    <!DOCTYPE html>
    <html>
      <head>
        ...
        <script>
          !function(t,e){var o,n,p,r;e.__SV||(window.posthog && window.posthog.__loaded)||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}p||((p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",p.onerror=function(){p=null},(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r));var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="init capture register register_once register_for_session unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group identify setPersonProperties setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags resetGroups onFeatureFlags addFeatureFlagsHandler onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
          posthog.init('<ph_project_token>', {
              api_host: 'https://us.i.posthog.com',
              defaults: '2026-08-30',
          })
        </script>
      </head>
      <body>
        ...
      </body>
    </html>
    ```

3.  3

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events to test your integration:

    Dart

    ```dart
    import 'package:posthog_flutter/posthog_flutter.dart';
    
    await Posthog().capture(
        eventName: 'button_clicked',
        properties: {
          'button_name': 'signup'
        }
    );
    ```

4.  4

    ## Set up exception autocapture

    Recommended

    **Client-side configuration only**

    This configuration is client-side only. Support for remote configuration in the [error tracking settings](https://app.posthog.com/settings/project-error-tracking#exception-autocapture) will be added in a future release.

    Dart AOT symbolication and background isolate listeners require `posthog_flutter` 5.58.0 or later. If your project uses an earlier version, set `posthog_flutter: ^5.58.0` in `pubspec.yaml` and run `flutter pub get`.

    You can autocapture exceptions by configuring the `errorTrackingConfig` when setting up PostHog:

    Dart

    ```dart
    final config = PostHogConfig('<ph_project_token>');
    // Enable exception autocapture
    config.errorTrackingConfig.captureFlutterErrors = true;
    config.errorTrackingConfig.capturePlatformDispatcherErrors = true;
    config.errorTrackingConfig.captureIsolateErrors = true;
    // Requires SDK version 5.22.0 or higher
    config.errorTrackingConfig.captureNativeExceptions = true;
    config.errorTrackingConfig.captureSilentFlutterErrors = false;
    await Posthog().setup(config);
    ```

    **Configuration options:**

    | Option | Description |
    | --- | --- |
    | `captureFlutterErrors` | Captures Flutter framework errors (`FlutterError.onError`) |
    | `capturePlatformDispatcherErrors` | Captures Dart runtime errors (`PlatformDispatcher.onError`). Web not supported. |
    | `captureIsolateErrors` | Captures errors from the isolate where PostHog is set up. Spawn background isolates paused and call `isolate.addPostHogErrorListener()` before resuming them to capture their errors. Web not supported. |
    | `captureNativeExceptions` | Captures native exceptions. Android (Java/Kotlin) and Apple platforms (iOS, macOS, tvOS). |
    | `captureSilentFlutterErrors` | Captures Flutter errors that are marked as silent. Default: false. |

5.  5

    ## Manually capture exceptions

    Optional

    ### Basic usage

    You can manually capture exceptions using the `captureException` method:

    Dart

    ```dart
    try {
      // Your awesome code that may throw
      await someRiskyOperation();
    } catch (exception, stackTrace) {
      // Capture the exception with PostHog
      await Posthog().captureException(
        error: exception,
        stackTrace: stackTrace,
        properties: {
          'user_action': 'button_press',
          'feature_name': 'data_sync',
        },
      );
    }
    ```

    This is helpful if you've built your own error handling logic or want to capture exceptions that are handled by your application code.

    ### Error tracking configuration

    You can configure error tracking behavior when setting up PostHog:

    **Flutter web apps use minified stack trace frames**

    Flutter web apps generate minified stack trace frames by default, which may cause the configurations below to behave differently or not work as expected.

    Dart

    ```dart
    final config = PostHogConfig('<ph_project_token>');
    // Configure error tracking
    config.errorTrackingConfig.inAppIncludes.add('package:your_app');
    config.errorTrackingConfig.inAppExcludes.add('package:third_party_lib');
    config.errorTrackingConfig.inAppByDefault = true;
    await Posthog().setup(config);
    ```

    **Configuration options:**

    | Option | Description |
    | --- | --- |
    | `inAppIncludes` | List of package names to be considered inApp frames (takes precedence over excludes) |
    | `inAppExcludes` | List of package names to be excluded from inApp frames |
    | `inAppByDefault` | Whether frames are considered inApp by default when their origin cannot be determined |

    `inApp` frames are stack trace frames that belong to your application code (as opposed to third-party libraries or system code). These are highlighted in the PostHog error tracking interface to help you focus on the relevant parts of the stack trace.

6.  6

    ## Upload Dart debug symbols

    Optional

    Flutter writes Dart debug symbols for release builds when you pass `--split-debug-info`. Upload the symbols for each build you ship so PostHog can show Dart function names and line numbers for Android and iOS exceptions. Add `--obfuscate` to the build command if you obfuscate your app.

    ### Android

    ```bash
    flutter build apk --release \
      --split-debug-info=build/posthog-symbols/android
    ```

    ### iOS

    ```bash
    flutter build ipa --release \
      --split-debug-info=build/posthog-symbols/ios
    ```

    Run these commands from your app's root directory to upload each build's `.symbols` files. Sign in with `posthog-cli login`, or set `POSTHOG_CLI_API_KEY` and `POSTHOG_CLI_PROJECT_ID` in CI. Keep each build's symbols in its own directory.

    ### Android

    ```bash
    posthog-cli symbol-sets upload \
      --directory build/posthog-symbols/android
    ```

    ### iOS

    ```bash
    posthog-cli symbol-sets upload \
      --directory build/posthog-symbols/ios
    ```

    To show [source code context](https://posthog.com/docs/error-tracking/stack-traces.md), use this command instead of the symbol-only upload. It includes your app's source files:

    ### Android

    ```bash
    posthog-cli symbol-sets upload \
      --directory build/posthog-symbols/android \
      --include-source --source-root ./lib
    ```

    ### iOS

    ```bash
    posthog-cli symbol-sets upload \
      --directory build/posthog-symbols/ios \
      --include-source --source-root ./lib
    ```

    `--source-root ./lib` limits source files, not symbol files. Run the upload on the build machine while your app source is available. Review your source files before uploading them. See the [CLI debug symbol guide](https://github.com/PostHog/posthog/blob/master/cli/README.md#uploading-native-debug-symbols) for more options.

7.  7

    ## Future features

    Optional

    We currently don't support the following features:

    -   Restoring obfuscated Dart exception class names
    -   Capturing native C/C++ exceptions on Android (Java/Kotlin only)

    For symbolicated native Android and iOS stack traces, see the [Flutter debug symbols guide](https://posthog.com/docs/error-tracking/upload-source-maps/flutter.md).

8.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

9.  8

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](https://posthog.com/docs/error-tracking/upload-source-maps/flutter.md)

## iOS and macOS dependency resolution

> **CocoaPods is becoming read-only.** [CocoaPods has announced](https://blog.cocoapods.org/CocoaPods-Specs-Repo/) the following schedule for its public specs repository:
>
> -   November 2–6, 2026: A read-only dry run will prevent us from publishing new PostHog iOS SDK versions to CocoaPods.
> -   December 2, 2026 onward: The repository will be permanently read-only. New PostHog iOS SDK versions will only be available through Swift Package Manager (SPM).
>
> Existing native SDK versions will remain available through CocoaPods. To keep receiving native SDK updates on iOS and macOS, migrate your Flutter app to SPM. The `posthog_flutter` package supports SPM, and Flutter 3.44 and later enable it by default. On earlier Flutter versions that support SPM, or if you disabled it, run `flutter config --enable-swift-package-manager`, then rebuild your app. Follow [Flutter's SPM migration guide](https://docs.flutter.dev/packages-and-plugins/swift-package-manager/for-app-developers) for project setup and troubleshooting.
>
> This change does not affect `posthog_flutter` releases on pub.dev, Android, or web.
