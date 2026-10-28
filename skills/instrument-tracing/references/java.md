> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Java tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/java

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install the OpenTelemetry Java agent](#install-the-opentelemetry-java-agent)
- [Get your project token](#get-your-project-token)
- [Configure the agent](#configure-the-agent)
- [Create spans](#create-spans)
- [Test your setup](#test-your-setup)
- [Next steps](#next-steps)

1.  1

    ## Install the OpenTelemetry Java agent

    Required

    For the complete SDK reference, see the [OpenTelemetry Java docs](https://opentelemetry.io/docs/languages/java/).

    The zero-code Java agent is the recommended way to instrument a Java app. Download the latest agent jar:

    ```bash
    curl -L -O https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar
    ```

    The agent instruments your application at runtime, so you don't need to add any dependencies to get started. If you'd rather instrument manually, see the SDK alternative in the configuration step.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate trace requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project settings](https://app.posthog.com/settings).

3.  3

    ## Configure the agent

    Required

    Set the OpenTelemetry environment variables to export spans to PostHog over OTLP HTTP, then start your app with the agent attached.

    ```bash
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://us.i.posthog.com/i/v1/traces
    OTEL_EXPORTER_OTLP_TRACES_HEADERS=Authorization=Bearer <ph_project_token>
    OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf
    OTEL_SERVICE_NAME=my-service
    ```

    ```bash
    java -javaagent:opentelemetry-javaagent.jar -jar myapp.jar
    ```

    To instrument manually instead, add the SDK dependencies (`opentelemetry-api`, `opentelemetry-sdk`, and `opentelemetry-exporter-otlp` via the `opentelemetry-bom`) and build the exporter in code:

    ```java
    import io.opentelemetry.exporter.otlp.http.trace.OtlpHttpSpanExporter;
    import io.opentelemetry.sdk.OpenTelemetrySdk;
    import io.opentelemetry.sdk.trace.SdkTracerProvider;
    import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
    
    OtlpHttpSpanExporter spanExporter = OtlpHttpSpanExporter.builder()
        .setEndpoint("https://us.i.posthog.com/i/v1/traces")
        .addHeader("Authorization", "Bearer <ph_project_token>")
        .build();
    
    SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
        .addSpanProcessor(BatchSpanProcessor.builder(spanExporter).build())
        .build();
    
    OpenTelemetrySdk openTelemetry = OpenTelemetrySdk.builder()
        .setTracerProvider(tracerProvider)
        .buildAndRegisterGlobal();
    ```

    The `buildAndRegisterGlobal()` call registers the SDK as the global instance, so `GlobalOpenTelemetry.getTracer(...)` in the next step works. (The Java agent does this for you, which is why the zero-code path needs no registration.)

    > **Note:** Pass the full `/i/v1/traces` path to the traces endpoint. `OtlpHttpSpanExporter` already sends OTLP over HTTP/protobuf, so no protocol setting is needed in code. If you configure via the environment variables above instead, set `OTEL_EXPORTER_OTLP_TRACES_PROTOCOL=http/protobuf` – the SDK's autoconfigure path defaults to gRPC.

4.  4

    ## Create spans

    Required

    Wrap the operations you want to measure in spans, and attach attributes for context.

    ```java
    import io.opentelemetry.api.GlobalOpenTelemetry;
    import io.opentelemetry.api.trace.Span;
    import io.opentelemetry.api.trace.Tracer;
    import io.opentelemetry.context.Scope;
    
    Tracer tracer = GlobalOpenTelemetry.getTracer("my-service");
    
    Span span = tracer.spanBuilder("checkout-order").startSpan();
    try (Scope scope = span.makeCurrent()) {
        span.setAttribute("order.id", orderId);
        // ... do work ...
    } catch (Exception e) {
        span.recordException(e);
        throw e;
    } finally {
        span.end();
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
