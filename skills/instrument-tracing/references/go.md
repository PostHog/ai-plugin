> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Go tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/go

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

    For the complete SDK reference, see the [OpenTelemetry Go docs](https://opentelemetry.io/docs/languages/go/).

    ```bash
    go get go.opentelemetry.io/otel
    go get go.opentelemetry.io/otel/sdk
    go get go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp
    ```

    `otlptracehttp` is the OTLP HTTP/protobuf trace exporter. The `otlptracegrpc` module sends gRPC, so pick `otlptracehttp` to match this guide.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate trace requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project settings](https://app.posthog.com/settings).

3.  3

    ## Configure the SDK

    Required

    Set up the OpenTelemetry SDK to export spans to PostHog over OTLP HTTP. Use `WithEndpointURL` so the full `/i/v1/traces` path is sent as-is.

    ```go
    package main
    
    import (
        "context"
    
        "go.opentelemetry.io/otel"
        "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp"
        "go.opentelemetry.io/otel/sdk/resource"
        sdktrace "go.opentelemetry.io/otel/sdk/trace"
        semconv "go.opentelemetry.io/otel/semconv/v1.41.0"
    )
    
    func initTracer(ctx context.Context) (*sdktrace.TracerProvider, error) {
        exporter, err := otlptracehttp.New(ctx,
            otlptracehttp.WithEndpointURL("https://us.i.posthog.com/i/v1/traces"),
            otlptracehttp.WithHeaders(map[string]string{
                "Authorization": "Bearer <ph_project_token>",
            }),
        )
        if err != nil {
            return nil, err
        }
    
        res, err := resource.New(ctx,
            resource.WithAttributes(semconv.ServiceName("my-service")),
        )
        if err != nil {
            return nil, err
        }
    
        tp := sdktrace.NewTracerProvider(
            sdktrace.WithBatcher(exporter),
            sdktrace.WithResource(res),
        )
        otel.SetTracerProvider(tp)
        return tp, nil
    }
    ```

    Call `defer tp.Shutdown(ctx)` in `main` so buffered spans flush on exit.

    Alternatively, configure the exporter with environment variables and call `otlptracehttp.New(ctx)` with no options:

    ```bash
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://us.i.posthog.com/i/v1/traces"
    OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer <ph_project_token>"
    OTEL_SERVICE_NAME="my-service"
    ```

    > **Note:** `WithEndpoint` sets only the host and defaults the path to `/v1/traces`. To send to the full `/i/v1/traces` path, use `WithEndpointURL` (or the per-signal `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`), as shown.

4.  4

    ## Create spans

    Required

    Wrap the operations you want to measure in spans, and attach attributes for context.

    ```go
    import (
        "context"
    
        "go.opentelemetry.io/otel"
        "go.opentelemetry.io/otel/attribute"
    )
    
    var tracer = otel.Tracer("my-service")
    
    func chargeCustomer(ctx context.Context, customerID string) error {
        ctx, span := tracer.Start(ctx, "charge-customer")
        defer span.End()
    
        span.SetAttributes(attribute.String("customer.id", customerID))
        // ... do work ...
        return nil
    }
    ```

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
