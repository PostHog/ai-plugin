> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Unity

Canonical URL: https://posthog.com/docs/libraries/unity

## On this page

- [Installation](#installation)
- [Capturing events](#capturing-events)
- [Identifying users](#identifying-users)
- [Anonymous vs identified events](#anonymous-vs-identified-events)
- [Super properties](#super-properties)
- [Group analytics](#group-analytics)
- [Feature Flags](#feature-flags)
- [Experiments (A/B tests)](#experiments-ab-tests)
- [Error Tracking](#error-tracking)
- [Session Replay](#session-replay)
- [Application lifecycle events](#application-lifecycle-events)
- [Opt out of data capture](#opt-out-of-data-capture)
- [Debug mode](#debug-mode)
- [Manual flush](#manual-flush)
- [Shutdown](#shutdown)
- [Platform support](#platform-support)
- [Troubleshooting](#troubleshooting)

This is the official PostHog SDK for Unity. It uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your Unity game or application.

PostHog Unity SDK supports Windows, Mac, Linux, iOS, Android, and WebGL platforms.

## Installation

PostHog is available for Unity via the [Unity Package Manager](https://docs.unity3d.com/Manual/upm-ui.html).

### Requirements

-   Unity 2021.3 LTS or later
-   .NET Standard 2.1 API Compatibility Level

### Via Unity Package Manager (Git URL)

1.  Open **Window > Package Manager**
2.  Click the **+** button and select **Add package from git URL**
3.  Enter: `https://github.com/PostHog/posthog-unity.git?path=com.posthog.unity`

### Via local package

1.  Clone or download the [posthog-unity repository](https://github.com/PostHog/posthog-unity)
2.  Open **Window > Package Manager**
3.  Click the **+** button and select **Add package from disk**
4.  Navigate to `com.posthog.unity/package.json`

### Configuration

There are two ways to configure PostHog in Unity:

#### Option 1: Unity Inspector (recommended)

The easiest way to configure PostHog is through the Unity Inspector:

1.  Go to **Edit > Project Settings > PostHog** (this creates a settings asset if one doesn't exist)
2.  Enter your **API Key** and select your **Host** (US or EU Cloud)
3.  Configure other options as needed

The settings asset is created at `Assets/Resources/PostHogSettings.asset`. PostHog automatically initializes when your game starts using these settings.

You can also create the settings asset manually via **Assets > Create > PostHog > Settings in Resources**.

> **Tip:** Click **Test Connection** in the Inspector to verify your API key is valid.

#### Option 2: Code-based initialization

For more control, initialize PostHog in your game's startup script:

```csharp
using PostHogUnity;
using UnityEngine;

public class GameManager : MonoBehaviour
{
    void Start()
    {
        PostHog.Setup(new PostHogConfig
        {
            ApiKey = "<ph_project_token>",
            Host = "https://us.i.posthog.com" // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
        });
    }
}
```

> **Note:** If you use code-based initialization, remove any `PostHogSettings.asset` from your Resources folder to avoid double initialization.

### Configuration options

All options below can be set via the Unity Inspector or in code:

```csharp
PostHog.Setup(new PostHogConfig
{
    // Required
    ApiKey = "<ph_project_token>",

    // Optional
    Host = "https://us.i.posthog.com",         // PostHog instance URL (default: https://us.i.posthog.com)
    FlushAt = 20,                           // Events before auto-flush (default: 20)
    FlushIntervalSeconds = 30,              // Seconds between flushes (default: 30)
    MaxQueueSize = 1000,                    // Max queued events (default: 1000)
    MaxBatchSize = 50,                      // Max events per request (default: 50)
    CaptureApplicationLifecycleEvents = true, // Auto-capture app lifecycle events (default: true)
    CaptureExceptions = true,               // Auto-capture unhandled exceptions (default: true)
    PersonProfiles = PersonProfiles.IdentifiedOnly, // When to create person profiles
    PreloadFeatureFlags = true,             // Fetch flags on init (default: true)
    SendFeatureFlagEvent = true,            // Track flag usage (default: true)
    LogLevel = PostHogLogLevel.Warning      // Log verbosity (default: Warning)
});
```

## Capturing events

You can send custom events using `capture`:

```csharp
PostHog.Capture("level_completed");
```

> **Tip:** We recommend naming events in an `[object] [verb]` format, where `[object]` is the entity the behavior relates to, and `[verb]` is the behavior itself. For example, `level completed`, `item purchased`, or `quest started`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](https://posthog.com/docs/data/events.md#event-properties) object:

```csharp
PostHog.Capture("level_completed", new Dictionary<string, object>
{
    { "level_id", 5 },
    { "score", 1250 }
});
```

### Capturing screen views

Track screen views to understand user navigation through your game:

```csharp
PostHog.Screen("Main Menu");

// With additional properties
PostHog.Screen("Level Select", new Dictionary<string, object>
{
    { "unlocked_levels", 5 }
});
```

## Identifying users

> We highly recommend reading our section on [Identifying users](https://posthog.com/docs/integrate/identifying-users.md) to better understand how to correctly use this method.

When a user logs in, you can associate their events with their identity by calling `IdentifyAsync`:

```csharp
using PostHogUnity;
using System.Collections.Generic;

await PostHog.IdentifyAsync("user_123", new Dictionary<string, object>
{
    { "email", "user@example.com" },
    { "name", "Max Hedgehog" },
    { "plan", "premium" }
});
```

### Reset on logout

When a user logs out, call `ResetAsync` to clear the current user's identity and generate a new anonymous distinct ID:

```csharp
await PostHog.ResetAsync();
```

## Anonymous vs identified events

PostHog captures two types of events: [**anonymous** and **identified**](https://posthog.com/docs/data/anonymous-vs-identified-events.md).

**Identified events** let you attribute events to a specific player and attach [person properties](https://posthog.com/docs/product-analytics/person-properties.md). They're best suited for players who have signed in.

Scenarios where you want identified events are:

-   Tracking signed-in players across sessions and devices
-   Segmenting your analysis by individual player
-   Following a player's full journey from install through retention

**Anonymous events** have no individually identifiable data. They're best suited for players you haven't identified yet.

Scenarios where you want anonymous events are:

-   Players in a guest or pre-login flow
-   Sessions where players never create an account

Under the hood, the key difference is that identified events create a [person profile](https://posthog.com/docs/data/persons.md) and anonymous events do not.

> **Important:** Anonymous events can be up to 4x cheaper to process than identified ones, so we recommend only capturing identified events when needed.

### Controlling person profiles

By default, the SDK captures identified events. To control whether events create person profiles, configure `PersonProfiles` during initialization:

```csharp
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",
    Host = "https://us.i.posthog.com",
    PersonProfiles = PersonProfiles.IdentifiedOnly // Only create profiles on identify
});
```

Available options:

-   `PersonProfiles.IdentifiedOnly` (default) – Only creates person profiles when `IdentifyAsync` is called
-   `PersonProfiles.Always` – Creates person profiles for all events
-   `PersonProfiles.Never` – Never creates person profiles (anonymous events only)

## Super properties

Super properties are properties associated with events that are set once and then sent with every `Capture` call.

They are set using `Register`, which takes a key and value, and they persist across sessions.

```csharp
// Register a super property
PostHog.Register("app_version", "1.2.3");
PostHog.Register("platform", "iOS");
```

This ensures that every event you send will include these properties.

### Removing super properties

Super properties are persisted across sessions so you have to explicitly remove them if they are no longer relevant:

```csharp
PostHog.Unregister("app_version");
```

If you are doing this as part of a user logging out you can instead use `PostHog.ResetAsync()` which takes care of clearing all stored super properties and more.

## Group analytics

Group analytics allows you to associate the events for that person's session with a group (e.g. teams, organizations, etc.). Read the [Group Analytics](https://posthog.com/docs/user-guides/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](https://posthog.com/pricing.md).

-   Associate events with a group:

```csharp
PostHog.Group("company", "company_id_in_your_db");
```

-   Associate events with a group AND update group properties:

```csharp
PostHog.Group("company", "company_id_in_your_db", new Dictionary<string, object>
{
    { "name", "Acme Inc" },
    { "plan", "enterprise" },
    { "employees", 100 }
});
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

## Feature Flags

PostHog's [feature flags](https://posthog.com/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

### Boolean feature flags

```csharp
if (PostHog.IsFeatureEnabled("flag-key"))
{
    // Do something differently for this user
}
```

### Multivariate feature flags

```csharp
var flag = PostHog.GetFeatureFlag("flag-key");
if (flag.IsEnabled)
{
    string variant = flag.GetVariant("control"); // "control" is the default value
    if (variant == "variant-key") // Replace with your variant key
    {
        // Do something for this variant
    }
}
```

### Feature flag payloads

Access payloads through the feature flag object:

```csharp
// Define your payload class (must use [Serializable] and public fields for JsonUtility)
[Serializable]
public class CheckoutConfig
{
    public string theme;
    public int maxItems;
    public bool showBanner;
}

// Get flag and access payload
var flag = PostHog.GetFeatureFlag("checkout-config");
if (flag.IsEnabled)
{
    var config = flag.GetPayload<CheckoutConfig>();
    Debug.Log($"Theme: {config.theme}, Max items: {config.maxItems}");
}

// For dynamic/nested payloads, use PostHogJson
var payload = flag.GetPayloadJson();
string theme = payload["theme"].GetString("light");
int maxItems = payload["settings"]["maxItems"].GetInt(10);
```

### Ensuring flags are loaded before usage

Every time a user opens the app, we send a request in the background to fetch the feature flags that apply to that user. We store those flags in storage.

This means that for most screens, the feature flags are available immediately – **except for the first time a user visits**.

To be notified when flags are loaded:

```csharp
// Via callback during setup
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",
    OnFeatureFlagsLoaded = () => Debug.Log("Flags ready!")
});

// Or via event
PostHog.OnFeatureFlagsLoaded += () => UpdateUI();
```

### Reloading feature flags

Feature flag values are cached. If something has changed with your user and you'd like to refetch their flag values, call:

```csharp
await PostHog.ReloadFeatureFlagsAsync();
```

### Overriding server properties for flags

You can set properties used for flag evaluation:

```csharp
// Set person properties for targeting
PostHog.SetPersonPropertiesForFlags(new Dictionary<string, object>
{
    { "plan", "premium" },
    { "beta_user", true }
});

// Set group properties for targeting
PostHog.SetGroupPropertiesForFlags("company", new Dictionary<string, object>
{
    { "size", "enterprise" }
});

// Reset properties
PostHog.ResetPersonPropertiesForFlags();
PostHog.ResetGroupPropertiesForFlags();
```

## Experiments (A/B tests)

Since [Experiments](https://posthog.com/docs/experiments/start-here.md) use Feature Flags, the code for running an experiment is very similar to the Feature Flags code:

```csharp
var flag = PostHog.GetFeatureFlag("experiment-feature-flag-key");
if (flag.GetVariant("control") == "variant-name")
{
    // Do something for this variant
}
```

It's also possible to [run Experiments without using Feature Flags](https://posthog.com/docs/experiments/running-experiments-without-feature-flags.md).

## Error Tracking

The Unity SDK automatically captures unhandled exceptions and sends them to PostHog. This is enabled by default.

For the full setup guide, see the [Unity error tracking installation docs](https://posthog.com/docs/error-tracking/installation/unity.md).

### Manual exception capture

For handled exceptions that you want to report:

```csharp
try
{
    // Risky operation
}
catch (Exception e)
{
    PostHog.CaptureException(e);
    // Handle the error gracefully
}

// With additional properties
PostHog.CaptureException(e, new Dictionary<string, object>
{
    { "context", "checkout_flow" },
    { "item_count", 5 }
});
```

### Configuration

```csharp
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",

    // Exception tracking options
    CaptureExceptions = true,              // Enable automatic capture (default: true)
    ExceptionDebounceIntervalMs = 1000,    // Min ms between captures (default: 1000)
    CaptureExceptionsInEditor = true       // Capture in Unity Editor (default: true)
});
```

### Disabling Error Tracking

```csharp
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",
    CaptureExceptions = false  // Disable automatic exception capture
});
```

## Session Replay

Session Replay enables you to record and watch user sessions in your Unity game. It captures screenshots, touch/mouse input, network requests, and console logs. Session Replay is **disabled by default** and must be explicitly enabled. Performance impact varies based on your game's complexity and target devices.

The SDK uses `AsyncGPUReadback` to capture screenshots without blocking the main thread, ensuring minimal performance impact during gameplay.

### Enabling Session Replay

```csharp
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",
    Host = "https://us.i.posthog.com",
    SessionReplay = true
});
```

### Configuration options

You can customize Session Replay behavior with `SessionReplayConfig`:

```csharp
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",
    SessionReplay = true,
    SessionReplayConfig = new PostHogSessionReplayConfig
    {
        // Screenshot settings
        ThrottleDelaySeconds = 1.0f,    // Min time between screenshots (default: 1.0)
        ScreenshotQuality = 80,          // JPEG quality 1-100 (default: 80)
        ScreenshotScale = 0.75f,         // Resolution scale 0.1-1.0 (default: 0.75)

        // Telemetry capture
        CaptureNetworkTelemetry = true,  // Record HTTP request metadata (default: true)
        CaptureLogs = false,             // Record console logs (default: false)
        MinLogLevel = SessionReplayLogLevel.Warning,  // Log, Warning, or Error

        // Queue settings
        FlushAt = 20,                    // Events before auto-flush (default: 20)
        FlushIntervalSeconds = 30,       // Auto-flush interval (default: 30)
        MaxQueueSize = 100               // Max queued events (default: 100)
    }
});
```

### Manual control

You can manually start and stop session recording:

```csharp
// Check if Session Replay is active
if (PostHogSDK.IsSessionReplayActive)
{
    // Stop recording
    PostHogSDK.StopSessionReplay();
}

// Start recording (if not already active)
PostHogSDK.StartSessionReplay();
```

### Recording network requests

You can manually record request metadata when `CaptureNetworkTelemetry` is enabled:

```csharp
PostHogSDK.RecordNetworkRequest(
    url: "https://api.example.com/data",
    method: "GET",
    statusCode: 200,
    durationMs: 150,
    responseSize: 1024
);
```

### Platform support for Session Replay

| Platform | Session Replay Support |
| --- | --- |
| Windows/Mac/Linux | Full |
| iOS | Full |
| Android | Full |
| WebGL | Not supported |

> **Note:** Session Replay requires async GPU readback support. On WebGL, Session Replay is automatically disabled.

### Performance considerations

Session Replay captures screenshots which can impact performance. To optimize:

-   Increase `ThrottleDelaySeconds` to reduce capture frequency
-   Lower `ScreenshotScale` to reduce resolution
-   Lower `ScreenshotQuality` to reduce file size
-   Disable `CaptureNetworkTelemetry` and `CaptureLogs` if not needed

## Application lifecycle events

When `CaptureApplicationLifecycleEvents` is enabled (default: `true`), these events are captured automatically:

-   `Application Installed` – First launch
-   `Application Updated` – Version changed
-   `Application Opened` – App foregrounded
-   `Application Backgrounded` – App backgrounded

## Opt out of data capture

For GDPR compliance, you can disable data collection at any time:

```csharp
// Opt out (stops all tracking, clears queue)
PostHog.OptOut();

// Opt back in
PostHog.OptIn();

// Check status
if (PostHog.IsOptedOut)
{
    // Show consent dialog
}
```

## Debug mode

If you're not seeing the expected events being captured or Feature Flags being evaluated, enable debug mode to see what's happening:

```csharp
PostHog.Setup(new PostHogConfig
{
    ApiKey = "<ph_project_token>",
    Host = "https://us.i.posthog.com",
    LogLevel = PostHogLogLevel.Debug
});
```

Available log levels: `None`, `Error`, `Warning`, `Info`, `Debug`

## Manual flush

Force send all queued events immediately:

```csharp
PostHog.Flush();
```

## Shutdown

Clean up when your app exits:

```csharp
void OnApplicationQuit()
{
    PostHog.Shutdown();
}
```

> **Note:** The SDK automatically flushes on app quit, so explicit shutdown is optional.

## Platform support

| Platform | Support |
| --- | --- |
| Windows/Mac/Linux | Full |
| iOS | Full |
| Android | Full |
| WebGL | With limitations\* |
| Consoles | Untested |

\*WebGL uses PlayerPrefs for storage (limited size) and is subject to CORS restrictions.

## Troubleshooting

### Events not appearing in PostHog

1.  Check your API key is correct
2.  Verify the host URL matches your PostHog instance (e.g., `https://us.i.posthog.com` or `https://eu.i.posthog.com`)
3.  Set `LogLevel = PostHogLogLevel.Debug` to see detailed logs
4.  Ensure you're not opted out (`PostHog.IsOptedOut`)

### WebGL issues

-   Ensure your PostHog instance allows CORS from your domain
-   WebGL has limited storage – consider reducing `MaxQueueSize`
