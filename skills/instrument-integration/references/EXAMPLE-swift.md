# PostHog swift Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/swift

---

## README.md

# PostHog Swift (iOS/macOS) example

This is a [SwiftUI](https://developer.apple.com/xcode/swiftui/) example demonstrating PostHog integration with product analytics, error tracking, and user identification. The app targets both iOS and macOS using `NavigationSplitView`.

## Features

- **Product analytics**: Track user events and behaviors
- **Error tracking**: Capture and track errors
- **User identification**: Associate events with authenticated users
- **Multi-platform**: Runs on iOS, iPadOS, macOS, and visionOS

## Getting started

### 1. Add the PostHog dependency

The Xcode project already includes the PostHog iOS SDK via Swift Package Manager. When you open the project, Xcode will resolve the package automatically.

To add it manually to a new project: File > Add Package Dependencies > enter `https://github.com/PostHog/posthog-ios`.

### 2. Set your PostHog project token

Open `BurritoConsiderationClientApp.swift` and replace the `<your-project-token>` placeholder in `posthogProjectToken` with your project token from your [PostHog project settings](https://app.posthog.com/project/settings).

The PostHog project token is a **public client-side key** — it is designed to ship in the app binary — so hardcoding it is safe and is the recommended approach for iOS distribution.

> **Don't rely on Xcode scheme environment variables as the only source.** Scheme environment variables are injected only when launching from Xcode (debug/simulator); they are **absent** in Archive / Release builds (TestFlight, App Store). Reading them is fine, but treat them as an optional override over a value that ships in the binary — never force-unwrap or `fatalError` on their absence, or production builds will crash on launch.

### 3. Build and run

Open `BurritoConsiderationClient.xcodeproj` in Xcode and run on an iOS Simulator or macOS.

## Project structure

```
BurritoConsiderationClient/
├── BurritoConsiderationClientApp.swift  # App entry point with PostHog initialization
├── ContentView.swift                    # NavigationSplitView with sidebar routing
├── UserState.swift                      # @Observable user state with PostHog identify
├── LoginView.swift                      # Login form
├── DashboardView.swift                  # Welcome screen with dashboard_viewed tracking
├── BurritoView.swift                    # Burrito consideration with event capture
├── ProfileView.swift                    # Profile with journey progress and error trigger
└── Assets.xcassets/                     # Asset catalog
```

## Key integration points

### PostHog initialization (BurritoConsiderationClientApp.swift)

```swift
import PostHog

// The project token is a public client-side key, so it's safe to ship in the
// binary. Replace the placeholder with your token from the PostHog project settings.
let config = PostHogConfig(apiKey: "<your-project-token>", host: "https://us.i.posthog.com")
config.captureApplicationLifecycleEvents = true
PostHogSDK.shared.setup(config)
```

### User identification (UserState.swift)

```swift
PostHogSDK.shared.identify(username, userProperties: [
    "username": username,
])
```

### Screen view tracking (DashboardView.swift, ProfileView.swift)

```swift
.onAppear {
    PostHogSDK.shared.capture("dashboard_viewed", properties: [
        "username": userState.username ?? "unknown",
    ])
}
```

### Event tracking (BurritoView.swift)

```swift
PostHogSDK.shared.capture("burrito_considered", properties: [
    "total_considerations": count,
    "username": username,
])
```

### Error tracking (ProfileView.swift)

```swift
PostHogSDK.shared.capture("test_error_triggered", properties: [
    "error_type": "test",
    "error_message": error.localizedDescription,
])
```

### User logout (UserState.swift)

```swift
PostHogSDK.shared.capture("user_logged_out")
PostHogSDK.shared.reset()
```

## Learn more

- [PostHog iOS SDK Documentation](https://posthog.com/docs/libraries/ios)
- [PostHog Documentation](https://posthog.com/docs)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)

---

## BurritoConsiderationClient.xcodeproj/project.xcworkspace/contents.xcworkspacedata

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

## BurritoConsiderationClient.xcodeproj/project.xcworkspace/xcshareddata/swiftpm/Package.resolved

```resolved
{
  "originHash" : "a2fc303e4b16c93c972ef2ddc4042cf91a9400e5d1639bc9740a80c0336cdd4e",
  "pins" : [
    {
      "identity" : "posthog-ios",
      "kind" : "remoteSourceControl",
      "location" : "https://github.com/PostHog/posthog-ios",
      "state" : {
        "revision" : "1783865d79a1cabc472cf2d56a1fe3f797417b52",
        "version" : "3.40.0"
      }
    }
  ],
  "version" : 3
}

```

---

## BurritoConsiderationClient.xcodeproj/xcshareddata/xcschemes/BurritoConsiderationClient.xcscheme

```xcscheme
<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "2630"
   version = "1.7">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES"
      buildArchitectures = "Automatic">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "1F6BD9732F3520A100189B0B"
               BuildableName = "BurritoConsiderationClient.app"
               BlueprintName = "BurritoConsiderationClient"
               ReferencedContainer = "container:BurritoConsiderationClient.xcodeproj">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES"
      shouldAutocreateTestPlan = "YES">
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
      allowLocationSimulation = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "1F6BD9732F3520A100189B0B"
            BuildableName = "BurritoConsiderationClient.app"
            BlueprintName = "BurritoConsiderationClient"
            ReferencedContainer = "container:BurritoConsiderationClient.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
      <EnvironmentVariables>
         <EnvironmentVariable
            key = "POSTHOG_PROJECT_TOKEN"
            value = "phc_jE9kXU0depRekiuabVROlxxkIXn95NqsNO3qB4qNKtl"
            isEnabled = "YES">
         </EnvironmentVariable>
         <EnvironmentVariable
            key = "POSTHOG_HOST"
            value = "https://us.i.posthog.com"
            isEnabled = "YES">
         </EnvironmentVariable>
      </EnvironmentVariables>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Release"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable
         runnableDebuggingMode = "0">
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "1F6BD9732F3520A100189B0B"
            BuildableName = "BurritoConsiderationClient.app"
            BlueprintName = "BurritoConsiderationClient"
            ReferencedContainer = "container:BurritoConsiderationClient.xcodeproj">
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

## BurritoConsiderationClient/BurritoConsiderationClientApp.swift

```swift
//
//  BurritoConsiderationClientApp.swift
//  BurritoConsiderationClient
//
//  Created by Danilo Campos on 2/5/26.
//

import SwiftUI
import PostHog

// PostHog configuration.
//
// The project token is a PUBLIC client-side key — it is designed to ship in the
// app binary, so hardcoding it here is safe and is the recommended approach for
// iOS. Replace the placeholder below with your project token from
// https://app.posthog.com/project/settings.
private let posthogProjectToken = "<your-project-token>"
private let posthogHost = "https://us.i.posthog.com"

@main
struct BurritoConsiderationClientApp: App {
    @State private var userState = UserState()

    init() {
        let config = PostHogConfig(apiKey: posthogProjectToken, host: posthogHost)
        config.captureApplicationLifecycleEvents = true
        config.debug = true
        PostHogSDK.shared.setup(config)
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(userState)
        }
    }
}

```

---

## BurritoConsiderationClient/BurritoView.swift

```swift
//
//  BurritoView.swift
//  BurritoConsiderationClient
//

import SwiftUI
import PostHog

struct BurritoView: View {
    @Environment(UserState.self) private var userState
    @State private var showConfirmation = false

    var body: some View {
        VStack(spacing: 24) {
            Text("Take a moment to truly consider the potential of burritos.")
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            Text("🌯")
                .font(.system(size: 80))

            Button("I Have Considered the Burrito Potential") {
                userState.burritoConsiderations += 1

                // PostHog: Capture burrito consideration event
                PostHogSDK.shared.capture("burrito_considered", properties: [
                    "total_considerations": userState.burritoConsiderations,
                    "username": userState.username ?? "unknown",
                ])

                showConfirmation = true
                Task {
                    try? await Task.sleep(for: .seconds(2))
                    showConfirmation = false
                }
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            if showConfirmation {
                Text("Thank you for your consideration! Count: \(userState.burritoConsiderations)")
                    .foregroundStyle(.green)
                    .transition(.opacity)
            }

            Text("Total considerations: \(userState.burritoConsiderations)")
                .font(.title2)
                .padding(.top)
        }
        .padding()
        .animation(.default, value: showConfirmation)
        .navigationTitle("Burrito Consideration Zone")
    }
}

```

---

## BurritoConsiderationClient/ContentView.swift

```swift
//
//  ContentView.swift
//  BurritoConsiderationClient
//
//  Created by Danilo Campos on 2/5/26.
//

import SwiftUI

enum Screen: CaseIterable, Identifiable {
    case dashboard, burrito, profile

    var id: Self { self }

    var title: String {
        switch self {
        case .dashboard: "Home"
        case .burrito: "Burrito"
        case .profile: "Profile"
        }
    }

    var icon: String {
        switch self {
        case .dashboard: "house"
        case .burrito: "fork.knife"
        case .profile: "person.circle"
        }
    }
}

struct ContentView: View {
    @Environment(UserState.self) private var userState
    @State private var selectedScreen: Screen? = .dashboard

    var body: some View {
        if userState.isLoggedIn {
            NavigationSplitView {
                List(Screen.allCases, selection: $selectedScreen) { screen in
                    Label(screen.title, systemImage: screen.icon)
                }
                .navigationTitle("Menu")
            } detail: {
                if let selectedScreen {
                    switch selectedScreen {
                    case .dashboard:
                        DashboardView()
                    case .burrito:
                        BurritoView()
                    case .profile:
                        ProfileView()
                    }
                } else {
                    Text("Select an item from the sidebar")
                        .foregroundStyle(.secondary)
                }
            }
        } else {
            NavigationStack {
                LoginView()
            }
        }
    }
}

```

---

## BurritoConsiderationClient/DashboardView.swift

```swift
//
//  DashboardView.swift
//  BurritoConsiderationClient
//

import SwiftUI
import PostHog

struct DashboardView: View {
    @Environment(UserState.self) private var userState

    var body: some View {
        VStack(spacing: 20) {
            Text("Welcome back, \(userState.username ?? "")!")
                .font(.largeTitle)
                .padding(.top, 40)

            Text("You are logged in. Feel free to explore:")
                .foregroundStyle(.secondary)

            VStack(alignment: .leading, spacing: 12) {
                Label("Consider the potential of burritos", systemImage: "fork.knife")
                Label("View your profile and statistics", systemImage: "person.circle")
            }
            .padding()

            Spacer()
        }
        .padding()
        .navigationTitle("Home")
        .onAppear {
            // PostHog: Track dashboard view
            PostHogSDK.shared.capture("dashboard_viewed", properties: [
                "username": userState.username ?? "unknown",
            ])
        }
    }
}

```

---

## BurritoConsiderationClient/LoginView.swift

```swift
//
//  LoginView.swift
//  BurritoConsiderationClient
//

import SwiftUI

struct LoginView: View {
    @Environment(UserState.self) private var userState
    @State private var username = ""
    @State private var password = ""
    @State private var showError = false

    var body: some View {
        Form {
            Section("Login") {
                TextField("Username", text: $username)
                    #if os(iOS)
                    .textInputAutocapitalization(.never)
                    #endif
                    .autocorrectionDisabled()

                SecureField("Password", text: $password)
            }

            Section {
                Button("Log In") {
                    if !userState.login(username: username, password: password) {
                        showError = true
                    }
                }
                .disabled(username.isEmpty || password.isEmpty)
            }
        }
        .formStyle(.grouped)
        .navigationTitle("Burrito Consideration")
        .alert("Login Failed", isPresented: $showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text("Please enter a valid username and password.")
        }
    }
}

```

---

## BurritoConsiderationClient/ProfileView.swift

```swift
//
//  ProfileView.swift
//  BurritoConsiderationClient
//

import SwiftUI
import PostHog

struct ProfileView: View {
    @Environment(UserState.self) private var userState

    private var journeyMessage: String {
        switch userState.burritoConsiderations {
        case 0:
            "You haven't considered any burritos yet. Visit the Burrito Consideration page to start!"
        case 1:
            "You've considered the burrito potential once. Keep going!"
        case 2...4:
            "You're getting the hang of burrito consideration!"
        case 5...9:
            "You're becoming a burrito consideration expert!"
        default:
            "You are a true burrito consideration master!"
        }
    }

    var body: some View {
        Form {
            Section("Your Information") {
                LabeledContent("Username", value: userState.username ?? "—")
                LabeledContent("Burrito Considerations", value: "\(userState.burritoConsiderations)")
            }

            Section("Your Burrito Journey") {
                Text(journeyMessage)
            }

            Section("Diagnostics") {
                Button("Trigger Test Error") {
                    let error = NSError(
                        domain: "com.posthog.BurritoConsiderationClient",
                        code: 42,
                        userInfo: [NSLocalizedDescriptionKey: "Test error triggered by user"]
                    )

                    // PostHog: Capture exception for error tracking
                    PostHogSDK.shared.capture("test_error_triggered", properties: [
                        "error_type": "test",
                        "error_message": error.localizedDescription,
                        "username": userState.username ?? "unknown",
                    ])
                }
            }

            Section {
                Button("Log Out", role: .destructive) {
                    userState.logout()
                }
            }
        }
        .formStyle(.grouped)
        .navigationTitle("Profile")
        .onAppear {
            // PostHog: Track profile view
            PostHogSDK.shared.capture("profile_viewed", properties: [
                "username": userState.username ?? "unknown",
            ])
        }
    }
}

```

---

## BurritoConsiderationClient/UserState.swift

```swift
//
//  UserState.swift
//  BurritoConsiderationClient
//

import Foundation
import PostHog

@Observable
class UserState {
    var username: String?
    var burritoConsiderations: Int = 0

    var isLoggedIn: Bool {
        username != nil
    }

    func login(username: String, password: String) -> Bool {
        // In a real app, validate credentials against a backend
        guard !username.isEmpty, !password.isEmpty else {
            return false
        }

        self.username = username
        self.burritoConsiderations = 0

        // PostHog: Identify user on login
        PostHogSDK.shared.identify(username, userProperties: [
            "username": username,
        ])

        // PostHog: Capture login event
        PostHogSDK.shared.capture("user_logged_in", properties: [
            "username": username,
        ])

        return true
    }

    func logout() {
        // PostHog: Capture logout event before reset
        PostHogSDK.shared.capture("user_logged_out")
        PostHogSDK.shared.reset()

        username = nil
        burritoConsiderations = 0
    }
}

```

---

