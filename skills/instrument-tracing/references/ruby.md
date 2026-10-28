> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Ruby tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/ruby

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

    For the complete SDK reference, see the [OpenTelemetry Ruby docs](https://opentelemetry.io/docs/languages/ruby/).

    Add the SDK and OTLP exporter to your `Gemfile`:

    ```ruby
    gem 'opentelemetry-sdk'
    gem 'opentelemetry-exporter-otlp'
    ```

    Then run `bundle install`. The `opentelemetry-exporter-otlp` gem exports over OTLP HTTP/protobuf.

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

    ```ruby
    require 'opentelemetry/sdk'
    require 'opentelemetry/exporter/otlp'
    
    OpenTelemetry::SDK.configure do |c|
      c.service_name = 'my-service'
      c.add_span_processor(
        OpenTelemetry::SDK::Trace::Export::BatchSpanProcessor.new(
          OpenTelemetry::Exporter::OTLP::Exporter.new(
            endpoint: 'https://us.i.posthog.com/i/v1/traces',
            headers: { 'Authorization' => 'Bearer <ph_project_token>' }
          )
        )
      )
    end
    ```

    Alternatively, configure the exporter with environment variables and use a bare `OpenTelemetry::SDK.configure`:

    ```bash
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://us.i.posthog.com/i/v1/traces"
    OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer <ph_project_token>"
    OTEL_SERVICE_NAME="my-service"
    ```

    > **Note:** Pass the full `/i/v1/traces` path to the traces endpoint. Don't use the base `OTEL_EXPORTER_OTLP_ENDPOINT` variable, which appends its own `/v1/traces`.

4.  4

    ## Create spans

    Required

    Wrap the operations you want to measure in spans, and attach attributes for context.

    ```ruby
    tracer = OpenTelemetry.tracer_provider.tracer('my-app')
    
    tracer.in_span('process-order') do |span|
      span.set_attribute('order.id', order_id)
      # ... do work ...
    end
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
