> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# PHP tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/php

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
