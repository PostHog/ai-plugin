> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# PHP tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/php

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install OpenTelemetry packages](#install-opentelemetry-packages)
- [Get your project token](#get-your-project-token)
- [Configure the SDK](#configure-the-sdk)
- [Create spans](#create-spans)
- [Link spans to people and sessions](#link-spans-to-people-and-sessions)
- [Test your setup](#test-your-setup)
- [Next steps](#next-steps)

1.  1

    ## Install OpenTelemetry packages

    Required

    For the complete SDK reference, see the [OpenTelemetry PHP docs](https://opentelemetry.io/docs/languages/php/).

    ```bash
    composer require open-telemetry/api open-telemetry/sdk open-telemetry/exporter-otlp
    composer require guzzlehttp/guzzle php-http/guzzle7-adapter
    ```

    The OTLP HTTP transport needs a PSR-18 HTTP client and PSR-17 factories, which `php-http/discovery` finds at runtime. Guzzle (above) or `symfony/http-client` with `nyholm/psr7` both work. For production, install the native protobuf extension (`pecl install protobuf`) – the pure-PHP fallback is slower.

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate trace requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project settings](https://app.posthog.com/settings).

3.  3

    ## Configure the SDK

    Required

    Set up the OpenTelemetry SDK to export spans to PostHog over OTLP HTTP.

    ```php
    <?php
    
    use OpenTelemetry\Contrib\Otlp\OtlpHttpTransportFactory;
    use OpenTelemetry\Contrib\Otlp\SpanExporter;
    use OpenTelemetry\SDK\Common\Attribute\Attributes;
    use OpenTelemetry\SDK\Resource\ResourceInfo;
    use OpenTelemetry\SDK\Resource\ResourceInfoFactory;
    use OpenTelemetry\SDK\Trace\SpanProcessor\BatchSpanProcessor;
    use OpenTelemetry\SDK\Trace\TracerProvider;
    
    $resource = ResourceInfoFactory::defaultResource()->merge(
        ResourceInfo::create(Attributes::create([
            'service.name' => 'my-service',
        ]))
    );
    
    $transport = (new OtlpHttpTransportFactory())->create(
        'https://us.i.posthog.com/i/v1/traces',
        'application/x-protobuf',
        ['Authorization' => 'Bearer <ph_project_token>'],
    );
    
    $tracerProvider = TracerProvider::builder()
        ->addSpanProcessor(new BatchSpanProcessor(new SpanExporter($transport)))
        ->setResource($resource)
        ->build();
    ```

    Alternatively, configure the SDK with environment variables and let it autoconfigure:

    ```bash
    OTEL_PHP_AUTOLOAD_ENABLED=true
    OTEL_SERVICE_NAME=my-service
    OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://us.i.posthog.com/i/v1/traces"
    OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer <ph_project_token>"
    ```

    > **Note:** Pass the full `/i/v1/traces` path to the traces endpoint. Don't use the base `OTEL_EXPORTER_OTLP_ENDPOINT` variable, which appends its own `/v1/traces`.

4.  4

    ## Create spans

    Required

    Wrap the operations you want to measure in spans, and attach attributes for context.

    ```php
    $tracer = $tracerProvider->getTracer('my-service');
    
    $span = $tracer->spanBuilder('process-order')->startSpan();
    $scope = $span->activate();
    
    try {
        $span->setAttribute('order.id', $orderId);
        // ... do work ...
    } finally {
        $scope->detach();
        $span->end();
    }
    ```

5.  5

    ## Link spans to people and sessions

    Recommended

    After your existing PostHog client is initialized, add the optional processor to your existing OpenTelemetry provider builder alongside its exporter:

    ```php
    use PostHog\OpenTelemetry\ContextSpanProcessor;
    use PostHog\PostHog;
    
    $tracerProvider = TracerProvider::builder()
        ->addSpanProcessor(new ContextSpanProcessor(PostHog::getClient()))
        ->addSpanProcessor(new BatchSpanProcessor(new SpanExporter($transport)))
        ->setResource($resource)
        ->build();
    ```

    Use this configuration in place of the builder above. Keep your existing provider, exporter, and sampler. Register the processor before requests start. OpenTelemetry SDK 1.0.0 or later is supported and remains an optional application dependency.

    The processor reads this client's PostHog context when each span starts. The [Laravel request middleware](https://posthog.com/docs/libraries/laravel.md) sets that context with `PostHog::withContext()`. With the processor registered, entering a context also enriches the active request span in normal PHP execution. Configure [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) for your backend hostname in the browser SDK.

    Existing `sessionId` and `posthogDistinctId` span attributes take precedence. Missing IDs stay absent. The scope closes after success or failure, while spans that already started keep their attributes.

    **Fiber limit:** Incoming spans that started before `withContext()` inside a Fiber are skipped. OpenTelemetry has no safe public check for initialized Fiber storage. Child spans can receive IDs from Fiber-local PostHog context when the application's OpenTelemetry Fiber context is initialized. New Fibers and queue jobs need explicit context transfer.

6.  6

    ## Test your setup

    Recommended

    Once everything is configured, confirm spans are reaching PostHog:

    1.  Run your application and trigger the instrumented code
    2.  Open the PostHog Tracing interface
    3.  Confirm your spans and traces appear

    [View your traces in PostHog](https://app.posthog.com/tracing)

8.  ## Next steps

    Checkpoint

    *What you can do with your traces*

    | Action | Description |
    | --- | --- |
    | **[Why you need distributed tracing](https://posthog.com/docs/distributed-tracing/basics.md)** | What a trace shows you that nothing else does |
    | **Explore traces** | Read a trace as a waterfall to see where time goes |
    | **Filter spans** | Narrow down by service, status, duration, and attributes |
    | **Propagate context** | Pass trace context across services so spans join the same trace |

    [View your traces in PostHog](https://app.posthog.com/tracing)
