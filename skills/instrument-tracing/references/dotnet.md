> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# .NET tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/dotnet

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install OpenTelemetry packages](#install-opentelemetry-packages)
- [Get your project token](#get-your-project-token)
- [Configure the SDK](#configure-the-sdk)
- [Create spans](#create-spans)
- [Test your setup](#test-your-setup)
- [Next steps](#next-steps)

1.  1

    ## Install OpenTelemetry packages

    Required

    For the complete SDK reference, see the [OpenTelemetry .NET docs](https://opentelemetry.io/docs/languages/dotnet/).

    ```bash
    dotnet add package OpenTelemetry
    dotnet add package OpenTelemetry.Exporter.OpenTelemetryProtocol
    dotnet add package OpenTelemetry.Extensions.Hosting
    ```

    `OpenTelemetry.Extensions.Hosting` wires OpenTelemetry into the host builder. For a plain console app using `Sdk.CreateTracerProviderBuilder()`, you can leave it out.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate trace requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project settings](https://app.posthog.com/settings).

3.  3

    ## Configure the SDK

    Required

    Set up OpenTelemetry to export spans to PostHog over OTLP HTTP. The `AddSource` name must match the `ActivitySource` you create in the next step.

    ```csharp
    using OpenTelemetry;
    using OpenTelemetry.Exporter;
    using OpenTelemetry.Resources;
    using OpenTelemetry.Trace;
    
    var builder = WebApplication.CreateBuilder(args);
    
    builder.Services.AddOpenTelemetry()
        .ConfigureResource(resource => resource.AddService("my-service"))
        .WithTracing(tracing => tracing
            .AddSource("MyCompany.MyApp")
            .AddOtlpExporter(options =>
            {
                options.Endpoint = new Uri("https://us.i.posthog.com/i/v1/traces");
                options.Protocol = OtlpExportProtocol.HttpProtobuf;
                options.Headers = "Authorization=Bearer <ph_project_token>";
            }));
    ```

    Alternatively, configure the exporter with environment variables and call `AddOtlpExporter()` with no arguments:

    ```bash
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://us.i.posthog.com/i/v1/traces"
    OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer <ph_project_token>"
    OTEL_EXPORTER_OTLP_TRACES_PROTOCOL="http/protobuf"
    OTEL_SERVICE_NAME="my-service"
    ```

    > **Note:** With `HttpProtobuf`, the `Endpoint` is used as-is, so include the full `/i/v1/traces` path. Don't use the base `OTEL_EXPORTER_OTLP_ENDPOINT` variable, which appends its own `/v1/traces`.

4.  4

    ## Create spans

    Required

    .NET uses the built-in `ActivitySource` API for tracing. The source name must match the `AddSource` call above.

    ```csharp
    using System.Diagnostics;
    
    static readonly ActivitySource MyActivitySource = new("MyCompany.MyApp");
    
    public void ProcessOrder(string orderId)
    {
        using Activity? activity = MyActivitySource.StartActivity("process-order");
        activity?.SetTag("order.id", orderId);
        // ... do work ...
    }
    ```

    `StartActivity` returns `null` when nothing is listening to the source, so use the null-conditional `activity?.` operator.

5.  5

    ## Test your setup

    Recommended

    Once everything is configured, confirm spans are reaching PostHog:

    1.  Run your application and trigger the instrumented code
    2.  Open the PostHog Tracing interface
    3.  Confirm your spans and traces appear

    [View your traces in PostHog](https://app.posthog.com/tracing)

7.  ## Next steps

    Checkpoint

    *What you can do with your traces*

    | Action | Description |
    | --- | --- |
    | **[Why you need distributed tracing](https://posthog.com/docs/distributed-tracing/basics.md)** | What a trace shows you that nothing else does |
    | **Explore traces** | Read a trace as a waterfall to see where time goes |
    | **Filter spans** | Narrow down by service, status, duration, and attributes |
    | **Propagate context** | Pass trace context across services so spans join the same trace |

    [View your traces in PostHog](https://app.posthog.com/tracing)
