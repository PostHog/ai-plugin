# Flutter error tracking installation - Docs

1.  1

    ## Install the package

    Required

    Add the PostHog Flutter SDK to your `pubspec.yaml`:

    pubspec.yaml

    PostHog AI

    ```yaml
    posthog_flutter: ^5.0.0
    ```

2.  2

    ## Platform setup

    Required

    ## Tab

    Add these values to your `AndroidManifest.xml`:

    android/app/src/main/AndroidManifest.xml

    PostHog AI

    ```xml
    <application>
      <activity>
        [...]
      </activity>
      <meta-data android:name="com.posthog.posthog.API_KEY" android:value="<ph_project_token>" />
      <meta-data android:name="com.posthog.posthog.POSTHOG_HOST" android:value="https://us.i.posthog.com" />
      <meta-data android:name="com.posthog.posthog.TRACK_APPLICATION_LIFECYCLE_EVENTS" android:value="true" />
      <meta-data android:name="com.posthog.posthog.DEBUG" android:value="true" />
    </application>
    ```

    Update the minimum Android SDK version to **21** in `android/app/build.gradle`:

    android/app/build.gradle

    PostHog AI

    ```groovy
    defaultConfig {
      minSdkVersion 21
      // rest of your config
    }
    ```

    ## Tab

    Add these values to your `Info.plist`:

    ios/Runner/Info.plist

    PostHog AI

    ```xml
    <dict>
      [...]
      <key>com.posthog.posthog.API_KEY</key>
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

    PostHog AI

    ```ruby
    platform :ios, '13.0'
    # rest of your config
    ```

    ## Tab

    Add these values in `index.html`:

    web/index.html

    PostHog AI

    ```html
    <!DOCTYPE html>
    <html>
      <head>
        ...
        <script>
          !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group identify setPersonProperties setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags resetGroups onFeatureFlags addFeatureFlagsHandler onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
          posthog.init('<ph_project_token>', {
              api_host: 'https://us.i.posthog.com',
              defaults: '2026-01-30',
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

    PostHog AI

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

    You can autocapture exceptions by configuring the `errorTrackingConfig` when setting up PostHog:

    Dart

    PostHog AI

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
    | captureFlutterErrors | Captures Flutter framework errors (FlutterError.onError) |
    | capturePlatformDispatcherErrors | Captures Dart runtime errors (PlatformDispatcher.onError). Web not supported. |
    | captureIsolateErrors | Captures errors from main isolate. Web not supported. |
    | captureNativeExceptions | Captures native exceptions. Android (Java/Kotlin) and Apple platforms (iOS, macOS, tvOS). |
    | captureSilentFlutterErrors | Captures Flutter errors that are marked as silent. Default: false. |

5.  5

    ## Manually capture exceptions

    Optional

    ### Basic usage

    You can manually capture exceptions using the `captureException` method:

    Dart

    PostHog AI

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

    PostHog AI

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
    | inAppIncludes | List of package names to be considered inApp frames (takes precedence over excludes) |
    | inAppExcludes | List of package names to be excluded from inApp frames |
    | inAppByDefault | Whether frames are considered inApp by default when their origin cannot be determined |

    `inApp` frames are stack trace frames that belong to your application code (as opposed to third-party libraries or system code). These are highlighted in the PostHog error tracking interface to help you focus on the relevant parts of the stack trace.

6.  6

    ## Future features

    Optional

    We currently don't support the following features:

    -   No de-obfuscating stacktraces from obfuscated builds ([\--obfuscate](https://docs.flutter.dev/deployment/obfuscate) and [\--split-debug-info](https://docs.flutter.dev/deployment/obfuscate)) for Dart code
    -   No [Source code context](/docs/error-tracking/stack-traces.md) associated with an exception (native Android Java/Kotlin errors and Flutter web only)
    -   No native C/C++ exception capture on Android (Java/Kotlin only)
    -   No background isolate error capture

    For symbolicated stack traces on native platforms, see the [Flutter debug symbols guide](/docs/error-tracking/upload-source-maps/flutter.md).

    These features will be added in future releases. We recommend you stay up to date with the latest version of the PostHog Flutter SDK.

7.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

8.  7

    ## Upload source maps

    Required

    Great, you're capturing exceptions! If you serve minified bundles, the next step is to upload source maps to generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps](/docs/error-tracking/upload-source-maps/flutter.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better