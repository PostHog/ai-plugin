# PostHog flutter Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/flutter

---

## README.md

# PostHog Flutter example

A [Flutter](https://flutter.dev/) example app demonstrating PostHog integration with product analytics, user identification, screen tracking, and error tracking across Android, iOS, Web, and macOS — the platforms the [posthog_flutter](https://pub.dev/packages/posthog_flutter) SDK supports.

## Features

- **Product analytics**: Track user events and behaviors with `Posthog().capture()`
- **Screen tracking**: Automatic `$screen` events for named routes via `PosthogObserver`
- **Error tracking**: Manual `captureException()` plus autocapture of uncaught Flutter errors
- **User authentication**: Demo login flow with PostHog `identify()`/`reset()`
- **Manual SDK setup**: Dart-side configuration with native auto-init disabled (required for session replay and surveys)

**Flutter Web initializes separately.** `Posthog().setup()` is a no-op on web, so
an app that ships a `web/` target needs the posthog-js snippet in `web/index.html`
as well — a Dart-side setup alone leaves web builds capturing nothing. See
`web/index.html` in this example.

## Prerequisites

1. **Flutter SDK** — follow the [install guide](https://docs.flutter.dev/get-started/install) for your OS, then verify with:
   ```bash
   flutter doctor
   ```
2. **For iOS/macOS**: a Mac with Xcode and [CocoaPods](https://guides.cocoapods.org/using/getting-started.html) (`brew install cocoapods`)
3. **For Android**: Android Studio with an emulator or a connected device
4. **For Web**: Chrome

## Getting started

### 1. Regenerate icons and install dependencies

```bash
flutter create --platforms=android,ios,web,macos .
flutter pub get
```

Binary launcher/app icons are deliberately not committed. The `flutter create` step regenerates them — it only adds missing files and never overwrites the committed configs.

### 2. Configure your PostHog project token

Get your project token from your [PostHog project settings](https://app.posthog.com/settings/project).

For **Android, iOS, and macOS**, the token is embedded at build time via `--dart-define` (no file to edit):

```bash
flutter run \
  --dart-define=POSTHOG_PROJECT_TOKEN=phc_your_project_token_here \
  --dart-define=POSTHOG_HOST=https://us.i.posthog.com
```

`POSTHOG_HOST` is optional and defaults to `https://us.i.posthog.com` (use `https://eu.i.posthog.com` for EU Cloud).

For **Web**, edit `web/index.html` and replace `phc_your_project_token_here` in the posthog-js snippet — Flutter Web is initialized by that snippet, not by the Dart config.

> **Note:** The app still runs without a token — analytics are simply disabled (a warning is logged).

### 3. Run per platform

```bash
flutter devices                      # list available targets

flutter run --dart-define=POSTHOG_PROJECT_TOKEN=phc_...              # default device
flutter run -d chrome                                                 # Web (token comes from web/index.html)
flutter run -d macos --dart-define=POSTHOG_PROJECT_TOKEN=phc_...     # macOS
```

For iOS, install pods first (first time only): `cd ios && pod install && cd ..`

## Project structure

```
lib/
├── main.dart                    # Entry point: PostHog setup, MaterialApp with
│                                # named routes + PosthogObserver
├── posthog/
│   └── posthog.dart             # PostHog configuration (manual setup)
├── auth/
│   └── auth_state.dart          # Fake auth with identify()/reset()
└── screens/
    ├── home_screen.dart         # Home/login screen
    ├── burrito_screen.dart      # Demo feature screen with event capture
    └── profile_screen.dart      # Profile with error tracking demo

test/
├── mocks.dart                   # FakePosthogPlatform: records identify/capture/
│                                # screen/captureException calls for assertions
├── posthog/                     # SDK setup config tests
├── auth/                        # identify()/reset() lifecycle tests
└── screens/                     # Event capture + error tracking widget tests

android/                         # AUTO_INIT disabled in AndroidManifest.xml
ios/                             # AUTO_INIT disabled in Runner/Info.plist; Podfile pins iOS 13+
web/                             # posthog-js snippet in index.html
macos/                           # AUTO_INIT disabled in Runner/Info.plist;
                                 # network.client entitlement for the app sandbox
```

## Key integration points

### Manual SDK setup (lib/posthog/posthog.dart)

PostHog is configured once in Dart. Manual setup (instead of the native auto-init path) is required for session replay and surveys, so the native layers disable auto-init with `com.posthog.posthog.AUTO_INIT: false`:

```dart
final config = PostHogConfig(PosthogEnv.projectToken);
config.host = PosthogEnv.host;
config.debug = kDebugMode;
config.errorTrackingConfig.captureFlutterErrors = true;
config.errorTrackingConfig.capturePlatformDispatcherErrors = true;
await Posthog().setup(config);
```

On Flutter Web, `setup()` is a no-op — the posthog-js snippet in `web/index.html` initializes the SDK instead.

### Screen tracking (lib/main.dart)

`PosthogObserver` captures a `$screen` event on every route change. Routes must be named or they won't be recorded:

```dart
MaterialApp(
  navigatorObservers: [PosthogObserver()],
  routes: {
    '/': (_) => const HomeScreen(),
    '/burrito': (_) => const BurritoScreen(),
    '/profile': (_) => const ProfileScreen(),
  },
)
```

### User identification (lib/auth/auth_state.dart)

Identify users as soon as they log in; person data goes in `userProperties` (`$set`) / `userPropertiesSetOnce` (`$set_once`), not event properties. Call `reset()` on logout:

```dart
await Posthog().identify(
  userId: username, // in a real app, use your database user ID here
  userProperties: {'username': username},
  userPropertiesSetOnce: {'first_login_date': DateTime.now().toIso8601String()},
);

// on logout
await Posthog().reset();
```

### Event capture (lib/screens/burrito_screen.dart)

Capture custom events with properties. We recommend a `[object] [verb]` format for event names:

```dart
await Posthog().capture(
  eventName: 'burrito_considered',
  properties: {
    'total_considerations': total,
    'is_first_consideration': total == 1,
  },
);
```

### Error tracking (lib/screens/profile_screen.dart)

Uncaught Flutter errors are captured automatically via `errorTrackingConfig`. Handled errors can be captured manually:

```dart
try {
  throw StateError('Test error for PostHog error tracking');
} catch (error, stackTrace) {
  await Posthog().captureException(
    error: error,
    stackTrace: stackTrace,
    properties: {'source': 'profile_test_button'},
  );
}
```

### Application lifecycle events

`Application Installed`, `Application Updated`, `Application Opened`, and `Application Backgrounded` are captured automatically (`captureApplicationLifecycleEvents` is enabled by default).

## Reverse proxy

On the web build, ad blockers often drop requests sent to PostHog's own domain. Set `POSTHOG_HOST` (and the `api_host` in `web/index.html`) to a reverse proxy to keep those events, for example PostHog's [managed reverse proxy](https://posthog.com/docs/advanced/proxy/managed-reverse-proxy.md). The iOS and Android builds aren't affected by browser ad blockers, so they can keep the default host.

## Testing

```bash
flutter test
```

The tests show how to verify a PostHog integration without a network or a
device. `test/mocks.dart` installs a fake `PosthogFlutterPlatformInterface`
that records every `identify`, `capture`, `screen`, `reset`, and
`captureException` call, so tests assert on exactly what would be sent to
PostHog. The fake must `extend` the platform interface (not `implement` it) —
`PlatformInterface.verifyToken` rejects generated mockito/mocktail mocks.

## Learn more

- [PostHog documentation](https://posthog.com/docs)
- [PostHog Flutter integration](https://posthog.com/docs/libraries/flutter)
- [PostHog error tracking](https://posthog.com/docs/error-tracking)
- [Flutter documentation](https://docs.flutter.dev/)

---

## .metadata

```
# This file tracks properties of this Flutter project.
# Used by Flutter tool to assess capabilities and perform upgrades etc.
#
# This file should be version controlled and should not be manually edited.

version:
  revision: "84fc5cbb223bc12f83d65b647ff8a56caf779ffd"
  channel: "stable"

project_type: app

# Tracks metadata for the flutter migrate command
migration:
  platforms:
    - platform: root
      create_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
      base_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
    - platform: android
      create_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
      base_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
    - platform: ios
      create_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
      base_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
    - platform: macos
      create_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
      base_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
    - platform: web
      create_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd
      base_revision: 84fc5cbb223bc12f83d65b647ff8a56caf779ffd

  # User provided section

  # List of Local paths (relative to this file) that should be
  # ignored by the migrate tool.
  #
  # Files that are not part of the templates will be ignored by default.
  unmanaged_files:
    - 'lib/main.dart'
    - 'ios/Runner.xcodeproj/project.pbxproj'

```

---

## android/app/src/debug/AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- The INTERNET permission is required for development. Specifically,
         the Flutter tool needs it to communicate with the running application
         to allow setting breakpoints, to provide hot reload, etc.
    -->
    <uses-permission android:name="android.permission.INTERNET"/>
</manifest>

```

---

## android/app/src/main/AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- Required for PostHog to send events in release builds
         (debug/profile builds get it from their own manifests) -->
    <uses-permission android:name="android.permission.INTERNET"/>
    <application
        android:label="burrito_app"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher">
        <!-- PostHog is set up manually from Dart (lib/posthog/posthog.dart),
             so disable the SDK's native auto-init.
             @see https://posthog.com/docs/libraries/flutter -->
        <meta-data android:name="com.posthog.posthog.AUTO_INIT" android:value="false" />
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:taskAffinity=""
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            <!-- Specifies an Android theme to apply to this Activity as soon as
                 the Android process has started. This theme is visible to the user
                 while the Flutter UI initializes. After that, this theme continues
                 to determine the Window background behind the Flutter UI. -->
            <meta-data
              android:name="io.flutter.embedding.android.NormalTheme"
              android:resource="@style/NormalTheme"
              />
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <!-- Don't delete the meta-data below.
             This is used by the Flutter tool to generate GeneratedPluginRegistrant.java -->
        <meta-data
            android:name="flutterEmbedding"
            android:value="2" />
    </application>
    <!-- Required to query activities that can process text, see:
         https://developer.android.com/training/package-visibility and
         https://developer.android.com/reference/android/content/Intent#ACTION_PROCESS_TEXT.

         In particular, this is used by the Flutter engine in io.flutter.plugin.text.ProcessTextPlugin. -->
    <queries>
        <intent>
            <action android:name="android.intent.action.PROCESS_TEXT"/>
            <data android:mimeType="text/plain"/>
        </intent>
    </queries>
</manifest>

```

---

## android/app/src/main/kotlin/com/posthog/burrito_app/MainActivity.kt

```kt
package com.posthog.burrito_app

import io.flutter.embedding.android.FlutterActivity

class MainActivity : FlutterActivity()

```

---

## android/app/src/main/res/drawable-v21/launch_background.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Modify this file to customize your launch splash screen -->
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="?android:colorBackground" />

    <!-- You can insert your own image assets here -->
    <!-- <item>
        <bitmap
            android:gravity="center"
            android:src="@mipmap/launch_image" />
    </item> -->
</layer-list>

```

---

## android/app/src/main/res/drawable/launch_background.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Modify this file to customize your launch splash screen -->
<layer-list xmlns:android="http://schemas.android.com/apk/res/android">
    <item android:drawable="@android:color/white" />

    <!-- You can insert your own image assets here -->
    <!-- <item>
        <bitmap
            android:gravity="center"
            android:src="@mipmap/launch_image" />
    </item> -->
</layer-list>

```

---

## android/app/src/main/res/values-night/styles.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Theme applied to the Android Window while the process is starting when the OS's Dark Mode setting is on -->
    <style name="LaunchTheme" parent="@android:style/Theme.Black.NoTitleBar">
        <!-- Show a splash screen on the activity. Automatically removed when
             the Flutter engine draws its first frame -->
        <item name="android:windowBackground">@drawable/launch_background</item>
    </style>
    <!-- Theme applied to the Android Window as soon as the process has started.
         This theme determines the color of the Android Window while your
         Flutter UI initializes, as well as behind your Flutter UI while its
         running.

         This Theme is only used starting with V2 of Flutter's Android embedding. -->
    <style name="NormalTheme" parent="@android:style/Theme.Black.NoTitleBar">
        <item name="android:windowBackground">?android:colorBackground</item>
    </style>
</resources>

```

---

## android/app/src/main/res/values/styles.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <!-- Theme applied to the Android Window while the process is starting when the OS's Dark Mode setting is off -->
    <style name="LaunchTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <!-- Show a splash screen on the activity. Automatically removed when
             the Flutter engine draws its first frame -->
        <item name="android:windowBackground">@drawable/launch_background</item>
    </style>
    <!-- Theme applied to the Android Window as soon as the process has started.
         This theme determines the color of the Android Window while your
         Flutter UI initializes, as well as behind your Flutter UI while its
         running.

         This Theme is only used starting with V2 of Flutter's Android embedding. -->
    <style name="NormalTheme" parent="@android:style/Theme.Light.NoTitleBar">
        <item name="android:windowBackground">?android:colorBackground</item>
    </style>
</resources>

```

---

## android/app/src/profile/AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <!-- The INTERNET permission is required for development. Specifically,
         the Flutter tool needs it to communicate with the running application
         to allow setting breakpoints, to provide hot reload, etc.
    -->
    <uses-permission android:name="android.permission.INTERNET"/>
</manifest>

```

---

## android/gradle.properties

```properties
org.gradle.jvmargs=-Xmx8G -XX:MaxMetaspaceSize=4G -XX:ReservedCodeCacheSize=512m -XX:+HeapDumpOnOutOfMemoryError
android.useAndroidX=true
# This newDsl flag was added by the Flutter template
android.newDsl=false
# This builtInKotlin flag was added by the Flutter template
android.builtInKotlin=false

```

---

## ios/Flutter/AppFrameworkInfo.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleDevelopmentRegion</key>
  <string>en</string>
  <key>CFBundleExecutable</key>
  <string>App</string>
  <key>CFBundleIdentifier</key>
  <string>io.flutter.flutter.app</string>
  <key>CFBundleInfoDictionaryVersion</key>
  <string>6.0</string>
  <key>CFBundleName</key>
  <string>App</string>
  <key>CFBundlePackageType</key>
  <string>FMWK</string>
  <key>CFBundleShortVersionString</key>
  <string>1.0</string>
  <key>CFBundleSignature</key>
  <string>????</string>
  <key>CFBundleVersion</key>
  <string>1.0</string>
</dict>
</plist>

```

---

## ios/Flutter/Debug.xcconfig

```xcconfig
#include "Generated.xcconfig"

```

---

## ios/Flutter/Release.xcconfig

```xcconfig
#include "Generated.xcconfig"

```

---

## ios/Podfile

```
# posthog_flutter requires iOS 13.0+
# @see https://posthog.com/docs/libraries/flutter
platform :ios, '13.0'

# CocoaPods analytics sends network stats synchronously affecting flutter build latency.
ENV['COCOAPODS_DISABLE_STATS'] = 'true'

project 'Runner', {
  'Debug' => :debug,
  'Profile' => :release,
  'Release' => :release,
}

def flutter_root
  generated_xcode_build_settings_path = File.expand_path(File.join('..', 'Flutter', 'Generated.xcconfig'), __FILE__)
  unless File.exist?(generated_xcode_build_settings_path)
    raise "#{generated_xcode_build_settings_path} must exist. If you're running pod install manually, make sure flutter pub get is executed first"
  end

  File.foreach(generated_xcode_build_settings_path) do |line|
    matches = line.match(/FLUTTER_ROOT\=(.*)/)
    return matches[1].strip if matches
  end
  raise "FLUTTER_ROOT not found in #{generated_xcode_build_settings_path}. Try deleting Generated.xcconfig, then run flutter pub get"
end

require File.expand_path(File.join('packages', 'flutter_tools', 'bin', 'podhelper'), flutter_root)

flutter_ios_podfile_setup

target 'Runner' do
  use_frameworks!

  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
  target 'RunnerTests' do
    inherit! :search_paths
  end
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
  end
end

```

---

## ios/Runner.xcodeproj/project.xcworkspace/contents.xcworkspacedata

```xcworkspacedata
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:">
   </FileRef>
</Workspace>

```

---

## ios/Runner.xcodeproj/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEDidComputeMac32BitWarning</key>
	<true/>
</dict>
</plist>

```

---

## ios/Runner.xcodeproj/project.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings

```xcsettings
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PreviewsEnabled</key>
	<false/>
</dict>
</plist>

```

---

## ios/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme

```xcscheme
<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "1510"
   version = "1.3">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <PreActions>
         <ExecutionAction
            ActionType = "Xcode.IDEStandardExecutionActionsCore.ExecutionActionType.ShellScriptAction">
            <ActionContent
               title = "Run Prepare Flutter Framework Script"
               scriptText = "/bin/sh &quot;$FLUTTER_ROOT/packages/flutter_tools/bin/xcode_backend.sh&quot; prepare&#10;">
               <EnvironmentBuildable>
                  <BuildableReference
                     BuildableIdentifier = "primary"
                     BlueprintIdentifier = "97C146ED1CF9000F007C117D"
                     BuildableName = "Runner.app"
                     BlueprintName = "Runner"
                     ReferencedContainer = "container:Runner.xcodeproj">
                  </BuildableReference>
               </EnvironmentBuildable>
            </ActionContent>
         </ExecutionAction>
      </PreActions>
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "97C146ED1CF9000F007C117D"
               BuildableName = "Runner.app"
               BlueprintName = "Runner"
               ReferencedContainer = "container:Runner.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      customLLDBInitFile = "$(SRCROOT)/Flutter/ephemeral/flutter_lldbinit"
      shouldUseLaunchSchemeArgsEnv = "YES">
      <MacroExpansion>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "97C146ED1CF9000F007C117D"
            BuildableName = "Runner.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </MacroExpansion>
      <Testables>
         <TestableReference
            skipped = "NO"
            parallelizable = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "331C8080294A63A400263BE5"
               BuildableName = "RunnerTests.xctest"
               BlueprintName = "RunnerTests"
               ReferencedContainer = "container:Runner.xcodeproj">
            </BuildableReference>
         </TestableReference>
      </Testables>
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      customLLDBInitFile = "$(SRCROOT)/Flutter/ephemeral/flutter_lldbinit"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      enableGPUValidationMode = "1"
      allowLocationSimulation = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "97C146ED1CF9000F007C117D"
            BuildableName = "Runner.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Profile"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "97C146ED1CF9000F007C117D"
            BuildableName = "Runner.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>

```

---

## ios/Runner.xcworkspace/contents.xcworkspacedata

```xcworkspacedata
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "group:Runner.xcodeproj">
   </FileRef>
</Workspace>

```

---

## ios/Runner.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEDidComputeMac32BitWarning</key>
	<true/>
</dict>
</plist>

```

---

## ios/Runner.xcworkspace/xcshareddata/WorkspaceSettings.xcsettings

```xcsettings
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>PreviewsEnabled</key>
	<false/>
</dict>
</plist>

```

---

## ios/Runner/AppDelegate.swift

```swift
import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate, FlutterImplicitEngineDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  func didInitializeImplicitFlutterEngine(_ engineBridge: FlutterImplicitEngineBridge) {
    GeneratedPluginRegistrant.register(with: engineBridge.pluginRegistry)
  }
}

```

---

## ios/Runner/Base.lproj/LaunchScreen.storyboard

```storyboard
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="12121" systemVersion="16G29" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" launchScreen="YES" colorMatched="YES" initialViewController="01J-lp-oVM">
    <dependencies>
        <deployment identifier="iOS"/>
        <plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="12089"/>
    </dependencies>
    <scenes>
        <!--View Controller-->
        <scene sceneID="EHf-IW-A2E">
            <objects>
                <viewController id="01J-lp-oVM" sceneMemberID="viewController">
                    <layoutGuides>
                        <viewControllerLayoutGuide type="top" id="Ydg-fD-yQy"/>
                        <viewControllerLayoutGuide type="bottom" id="xbc-2k-c8Z"/>
                    </layoutGuides>
                    <view key="view" contentMode="scaleToFill" id="Ze5-6b-2t3">
                        <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
                        <subviews>
                            <imageView opaque="NO" clipsSubviews="YES" multipleTouchEnabled="YES" contentMode="center" image="LaunchImage" translatesAutoresizingMaskIntoConstraints="NO" id="YRO-k0-Ey4">
                            </imageView>
                        </subviews>
                        <color key="backgroundColor" red="1" green="1" blue="1" alpha="1" colorSpace="custom" customColorSpace="sRGB"/>
                        <constraints>
                            <constraint firstItem="YRO-k0-Ey4" firstAttribute="centerX" secondItem="Ze5-6b-2t3" secondAttribute="centerX" id="1a2-6s-vTC"/>
                            <constraint firstItem="YRO-k0-Ey4" firstAttribute="centerY" secondItem="Ze5-6b-2t3" secondAttribute="centerY" id="4X2-HB-R7a"/>
                        </constraints>
                    </view>
                </viewController>
                <placeholder placeholderIdentifier="IBFirstResponder" id="iYj-Kq-Ea1" userLabel="First Responder" sceneMemberID="firstResponder"/>
            </objects>
            <point key="canvasLocation" x="53" y="375"/>
        </scene>
    </scenes>
    <resources>
        <image name="LaunchImage" width="168" height="185"/>
    </resources>
</document>

```

---

## ios/Runner/Base.lproj/Main.storyboard

```storyboard
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="com.apple.InterfaceBuilder3.CocoaTouch.Storyboard.XIB" version="3.0" toolsVersion="10117" systemVersion="15F34" targetRuntime="iOS.CocoaTouch" propertyAccessControl="none" useAutolayout="YES" useTraitCollections="YES" initialViewController="BYZ-38-t0r">
    <dependencies>
        <deployment identifier="iOS"/>
        <plugIn identifier="com.apple.InterfaceBuilder.IBCocoaTouchPlugin" version="10085"/>
    </dependencies>
    <scenes>
        <!--Flutter View Controller-->
        <scene sceneID="tne-QT-ifu">
            <objects>
                <viewController id="BYZ-38-t0r" customClass="FlutterViewController" sceneMemberID="viewController">
                    <layoutGuides>
                        <viewControllerLayoutGuide type="top" id="y3c-jy-aDJ"/>
                        <viewControllerLayoutGuide type="bottom" id="wfy-db-euE"/>
                    </layoutGuides>
                    <view key="view" contentMode="scaleToFill" id="8bC-Xf-vdC">
                        <rect key="frame" x="0.0" y="0.0" width="600" height="600"/>
                        <autoresizingMask key="autoresizingMask" widthSizable="YES" heightSizable="YES"/>
                        <color key="backgroundColor" white="1" alpha="1" colorSpace="custom" customColorSpace="calibratedWhite"/>
                    </view>
                </viewController>
                <placeholder placeholderIdentifier="IBFirstResponder" id="dkx-z0-nzr" sceneMemberID="firstResponder"/>
            </objects>
        </scene>
    </scenes>
</document>

```

---

## ios/Runner/Info.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<!-- PostHog is set up manually from Dart (lib/posthog/posthog.dart),
	     so disable the SDK's native auto-init.
	     See https://posthog.com/docs/libraries/flutter -->
	<key>com.posthog.posthog.AUTO_INIT</key>
	<false/>
	<key>CADisableMinimumFrameDurationOnPhone</key>
	<true/>
	<key>CFBundleDevelopmentRegion</key>
	<string>$(DEVELOPMENT_LANGUAGE)</string>
	<key>CFBundleDisplayName</key>
	<string>Burrito App</string>
	<key>CFBundleExecutable</key>
	<string>$(EXECUTABLE_NAME)</string>
	<key>CFBundleIdentifier</key>
	<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>burrito_app</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>$(FLUTTER_BUILD_NAME)</string>
	<key>CFBundleSignature</key>
	<string>????</string>
	<key>CFBundleVersion</key>
	<string>$(FLUTTER_BUILD_NUMBER)</string>
	<key>LSRequiresIPhoneOS</key>
	<true/>
	<key>UIApplicationSceneManifest</key>
	<dict>
		<key>UIApplicationSupportsMultipleScenes</key>
		<false/>
		<key>UISceneConfigurations</key>
		<dict>
			<key>UIWindowSceneSessionRoleApplication</key>
			<array>
				<dict>
					<key>UISceneClassName</key>
					<string>UIWindowScene</string>
					<key>UISceneConfigurationName</key>
					<string>flutter</string>
					<key>UISceneDelegateClassName</key>
					<string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
					<key>UISceneStoryboardFile</key>
					<string>Main</string>
				</dict>
			</array>
		</dict>
	</dict>
	<key>UIApplicationSupportsIndirectInputEvents</key>
	<true/>
	<key>UILaunchStoryboardName</key>
	<string>LaunchScreen</string>
	<key>UIMainStoryboardFile</key>
	<string>Main</string>
	<key>UISupportedInterfaceOrientations</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
	<key>UISupportedInterfaceOrientations~ipad</key>
	<array>
		<string>UIInterfaceOrientationPortrait</string>
		<string>UIInterfaceOrientationPortraitUpsideDown</string>
		<string>UIInterfaceOrientationLandscapeLeft</string>
		<string>UIInterfaceOrientationLandscapeRight</string>
	</array>
</dict>
</plist>

```

---

## ios/Runner/Runner-Bridging-Header.h

```h
#import "GeneratedPluginRegistrant.h"

```

---

## ios/Runner/SceneDelegate.swift

```swift
import Flutter
import UIKit

class SceneDelegate: FlutterSceneDelegate {

}

```

---

## ios/RunnerTests/RunnerTests.swift

```swift
import Flutter
import UIKit
import XCTest

class RunnerTests: XCTestCase {

  func testExample() {
    // If you add code to the Runner application, consider adding tests here.
    // See https://developer.apple.com/documentation/xctest for more information about using XCTest.
  }

}

```

---

## lib/auth/auth_state.dart

```dart
import 'package:flutter/foundation.dart';
import 'package:posthog_flutter/posthog_flutter.dart';

/// Fake in-memory authentication demonstrating PostHog user identification.
///
/// This is intentionally not production grade — there is no password and no
/// persistence. It exists to show where `identify()` and `reset()` belong in
/// a real login flow.
///
/// @see https://posthog.com/docs/libraries/flutter#identifying-users
class AuthState extends ChangeNotifier {
  /// In production, use [instance]. Tests construct fresh instances to
  /// stay isolated from each other.
  @visibleForTesting
  AuthState();

  static AuthState _instance = AuthState();
  static AuthState get instance => _instance;
  @visibleForTesting
  static set instance(AuthState value) => _instance = value;

  String? _username;
  int _burritoConsiderations = 0;

  String? get username => _username;
  bool get isLoggedIn => _username != null;
  int get burritoConsiderations => _burritoConsiderations;

  Future<void> logIn(String username) async {
    _username = username;
    _burritoConsiderations = 0;
    notifyListeners();

    // Identify the user as soon as they log in. Events captured anonymously
    // before this point are linked to the user retroactively.
    // Person data (like the username) belongs in userProperties ($set) and
    // userPropertiesSetOnce ($set_once), not in event properties.
    await Posthog().identify(
      // In a real app, use your database user ID here — a stable identifier
      // that never changes throughout the user's lifecycle.
      // @see https://posthog.com/docs/product-analytics/identity-resolution#choosing-your-identity-strategy
      userId: username,
      userProperties: {'username': username},
      userPropertiesSetOnce: {
        'first_login_date': DateTime.now().toIso8601String(),
      },
    );

    await Posthog().capture(
      eventName: 'user_logged_in',
      properties: {'login_method': 'demo_form'},
    );
  }

  Future<void> logOut() async {
    _username = null;
    _burritoConsiderations = 0;
    notifyListeners();

    await Posthog().capture(eventName: 'user_logged_out');

    // Clears the distinct ID and anonymous ID so the next user on this
    // device starts a fresh identity.
    await Posthog().reset();
  }

  int incrementBurritoConsiderations() {
    _burritoConsiderations++;
    notifyListeners();
    return _burritoConsiderations;
  }
}

```

---

## lib/main.dart

```dart
import 'package:flutter/material.dart';
import 'package:posthog_flutter/posthog_flutter.dart';

import 'posthog/posthog.dart';
import 'screens/burrito_screen.dart';
import 'screens/home_screen.dart';
import 'screens/profile_screen.dart';
import 'theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await setupPostHog();
  runApp(const BurritoApp());
}

class BurritoApp extends StatelessWidget {
  const BurritoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Burrito App',
      // Match the web examples' look: system font stack on a light grey
      // page with #333 body text (see globals.css in the web examples).
      theme: ThemeData(
        colorSchemeSeed: AppColors.primary,
        scaffoldBackgroundColor: AppColors.background,
        textTheme: Typography.blackCupertino.apply(
          bodyColor: AppColors.text,
          displayColor: AppColors.text,
        ),
      ),
      // PosthogObserver captures a $screen event on every route change.
      // Routes must be named (like the `routes` map below) or the screen
      // views won't be recorded.
      // @see https://posthog.com/docs/libraries/flutter#capturing-screen-views
      navigatorObservers: [PosthogObserver()],
      initialRoute: HomeScreen.route,
      routes: {
        HomeScreen.route: (_) => const HomeScreen(),
        BurritoScreen.route: (_) => const BurritoScreen(),
        ProfileScreen.route: (_) => const ProfileScreen(),
      },
    );
  }
}

```

---

## lib/posthog/posthog.dart

```dart
import 'package:flutter/foundation.dart';
import 'package:posthog_flutter/posthog_flutter.dart';

/// PostHog credentials embedded at build time via --dart-define:
///
/// ```bash
/// flutter run \
///   --dart-define=POSTHOG_PROJECT_TOKEN=phc_your_project_token_here \
///   --dart-define=POSTHOG_HOST=https://us.i.posthog.com
/// ```
///
/// Get your project token from your PostHog project settings
/// (https://app.posthog.com/settings/project).
class PosthogEnv {
  static const projectToken = String.fromEnvironment('POSTHOG_PROJECT_TOKEN');
  static const host = String.fromEnvironment(
    'POSTHOG_HOST',
    // Usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
    defaultValue: 'https://us.i.posthog.com',
  );
}

/// Sets up the PostHog Flutter SDK manually from Dart.
///
/// Manual setup keeps all configuration in one place and is required for
/// session replay and surveys. Native auto-init is disabled with
/// `com.posthog.posthog.AUTO_INIT: false` in:
/// - android/app/src/main/AndroidManifest.xml
/// - ios/Runner/Info.plist
/// - macos/Runner/Info.plist
///
/// On Flutter Web the SDK is initialized by the posthog-js snippet in
/// web/index.html instead — the native `setup()` call is a no-op there.
///
/// The [projectToken] and [host] parameters exist for tests; production code
/// uses the build-time values from [PosthogEnv].
///
/// @see https://posthog.com/docs/libraries/flutter
Future<void> setupPostHog({
  String projectToken = PosthogEnv.projectToken,
  String host = PosthogEnv.host,
}) async {
  if (projectToken.isEmpty) {
    debugPrint(
      'PostHog project token not configured. Analytics will be disabled. '
      'Run with --dart-define=POSTHOG_PROJECT_TOKEN=phc_... to enable it.',
    );
    return;
  }

  final config = PostHogConfig(projectToken);
  config.host = host;

  // Verbose SDK logging in debug builds
  config.debug = kDebugMode;

  // Application lifecycle events (Application Installed, Application Updated,
  // Application Opened, Application Backgrounded) are captured by default
  // (captureApplicationLifecycleEvents, enabled since 5.23.0).

  // Error tracking: capture uncaught Flutter framework and platform
  // dispatcher errors as $exception events. Handled errors can be captured
  // manually with Posthog().captureException() (see ProfileScreen).
  // @see https://posthog.com/docs/error-tracking
  config.errorTrackingConfig.captureFlutterErrors = true;
  config.errorTrackingConfig.capturePlatformDispatcherErrors = true;
  // Mark this app's stack frames as in-app in the error tracking UI
  config.errorTrackingConfig.inAppIncludes.add('package:burrito_app');

  await Posthog().setup(config);
}

```

---

## lib/screens/burrito_screen.dart

```dart
import 'dart:async';

import 'package:flutter/material.dart';
import 'package:posthog_flutter/posthog_flutter.dart';

import '../auth/auth_state.dart';
import '../theme.dart';
import '../widgets/page_scaffold.dart';

/// Burrito Consideration Screen.
///
/// Demonstrates PostHog event capture with custom properties. Each time the
/// user considers a burrito, an event is captured.
///
/// @see https://posthog.com/docs/libraries/flutter#capturing-events
class BurritoScreen extends StatefulWidget {
  const BurritoScreen({super.key});

  static const route = '/burrito';

  @override
  State<BurritoScreen> createState() => _BurritoScreenState();
}

class _BurritoScreenState extends State<BurritoScreen> {
  bool _hasConsidered = false;
  Timer? _resetTimer;

  @override
  void dispose() {
    _resetTimer?.cancel();
    super.dispose();
  }

  Future<void> _considerBurrito() async {
    final total = AuthState.instance.incrementBurritoConsiderations();
    setState(() => _hasConsidered = true);
    _resetTimer?.cancel();
    _resetTimer = Timer(const Duration(seconds: 2), () {
      if (mounted) setState(() => _hasConsidered = false);
    });

    // Capture a custom event with properties. We recommend a
    // [object] [verb] format for event names. Person data (like the
    // username) belongs in identify(), not in event properties.
    await Posthog().capture(
      eventName: 'burrito_considered',
      properties: {
        'total_considerations': total,
        'is_first_consideration': total == 1,
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      child: ListenableBuilder(
        listenable: AuthState.instance,
        builder: (context, _) {
          final auth = AuthState.instance;
          if (!auth.isLoggedIn) {
            return const Text(
              'Log in to consider burritos.',
              style: AppTextStyles.body,
            );
          }
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.only(bottom: 16),
                child: Text(
                  'Burrito consideration zone',
                  style: AppTextStyles.h1,
                ),
              ),
              const Text(
                'Take a moment to truly consider the potential of burritos.',
                style: AppTextStyles.body,
              ),
              const SizedBox(height: 8),
              Center(
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 32),
                      child: TextButton(
                        onPressed: _considerBurrito,
                        style: TextButton.styleFrom(
                          backgroundColor: AppColors.success,
                          foregroundColor: Colors.white,
                          overlayColor: AppColors.successHover,
                          padding: const EdgeInsets.symmetric(
                            vertical: 16,
                            horizontal: 32,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(4),
                          ),
                          textStyle: const TextStyle(
                            fontSize: 18,
                            height: 1.6,
                          ),
                        ),
                        child: const Text(
                          'I have considered the burrito potential',
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                    if (_hasConsidered)
                      Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Text(
                          'Thank you for your consideration! '
                          'Count: ${auth.burritoConsiderations}',
                          style: AppTextStyles.success,
                          textAlign: TextAlign.center,
                        ),
                      ),
                  ],
                ),
              ),
              StatsBox(
                children: [
                  const Text('Consideration stats', style: AppTextStyles.h3),
                  Text(
                    'Total considerations: ${auth.burritoConsiderations}',
                    style: AppTextStyles.body,
                  ),
                ],
              ),
            ],
          );
        },
      ),
    );
  }
}

```

---

## lib/screens/home_screen.dart

```dart
import 'package:flutter/material.dart';

import '../auth/auth_state.dart';
import '../theme.dart';
import '../widgets/page_scaffold.dart';

/// Home/login screen.
///
/// Logging in identifies the user in PostHog (see AuthState.logIn).
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  static const route = '/';

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  String _error = '';

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _signIn() async {
    setState(() => _error = '');
    final username = _usernameController.text.trim();
    final password = _passwordController.text;
    if (username.isEmpty || password.isEmpty) {
      setState(() => _error = 'Please provide both username and password');
      return;
    }
    await AuthState.instance.logIn(username);
    if (!mounted) return;
    _usernameController.clear();
    _passwordController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      child: ListenableBuilder(
        listenable: AuthState.instance,
        builder: (context, _) {
          final auth = AuthState.instance;
          if (auth.isLoggedIn) {
            return _LoggedInView(username: auth.username!);
          }
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.only(bottom: 16),
                child: Text(
                  'Welcome to Burrito Consideration App',
                  style: AppTextStyles.h1,
                ),
              ),
              const Text(
                'Please sign in to begin your burrito journey',
                style: AppTextStyles.body,
              ),
              const SizedBox(height: 32),
              const _FieldLabel('Username:'),
              _TextInput(
                controller: _usernameController,
                hint: 'Enter any username',
                onSubmitted: _signIn,
              ),
              const SizedBox(height: 16),
              const _FieldLabel('Password:'),
              _TextInput(
                controller: _passwordController,
                hint: 'Enter any password',
                obscure: true,
                onSubmitted: _signIn,
              ),
              if (_error.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(_error, style: AppTextStyles.error),
                ),
              const SizedBox(height: 16),
              _PrimaryButton(label: 'Sign In', onPressed: _signIn),
              const SizedBox(height: 32),
              const Center(
                child: Text(
                  'Note: This is a demo app. Use any username and password '
                  'to sign in.',
                  style: AppTextStyles.note,
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _LoggedInView extends StatelessWidget {
  const _LoggedInView({required this.username});

  final String username;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(bottom: 16),
          child: Text('Welcome back, $username!', style: AppTextStyles.h1),
        ),
        const Text(
          'You are logged in. Feel free to explore:',
          style: AppTextStyles.body,
        ),
        const SizedBox(height: 16),
        const Padding(
          padding: EdgeInsets.only(left: 24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _Bullet('Consider the potential of burritos'),
              _Bullet('View your profile and statistics'),
            ],
          ),
        ),
      ],
    );
  }
}

class _Bullet extends StatelessWidget {
  const _Bullet(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('•  ', style: AppTextStyles.body),
          Expanded(child: Text(text, style: AppTextStyles.body)),
        ],
      ),
    );
  }
}

class _FieldLabel extends StatelessWidget {
  const _FieldLabel(this.text);

  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(text, style: AppTextStyles.label),
    );
  }
}

class _TextInput extends StatelessWidget {
  const _TextInput({
    required this.controller,
    required this.hint,
    required this.onSubmitted,
    this.obscure = false,
  });

  final TextEditingController controller;
  final String hint;
  final VoidCallback onSubmitted;
  final bool obscure;

  @override
  Widget build(BuildContext context) {
    return TextField(
      controller: controller,
      obscureText: obscure,
      style: AppTextStyles.body,
      onSubmitted: (_) => onSubmitted(),
      decoration: InputDecoration(
        hintText: hint,
        hintStyle: AppTextStyles.body.copyWith(color: AppColors.note),
        isDense: true,
        contentPadding: const EdgeInsets.all(8),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(4),
          borderSide: const BorderSide(color: AppColors.inputBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(4),
          borderSide: const BorderSide(color: AppColors.primary),
        ),
      ),
    );
  }
}

class _PrimaryButton extends StatelessWidget {
  const _PrimaryButton({required this.label, required this.onPressed});

  final String label;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      child: TextButton(
        onPressed: onPressed,
        style: TextButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          overlayColor: AppColors.primaryHover,
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 32),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(4),
          ),
          textStyle: const TextStyle(fontSize: 16, height: 1.6),
        ),
        child: Text(label),
      ),
    );
  }
}

```

---

## lib/screens/profile_screen.dart

```dart
import 'package:flutter/material.dart';
import 'package:posthog_flutter/posthog_flutter.dart';

import '../auth/auth_state.dart';
import '../theme.dart';
import '../widgets/page_scaffold.dart';

/// User profile screen with an error tracking demo.
///
/// @see https://posthog.com/docs/error-tracking
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  static const route = '/profile';

  Future<void> _triggerTestError(BuildContext context) async {
    try {
      throw StateError('Test error for PostHog error tracking');
    } catch (error, stackTrace) {
      // Capture handled exceptions manually. Uncaught Flutter errors are
      // captured automatically via errorTrackingConfig (see setupPostHog).
      await Posthog().captureException(
        error: error,
        stackTrace: stackTrace,
        properties: {'source': 'profile_test_button'},
      );
    }
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error captured and sent to PostHog!')),
      );
    }
  }

  String _journeyMessage(int considerations) {
    if (considerations == 0) {
      return "You haven't considered any burritos yet. "
          'Visit the Burrito Consideration page to start!';
    }
    if (considerations == 1) {
      return "You've considered the burrito potential once. Keep going!";
    }
    if (considerations < 5) {
      return "You're getting the hang of burrito consideration!";
    }
    if (considerations < 10) {
      return "You're becoming a burrito consideration expert!";
    }
    return 'You are a true burrito consideration master! 🌯';
  }

  @override
  Widget build(BuildContext context) {
    return PageScaffold(
      child: ListenableBuilder(
        listenable: AuthState.instance,
        builder: (context, _) {
          final auth = AuthState.instance;
          if (!auth.isLoggedIn) {
            return const Text('Not logged in.', style: AppTextStyles.body);
          }
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Padding(
                padding: EdgeInsets.only(bottom: 16),
                child: Text('User Profile', style: AppTextStyles.h1),
              ),
              StatsBox(
                children: [
                  const Text('Your Information', style: AppTextStyles.h2),
                  _BoldLabelText(
                    label: 'Username:',
                    value: auth.username!,
                  ),
                  _BoldLabelText(
                    label: 'Burrito Considerations:',
                    value: '${auth.burritoConsiderations}',
                  ),
                ],
              ),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: TextButton(
                  onPressed: () => _triggerTestError(context),
                  style: TextButton.styleFrom(
                    backgroundColor: AppColors.danger,
                    foregroundColor: Colors.white,
                    overlayColor: AppColors.dangerHover,
                    padding: const EdgeInsets.symmetric(
                      vertical: 12,
                      horizontal: 32,
                    ),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(4),
                    ),
                    textStyle: const TextStyle(fontSize: 16, height: 1.6),
                  ),
                  child: const Text('Trigger Test Error (for PostHog)'),
                ),
              ),
              const SizedBox(height: 32),
              const Text('Your Burrito Journey', style: AppTextStyles.h3),
              const SizedBox(height: 8),
              Text(
                _journeyMessage(auth.burritoConsiderations),
                style: AppTextStyles.body,
              ),
            ],
          );
        },
      ),
    );
  }
}

class _BoldLabelText extends StatelessWidget {
  const _BoldLabelText({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Text.rich(
      TextSpan(
        style: AppTextStyles.body,
        children: [
          TextSpan(
            text: '$label ',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          TextSpan(text: value),
        ],
      ),
    );
  }
}

```

---

## lib/theme.dart

```dart
import 'package:flutter/material.dart';

/// Design tokens mirroring the web examples' globals.css so every burrito
/// consideration app looks identical.
abstract final class AppColors {
  static const text = Color(0xFF333333); // body color: #333
  static const background = Color(0xFFF5F5F5); // body background: #f5f5f5
  static const header = Color(0xFF333333); // .header background
  static const headerHover = Color(0xFF555555); // .header a:hover
  static const primary = Color(0xFF0070F3); // .btn-primary
  static const primaryHover = Color(0xFF0051CC);
  static const danger = Color(0xFFDC3545); // .btn-logout / .error
  static const dangerHover = Color(0xFFC82333);
  static const success = Color(0xFF28A745); // .btn-burrito / .success
  static const successHover = Color(0xFF218838);
  static const note = Color(0xFF666666); // .note
  static const statsBackground = Color(0xFFF8F9FA); // .stats
  static const inputBorder = Color(0xFFDDDDDD); // .form-group input border
}

/// Text styles matching the browser defaults the CSS relies on
/// (16px body, line-height 1.6, bold headings at 2em/1.5em/1.17em).
abstract final class AppTextStyles {
  static const body = TextStyle(
    fontSize: 16,
    height: 1.6,
    color: AppColors.text,
  );

  static const h1 = TextStyle(
    fontSize: 32,
    height: 1.6,
    fontWeight: FontWeight.bold,
    color: AppColors.text,
  );

  static const h2 = TextStyle(
    fontSize: 24,
    height: 1.6,
    fontWeight: FontWeight.bold,
    color: AppColors.text,
  );

  static const h3 = TextStyle(
    fontSize: 18.7,
    height: 1.6,
    fontWeight: FontWeight.bold,
    color: AppColors.text,
  );

  static const label = TextStyle(
    fontSize: 16,
    height: 1.6,
    fontWeight: FontWeight.w500,
    color: AppColors.text,
  );

  static const note = TextStyle(
    fontSize: 14,
    height: 1.6,
    color: AppColors.note,
  );

  static const error = TextStyle(
    fontSize: 16,
    height: 1.6,
    color: AppColors.danger,
  );

  static const success = TextStyle(
    fontSize: 16,
    height: 1.6,
    color: AppColors.success,
  );
}

```

---

## lib/widgets/app_header.dart

```dart
import 'package:flutter/material.dart';

import '../auth/auth_state.dart';
import '../screens/burrito_screen.dart';
import '../screens/home_screen.dart';
import '../screens/profile_screen.dart';
import '../theme.dart';

/// Dark navigation header mirroring the web examples' `.header` bar:
/// nav links on the left, user section with logout on the right.
/// Collapses to two stacked rows on narrow (mobile) screens.
class AppHeader extends StatelessWidget {
  const AppHeader({super.key});

  void _goTo(BuildContext context, String route) {
    final navigator = Navigator.of(context);
    if (ModalRoute.of(context)?.settings.name == route) return;
    if (route == HomeScreen.route) {
      navigator.popUntil((r) => r.isFirst);
    } else {
      navigator.pushNamed(route);
    }
  }

  Future<void> _logOut(BuildContext context) async {
    final navigator = Navigator.of(context);
    await AuthState.instance.logOut();
    navigator.popUntil((route) => route.isFirst);
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.header,
      padding: const EdgeInsets.all(16),
      child: SafeArea(
        bottom: false,
        child: ListenableBuilder(
          listenable: AuthState.instance,
          builder: (context, _) {
            final auth = AuthState.instance;

            final nav = Wrap(
              spacing: 16,
              runSpacing: 4,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                _HeaderLink(
                  label: 'Home',
                  onTap: () => _goTo(context, HomeScreen.route),
                ),
                if (auth.isLoggedIn) ...[
                  _HeaderLink(
                    label: 'Burrito Consideration',
                    onTap: () => _goTo(context, BurritoScreen.route),
                  ),
                  _HeaderLink(
                    label: 'Profile',
                    onTap: () => _goTo(context, ProfileScreen.route),
                  ),
                ],
              ],
            );

            final userSection = Wrap(
              spacing: 16,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                if (auth.isLoggedIn) ...[
                  Text(
                    'Welcome, ${auth.username}!',
                    style: AppTextStyles.body.copyWith(color: Colors.white),
                  ),
                  _LogoutButton(onPressed: () => _logOut(context)),
                ] else
                  Text(
                    'Not logged in',
                    style: AppTextStyles.body.copyWith(color: Colors.white),
                  ),
              ],
            );

            return LayoutBuilder(
              builder: (context, constraints) {
                final narrow = constraints.maxWidth < 640;
                if (narrow) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [nav, const SizedBox(height: 8), userSection],
                  );
                }
                return Center(
                  child: ConstrainedBox(
                    constraints: const BoxConstraints(maxWidth: 1200),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [Flexible(child: nav), userSection],
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}

class _HeaderLink extends StatelessWidget {
  const _HeaderLink({required this.label, required this.onTap});

  final String label;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      hoverColor: AppColors.headerHover,
      borderRadius: BorderRadius.circular(4),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        child: Text(
          label,
          style: AppTextStyles.body.copyWith(color: Colors.white),
        ),
      ),
    );
  }
}

class _LogoutButton extends StatelessWidget {
  const _LogoutButton({required this.onPressed});

  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return TextButton(
      onPressed: onPressed,
      style: TextButton.styleFrom(
        backgroundColor: AppColors.danger,
        foregroundColor: Colors.white,
        overlayColor: AppColors.dangerHover,
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
        textStyle: const TextStyle(fontSize: 14, height: 1.6),
      ),
      child: const Text('Logout'),
    );
  }
}

```

---

## lib/widgets/page_scaffold.dart

```dart
import 'package:flutter/material.dart';

import '../theme.dart';
import 'app_header.dart';

/// Page shell mirroring the web examples' layout: dark header on top,
/// then a white `.container` card (max-width 600, radius 8, subtle shadow)
/// centered on the grey page background. Scrolls and shrinks padding on
/// small screens so it works on mobile too.
class PageScaffold extends StatelessWidget {
  const PageScaffold({super.key, required this.child});

  final Widget child;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const AppHeader(),
          Expanded(
            child: SingleChildScrollView(
              child: LayoutBuilder(
                builder: (context, constraints) {
                  final narrow = constraints.maxWidth < 640;
                  return Padding(
                    padding: EdgeInsets.symmetric(
                      vertical: 32,
                      horizontal: narrow ? 16 : 32,
                    ),
                    child: Center(
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 600),
                        padding: EdgeInsets.all(narrow ? 20 : 32),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                          boxShadow: const [
                            BoxShadow(
                              color: Color(0x1A000000), // rgba(0,0,0,0.1)
                              offset: Offset(0, 2),
                              blurRadius: 4,
                            ),
                          ],
                        ),
                        child: child,
                      ),
                    ),
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Grey info panel matching the `.stats` box.
class StatsBox extends StatelessWidget {
  const StatsBox({super.key, required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      margin: const EdgeInsets.only(top: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.statsBackground,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: children,
      ),
    );
  }
}

```

---

## macos/Flutter/Flutter-Debug.xcconfig

```xcconfig
#include "ephemeral/Flutter-Generated.xcconfig"

```

---

## macos/Flutter/Flutter-Release.xcconfig

```xcconfig
#include "ephemeral/Flutter-Generated.xcconfig"

```

---

## macos/Flutter/GeneratedPluginRegistrant.swift

```swift
//
//  Generated file. Do not edit.
//

import FlutterMacOS
import Foundation

import posthog_flutter

func RegisterGeneratedPlugins(registry: FlutterPluginRegistry) {
  PosthogFlutterPlugin.register(with: registry.registrar(forPlugin: "PosthogFlutterPlugin"))
}

```

---

## macos/Podfile

```
# posthog_flutter requires macOS 10.15+, matching Flutter's default
platform :osx, '10.15'

# CocoaPods analytics sends network stats synchronously affecting flutter build latency.
ENV['COCOAPODS_DISABLE_STATS'] = 'true'

project 'Runner', {
  'Debug' => :debug,
  'Profile' => :release,
  'Release' => :release,
}

def flutter_root
  generated_xcode_build_settings_path = File.expand_path(File.join('..', 'Flutter', 'ephemeral', 'Flutter-Generated.xcconfig'), __FILE__)
  unless File.exist?(generated_xcode_build_settings_path)
    raise "#{generated_xcode_build_settings_path} must exist. If you're running pod install manually, make sure \"flutter pub get\" is executed first"
  end

  File.foreach(generated_xcode_build_settings_path) do |line|
    matches = line.match(/FLUTTER_ROOT\=(.*)/)
    return matches[1].strip if matches
  end
  raise "FLUTTER_ROOT not found in #{generated_xcode_build_settings_path}. Try deleting Flutter-Generated.xcconfig, then run \"flutter pub get\""
end

require File.expand_path(File.join('packages', 'flutter_tools', 'bin', 'podhelper'), flutter_root)

flutter_macos_podfile_setup

target 'Runner' do
  use_frameworks!

  flutter_install_all_macos_pods File.dirname(File.realpath(__FILE__))
  target 'RunnerTests' do
    inherit! :search_paths
  end
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_macos_build_settings(target)
  end
end

```

---

## macos/Runner.xcodeproj/project.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEDidComputeMac32BitWarning</key>
	<true/>
</dict>
</plist>

```

---

## macos/Runner.xcodeproj/xcshareddata/xcschemes/Runner.xcscheme

```xcscheme
<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "1510"
   version = "1.3">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <PreActions>
         <ExecutionAction
            ActionType = "Xcode.IDEStandardExecutionActionsCore.ExecutionActionType.ShellScriptAction">
            <ActionContent
               title = "Run Prepare Flutter Framework Script"
               scriptText = "&quot;$FLUTTER_ROOT&quot;/packages/flutter_tools/bin/macos_assemble.sh prepare&#10;">
               <EnvironmentBuildable>
                  <BuildableReference
                     BuildableIdentifier = "primary"
                     BlueprintIdentifier = "33CC10EC2044A3C60003C045"
                     BuildableName = "burrito_app.app"
                     BlueprintName = "Runner"
                     ReferencedContainer = "container:Runner.xcodeproj">
                  </BuildableReference>
               </EnvironmentBuildable>
            </ActionContent>
         </ExecutionAction>
      </PreActions>
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "33CC10EC2044A3C60003C045"
               BuildableName = "burrito_app.app"
               BlueprintName = "Runner"
               ReferencedContainer = "container:Runner.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES">
      <MacroExpansion>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "33CC10EC2044A3C60003C045"
            BuildableName = "burrito_app.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </MacroExpansion>
      <Testables>
         <TestableReference
            skipped = "NO"
            parallelizable = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "331C80D4294CF70F00263BE5"
               BuildableName = "RunnerTests.xctest"
               BlueprintName = "RunnerTests"
               ReferencedContainer = "container:Runner.xcodeproj">
            </BuildableReference>
         </TestableReference>
      </Testables>
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      enableGPUValidationMode = "1"
      allowLocationSimulation = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "33CC10EC2044A3C60003C045"
            BuildableName = "burrito_app.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Profile"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "33CC10EC2044A3C60003C045"
            BuildableName = "burrito_app.app"
            BlueprintName = "Runner"
            ReferencedContainer = "container:Runner.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>

```

---

## macos/Runner.xcworkspace/contents.xcworkspacedata

```xcworkspacedata
<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "group:Runner.xcodeproj">
   </FileRef>
</Workspace>

```

---

## macos/Runner.xcworkspace/xcshareddata/IDEWorkspaceChecks.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>IDEDidComputeMac32BitWarning</key>
	<true/>
</dict>
</plist>

```

---

## macos/Runner/AppDelegate.swift

```swift
import Cocoa
import FlutterMacOS

@main
class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }

  override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
    return true
  }
}

```

---

## macos/Runner/Base.lproj/MainMenu.xib

```xib
<?xml version="1.0" encoding="UTF-8"?>
<document type="com.apple.InterfaceBuilder3.Cocoa.XIB" version="3.0" toolsVersion="14490.70" targetRuntime="MacOSX.Cocoa" propertyAccessControl="none" useAutolayout="YES" customObjectInstantitationMethod="direct">
    <dependencies>
        <deployment identifier="macosx"/>
        <plugIn identifier="com.apple.InterfaceBuilder.CocoaPlugin" version="14490.70"/>
        <capability name="documents saved in the Xcode 8 format" minToolsVersion="8.0"/>
    </dependencies>
    <objects>
        <customObject id="-2" userLabel="File's Owner" customClass="NSApplication">
            <connections>
                <outlet property="delegate" destination="Voe-Tx-rLC" id="GzC-gU-4Uq"/>
            </connections>
        </customObject>
        <customObject id="-1" userLabel="First Responder" customClass="FirstResponder"/>
        <customObject id="-3" userLabel="Application" customClass="NSObject"/>
        <customObject id="Voe-Tx-rLC" customClass="AppDelegate" customModule="Runner" customModuleProvider="target">
            <connections>
                <outlet property="applicationMenu" destination="uQy-DD-JDr" id="XBo-yE-nKs"/>
                <outlet property="mainFlutterWindow" destination="QvC-M9-y7g" id="gIp-Ho-8D9"/>
            </connections>
        </customObject>
        <customObject id="YLy-65-1bz" customClass="NSFontManager"/>
        <menu title="Main Menu" systemMenu="main" id="AYu-sK-qS6">
            <items>
                <menuItem title="APP_NAME" id="1Xt-HY-uBw">
                    <modifierMask key="keyEquivalentModifierMask"/>
                    <menu key="submenu" title="APP_NAME" systemMenu="apple" id="uQy-DD-JDr">
                        <items>
                            <menuItem title="About APP_NAME" id="5kV-Vb-QxS">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <connections>
                                    <action selector="orderFrontStandardAboutPanel:" target="-1" id="Exp-CZ-Vem"/>
                                </connections>
                            </menuItem>
                            <menuItem isSeparatorItem="YES" id="VOq-y0-SEH"/>
                            <menuItem title="Preferences…" keyEquivalent="," id="BOF-NM-1cW"/>
                            <menuItem isSeparatorItem="YES" id="wFC-TO-SCJ"/>
                            <menuItem title="Services" id="NMo-om-nkz">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <menu key="submenu" title="Services" systemMenu="services" id="hz9-B4-Xy5"/>
                            </menuItem>
                            <menuItem isSeparatorItem="YES" id="4je-JR-u6R"/>
                            <menuItem title="Hide APP_NAME" keyEquivalent="h" id="Olw-nP-bQN">
                                <connections>
                                    <action selector="hide:" target="-1" id="PnN-Uc-m68"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Hide Others" keyEquivalent="h" id="Vdr-fp-XzO">
                                <modifierMask key="keyEquivalentModifierMask" option="YES" command="YES"/>
                                <connections>
                                    <action selector="hideOtherApplications:" target="-1" id="VT4-aY-XCT"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Show All" id="Kd2-mp-pUS">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <connections>
                                    <action selector="unhideAllApplications:" target="-1" id="Dhg-Le-xox"/>
                                </connections>
                            </menuItem>
                            <menuItem isSeparatorItem="YES" id="kCx-OE-vgT"/>
                            <menuItem title="Quit APP_NAME" keyEquivalent="q" id="4sb-4s-VLi">
                                <connections>
                                    <action selector="terminate:" target="-1" id="Te7-pn-YzF"/>
                                </connections>
                            </menuItem>
                        </items>
                    </menu>
                </menuItem>
                <menuItem title="Edit" id="5QF-Oa-p0T">
                    <modifierMask key="keyEquivalentModifierMask"/>
                    <menu key="submenu" title="Edit" id="W48-6f-4Dl">
                        <items>
                            <menuItem title="Undo" keyEquivalent="z" id="dRJ-4n-Yzg">
                                <connections>
                                    <action selector="undo:" target="-1" id="M6e-cu-g7V"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Redo" keyEquivalent="Z" id="6dh-zS-Vam">
                                <connections>
                                    <action selector="redo:" target="-1" id="oIA-Rs-6OD"/>
                                </connections>
                            </menuItem>
                            <menuItem isSeparatorItem="YES" id="WRV-NI-Exz"/>
                            <menuItem title="Cut" keyEquivalent="x" id="uRl-iY-unG">
                                <connections>
                                    <action selector="cut:" target="-1" id="YJe-68-I9s"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Copy" keyEquivalent="c" id="x3v-GG-iWU">
                                <connections>
                                    <action selector="copy:" target="-1" id="G1f-GL-Joy"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Paste" keyEquivalent="v" id="gVA-U4-sdL">
                                <connections>
                                    <action selector="paste:" target="-1" id="UvS-8e-Qdg"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Paste and Match Style" keyEquivalent="V" id="WeT-3V-zwk">
                                <modifierMask key="keyEquivalentModifierMask" option="YES" command="YES"/>
                                <connections>
                                    <action selector="pasteAsPlainText:" target="-1" id="cEh-KX-wJQ"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Delete" id="pa3-QI-u2k">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <connections>
                                    <action selector="delete:" target="-1" id="0Mk-Ml-PaM"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Select All" keyEquivalent="a" id="Ruw-6m-B2m">
                                <connections>
                                    <action selector="selectAll:" target="-1" id="VNm-Mi-diN"/>
                                </connections>
                            </menuItem>
                            <menuItem isSeparatorItem="YES" id="uyl-h8-XO2"/>
                            <menuItem title="Find" id="4EN-yA-p0u">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <menu key="submenu" title="Find" id="1b7-l0-nxx">
                                    <items>
                                        <menuItem title="Find…" tag="1" keyEquivalent="f" id="Xz5-n4-O0W">
                                            <connections>
                                                <action selector="performFindPanelAction:" target="-1" id="cD7-Qs-BN4"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Find and Replace…" tag="12" keyEquivalent="f" id="YEy-JH-Tfz">
                                            <modifierMask key="keyEquivalentModifierMask" option="YES" command="YES"/>
                                            <connections>
                                                <action selector="performFindPanelAction:" target="-1" id="WD3-Gg-5AJ"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Find Next" tag="2" keyEquivalent="g" id="q09-fT-Sye">
                                            <connections>
                                                <action selector="performFindPanelAction:" target="-1" id="NDo-RZ-v9R"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Find Previous" tag="3" keyEquivalent="G" id="OwM-mh-QMV">
                                            <connections>
                                                <action selector="performFindPanelAction:" target="-1" id="HOh-sY-3ay"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Use Selection for Find" tag="7" keyEquivalent="e" id="buJ-ug-pKt">
                                            <connections>
                                                <action selector="performFindPanelAction:" target="-1" id="U76-nv-p5D"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Jump to Selection" keyEquivalent="j" id="S0p-oC-mLd">
                                            <connections>
                                                <action selector="centerSelectionInVisibleArea:" target="-1" id="IOG-6D-g5B"/>
                                            </connections>
                                        </menuItem>
                                    </items>
                                </menu>
                            </menuItem>
                            <menuItem title="Spelling and Grammar" id="Dv1-io-Yv7">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <menu key="submenu" title="Spelling" id="3IN-sU-3Bg">
                                    <items>
                                        <menuItem title="Show Spelling and Grammar" keyEquivalent=":" id="HFo-cy-zxI">
                                            <connections>
                                                <action selector="showGuessPanel:" target="-1" id="vFj-Ks-hy3"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Check Document Now" keyEquivalent=";" id="hz2-CU-CR7">
                                            <connections>
                                                <action selector="checkSpelling:" target="-1" id="fz7-VC-reM"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem isSeparatorItem="YES" id="bNw-od-mp5"/>
                                        <menuItem title="Check Spelling While Typing" id="rbD-Rh-wIN">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleContinuousSpellChecking:" target="-1" id="7w6-Qz-0kB"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Check Grammar With Spelling" id="mK6-2p-4JG">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleGrammarChecking:" target="-1" id="muD-Qn-j4w"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Correct Spelling Automatically" id="78Y-hA-62v">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleAutomaticSpellingCorrection:" target="-1" id="2lM-Qi-WAP"/>
                                            </connections>
                                        </menuItem>
                                    </items>
                                </menu>
                            </menuItem>
                            <menuItem title="Substitutions" id="9ic-FL-obx">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <menu key="submenu" title="Substitutions" id="FeM-D8-WVr">
                                    <items>
                                        <menuItem title="Show Substitutions" id="z6F-FW-3nz">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="orderFrontSubstitutionsPanel:" target="-1" id="oku-mr-iSq"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem isSeparatorItem="YES" id="gPx-C9-uUO"/>
                                        <menuItem title="Smart Copy/Paste" id="9yt-4B-nSM">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleSmartInsertDelete:" target="-1" id="3IJ-Se-DZD"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Smart Quotes" id="hQb-2v-fYv">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleAutomaticQuoteSubstitution:" target="-1" id="ptq-xd-QOA"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Smart Dashes" id="rgM-f4-ycn">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleAutomaticDashSubstitution:" target="-1" id="oCt-pO-9gS"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Smart Links" id="cwL-P1-jid">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleAutomaticLinkDetection:" target="-1" id="Gip-E3-Fov"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Data Detectors" id="tRr-pd-1PS">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleAutomaticDataDetection:" target="-1" id="R1I-Nq-Kbl"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Text Replacement" id="HFQ-gK-NFA">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="toggleAutomaticTextReplacement:" target="-1" id="DvP-Fe-Py6"/>
                                            </connections>
                                        </menuItem>
                                    </items>
                                </menu>
                            </menuItem>
                            <menuItem title="Transformations" id="2oI-Rn-ZJC">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <menu key="submenu" title="Transformations" id="c8a-y6-VQd">
                                    <items>
                                        <menuItem title="Make Upper Case" id="vmV-6d-7jI">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="uppercaseWord:" target="-1" id="sPh-Tk-edu"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Make Lower Case" id="d9M-CD-aMd">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="lowercaseWord:" target="-1" id="iUZ-b5-hil"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Capitalize" id="UEZ-Bs-lqG">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="capitalizeWord:" target="-1" id="26H-TL-nsh"/>
                                            </connections>
                                        </menuItem>
                                    </items>
                                </menu>
                            </menuItem>
                            <menuItem title="Speech" id="xrE-MZ-jX0">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <menu key="submenu" title="Speech" id="3rS-ZA-NoH">
                                    <items>
                                        <menuItem title="Start Speaking" id="Ynk-f8-cLZ">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="startSpeaking:" target="-1" id="654-Ng-kyl"/>
                                            </connections>
                                        </menuItem>
                                        <menuItem title="Stop Speaking" id="Oyz-dy-DGm">
                                            <modifierMask key="keyEquivalentModifierMask"/>
                                            <connections>
                                                <action selector="stopSpeaking:" target="-1" id="dX8-6p-jy9"/>
                                            </connections>
                                        </menuItem>
                                    </items>
                                </menu>
                            </menuItem>
                        </items>
                    </menu>
                </menuItem>
                <menuItem title="View" id="H8h-7b-M4v">
                    <modifierMask key="keyEquivalentModifierMask"/>
                    <menu key="submenu" title="View" id="HyV-fh-RgO">
                        <items>
                            <menuItem title="Enter Full Screen" keyEquivalent="f" id="4J7-dP-txa">
                                <modifierMask key="keyEquivalentModifierMask" control="YES" command="YES"/>
                                <connections>
                                    <action selector="toggleFullScreen:" target="-1" id="dU3-MA-1Rq"/>
                                </connections>
                            </menuItem>
                        </items>
                    </menu>
                </menuItem>
                <menuItem title="Window" id="aUF-d1-5bR">
                    <modifierMask key="keyEquivalentModifierMask"/>
                    <menu key="submenu" title="Window" systemMenu="window" id="Td7-aD-5lo">
                        <items>
                            <menuItem title="Minimize" keyEquivalent="m" id="OY7-WF-poV">
                                <connections>
                                    <action selector="performMiniaturize:" target="-1" id="VwT-WD-YPe"/>
                                </connections>
                            </menuItem>
                            <menuItem title="Zoom" id="R4o-n2-Eq4">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <connections>
                                    <action selector="performZoom:" target="-1" id="DIl-cC-cCs"/>
                                </connections>
                            </menuItem>
                            <menuItem isSeparatorItem="YES" id="eu3-7i-yIM"/>
                            <menuItem title="Bring All to Front" id="LE2-aR-0XJ">
                                <modifierMask key="keyEquivalentModifierMask"/>
                                <connections>
                                    <action selector="arrangeInFront:" target="-1" id="DRN-fu-gQh"/>
                                </connections>
                            </menuItem>
                        </items>
                    </menu>
                </menuItem>
                <menuItem title="Help" id="EPT-qC-fAb">
                    <modifierMask key="keyEquivalentModifierMask"/>
                    <menu key="submenu" title="Help" systemMenu="help" id="rJ0-wn-3NY"/>
                </menuItem>
            </items>
            <point key="canvasLocation" x="142" y="-258"/>
        </menu>
        <window title="APP_NAME" allowsToolTipsWhenApplicationIsInactive="NO" autorecalculatesKeyViewLoop="NO" releasedWhenClosed="NO" animationBehavior="default" id="QvC-M9-y7g" customClass="MainFlutterWindow" customModule="Runner" customModuleProvider="target">
            <windowStyleMask key="styleMask" titled="YES" closable="YES" miniaturizable="YES" resizable="YES"/>
            <rect key="contentRect" x="335" y="390" width="800" height="600"/>
            <rect key="screenRect" x="0.0" y="0.0" width="2560" height="1577"/>
            <view key="contentView" wantsLayer="YES" id="EiT-Mj-1SZ">
                <rect key="frame" x="0.0" y="0.0" width="800" height="600"/>
                <autoresizingMask key="autoresizingMask"/>
            </view>
        </window>
    </objects>
</document>

```

---

## macos/Runner/Configs/AppInfo.xcconfig

```xcconfig
// Application-level settings for the Runner target.
//
// This may be replaced with something auto-generated from metadata (e.g., pubspec.yaml) in the
// future. If not, the values below would default to using the project name when this becomes a
// 'flutter create' template.

// The application's name. By default this is also the title of the Flutter window.
PRODUCT_NAME = burrito_app

// The application's bundle identifier
PRODUCT_BUNDLE_IDENTIFIER = com.posthog.burritoApp

// The copyright displayed in application information
PRODUCT_COPYRIGHT = Copyright © 2026 com.posthog. All rights reserved.

```

---

## macos/Runner/Configs/Debug.xcconfig

```xcconfig
#include "../../Flutter/Flutter-Debug.xcconfig"
#include "Warnings.xcconfig"

```

---

## macos/Runner/Configs/Release.xcconfig

```xcconfig
#include "../../Flutter/Flutter-Release.xcconfig"
#include "Warnings.xcconfig"

```

---

## macos/Runner/Configs/Warnings.xcconfig

```xcconfig
WARNING_CFLAGS = -Wall -Wconditional-uninitialized -Wnullable-to-nonnull-conversion -Wmissing-method-return-type -Woverlength-strings
GCC_WARN_UNDECLARED_SELECTOR = YES
CLANG_UNDEFINED_BEHAVIOR_SANITIZER_NULLABILITY = YES
CLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE
CLANG_WARN__DUPLICATE_METHOD_MATCH = YES
CLANG_WARN_PRAGMA_PACK = YES
CLANG_WARN_STRICT_PROTOTYPES = YES
CLANG_WARN_COMMA = YES
GCC_WARN_STRICT_SELECTOR_MATCH = YES
CLANG_WARN_OBJC_REPEATED_USE_OF_WEAK = YES
CLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES
GCC_WARN_SHADOW = YES
CLANG_WARN_UNREACHABLE_CODE = YES

```

---

## macos/Runner/DebugProfile.entitlements

```entitlements
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.security.app-sandbox</key>
	<true/>
	<key>com.apple.security.cs.allow-jit</key>
	<true/>
	<key>com.apple.security.network.server</key>
	<true/>
	<!-- Outgoing network access so PostHog can send events from the
	     sandboxed macOS app -->
	<key>com.apple.security.network.client</key>
	<true/>
</dict>
</plist>

```

---

## macos/Runner/Info.plist

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<!-- PostHog is set up manually from Dart (lib/posthog/posthog.dart),
	     so disable the SDK's native auto-init.
	     See https://posthog.com/docs/libraries/flutter -->
	<key>com.posthog.posthog.AUTO_INIT</key>
	<false/>
	<key>CFBundleDevelopmentRegion</key>
	<string>$(DEVELOPMENT_LANGUAGE)</string>
	<key>CFBundleExecutable</key>
	<string>$(EXECUTABLE_NAME)</string>
	<key>CFBundleIconFile</key>
	<string></string>
	<key>CFBundleIdentifier</key>
	<string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>$(PRODUCT_NAME)</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>$(FLUTTER_BUILD_NAME)</string>
	<key>CFBundleVersion</key>
	<string>$(FLUTTER_BUILD_NUMBER)</string>
	<key>LSMinimumSystemVersion</key>
	<string>$(MACOSX_DEPLOYMENT_TARGET)</string>
	<key>NSHumanReadableCopyright</key>
	<string>$(PRODUCT_COPYRIGHT)</string>
	<key>NSMainNibFile</key>
	<string>MainMenu</string>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
</dict>
</plist>

```

---

## macos/Runner/MainFlutterWindow.swift

```swift
import Cocoa
import FlutterMacOS

class MainFlutterWindow: NSWindow {
  override func awakeFromNib() {
    let flutterViewController = FlutterViewController()
    let windowFrame = self.frame
    self.contentViewController = flutterViewController
    self.setFrame(windowFrame, display: true)

    RegisterGeneratedPlugins(registry: flutterViewController)

    super.awakeFromNib()
  }
}

```

---

## macos/Runner/Release.entitlements

```entitlements
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.security.app-sandbox</key>
	<true/>
	<!-- Outgoing network access so PostHog can send events from the
	     sandboxed macOS app -->
	<key>com.apple.security.network.client</key>
	<true/>
</dict>
</plist>

```

---

## macos/RunnerTests/RunnerTests.swift

```swift
import Cocoa
import FlutterMacOS
import XCTest

class RunnerTests: XCTestCase {

  func testExample() {
    // If you add code to the Runner application, consider adding tests here.
    // See https://developer.apple.com/documentation/xctest for more information about using XCTest.
  }

}

```

---

## test/auth/auth_state_test.dart

```dart
import 'package:burrito_app/auth/auth_state.dart';
import 'package:flutter_test/flutter_test.dart';

import '../mocks.dart';

void main() {
  late FakePosthogPlatform posthog;

  setUp(() {
    posthog = installFakePosthog();
    AuthState.instance = AuthState();
  });

  group('AuthState', () {
    group('logIn', () {
      test('identifies the user with person properties', () async {
        await AuthState.instance.logIn('maria');

        final call = posthog.identifyCalls.single;
        expect(call.userId, 'maria');
        expect(call.userProperties, {'username': 'maria'});
        expect(
          call.userPropertiesSetOnce,
          containsPair('first_login_date', isA<String>()),
        );
      });

      test('captures the login event after identifying', () async {
        await AuthState.instance.logIn('maria');

        final event = posthog.capturedEvents.single;
        expect(event.eventName, 'user_logged_in');
        expect(event.properties, containsPair('login_method', 'demo_form'));
        // Identify first, so the login event is attributed to the user.
        expect(posthog.callOrder, ['identify', 'capture']);
      });
    });

    group('logOut', () {
      setUp(() async {
        await AuthState.instance.logIn('maria');
        // Discard the PostHog calls made by the logIn arrange step, so
        // tests only see what the action under test produced.
        posthog.clear();
      });

      test('captures the logout event before resetting identity', () async {
        await AuthState.instance.logOut();

        final event = posthog.capturedEvents.single;
        expect(event.eventName, 'user_logged_out');
        expect(posthog.resetCallCount, 1);
        // Capture first, so the logout event is still attributed to the
        // user; reset() clears the identity for the next user.
        expect(posthog.callOrder, ['capture', 'reset']);
      });
    });
  });
}

```

---

## test/helpers/pump_app.dart

```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

extension PumpApp on WidgetTester {
  /// Pumps [widget] wrapped in a [MaterialApp], like the real app does.
  Future<void> pumpApp(Widget widget) {
    return pumpWidget(MaterialApp(home: widget));
  }
}

```

---

## test/main_test.dart

```dart
import 'package:burrito_app/auth/auth_state.dart';
import 'package:burrito_app/main.dart';
import 'package:burrito_app/screens/burrito_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'mocks.dart';

void main() {
  late FakePosthogPlatform posthog;

  setUp(() {
    posthog = installFakePosthog();
    AuthState.instance = AuthState();
  });

  group('BurritoApp', () {
    testWidgets('captures a screen view for every named route change', (
      tester,
    ) async {
      await tester.pumpWidget(const BurritoApp());

      // PosthogObserver reports the initial route as root ('/').
      expect(posthog.screenNames, ["root ('/')"]);

      await tester.enterText(find.byType(TextField).at(0), 'maria');
      await tester.enterText(find.byType(TextField).at(1), 'secret');
      await tester.ensureVisible(find.text('Sign In'));
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      await tester.tap(find.text('Burrito Consideration'));
      await tester.pumpAndSettle();

      expect(posthog.screenNames, ["root ('/')", BurritoScreen.route]);
    });
  });
}

```

---

## test/mocks.dart

```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:posthog_flutter/posthog_flutter.dart';
// The platform interface is not exported from the package barrel — tests
// import it from src/ to swap in a fake, the same way the SDK's own test
// suite does.
import 'package:posthog_flutter/src/posthog_flutter_platform_interface.dart';

/// A hand-written fake of the PostHog platform interface that records every
/// call so tests can assert on what would have been sent to PostHog.
///
/// Hand-written (instead of generated with mockito/mocktail) because the
/// platform interface uses `PlatformInterface.verifyToken`, which requires
/// fakes to `extend` the base class — generated mocks `implement` it and are
/// rejected at runtime. This mirrors `PosthogFlutterPlatformFake` in the
/// posthog_flutter package's own tests.
class FakePosthogPlatform extends PosthogFlutterPlatformInterface {
  final setupConfigs = <PostHogConfig>[];
  final identifyCalls = <IdentifyCall>[];
  final capturedEvents = <CapturedEvent>[];
  final capturedExceptions = <CapturedException>[];
  final screenNames = <String>[];
  int resetCallCount = 0;

  /// Method names in invocation order, for asserting call ordering
  /// (e.g. identify before capture, capture before reset).
  final callOrder = <String>[];

  @override
  Future<void> setup(PostHogConfig config) async {
    callOrder.add('setup');
    setupConfigs.add(config);
  }

  @override
  Future<void> identify({
    required String userId,
    Map<String, Object>? userProperties,
    Map<String, Object>? userPropertiesSetOnce,
  }) async {
    callOrder.add('identify');
    identifyCalls.add((
      userId: userId,
      userProperties: userProperties,
      userPropertiesSetOnce: userPropertiesSetOnce,
    ));
  }

  @override
  Future<void> capture({
    required String eventName,
    Map<String, Object>? properties,
    Map<String, Object>? userProperties,
    Map<String, Object>? userPropertiesSetOnce,
  }) async {
    callOrder.add('capture');
    capturedEvents.add((eventName: eventName, properties: properties));
  }

  @override
  Future<void> captureException({
    required Object error,
    StackTrace? stackTrace,
    Map<String, Object>? properties,
  }) async {
    callOrder.add('captureException');
    capturedExceptions.add((
      error: error,
      stackTrace: stackTrace,
      properties: properties,
    ));
  }

  @override
  Future<void> screen({
    required String screenName,
    Map<String, Object>? properties,
  }) async {
    callOrder.add('screen');
    screenNames.add(screenName);
  }

  @override
  Future<void> reset() async {
    callOrder.add('reset');
    resetCallCount++;
  }

  @override
  Future<void> close() async {}

  void clear() {
    setupConfigs.clear();
    identifyCalls.clear();
    capturedEvents.clear();
    capturedExceptions.clear();
    screenNames.clear();
    resetCallCount = 0;
    callOrder.clear();
  }
}

typedef IdentifyCall = ({
  String userId,
  Map<String, Object>? userProperties,
  Map<String, Object>? userPropertiesSetOnce,
});

typedef CapturedEvent = ({String eventName, Map<String, Object>? properties});

typedef CapturedException = ({
  Object error,
  StackTrace? stackTrace,
  Map<String, Object>? properties,
});

/// Installs a [FakePosthogPlatform] for the current test and registers a
/// teardown that restores whatever platform implementation was installed
/// before. Call from `setUp`.
FakePosthogPlatform installFakePosthog() {
  // Reading `instance` lazily constructs the default PosthogFlutterIO,
  // which registers a MethodChannel handler — that needs the binding,
  // even in non-widget tests.
  TestWidgetsFlutterBinding.ensureInitialized();
  final original = PosthogFlutterPlatformInterface.instance;

  final fake = FakePosthogPlatform();
  PosthogFlutterPlatformInterface.instance = fake;

  addTearDown(() async {
    // Clear the Posthog singleton's internal state (current screen,
    // installed error handlers) while the fake is still installed, then
    // hand back the original implementation.
    await Posthog().close();
    PosthogFlutterPlatformInterface.instance = original;
  });
  return fake;
}

```

---

## test/posthog/posthog_test.dart

```dart
import 'package:burrito_app/posthog/posthog.dart';
import 'package:flutter_test/flutter_test.dart';

import '../mocks.dart';

void main() {
  late FakePosthogPlatform posthog;

  setUp(() {
    posthog = installFakePosthog();
  });

  group('setupPostHog', () {
    test('does not initialize the SDK without a project token', () async {
      await setupPostHog(projectToken: '');

      expect(posthog.setupConfigs, isEmpty);
    });

    test('initializes the SDK with the project token and host', () async {
      await setupPostHog(
        projectToken: 'phc_test_token',
        host: 'https://eu.i.posthog.com',
      );

      final config = posthog.setupConfigs.single;
      expect(config.projectToken, 'phc_test_token');
      expect(config.host, 'https://eu.i.posthog.com');
    });

    test('enables error tracking for uncaught errors', () async {
      await setupPostHog(projectToken: 'phc_test_token');

      final config = posthog.setupConfigs.single;
      expect(config.errorTrackingConfig.captureFlutterErrors, isTrue);
      expect(
        config.errorTrackingConfig.capturePlatformDispatcherErrors,
        isTrue,
      );
      expect(
        config.errorTrackingConfig.inAppIncludes,
        contains('package:burrito_app'),
      );
    });
  });
}

```

---

## test/screens/burrito_screen_test.dart

```dart
import 'package:burrito_app/auth/auth_state.dart';
import 'package:burrito_app/screens/burrito_screen.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';
import '../mocks.dart';

void main() {
  late FakePosthogPlatform posthog;

  setUp(() async {
    posthog = installFakePosthog();
    AuthState.instance = AuthState();
    await AuthState.instance.logIn('maria');
    // Discard the PostHog calls made by the logIn arrange step, so tests
    // only see what the action under test produced.
    posthog.clear();
  });

  Future<void> considerBurrito(WidgetTester tester) async {
    await tester.tap(find.text('I have considered the burrito potential'));
    await tester.pump();
  }

  group('BurritoScreen', () {
    testWidgets('considering a burrito captures an event with properties', (
      tester,
    ) async {
      await tester.pumpApp(const BurritoScreen());

      await considerBurrito(tester);

      final event = posthog.capturedEvents.single;
      expect(event.eventName, 'burrito_considered');
      expect(event.properties, containsPair('total_considerations', 1));
      expect(event.properties, containsPair('is_first_consideration', true));
      expect(find.text('Total considerations: 1'), findsOneWidget);
    });

    testWidgets('later considerations are not marked as the first', (
      tester,
    ) async {
      await tester.pumpApp(const BurritoScreen());

      await considerBurrito(tester);
      await considerBurrito(tester);

      final event = posthog.capturedEvents.last;
      expect(event.properties, containsPair('total_considerations', 2));
      expect(event.properties, containsPair('is_first_consideration', false));
    });
  });
}

```

---

## test/screens/home_screen_test.dart

```dart
import 'package:burrito_app/auth/auth_state.dart';
import 'package:burrito_app/screens/home_screen.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';
import '../mocks.dart';

void main() {
  late FakePosthogPlatform posthog;

  setUp(() {
    posthog = installFakePosthog();
    AuthState.instance = AuthState();
  });

  Future<void> signIn(
    WidgetTester tester, {
    String username = 'maria',
    String password = 'secret',
  }) async {
    await tester.enterText(find.byType(TextField).at(0), username);
    await tester.enterText(find.byType(TextField).at(1), password);
    await tester.ensureVisible(find.text('Sign In'));
    await tester.tap(find.text('Sign In'));
    await tester.pump();
  }

  group('HomeScreen', () {
    testWidgets('shows the login form when logged out', (tester) async {
      await tester.pumpApp(const HomeScreen());

      expect(find.text('Welcome to Burrito Consideration App'), findsOneWidget);
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text('Username:'), findsOneWidget);
      expect(find.text('Password:'), findsOneWidget);
    });

    testWidgets('rejects an empty form without touching PostHog', (
      tester,
    ) async {
      await tester.pumpApp(const HomeScreen());

      await tester.ensureVisible(find.text('Sign In'));
      await tester.tap(find.text('Sign In'));
      await tester.pump();

      expect(
        find.text('Please provide both username and password'),
        findsOneWidget,
      );
      expect(posthog.callOrder, isEmpty);
    });

    testWidgets('signing in identifies the user in PostHog', (tester) async {
      await tester.pumpApp(const HomeScreen());

      await signIn(tester, username: 'maria');

      expect(posthog.identifyCalls.single.userId, 'maria');
      expect(posthog.capturedEvents.single.eventName, 'user_logged_in');
      expect(find.text('Welcome back, maria!'), findsOneWidget);
    });
  });
}

```

---

## test/screens/profile_screen_test.dart

```dart
import 'package:burrito_app/auth/auth_state.dart';
import 'package:burrito_app/screens/profile_screen.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';
import '../mocks.dart';

void main() {
  late FakePosthogPlatform posthog;

  setUp(() async {
    posthog = installFakePosthog();
    AuthState.instance = AuthState();
    await AuthState.instance.logIn('maria');
    // Discard the PostHog calls made by the logIn arrange step, so tests
    // only see what the action under test produced.
    posthog.clear();
  });

  group('ProfileScreen', () {
    testWidgets('captures a handled exception with its stack trace', (
      tester,
    ) async {
      await tester.pumpApp(const ProfileScreen());

      await tester.tap(find.text('Trigger Test Error (for PostHog)'));
      await tester.pump();

      final captured = posthog.capturedExceptions.single;
      expect(
        captured.error,
        isA<StateError>().having(
          (error) => error.message,
          'message',
          'Test error for PostHog error tracking',
        ),
      );
      expect(captured.stackTrace, isNotNull);
      expect(
        captured.properties,
        containsPair('source', 'profile_test_button'),
      );
      expect(find.text('Error captured and sent to PostHog!'), findsOneWidget);
    });
  });
}

```

---

## web/index.html

```html
<!DOCTYPE html>
<html>
<head>
  <!--
    If you are serving your web app in a path other than the root, change the
    href value below to reflect the base path you are serving from.

    The path provided below has to start and end with a slash "/" in order for
    it to work correctly.

    For more details:
    * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/base

    This is a placeholder for base href that will be replaced by the value of
    the `--base-href` argument provided to `flutter build`.
  -->
  <base href="$FLUTTER_BASE_HREF">

  <meta charset="UTF-8">
  <meta content="IE=Edge" http-equiv="X-UA-Compatible">
  <meta name="description" content="PostHog Flutter example app.">

  <!--
    PostHog for Flutter Web is initialized by this posthog-js snippet — the
    Dart Posthog().setup() call is a no-op on web. Replace the token below
    with your project token from https://app.posthog.com/settings/project.
    For session replay on Flutter Web, also enable canvas capture in your
    PostHog project settings (Flutter renders into a canvas element).
    @see https://posthog.com/docs/libraries/flutter
  -->
  <script async>
    // POSTHOG_BROWSER_SNIPPET_START
    !function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.crossOrigin="anonymous",p.async=!0,p.src=s.api_host+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],Object.defineProperty(u,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e}}),Object.defineProperty(u.people,"toString",{configurable:!0,enumerable:!0,writable:!0,value:function(){return u.toString(1)+".people (stub)"}}),o="capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagResult reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep onSessionId".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);
    // POSTHOG_BROWSER_SNIPPET_END

    posthog.init("phc_your_project_token_here", {
      // Usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
      api_host: "https://us.i.posthog.com",
      defaults: "2026-08-30",
    });
  </script>

  <!-- iOS meta tags & icons -->
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black">
  <meta name="apple-mobile-web-app-title" content="burrito_app">
  <link rel="apple-touch-icon" href="icons/Icon-192.png">

  <!-- Favicon -->
  <link rel="icon" type="image/png" href="favicon.png"/>

  <title>burrito_app</title>
  <link rel="manifest" href="manifest.json">
</head>
<body>
  <!--
    You can customize the "flutter_bootstrap.js" script.
    This is useful to provide a custom configuration to the Flutter loader
    or to give the user feedback during the initialization process.

    For more details:
    * https://docs.flutter.dev/platform-integration/web/initialization
  -->
  <script src="flutter_bootstrap.js" async></script>
</body>
</html>

```

---

