# .NET - Docs

This is an optional library you can install if you're working with .NET Core. It uses an internal queue to make calls fast and non-blocking. It also batches requests and flushes asynchronously, making it perfect to use in any part of your web app or other server side application that needs performance.

## Installation

The `PostHog` package supports any .NET platform that targets .NET Standard 2.1 or .NET 8+, including MAUI, Blazor, and console applications. The `PostHog.AspNetCore` package provides additional conveniences for ASP.NET Core applications such as streamlined registration, request-scoped caching, and integration with [.NET Feature Management](https://learn.microsoft.com/en-us/azure/azure-app-configuration/feature-management-dotnet-reference).

> **Note:** We actively test with ASP.NET Core. Other platforms should work but haven't been specifically tested. If you encounter issues, please [report them on GitHub](https://github.com/PostHog/posthog-dotnet/issues).

> **Not supported:** Classic UWP (requires .NET Standard 2.0 only). Microsoft has [deprecated UWP](https://learn.microsoft.com/en-us/windows/apps/windows-app-sdk/migrate-to-windows-app-sdk/migrate-to-windows-app-sdk-ovw) in favor of the Windows App SDK. For Unity projects, see our dedicated [Unity SDK](/docs/libraries/unity.md).

Terminal

PostHog AI

```bash
dotnet add package PostHog.AspNetCore
```

In your `Program.cs` (or `Startup.cs` for ASP.NET Core 2.x) file, add the following code:

C#

PostHog AI

```csharp
using PostHog;
var builder = WebApplication.CreateBuilder(args);
// Add PostHog to the dependency injection container as a singleton.
builder.AddPostHog();
```

Make sure to configure PostHog with your project token, instance address, and optional personal API key. For example, in `appsettings.json`:

JSON

PostHog AI

```json
{
  "PostHog": {
    "ProjectToken": "<ph_project_token>",
    "HostUrl": "https://us.i.posthog.com"
  }
}
```

> **Note:** If the host is not specified, the default host `https://us.i.posthog.com` is used.

Use a secrets manager to store your personal API key. For example, when developing locally you can use the `UserSecrets` feature of the `dotnet` CLI:

Terminal

PostHog AI

```bash
dotnet user-secrets init
dotnet user-secrets set "PostHog:PersonalApiKey" "phx_..."
```

You can find your project token and instance address in the [project settings](https://app.posthog.com/project/settings) page in PostHog.

## Working with .NET Feature Management

`PostHog.AspNetCore` supports [.NET Feature Management](https://learn.microsoft.com/en-us/azure/azure-app-configuration/feature-management-dotnet-reference). This enables you to use the <feature /\> tag helper and the `FeatureGateAttribute` in your ASP.NET Core applications to gate access to certain features using PostHog feature flags.

To use feature flags with the .NET Feature Management library, you'll need to implement the `IPostHogFeatureFlagContextProvider` interface. The quickest way to do that is to inherit from the `PostHogFeatureFlagContextProvider` class and override the `GetDistinctId` and `GetFeatureFlagOptionsAsync` methods.

C#

PostHog AI

```csharp
public class MyFeatureFlagContextProvider(IHttpContextAccessor httpContextAccessor)
    : PostHogFeatureFlagContextProvider
{
    protected override string? GetDistinctId()
        => httpContextAccessor.HttpContext?.User.Identity?.Name;
    protected override ValueTask<FeatureFlagOptions> GetFeatureFlagOptionsAsync()
    {
        // In a real app, you might get this information from a
        // database or other source for the current user.
        return ValueTask.FromResult(
            new FeatureFlagOptions
            {
                PersonProperties = new Dictionary<string, object?>
                {
                    ["email"] = "some-test@example.com"
                },
                OnlyEvaluateLocally = true
            });
    }
}
```

Then, register your implementation in `Program.cs` (or `Startup.cs`):

C#

PostHog AI

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.AddPostHog(options => {
    options.UseFeatureManagement<MyFeatureFlagContextProvider>();
});
```

With this in place, you can now use `feature` tag helpers in your Razor views:

HTML

PostHog AI

```html
<feature name="awesome-new-feature">
    <p>This is the new feature!</p>
</feature>
<feature name="awesome-new-feature" negate="true">
    <p>Sorry, no awesome new feature for you.</p>
</feature>
```

Multivariate feature flags are also supported:

HTML

PostHog AI

```html
<feature name="awesome-new-feature" value="variant-a">
    <p>This is the new feature variant A!</p>
</feature>
<feature name="awesome-new-feature" value="variant-b">
    <p>This is the new feature variant B!</p>
</feature>
```

You can also use the `FeatureGateAttribute` to gate access to controllers or actions:

C#

PostHog AI

```csharp
[FeatureGate("awesome-new-feature")]
public class NewFeatureController : Controller
{
    public IActionResult Index()
    {
        return View();
    }
}
```

## Using the core package without ASP.NET Core

If you're not using ASP.NET Core (for example, in a console application, MAUI app, or Blazor WebAssembly), install the `PostHog` package instead of `PostHog.AspNetCore`. This package has no ASP.NET Core dependencies and can be used in any .NET project targeting .NET Standard 2.1 or .NET 8+.

Terminal

PostHog AI

```bash
dotnet add package PostHog
```

The `PostHogClient` class must be implemented as a singleton in your project. For `PostHog.AspNetCore`, this is handled by the `builder.AddPostHog();` method. For the `PostHog` package, you can do the following if you're using dependency injection:

C#

PostHog AI

```csharp
builder.Services.AddPostHog();
```

If you're not using a `builder` (such as in a console application), you can do the following:

C#

PostHog AI

```csharp
using PostHog;
var services = new ServiceCollection();
services.AddPostHog();
var serviceProvider = services.BuildServiceProvider();
var posthog = serviceProvider.GetRequiredService<IPostHogClient>();
```

The `AddPostHog` methods accept an optional `Action<PostHogOptions>` parameter that you can use to configure the client.

If you're not using dependency injection, you can create a static instance of the `PostHogClient` class and use that everywhere in your project:

C#

PostHog AI

```csharp
using PostHog;
public static readonly PostHogClient PostHog = new(new PostHogOptions {
    ProjectToken = "<ph_project_token>",
    HostUrl = new Uri("https://us.i.posthog.com"),
    PersonalApiKey = Environment.GetEnvironmentVariable(
      "PostHog__PersonalApiKey")
});
```

## Debug mode

If you're not seeing the expected events being captured, the feature flags being evaluated, or the surveys being shown, you can enable debug mode to see what's happening.

To see detailed logging, set the log level to `Debug` or `Trace` in `appsettings.json`:

JSON

PostHog AI

```json
{
  "DetailedErrors": true,
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "PostHog": "Trace"
    }
  },
  ...
}
```

## Identifying users

> **Identifying users is required.** Backend events need a `distinct_id` that matches the ID your frontend uses when calling `posthog.identify()`. Without this, backend events are orphaned — they can't be linked to frontend event captures, [session replays](/docs/session-replay.md), [LLM traces](/docs/ai-engineering.md), or [error tracking](/docs/error-tracking.md).
>
> See our guide on [identifying users](/docs/getting-started/identify-users.md) for how to set this up.

## Capturing events

You can send custom events using `capture`:

C#

PostHog AI

```csharp
posthog.Capture("distinct_id_of_the_user", "user_signed_up");
```

> **Tip:** We recommend using a `[object] [verb]` format for your event names, where `[object]` is the entity that the behavior relates to, and `[verb]` is the behavior itself. For example, `project created`, `user signed up`, or `invite sent`.

### Setting event properties

Optionally, you can include additional information with the event by including a [properties](/docs/data/events.md#event-properties) object:

C#

PostHog AI

```csharp
posthog.Capture(
    "distinct_id_of_the_user",
    "user_signed_up",
    properties: new() {
        ["login_type"] = "email",
        ["is_free_trial"] = "true"
    }
);
```

### Sending page views

If you're aiming for a backend-only implementation of PostHog and won't be capturing events from your frontend, you can send `$pageview` events from your backend like so:

C#

PostHog AI

```csharp
using PostHog;
using Microsoft.AspNetCore.Http.Extensions;
posthog.CapturePageView(
    "distinct_id_of_the_user",
    HttpContext.Request.GetDisplayUrl());
```

## Request context

For ASP.NET Core apps using `PostHog.AspNetCore`, add request context middleware before routes that call PostHog. This reads incoming PostHog tracing headers and attaches request metadata to captures, exceptions, and feature flag evaluation inside the request.

Program.cs

PostHog AI

```csharp
using PostHog;
using PostHog.AspNetCore;
var builder = WebApplication.CreateBuilder(args);
builder.AddPostHog();
var app = builder.Build();
app.UsePostHogRequestContext();
```

If you're using [PostHog JS](/docs/libraries/js.md) on the frontend, configure [`tracing_headers`](/docs/libraries/js/config.md#tracing-headers) for your ASP.NET Core backend hostname so browser requests include the session and distinct ID headers.

The middleware reads `X-PostHog-Distinct-Id` and `X-PostHog-Session-Id` as request-scoped analytics context. It also adds request metadata such as `$current_url`, `$request_method`, `$request_path`, `$user_agent`, and `$ip`. Explicit distinct IDs and event properties always override request context.

Tracing headers are client-controlled analytics context, not authentication or authorization. For security-sensitive server-side decisions, pass an authenticated distinct ID explicitly. You can ignore tracing headers while still collecting request metadata:

C#

PostHog AI

```csharp
app.UsePostHogRequestContext(options =>
{
    options.UseTracingHeaders = false;
});
```

Request-context overloads like `posthog.Capture("checkout started")` and `posthog.EvaluateFlagsAsync()` use the current request distinct ID when one is available.

## Error tracking

You can manually capture exceptions using `CaptureException`. This sends a `$exception` event with stack frames, inner exceptions, aggregate exceptions, source context when available, and .NET runtime metadata.

File names, line numbers, and source context depend on debug information already available from the captured .NET stack trace. PostHog doesn't support uploading .NET PDB files yet, so production builds without runtime-accessible debug information may show less detailed stack frames.

C#

PostHog AI

```csharp
try
{
    ProcessOrder(orderId);
}
catch (Exception exception)
{
    posthog.CaptureException(exception, "user_distinct_id");
}
```

Add custom properties to include request, tenant, or domain context:

C#

PostHog AI

```csharp
posthog.CaptureException(
    exception,
    "user_distinct_id",
    new Dictionary<string, object>
    {
        ["order_id"] = orderId,
        ["environment"] = "production",
    }
);
```

For the full setup guide, see the [.NET error tracking installation docs](/docs/error-tracking/installation/dotnet.md).

Automatic exception capture is not available in the .NET SDK yet.

## Person profiles and properties

The .NET SDK captures identified events by default. These create [person profiles](/docs/data/persons.md). To set [person properties](/docs/data/user-properties.md) in these profiles, include them when capturing an event:

C#

PostHog AI

```csharp
posthog.Capture(
    "distinct_id",
    "event_name",
    personPropertiesToSet: new() { ["name"] = "Max Hedgehog" },
    personPropertiesToSetOnce: new() { ["initial_url"] = "/blog" }
);
```

For more details on the difference between `$set` and `$set_once`, see our [person properties docs](/docs/data/user-properties.md#what-is-the-difference-between-set-and-set_once).

To capture [anonymous events](/docs/data/anonymous-vs-identified-events.md) without person profiles, set the event's `$process_person_profile` property to `false`:

C#

PostHog AI

```csharp
posthog.Capture(
    "distinct_id",
    "event_name",
    properties: new() {
        ["$process_person_profile"] = false
    }
)
```

## Alias

Sometimes, you want to assign multiple distinct IDs to a single user. This is helpful when your primary distinct ID is inaccessible. For example, if a distinct ID used on the frontend is not available in your backend.

In this case, you can use `alias` to assign another distinct ID to the same user.

C#

PostHog AI

```csharp
await posthog.AliasAsync("current_distinct_id", "new_distinct_id");
```

We strongly recommend reading our docs on [alias](/docs/product-analytics/identify.md#alias-assigning-multiple-distinct-ids-to-the-same-user) to best understand how to correctly use this method.

## Group analytics

Group analytics allows you to associate an event with a group (e.g. teams, organizations, etc.). Read the [group analytics](/docs/product-analytics/group-analytics.md) guide for more information.

> **Note:** This is a paid feature and is not available on the open-source or free cloud plan. Learn more on our [pricing page](/pricing.md).

To capture an event and associate it with a group, add the `groups` argument to your `Capture` call:

C#

PostHog AI

```csharp
posthog.Capture(
    "user_distinct_id",
    "some_event",
    groups: [new Group("company", "company_id_in_your_db")]);
```

Update properties on a group, use the `GroupIdentifyAsync` method:

C#

PostHog AI

```csharp
await posthog.GroupIdentifyAsync(
    type: "company",
    key: "company_id_in_your_db",
    name: "Awesome Inc.",
    properties: new()
    {
        ["employees"] = 11
    }
);
```

The `name` is a special property which is used in the PostHog UI for the name of the group. If you don't specify a `name` property, the group ID will be used instead.

## Feature flags

PostHog's [feature flags](/docs/feature-flags.md) enable you to safely deploy and roll back new features as well as target specific users and groups with them.

There are two steps to implement feature flags in .NET:

### Step 1: Evaluate flags once

Call `EvaluateFlagsAsync()` once for the user, then read values from the returned snapshot.

#### Boolean feature flags

C#

PostHog AI

```csharp
var flags = await posthog.EvaluateFlagsAsync("distinct_id_of_your_user");
if (flags.IsEnabled("flag-key"))
{
    // Do something differently for this user
    // Optional: fetch the payload
    var matchedPayload = flags.GetFlagPayload("flag-key");
}
```

#### Multivariate feature flags

C#

PostHog AI

```csharp
var flags = await posthog.EvaluateFlagsAsync("distinct_id_of_your_user");
var enabledVariant = flags.GetFlag("flag-key")?.VariantKey;
if (enabledVariant == "variant-key") // replace "variant-key" with the key of your variant
{
    // Do something differently for this user
    // Optional: fetch the payload
    var matchedPayload = flags.GetFlagPayload("flag-key");
}
```

`flags.GetFlag()` returns a nullable `FeatureFlag` object. Check `VariantKey` for multivariate flags and `IsEnabled` for boolean flags. It returns `null` when the flag wasn't returned by the evaluation.

> **Note:** `posthog.IsFeatureEnabledAsync()`, `posthog.GetFeatureFlagAsync()`, and `Capture(..., sendFeatureFlags: true, ...)` still work during the migration period, but they're deprecated. Prefer `EvaluateFlagsAsync()` for new code.

### Step 2: Include feature flag information when capturing events

If you want use your feature flag to breakdown or filter events in your [insights](/docs/product-analytics/insights.md), you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

> **Note:** This step is only required for events captured using our server-side SDKs or [API](/docs/api.md).

There are two methods you can use to include feature flag information in your events:

#### Method 1: Pass the evaluated flags snapshot to `Capture()`

Pass the same `flags` object that you used for branching. This attaches the exact flag values from that evaluation and doesn't make another `/flags` request.

C#

PostHog AI

```csharp
var flags = await posthog.EvaluateFlagsAsync("distinct_id_of_your_user");
if (flags.IsEnabled("flag-key"))
{
    // Do something differently for this user
}
posthog.Capture(
    "distinct_id_of_your_user",
    "event_name",
    properties: null,
    groups: null,
    flags: flags
);
```

By default, this attaches every flag in the snapshot using `$feature/<flag-key>` properties and `$active_feature_flags`.

To reduce event property bloat, pass a filtered snapshot:

C#

PostHog AI

```csharp
// Attach only flags accessed with IsEnabled() or GetFlag() before this call
posthog.Capture(
    "distinct_id_of_your_user",
    "event_name",
    properties: null,
    groups: null,
    flags: flags.OnlyAccessed()
);
// Attach only specific flags
posthog.Capture(
    "distinct_id_of_your_user",
    "event_name",
    properties: null,
    groups: null,
    flags: flags.Only("checkout-flow", "new-dashboard")
);
```

#### Method 2: Include the `$feature/feature_flag_name` property manually

In the event properties, include `$feature/feature_flag_name: variant_key`:

C#

PostHog AI

```csharp
posthog.Capture(
    "distinct_id_of_your_user",
    "event_name",
    properties: new()
    {
        // Replace feature-flag-key with your flag key and "variant-key" with the key of your variant
        ["$feature/feature-flag-key"] = "variant-key",
    }
);
```

### Evaluating only specific flags

By default, `EvaluateFlagsAsync()` evaluates every flag for the user. If you only need a few flags, pass `FlagKeysToEvaluate` to request only those flags:

C#

PostHog AI

```csharp
var flags = await posthog.EvaluateFlagsAsync(
    "distinct_id_of_your_user",
    options: new AllFeatureFlagsOptions
    {
        FlagKeysToEvaluate = new[] { "checkout-flow", "new-dashboard" },
    }
);
```

### Sending `$feature_flag_called` events

Capturing `$feature_flag_called` events enables PostHog to know when a flag was accessed by a user and provide [analytics and insights](/docs/product-analytics/insights.md) on the flag. With `EvaluateFlagsAsync()`, the SDK sends this event when you call `flags.IsEnabled()` or `flags.GetFlag()` for a flag.

The SDK deduplicates these events per `(distinct_id, flag, value)` in a local cache. If you reinitialize the PostHog client, the cache resets and `$feature_flag_called` events may be sent again. PostHog handles duplicates, so duplicate `$feature_flag_called` events don't affect your analytics.

`flags.GetFlagPayload()` doesn't send `$feature_flag_called` events and doesn't count as an access for `OnlyAccessed()`.

### Advanced: Overriding server properties

Sometimes, you may want to evaluate feature flags using [person properties](/docs/product-analytics/person-properties.md), [groups](/docs/product-analytics/group-analytics.md), or group properties that haven't been ingested yet, or were set incorrectly earlier.

You can provide properties to evaluate the flag with by using the `person properties`, `groups`, and `group properties` arguments. PostHog will then use these values to evaluate the flag, instead of any properties currently stored on your PostHog server.

For example:

C#

PostHog AI

```csharp
var flags = await posthog.EvaluateFlagsAsync(
    "distinct_id_of_the_user",
    options: new AllFeatureFlagsOptions
    {
        PersonProperties = new()
        {
            ["property_name"] = "value",
        },
        Groups = new()
        {
            new Group("your_group_type", "your_group_id")
            {
                ["group_property_name"] = "value",
            },
            new Group("another_group_type", "another_group_id")
            {
                ["group_property_name"] = "another value",
            },
        },
    }
);
if (flags.IsEnabled("flag-key"))
{
    // Do something differently for this user
}
```

### Overriding GeoIP properties

By default, a user's GeoIP properties are set using the IP address they use to capture events on the frontend. You may want to override the these properties when evaluating feature flags. A common reason to do this is when you're not using PostHog on your frontend, so the user has no GeoIP properties.

You can override GeoIP properties by including them in the `person_properties` parameter when evaluating feature flags. This is useful when you're evaluating flags on your backend and want to use the client's location instead of your server's location.

The following GeoIP properties can be overridden:

-   `$geoip_country_code`
-   `$geoip_country_name`
-   `$geoip_city_name`
-   `$geoip_city_confidence`
-   `$geoip_continent_code`
-   `$geoip_continent_name`
-   `$geoip_latitude`
-   `$geoip_longitude`
-   `$geoip_postal_code`
-   `$geoip_subdivision_1_code`
-   `$geoip_subdivision_1_name`
-   `$geoip_subdivision_2_code`
-   `$geoip_subdivision_2_name`
-   `$geoip_subdivision_3_code`
-   `$geoip_subdivision_3_name`
-   `$geoip_time_zone`

Simply include any of these properties in the `person_properties` parameter alongside your other person properties when calling feature flags.

### Evaluation contexts

Configure evaluation contexts so this SDK only evaluates flags intended for the matching application, platform, or product area. For ASP.NET Core apps using `PostHog.AspNetCore`, add them to the `PostHog` configuration section:

JSON

PostHog AI

```json
{
    "PostHog": {
        "ProjectToken": "<ph_project_token>",
        "HostUrl": "https://us.i.posthog.com",
        "EvaluationContexts": ["main-app", "api", "backend"]
    }
}
```

For code-based configuration, set `EvaluationContexts` on `PostHogOptions`:

C#

PostHog AI

```csharp
var posthog = new PostHogClient(new PostHogOptions
{
    ProjectToken = "<ph_project_token>",
    HostUrl = new Uri("https://us.i.posthog.com"),
    EvaluationContexts = ["main-app", "api", "backend"],
});
```

Remote `/flags` requests from `EvaluateFlagsAsync()` include `evaluation_contexts` when configured.

For more details, see the [evaluation contexts guide](/docs/feature-flags/evaluation-contexts.md).

### Local evaluation

Evaluating feature flags requires making a request to PostHog for each flag. However, you can improve performance by evaluating flags locally. Instead of making a request for each flag, PostHog will periodically request and store feature flag definitions locally, enabling you to evaluate flags without making additional requests.

It is best practice to use local evaluation flags when possible, since this enables you to resolve flags faster and with fewer API calls.

For details on how to implement local evaluation, see our [local evaluation guide](/docs/feature-flags/local-evaluation.md).

## Experiments (A/B tests)

Since [experiments](/docs/experiments/start-here.md) use feature flags, the code for running an experiment is very similar to the feature flags code:

C#

PostHog AI

```csharp
var flags = await posthog.EvaluateFlagsAsync("user_distinct_id");
var variant = flags.GetFlag("experiment-feature-flag-key")?.VariantKey;
if (variant == "variant-name")
{
    // Do something
}
```

It's also possible to [run experiments without using feature flags](/docs/experiments/running-experiments-without-feature-flags.md).

## AI observability

`PostHog.AI` adds [AI observability](/docs/ai-observability.md) for .NET applications using OpenAI or Azure OpenAI. It is currently pre-release, so expect breaking changes before a stable release.

For installation instructions, see the [OpenAI guide for .NET](/docs/ai-observability/installation/openai.md#net-support) or the [Azure OpenAI guide for .NET](/docs/ai-observability/installation/azure-openai.md#net-support).

## GeoIP properties

The `posthog-dotnet` library disregards the server IP, does not add the GeoIP properties, and does not use the values for feature flag evaluations.

## Serverless environments (Azure Functions/Render/Lambda/...)

By default, the library buffers events before sending them to the `/batch` endpoint for better performance. This can lead to lost events in serverless environments if the .NET process is terminated by the platform before the buffer is fully flushed.

To avoid this, call `await posthog.FlushAsync()` after processing every request by adding it as a middleware to your server. This allows `posthog.Capture()` to remain asynchronous for better performance.

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better