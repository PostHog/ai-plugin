> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Roblox

Canonical URL: https://posthog.com/docs/libraries/roblox

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Installation](#installation)
- [Capturing events](#capturing-events)
- [Identifying users](#identifying-users)
- [Anonymous vs identified events](#anonymous-vs-identified-events)
- [Super properties](#super-properties)
- [Group analytics](#group-analytics)
- [Feature flags](#feature-flags)
- [Experiments (A/B tests)](#experiments-ab-tests)
- [Error tracking](#error-tracking)
- [Autocapture](#autocapture)
- [Sessions and teleports](#sessions-and-teleports)
- [The client relay](#the-client-relay)
- [Opt out of data capture](#opt-out-of-data-capture)
- [Modify or drop events](#modify-or-drop-events)
- [Debug mode](#debug-mode)
- [Manual flush](#manual-flush)
- [Shutdown](#shutdown)
- [Troubleshooting](#troubleshooting)

> **Note:** This SDK is currently in **beta**. Please report any issues on [GitHub](https://github.com/PostHog/posthog-roblox/issues).

This is the official PostHog SDK for Roblox. It's **server-authoritative**: because only the Roblox server can make outbound HTTP requests, the server owns all batching, identity, feature flags, error tracking, and HTTP. A thin client module relays capture calls and client errors to the server over a `RemoteEvent`.

Each player is a PostHog user, keyed by their stable Roblox `UserId`. The SDK keeps an in-memory event queue that's flushed on an interval and again on `game:BindToClose()`, which suits Roblox's ephemeral servers.

## Installation

PostHog is available for Roblox through [Wally](https://wally.run) (the Roblox package manager), or as a model file you import in Studio. The SDK is server-authoritative: the server owns all batching and HTTP, and each player is a PostHog user keyed by their Roblox `UserId`.

### Requirements

-   HTTP requests enabled for your experience: **Game Settings > Security > Allow HTTP Requests**. Only the Roblox server can make outbound HTTP requests, and only when this is on.
-   Your PostHog project token, which you can find in your [project settings](https://app.posthog.com/settings/project).

### Via Wally (recommended)

Add the dependency to your `wally.toml`:

```toml
[dependencies]
PostHog = "posthog/posthog-roblox@0.2.0"
```

Run `wally install`, then map the installed package into `ReplicatedStorage` in your [Rojo](https://rojo.space) project file so it replicates to clients:

```json
"ReplicatedStorage": {
  "$className": "ReplicatedStorage",
  "PostHog": { "$path": "Packages/PostHog" }
}
```

### Via model file

Download the latest `posthog-roblox.rbxm` from the [releases page](https://github.com/PostHog/posthog-roblox/releases). In Studio, right-click `ReplicatedStorage`, choose **Insert from File**, and select the file. Make sure the inserted instance is named `PostHog`.

Either way, you should end up with `ReplicatedStorage > PostHog`, which both server and client code require.

### Initialize on the server

Initialize PostHog once from a server `Script` (for example in `ServerScriptService`):

```lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local PostHog = require(ReplicatedStorage:WaitForChild("PostHog"))

PostHog:Init({
    projectToken = "<ph_project_token>",
    host = "https://us.i.posthog.com", -- usually https://us.i.posthog.com or https://eu.i.posthog.com
})
```

> **Note:** `Init` must run on the server. Calling it from a `LocalScript` is ignored. Requiring the same module from a `LocalScript` gives you a thin client relay instead (see [Capturing events](#capturing-events)).

### Configuration options

Pass any of these to `PostHog:Init`. Only `projectToken` is required; everything else has a sensible default.

```lua
PostHog:Init({
    -- Required
    projectToken = "<ph_project_token>",

    -- Connection
    host = "https://us.i.posthog.com",

    -- Event queue
    flushAt = 20,                  -- Flush once this many events are queued (default: 20)
    flushIntervalSeconds = 30,     -- Flush at least this often (default: 30)
    maxQueueSize = 1000,           -- Drop the oldest events past this size (default: 1000)
    maxBatchSize = 50,             -- Maximum events per HTTP request (default: 50)

    -- Feature flags
    preloadFeatureFlags = true,    -- Fetch a player's flags when they join (default: true)
    sendFeatureFlagEvents = true,  -- Emit $feature_flag_called when a flag is read (default: true)
    sendDefaultPersonPropertiesForFlags = true,
    featureFlagRequestMaxRetries = 1, -- Retries after network errors and 502/504 responses (default: 1)

    -- Autocapture and error tracking
    captureLifecycleEvents = true, -- player_joined/left/idle, server_started/shutdown (default: true)
    captureErrors = true,          -- Capture unhandled errors as $exception events (default: true)
    errorDebounceSeconds = 1,      -- Minimum gap between auto-captured server errors (default: 1)

    -- Identity
    personProfiles = "identified_only", -- "identified_only" | "always" | "never"
    serverDistinctId = "server",        -- distinct_id used for server-scoped (nil subject) events

    -- Client events
    allowClientEvents = true,        -- Accept events relayed from clients (default: true)
    clientRateLimitPerSecond = 20,   -- Per-player rate limit for relayed messages (default: 20)
    maxClientPropertyCount = 100,    -- Maximum properties accepted from one client message (default: 100)

    -- Filtering
    beforeSend = nil,                -- Function that modifies or drops each event before it's queued

    -- Diagnostics
    logLevel = "warn",               -- "debug" | "info" | "warn" | "error" | "none"
})
```

## Capturing events

You can send custom events using `capture`:

On the server, every capture call takes a **subject** as its first argument so you can attribute the event to a specific player. Pass a `Player` and it resolves to their `UserId`:

```lua
local Players = game:GetService("Players")

Players.PlayerAdded:Connect(function(player)
    PostHog:Capture(player, "game_joined")
end)
```

> **Tip:** We recommend naming events in an `[object] [verb]` format, where `[object]` is the entity the behavior relates to, and `[verb]` is the behavior itself. For example, `level completed`, `item purchased`, or `quest started`.

The subject can be a `Player`, a numeric `UserId`, a string distinct ID, or `nil` for a server-scoped event that isn't attributed to any player:

```lua
PostHog:Capture(player, "level_completed")  -- a Player
PostHog:Capture(123456, "level_completed")  -- a UserId
PostHog:Capture(nil, "shop_restocked")      -- server-scoped, no person profile
```

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](https://posthog.com/docs/data/events.md#event-properties) object:

```lua
PostHog:Capture(player, "level_completed", {
    level = 5,
    duration_seconds = 92,
    used_powerup = true,
})
```

### Capturing from the client

The same `PostHog` module works in a `LocalScript`, where it acts as a thin relay: calls are sent to the server over a `RemoteEvent` and attributed to the firing player. There's no API key on the client, and no subject argument:

```lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local PostHog = require(ReplicatedStorage:WaitForChild("PostHog"))

PostHog:Capture("button_clicked", { button = "play" })
```

The server validates, rate-limits, and attributes every relayed event, so a client can't spoof another player or send reserved (`$`\-prefixed) event names.

### Capturing screen views

Track which screens or menus a player views:

```lua
PostHog:Screen(player, "Main Menu")

-- With additional properties
PostHog:Screen(player, "Level Select", {
    unlocked_levels = 5,
})

-- From a LocalScript (relayed, no subject)
PostHog:Screen("Shop")
```

## Identifying users

> We highly recommend reading our section on [Identifying users](https://posthog.com/docs/integrate/identifying-users.md) to better understand how to correctly use this method.

Every player already has a real identity, their Roblox `UserId`, so player events are attributed and create [person profiles](https://posthog.com/docs/data/persons.md) automatically. There's no anonymous-to-identified transition to manage and no `reset` to call. Use `Identify` to attach [person properties](https://posthog.com/docs/product-analytics/person-properties.md) to a player:

```lua
PostHog:Identify(player, {
    display_name = player.DisplayName,
    level = 12,
})
```

The first argument is a [subject](#capturing-events), so you can also identify by `UserId` or distinct ID. Pass a third argument to set properties only if they aren't already set (`$set_once`):

```lua
PostHog:Identify(player, { favorite_mode = "survival" }, { first_seen = os.time() })
```

## Anonymous vs identified events

PostHog captures two types of events: [**anonymous** and **identified**](https://posthog.com/docs/data/anonymous-vs-identified-events.md). Identified events are attributed to a person and build a [person profile](https://posthog.com/docs/data/persons.md); anonymous events are not.

On Roblox this is simpler than on most platforms. Every player already has a stable identity, their Roblox `UserId`, so events you capture for a player are **identified** and create a person profile automatically. There's no logged-out or guest state to reconcile, and no `reset` to call.

The events that stay **anonymous** are **server-scoped** events you capture with a `nil` subject. These describe the server or experience as a whole (for example `server_started` or `shop_restocked`) rather than any one player, so they don't create a person profile.

> **Tip:** Anonymous events are cheaper to process than identified ones, so capture server-wide telemetry that isn't about a specific player with a `nil` subject rather than attributing it to an arbitrary player.

### Controlling person profiles

By default, player events create person profiles and server-scoped events (those captured with a `nil` subject) do not. Change this with `personProfiles`:

```lua
PostHog:Init({
    projectToken = "<ph_project_token>",
    personProfiles = "identified_only", -- default
})
```

Available options:

-   `"identified_only"` (default) – player events create profiles; server-scoped events don't.
-   `"always"` – every event creates or updates a person profile.
-   `"never"` – no event creates a person profile.

## Super properties

Super properties are attached to every event the server sends. They're **server-global**: set once on the server, they apply to events from every player, which makes them a good fit for server-wide context like the place version or region.

Set them with `Register`, which takes a key and value:

```lua
PostHog:Register("place_version", game.PlaceVersion)
PostHog:Register("region", "us-east")
```

> **Note:** Super properties live in memory for the lifetime of the server. Unlike on persistent clients, they aren't stored across sessions, so register the ones you need during `Init` or server startup.

### Removing super properties

```lua
PostHog:Unregister("region")
```

## Group analytics

Group analytics lets you associate a player's events with a group (for example a guild, party, or server). Read the [Group analytics](https://posthog.com/docs/product-analytics/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on the [pricing page](https://posthog.com/pricing.md).

-   Associate a player's events with a group:

```lua
PostHog:Group(player, "guild", "guild_id_in_your_db")
```

-   Associate events with a group and update the group's properties:

```lua
PostHog:Group(player, "guild", "guild_id_in_your_db", {
    name = "The Knights",
    member_count = 42,
})
```

The `name` is a special property used in the PostHog UI for the group's name. If you don't specify it, the group key is used instead.

## Feature flags

PostHog's [feature flags](https://posthog.com/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

Feature flags in the Roblox SDK are evaluated **per player**, so each flag call takes the player (or another subject) as its first argument. When `preloadFeatureFlags` is enabled (the default), a player's flags are fetched automatically when they join, so they're ready to read for the rest of the session.

### Boolean feature flags

```lua
if PostHog:IsFeatureEnabled(player, "flag-key") then
    -- Do something differently for this player
end
```

`IsFeatureEnabled` accepts an optional default that's returned when the flag hasn't loaded yet:

```lua
if PostHog:IsFeatureEnabled(player, "flag-key", false) then
    -- ...
end
```

### Multivariate feature flags

`GetFeatureFlag` returns a table with the flag's `value`, `isEnabled`, `variant`, and `payload`:

```lua
local flag = PostHog:GetFeatureFlag(player, "flag-key")
if flag.isEnabled then
    if flag.variant == "variant-key" then -- Replace with your variant key
        -- Do something for this variant
    end
end
```

### Feature flag payloads

Read the JSON payload attached to a flag with `GetFeatureFlagPayload`:

```lua
local payload = PostHog:GetFeatureFlagPayload(player, "shop-config")
if payload then
    print(payload.theme, payload.maxItems)
end
```

The payload is also available on the flag object returned by `GetFeatureFlag`:

```lua
local flag = PostHog:GetFeatureFlag(player, "shop-config")
local theme = flag.payload and flag.payload.theme
```

### Ensuring flags are loaded before use

When a player joins, the SDK fetches their flags in the background (unless you set `preloadFeatureFlags = false`). For most of a session the flags are available immediately, but the very first read right after a player joins can race the network request.

To force a fresh fetch and wait for it, call `ReloadFeatureFlags`. It **yields** until the request completes and returns whether it succeeded:

```lua
local ok = PostHog:ReloadFeatureFlags(player)
if ok then
    local enabled = PostHog:IsFeatureEnabled(player, "flag-key")
end
```

### Overriding properties for flag evaluation

Set the person or group properties used to evaluate a player's flags. By default this reloads their flags; pass `false` as the final argument to skip the reload:

```lua
-- Person properties for targeting
PostHog:SetPersonPropertiesForFlags(player, {
    level = 12,
    is_vip = true,
})

-- Group properties for targeting
PostHog:SetGroupPropertiesForFlags(player, "guild", {
    member_count = 42,
})
```

## Experiments (A/B tests)

Since [experiments](https://posthog.com/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

```lua
local flag = PostHog:GetFeatureFlag(player, "experiment-feature-flag-key")
if flag.variant == "control" then
    -- Do something for the control group
elseif flag.variant == "test" then
    -- Do something for the test group
end
```

It's also possible to [run experiments without feature flags](https://posthog.com/docs/experiments/running-experiments-without-feature-flags.md).

## Error tracking

The Roblox SDK captures unhandled errors automatically and sends them to PostHog as `$exception` events. This is enabled by default. On the server it listens to `ScriptContext.Error`; requiring the module on the client captures unhandled client errors and relays them to the server.

For the full setup guide, see the [Roblox Error Tracking installation docs](https://posthog.com/docs/error-tracking/installation/roblox.md).

### Manual exception capture

For handled errors you want to report, call `CaptureException` with a subject, a message, and an optional stack trace and properties:

```lua
local ok, err = pcall(riskyOperation)
if not ok then
    PostHog:CaptureException(player, err, debug.traceback(), {
        context = "load_world",
        world = "desert",
    })
end
```

From a `LocalScript`, the relay version takes no subject:

```lua
PostHog:CaptureException("Something went wrong", debug.traceback())
```

### Configuration

```lua
PostHog:Init({
    projectToken = "<ph_project_token>",
    captureErrors = true,        -- Enable automatic capture (default: true)
    errorDebounceSeconds = 1,    -- Minimum gap between auto-captured server errors (default: 1)
})
```

To disable automatic capture, set `captureErrors = false`.

## Autocapture

With `captureLifecycleEvents` enabled (the default), the SDK records a set of session and server events automatically, with no manual instrumentation. These give you concurrency, retention, and engagement metrics from the moment you initialize, so there's meaningful data to chart before you write a single custom event.

| Event | When it fires | Key properties |
| --- | --- | --- |
| `server_started` | The SDK initializes on a server | `player_count`, `max_players`, `is_private_server`, `is_reserved_server` |
| `server_shutdown` | The server shuts down (`game:BindToClose`) | `player_count`, `uptime_seconds` |
| `player_joined` | A player joins | `is_teleport`, `player_count`, `account_age_days`, `membership_type`, `country_code` |
| `player_left` | A player leaves | `session_duration_seconds`, `player_count`, `platform`, `country_code` |
| `player_idle` | Roblox reports a player has gone idle | `idle_seconds` |

Every event, autocaptured or manual, also carries standard context such as `$session_id`, `$os`, `$device_type`, place and server identifiers, and the SDK version.

To turn autocapture off:

```lua
PostHog:Init({
    projectToken = "<ph_project_token>",
    captureLifecycleEvents = false,
})
```

> **Note:** `platform` is reported by the client relay, so on `player_joined` (which fires the instant a player connects) it's usually not known yet; it's populated by the time `player_left` fires. `country_code` is resolved before `player_joined` is sent.

## Sessions and teleports

A session corresponds to a player's connection to a server, and every event carries its `$session_id`. Because experiences often teleport players between places, you can continue a player's session across a teleport so the whole journey is stitched together.

Merge the SDK's teleport data into your `TeleportData` before teleporting:

```lua
local TeleportService = game:GetService("TeleportService")

local options = Instance.new("TeleportOptions")
options:SetTeleportData(PostHog:GetSessionTeleportData(player))

TeleportService:TeleportAsync(placeId, { player }, options)
```

The destination server restores the session automatically when the player arrives, so their events keep the same `$session_id`.

## The client relay

Requiring `PostHog` from a `LocalScript` gives you a thin relay rather than the full SDK. It can't make HTTP requests, so it forwards capture calls and client errors to the server over a `RemoteEvent`, where they're attributed to the firing player.

```lua
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local PostHog = require(ReplicatedStorage:WaitForChild("PostHog"))

-- Optional. Errors are captured automatically; pass { captureErrors = false } to turn that off.
PostHog:Init()

PostHog:Capture("button_clicked", { button = "play" })
```

The client is treated as untrusted. The server validates every relayed message, caps the number of properties, rate-limits per player, blocks reserved (`$`\-prefixed) event names, and always attributes events to the sender, so a client can never spoof another player or the server. Set `allowClientEvents = false` during `Init` if you only capture on the server and want no client surface at all.

## Opt out of data capture

For privacy compliance, you can stop and resume capturing for a given subject at any time:

```lua
PostHog:OptOut(player)

-- Later
PostHog:OptIn(player)
```

## Modify or drop events

To change or drop events before they're sent, pass a `beforeSend` function to `Init`. It runs on every event after the SDK adds its own properties. Return the event to send it, or `nil` to drop it. If `beforeSend` errors, the event is dropped.

```lua
PostHog:Init({
    projectToken = "<ph_project_token>",
    beforeSend = function(event)
        if event.event == "player_idle" then
            return nil
        end
        event.properties.email = nil
        return event
    end,
})
```

## Debug mode

If you're not seeing the events or feature flags you expect, raise the log level to see what the SDK is doing in the output:

```lua
PostHog:Init({
    projectToken = "<ph_project_token>",
    host = "https://us.i.posthog.com",
    logLevel = "debug",
})
```

Available log levels: `"none"`, `"error"`, `"warn"`, `"info"`, `"debug"`.

## Manual flush

Events are sent in batches (every `flushIntervalSeconds`, or once `flushAt` events are queued). Force a send immediately, for example while testing:

```lua
PostHog:Flush()
```

This is asynchronous and doesn't yield. On the client, `Flush` is a no-op since flushing happens on the server.

## Shutdown

The SDK flushes automatically on `game:BindToClose()`, so you rarely need to shut it down explicitly. If you want to stop autocapture, error tracking, and the relay, and flush early:

```lua
PostHog:Shutdown()
```

## Troubleshooting

### Events not appearing in PostHog

1.  **HTTP is enabled.** Turn on **Game Settings > Security > Allow HTTP Requests**. Without it the server can't send anything.
2.  **`Init` ran on the server.** It must be called from a `Script`, not a `LocalScript`. With `logLevel = "debug"` you should see `PostHog initialized` in the output.
3.  **The key and host are correct.** The key starts with `phc_`, and the host matches your region (`https://us.i.posthog.com` or `https://eu.i.posthog.com`).
4.  **You waited for a flush.** Events batch every `flushIntervalSeconds` or once `flushAt` are queued. Call `PostHog:Flush()` to send immediately.

### Client events not arriving

Client events are relayed to the server, so the server SDK must be initialized with `allowClientEvents = true` (the default). If the client logs that the relay `RemoteEvent` wasn't found, the server SDK isn't running.
