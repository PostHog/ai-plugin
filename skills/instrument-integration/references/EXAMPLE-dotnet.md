# PostHog dotnet Example Project

Repository: https://github.com/PostHog/context-mill
Path: example-apps/dotnet

---

## README.md

# PostHog .NET example

This is an [ASP.NET Core](https://learn.microsoft.com/aspnet/core) example demonstrating PostHog integration with product analytics, feature flags, user identification, and error tracking using the server-side [PostHog .NET SDK](https://posthog.com/docs/libraries/dotnet) and minimal APIs.

## Features

- **Product analytics**: Track user events and behaviors
- **User identification**: Associate events with a user via person properties; signed-out visitors get a random id and anonymous events
- **Feature flags**: Control feature rollouts with PostHog feature flags
- **Error tracking**: Report handled exceptions to PostHog error tracking (the .NET SDK has no automatic exception capture yet, so exceptions are reported manually)
- **Server-side tracking**: All tracking happens server-side with the `PostHog.AspNetCore` package
- **Single client per app**: One PostHog client registered through dependency injection, flushed on shutdown

## Getting started

### 1. Install dependencies

```bash
dotnet add package PostHog.AspNetCore
```

Or restore the packages already listed in `PostHogExample.csproj`:

```bash
dotnet restore
```

### 2. Configure environment variables

Copy `.env.example` to `.env` and fill in your values, then export them:

```bash
export POSTHOG_PROJECT_TOKEN=your_posthog_project_token
export POSTHOG_HOST=https://us.i.posthog.com
```

Get your PostHog project token from your [PostHog project settings](https://app.posthog.com/project/settings).

### 3. Run the app

```bash
dotnet run
```

Open [http://localhost:8000](http://localhost:8000) with your browser to see the app.

## Project structure

```
dotnet/
├── PostHogExample.csproj  # Project file and the PostHog.AspNetCore dependency
├── .env.example           # Environment variable template
├── .gitignore
├── Program.cs             # Entry point: app wiring
├── PostHogSetup.cs        # The single PostHog client (config from env)
└── Endpoints.cs           # Routes: identify, events, flags, error tracking
```

## Key integration points

### PostHog client (PostHogSetup.cs)

Register **one client per app** with `builder.AddPostHog()`. It adds `IPostHogClient` to the dependency injection container as a singleton, so inject it into handlers instead of creating clients yourself. The SDK batches events in the background.

```csharp
builder.AddPostHog();
```

### Configuration from the environment (PostHogSetup.cs)

`AddPostHog` reads the `PostHog` configuration section. Map `POSTHOG_PROJECT_TOKEN` and `POSTHOG_HOST` onto it so secrets never live in source. A blank token never breaks the app: the SDK disables itself and every call becomes a no-op. In Development the app also logs a warning that names the variable.

```csharp
builder.Configuration["PostHog:ProjectToken"] = projectToken;
builder.Configuration["PostHog:HostUrl"] = string.IsNullOrWhiteSpace(host)
    ? "https://us.i.posthog.com"
    : host;

builder.AddPostHog();
```

### User identification (Endpoints.cs)

The .NET SDK identifies a user by capturing an event with person properties. The distinct id is the stable user id and must match the id your frontend `identify` call uses.

```csharp
posthog.Capture(
    userId,
    "user_logged_in",
    properties: new() { ["login_method"] = "email" },
    personPropertiesToSet: new() { ["email"] = email },
    personPropertiesToSetOnce: new() { ["first_login_method"] = "email" });
```

### Signed-out visitors (Endpoints.cs)

The `Visitor` helper returns the distinct id and whether the visitor is anonymous. Signed-in users (a `user_id` cookie) keep their stable user id. For everyone else it generates a random GUID, stores it in an `anon_id` cookie so it is reused for the rest of the visit, and `EventProperties` sets `$process_person_profile` to `false` on their events so PostHog does not create a person profile for them.

```csharp
var (userId, anonymous) = Visitor(context);

posthog.Capture(
    userId,
    "burrito_considered",
    properties: EventProperties(anonymous, new() { ["total_considerations"] = count }));
```

Feature flags use the same visitor id, so flag evaluation works for anonymous visitors too.

### Event tracking (Endpoints.cs)

Capture a business event with the visitor's distinct id and an event property.

```csharp
posthog.Capture(
    userId,
    "burrito_considered",
    properties: EventProperties(anonymous, new() { ["total_considerations"] = count }));
```

### Feature flags (Endpoints.cs)

Evaluate flags once per request with `EvaluateFlagsAsync`, then read individual flags off the returned snapshot with `IsEnabled`. This is the current API; the per-flag helpers such as `IsFeatureEnabledAsync` are deprecated.

```csharp
var flags = await posthog.EvaluateFlagsAsync(
    userId,
    options: new AllFeatureFlagsOptions
    {
        FlagKeysToEvaluate = ["new-dashboard-feature"],
    });

var showNewFeature = flags.IsEnabled("new-dashboard-feature");
```

### Error tracking (Endpoints.cs)

Report a handled exception with `CaptureException`. It sends a `$exception` event with the stack frames and inner exceptions. Pass the distinct id and any extra properties.

```csharp
try
{
    RiskyOperation();
}
catch (Exception exception)
{
    posthog.CaptureException(
        exception,
        userId,
        new Dictionary<string, object> { ["route"] = "/profile" });
}
```

### Flush and shutdown (Program.cs)

The client is a DI singleton, so the host disposes it on shutdown (Ctrl+C or SIGTERM). Disposal flushes the queued events before the process exits, so no extra code is needed in a long-running ASP.NET Core app. In serverless environments, call `await posthog.FlushAsync()` after each request instead.

```csharp
app.Run();
```

## Reverse proxy

Server-side SDKs send events from your backend, so they don't need a reverse proxy. Only the browser SDK does.

## Learn more

- [PostHog .NET integration](https://posthog.com/docs/libraries/dotnet)
- [PostHog .NET error tracking](https://posthog.com/docs/error-tracking/installation/dotnet)
- [PostHog feature flags](https://posthog.com/docs/feature-flags)
- [PostHog documentation](https://posthog.com/docs)
- [ASP.NET Core documentation](https://learn.microsoft.com/aspnet/core)

---

## .env.example

```example
POSTHOG_PROJECT_TOKEN=
POSTHOG_HOST=https://us.i.posthog.com

```

---

## Endpoints.cs

```cs
using System.Net;
using PostHog;

public static class Endpoints
{
    // Returns the distinct id for the request and whether the visitor is anonymous.
    //
    // Signed-in users have a "user_id" cookie; that stable id is the join key for all
    // analytics and must match the id your frontend posthog.identify(...) call uses
    // so server- and client-side events land on the same person.
    //
    // Signed-out visitors get a random GUID stored in a cookie so it is reused for
    // the rest of the visit. Never share one fixed id across visitors: they would
    // all collapse into a single person.
    private static (string Id, bool Anonymous) Visitor(HttpContext context)
    {
        if (context.Request.Cookies.TryGetValue("user_id", out var userId) && !string.IsNullOrEmpty(userId))
        {
            return (userId, false);
        }

        if (context.Request.Cookies.TryGetValue("anon_id", out var anonId) && !string.IsNullOrEmpty(anonId))
        {
            return (anonId, true);
        }

        anonId = Guid.NewGuid().ToString();
        context.Response.Cookies.Append("anon_id", anonId, CookieOptions);
        return (anonId, true);
    }

    // Anonymous events set $process_person_profile to false so PostHog does not
    // create a person profile for the visitor.
    private static Dictionary<string, object> EventProperties(bool anonymous, Dictionary<string, object>? properties = null)
    {
        properties ??= new Dictionary<string, object>();
        if (anonymous)
        {
            properties["$process_person_profile"] = false;
        }
        return properties;
    }

    private static CookieOptions CookieOptions => new()
    {
        HttpOnly = true,
        Secure = true,
        SameSite = SameSiteMode.Lax,
    };

    public static void MapBurritoEndpoints(this WebApplication app)
    {
        app.MapGet("/", (HttpContext context) =>
        {
            var (userId, anonymous) = Visitor(context);
            return Page("Burrito app", $"""
            <p>{(anonymous ? "Not signed in, anonymous visitor" : "Signed in as")}: <strong>{Html(userId)}</strong></p>
            <form method="POST" action="/login">
                <label>User id <input name="user_id" value="burrito-fan-42"></label>
                <label>Email <input name="email" value="fan@example.com"></label>
                <button type="submit">Log in</button>
            </form>
            <ul>
                <li><a href="/burrito">Consider a burrito</a> (event tracking)</li>
                <li><a href="/dashboard">Dashboard</a> (feature flag)</li>
                <li><a href="/profile">Profile</a> (error tracking)</li>
            </ul>
            """);
        });

        // User identification: capture an event with person properties. The
        // distinct id is the stable user id.
        app.MapPost("/login", (HttpContext context, IPostHogClient posthog) =>
        {
            var form = context.Request.Form;
            var userId = form["user_id"].ToString();
            if (string.IsNullOrEmpty(userId))
            {
                userId = "burrito-fan-42";
            }

            context.Response.Cookies.Append("user_id", userId, CookieOptions);

            posthog.Capture(
                userId,
                "user_logged_in",
                properties: new() { ["login_method"] = "email" },
                personPropertiesToSet: new() { ["email"] = form["email"].ToString() },
                personPropertiesToSetOnce: new() { ["first_login_method"] = "email" });

            return Results.Redirect("/");
        }).DisableAntiforgery();

        // Event tracking: capture a business event with the visitor's distinct id
        // and an event property.
        app.MapGet("/burrito", (HttpContext context, IPostHogClient posthog) =>
        {
            var (userId, anonymous) = Visitor(context);

            var count = int.TryParse(context.Request.Cookies["burrito_count"], out var previous)
                ? previous + 1
                : 1;
            context.Response.Cookies.Append("burrito_count", count.ToString(), CookieOptions);

            posthog.Capture(
                userId,
                "burrito_considered",
                properties: EventProperties(anonymous, new() { ["total_considerations"] = count }));

            return Page("Burrito considered", $"""
                <p>You have considered a burrito <strong>{count}</strong> time(s).</p>
                <p>A <code>burrito_considered</code> event was captured for <code>{Html(userId)}</code>.</p>
                <p><a href="/">Back home</a></p>
                """);
        });

        // Feature flags: evaluate once per request, then read flags off the
        // returned snapshot.
        app.MapGet("/dashboard", async (HttpContext context, IPostHogClient posthog, ILogger<Program> logger) =>
        {
            var (userId, _) = Visitor(context);

            var showNewFeature = false;
            try
            {
                var flags = await posthog.EvaluateFlagsAsync(
                    userId,
                    options: new AllFeatureFlagsOptions
                    {
                        FlagKeysToEvaluate = ["new-dashboard-feature"],
                    });
                showNewFeature = flags.IsEnabled("new-dashboard-feature");
            }
            catch (Exception exception)
            {
                // A failed flag evaluation should never take the page down.
                logger.LogError(exception, "Feature flag evaluation failed");
            }

            var body = showNewFeature
                ? "<p>You are seeing the <strong>new</strong> dashboard feature!</p>"
                : "<p>You are seeing the <strong>standard</strong> dashboard.</p>";

            return Page("Dashboard", $"""
                {body}
                <p>Flag <code>new-dashboard-feature</code> for <code>{Html(userId)}</code>: <strong>{showNewFeature}</strong></p>
                <p><a href="/">Back home</a></p>
                """);
        });

        // Error tracking: catch an exception and report it with CaptureException.
        // The app keeps serving.
        app.MapGet("/profile", (HttpContext context, IPostHogClient posthog, ILogger<Program> logger) =>
        {
            var (userId, anonymous) = Visitor(context);

            var caught = "";
            try
            {
                RiskyOperation();
            }
            catch (Exception exception)
            {
                caught = exception.Message;
                logger.LogError(exception, "Profile risky operation failed");

                posthog.CaptureException(
                    exception,
                    userId,
                    EventProperties(anonymous, new() { ["route"] = "/profile" }));
            }

            return Page("Profile", $"""
                <p>User: <strong>{Html(userId)}</strong></p>
                <p>Triggered and captured an exception: <code>{Html(caught)}</code></p>
                <p><a href="/">Back home</a></p>
                """);
        });
    }

    private static void RiskyOperation() =>
        throw new InvalidOperationException("profile data source is temporarily unavailable");

    private static string Html(string value) => WebUtility.HtmlEncode(value);

    // A minimal HTML document so the example needs no template files.
    private static IResult Page(string title, string body) => Results.Content(
        $"<!doctype html><html><head><meta charset=\"utf-8\"><title>{title}</title></head>" +
        $"<body><h1>{title}</h1>{body}</body></html>",
        "text/html; charset=utf-8");
}

```

---

## PostHogExample.csproj

```csproj
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="PostHog.AspNetCore" Version="2.9.12" />
  </ItemGroup>

</Project>

```

---

## PostHogSetup.cs

```cs
using PostHog;

public static class PostHogSetup
{
    // Registers the single PostHog client for the app. The SDK reads the "PostHog"
    // configuration section, so we map our environment variables onto it.
    public static void AddPostHogFromEnvironment(this WebApplicationBuilder builder)
    {
        var projectToken = Environment.GetEnvironmentVariable("POSTHOG_PROJECT_TOKEN");
        var host = Environment.GetEnvironmentVariable("POSTHOG_HOST");

        // A blank token never breaks the app: the SDK logs an error and turns every
        // call into a no-op, so we only add a clearer hint in Development.
        if (string.IsNullOrWhiteSpace(projectToken) && builder.Environment.IsDevelopment())
        {
            Console.WriteLine(
                "WARNING: POSTHOG_PROJECT_TOKEN is not set. PostHog is disabled and no events " +
                "will be delivered. Set it in your environment (see .env.example) to enable analytics.");
        }

        builder.Configuration["PostHog:ProjectToken"] = projectToken;
        builder.Configuration["PostHog:HostUrl"] = string.IsNullOrWhiteSpace(host)
            ? "https://us.i.posthog.com"
            : host;

        // Registers IPostHogClient as a singleton: one client for the whole app.
        builder.AddPostHog();
    }
}

```

---

## Program.cs

```cs
// A tiny "burrito app" that mirrors the other PostHog example apps. Each route
// shows one server-side integration point:
//
//   /           home / login form
//   /login      user identification (capture with person properties)
//   /burrito    event tracking (burrito_considered)
//   /dashboard  feature flags (new-dashboard-feature via EvaluateFlagsAsync)
//   /profile    error tracking (CaptureException)

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://localhost:8000");

builder.AddPostHogFromEnvironment();

var app = builder.Build();

app.MapBurritoEndpoints();

// The PostHog client is a DI singleton. When the host shuts down (Ctrl+C or
// SIGTERM) it disposes the client, which flushes any queued events first.
app.Run();

```

---

