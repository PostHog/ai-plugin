> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# .NET Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/dotnet

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install the .NET SDK](#install-the-net-sdk)
- [Configure PostHog](#configure-posthog)
- [Capture exceptions](#capture-exceptions)
- [Capture ASP.NET Core request exceptions](#capture-aspnet-core-request-exceptions)
- [Capture unhandled runtime exceptions](#capture-unhandled-runtime-exceptions)
- [Verify error tracking](#verify-error-tracking)

1.  1

    ## Install the .NET SDK

    Required

    For ASP.NET Core projects, install the [PostHog.AspNetCore](https://posthog.com/docs/libraries/dotnet.md) package:

    ```bash
    dotnet add package PostHog.AspNetCore --version 2.10.0
    ```

    For other .NET projects, such as console applications, MAUI, or Blazor, install the core `PostHog` package:

    ```bash
    dotnet add package PostHog --version 2.23.0
    ```

2.  2

    ## Configure PostHog

    Required

    For ASP.NET Core, add PostHog to your `Program.cs` file:

    ```csharp
    using PostHog;
    
    var builder = WebApplication.CreateBuilder(args);
    
    builder.AddPostHog();
    ```

    Configure your project token and host in `appsettings.json`:

    ```json
    {
      "PostHog": {
        "ProjectToken": "<ph_project_token>",
        "HostUrl": "https://us.i.posthog.com"
      }
    }
    ```

    For non-ASP.NET Core projects, initialize the core client as a singleton:

    ```csharp
    using PostHog;
    
    public static readonly PostHogClient PostHog = new(new PostHogOptions {
        ProjectToken = "<ph_project_token>",
        HostUrl = new Uri("https://us.i.posthog.com"),
    });
    ```

    You can find your project token and instance address in the [project settings](https://app.posthog.com/project/settings) page in PostHog.

3.  3

    ## Capture exceptions

    Required

    The .NET SDK supports manual exception capture with `CaptureException`. It builds the `$exception` event for you, including exception type, message, stack frames, inner exceptions, aggregate exceptions, source context when available, and .NET runtime metadata.

    **PDB uploads are not yet supported**

    File names, line numbers, and source context depend on debug information already available from the captured .NET stack trace. PostHog doesn't support uploading .NET PDB files yet, so production builds without runtime-accessible debug information may show less detailed stack frames ([issue](https://github.com/PostHog/posthog-dotnet/issues/166)).

    The examples below assume `posthog` is an `IPostHogClient` from dependency injection, or your singleton `PostHogClient`.

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

    Pass additional properties to add request, tenant, or domain context to the exception:

    ```csharp
    try
    {
        ProcessOrder(orderId);
    }
    catch (Exception exception)
    {
        posthog.CaptureException(
            exception,
            "user_distinct_id",
            new Dictionary<string, object>
            {
                ["order_id"] = orderId,
                ["environment"] = "production",
            }
        );
    }
    ```

    You can also attach feature flag values to the exception event with a feature flag snapshot:

    ```csharp
    var flags = await posthog.EvaluateFlagsAsync("user_distinct_id");
    
    posthog.CaptureException(
        exception,
        "user_distinct_id",
        properties: null,
        groups: null,
        flags: flags
    );
    ```

    The next steps cover automatic capture. ASP.NET Core apps can capture request exceptions, and any .NET app can capture unhandled runtime exceptions.

4.  4

    ## Capture ASP.NET Core request exceptions

    Recommended

    ASP.NET Core automatic capture is available in `PostHog.AspNetCore` version 2.7.0 and later. Add the PostHog request context middleware after building the app, and enable exception capture:

    ```csharp
    var app = builder.Build();
    
    app.UsePostHogRequestContext(options =>
    {
        options.CaptureExceptions = true;
    });
    ```

    Place it before the request handlers whose exceptions you want to capture. The PostHog middleware captures the exception with the active request context and adds the HTTP response status.

    How the exception appears in PostHog depends on where it stops:

    -   **The exception escapes the PostHog middleware.** PostHog captures it as unhandled, then throws it again. Exception-handling middleware that you register before the PostHog middleware can still handle it.
    -   **Exception-handling middleware that runs after the PostHog middleware handles the exception.** In `PostHog.AspNetCore` version 2.10.0 and later, PostHog still captures it, and marks it as handled. For example, this applies to `UseExceptionHandler`.

    ```csharp
    app.UsePostHogRequestContext(options =>
    {
        options.CaptureExceptions = true;
    });
    
    // PostHog also captures exceptions that this handler converts to an error response
    app.UseExceptionHandler("/error");
    ```

5.  5

    ## Capture unhandled runtime exceptions

    Optional

    Some exceptions never reach a request. A background thread can crash the process, or a fire-and-forget task can fail with nobody observing it. In `PostHog` version 2.23.0 and later, enable `CaptureUnhandledExceptions` to capture these:

    ```csharp
    using PostHog;
    
    public static readonly PostHogClient PostHog = new(new PostHogOptions {
        ProjectToken = "<ph_project_token>",
        HostUrl = new Uri("https://us.i.posthog.com"),
        CaptureUnhandledExceptions = true,
    });
    ```

    For ASP.NET Core, set it in `appsettings.json`:

    ```json
    {
      "PostHog": {
        "ProjectToken": "<ph_project_token>",
        "HostUrl": "https://us.i.posthog.com",
        "CaptureUnhandledExceptions": true
      }
    }
    ```

    The option is off by default. When you enable it, the client listens to two .NET runtime events:

    | Runtime event | What PostHog captures |
    | --- | --- |
    | `AppDomain.UnhandledException` | An exception that no code caught. If it terminates the process, PostHog marks it as `fatal` and waits up to two seconds to send queued events before the process exits. |
    | `TaskScheduler.UnobservedTaskException` | An exception from a task that no code awaited or observed. PostHog reports the exception that the task threw, not the `AggregateException` that the runtime wraps it in. |

    PostHog marks both as unhandled. If the ASP.NET Core middleware already captured an exception, the runtime events don't capture it again.

    Dispose the client to stop listening to the runtime events.

    **Logged exceptions are not captured**

    An exception that your code or a framework catches and logs doesn't reach either runtime event. For example, the .NET host logs a failed `BackgroundService` instead of leaving it unhandled. Capture these with `CaptureException` ([issue](https://github.com/PostHog/posthog-dotnet/issues/384)).

6.  ## Verify error tracking

    Recommended

    Trigger and capture a test exception to confirm events are being sent to PostHog. You should see it appear in the [Error Tracking](https://app.posthog.com/error_tracking) tab.

    ```csharp
    try
    {
        throw new InvalidOperationException("Test exception from .NET");
    }
    catch (Exception exception)
    {
        posthog.CaptureException(exception, "test_user");
        await posthog.FlushAsync();
    }
    ```

    For serverless environments, call `FlushAsync()` before the process exits so queued exception events are sent.
