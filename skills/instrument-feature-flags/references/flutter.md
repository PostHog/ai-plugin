# Flutter Feature Flags installation - Docs

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

    ## Evaluate boolean feature flags

    Required

    Check if a feature flag is enabled:

    Dart

    PostHog AI

    ```dart
    final isMyFlagEnabled = await Posthog().isFeatureEnabled('flag-key');
    if (isMyFlagEnabled) {
        // Do something differently for this user
        // Optional: fetch the payload
        final matchedFlagPayload = await Posthog().getFeatureFlagPayload('flag-key');
    }
    ```

5.  5

    ## Evaluate multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    Dart

    PostHog AI

    ```dart
    final enabledVariant = await Posthog().getFeatureFlag('flag-key');
    if (enabledVariant == 'variant-key') { // replace 'variant-key' with the key of your variant
        // Do something differently for this user
        // Optional: fetch the payload
        final matchedFlagPayload = await Posthog().getFeatureFlagPayload('flag-key');
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