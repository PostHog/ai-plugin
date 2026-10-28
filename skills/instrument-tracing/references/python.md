> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Python tracing installation

Canonical URL: https://posthog.com/docs/distributed-tracing/installation/python

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [With posthog](#with-posthog)
- [With OpenTelemetry](#with-opentelemetry)
- [Test your setup](#test-your-setup)
- [Next steps](#next-steps)

There are two ways to send spans from Python.

|  | `posthog` | OpenTelemetry |
| --- | --- | --- |
| **Packages** | The SDK you already use for analytics | `opentelemetry-sdk` and an OTLP exporter |
| **Instrumentation** | Manual – you wrap the operations you care about | Manual, plus auto-instrumentation for Django, Flask, FastAPI, databases, and more |
| **Person and session join** | Automatic inside a PostHog context that identifies them | Set the attributes yourself |

Pick OpenTelemetry if you already run it, if you use `asyncio` with `AsyncPosthog`, or if you want spans from your web framework and database driver without writing them yourself. Pick `posthog` if PostHog is your only tracing backend and you'd rather instrument a handful of operations by hand than add an exporter pipeline.

Both routes send OTLP spans to the same endpoint, so you can start with one and switch later without losing your traces.

## With `posthog`

> **Minimum version:** `posthog` 7.58.0 or later.

1.  1

    ### Install posthog

    Required

    ```bash
    pip install "posthog>=7.58.0"
    ```

2.  2

    ### Enable tracing

    Required

    Tracing is off until you set the `traces` option. There's no OpenTelemetry dependency to add.

    ```python
    from posthog import Posthog
    
    posthog = Posthog(
        "<ph_project_token>",
        host="https://us.i.posthog.com",
        traces={
            "service_name": "checkout-api",
            "environment": "production",
        },
    )
    ```

    | Option | Description |
    | --- | --- |
    | `service_name` | Identifies the service in the Tracing UI. Maps to `service.name` |
    | `service_version` | Release version. Maps to `service.version` |
    | `environment` | Deployment environment, e.g. `production`. Maps to `deployment.environment` |
    | `resource_attributes` | Additional OpenTelemetry resource attributes |

    Use your **project token** (the same one you use for capturing events), not a [personal API key](https://posthog.com/docs/api.md#authentication). Tracing works with the synchronous `Posthog` client and the module-level API, not `AsyncPosthog`.

    See the [Python SDK docs](https://posthog.com/docs/libraries/python.md#configuration) for batching, queue, and span-limit options, and [`before_span_send`](https://posthog.com/docs/libraries/python.md#scrubbing-and-dropping-spans) for scrubbing attributes or dropping spans before they're exported.

3.  3

    ### Create spans with posthog

    Required

    `start_span` used in a `with` block makes the span active for the block and ends it when the block exits. Spans started inside the block nest underneath it automatically.

    ```python
    with posthog.start_span("POST /checkout", kind="server") as span:
        span.set_attribute("plan", user.plan)
    
        with posthog.start_span("create-order"):
            order = create_order(cart)
        with posthog.start_span("charge-card"):
            stripe.charge(order)
    ```

    If an exception escapes the block, the span records it, its status is set to `error`, and the exception propagates unchanged.

    Span names should be low-cardinality operation names – `GET /users/:id`, not `GET /users/123`. Variable values belong in attributes.

    For work that can't wrap a block, call `start_span` without `with` and call `end()` yourself. See the [Python SDK docs](https://posthog.com/docs/libraries/python.md#distributed-tracing) for the full span API and for continuing a trace across services with W3C `traceparent` headers.

4.  4

    ### Link spans to people and sessions

    Recommended

    Spans created inside a PostHog [context](https://posthog.com/docs/libraries/python.md#contexts) that has a distinct ID or session ID carry `posthogDistinctId` and `sessionId` attributes, which is what makes a trace reachable from a person or a Session Replay recording.

    ```python
    from posthog import new_context, identify_context, set_context_session
    
    with new_context():
        identify_context(user.id)
        set_context_session(session_id)
    
        with posthog.start_span("POST /checkout"):
            process_order()
    ```

    If you use Django, the [contexts middleware](https://posthog.com/docs/libraries/django.md#django-contexts-middleware) sets this up for every request, and reads the `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers that [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) sends from the browser.

5.  5

    ### Flush before the process exits

    Recommended

    Queued spans are exported on an interval, even with `sync_mode` on, so a short-lived process can exit before they're sent. Both `flush()` and `shutdown()` export spans that have already ended.

    ```python
    def handler(event, context):
        with posthog.start_span("handler"):
            do_work()
        posthog.flush()
    ```

    In a serverless handler, call `flush()` before returning. Call `shutdown()` when the process is genuinely exiting.

## With OpenTelemetry

1.  1

    ### Install OpenTelemetry packages

    Required

    For the complete SDK reference, see the [OpenTelemetry Python docs](https://opentelemetry.io/docs/languages/python/).

    ```bash
    pip install opentelemetry-sdk opentelemetry-exporter-otlp-proto-http
    ```

    `opentelemetry-exporter-otlp-proto-http` is the OTLP HTTP/protobuf trace exporter. The `-proto-grpc` variant sends gRPC, so pick `-proto-http` to match this guide.

2.  2

    ### Get your project token

    Required

    You'll need your PostHog project token to authenticate trace requests. This is the same token you use for capturing events with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project settings](https://app.posthog.com/settings).

3.  3

    ### Configure the SDK

    Required

    Set up the OpenTelemetry SDK to export spans to PostHog over OTLP HTTP.

    ```python
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    
    resource = Resource.create({SERVICE_NAME: "my-service"})
    provider = TracerProvider(resource=resource)
    
    exporter = OTLPSpanExporter(
        endpoint="https://us.i.posthog.com/i/v1/traces",
        headers={"Authorization": "Bearer <ph_project_token>"},
    )
    
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    ```

    The `.http.` segment in the import path is what selects the HTTP/protobuf exporter.

    Alternatively, configure the exporter with environment variables:

    ```bash
    OTEL_EXPORTER_OTLP_TRACES_ENDPOINT="https://us.i.posthog.com/i/v1/traces"
    OTEL_EXPORTER_OTLP_TRACES_HEADERS="Authorization=Bearer <ph_project_token>"
    OTEL_SERVICE_NAME="my-service"
    ```

    > **Note:** Pass the full `/i/v1/traces` path to the traces endpoint. Don't use the base `OTEL_EXPORTER_OTLP_ENDPOINT` variable, which appends its own `/v1/traces`.

4.  4

    ### Create spans

    Required

    Wrap the operations you want to measure in spans, and attach attributes for context.

    ```python
    tracer = trace.get_tracer("my-service")
    
    def checkout(order_id, amount):
        with tracer.start_as_current_span("checkout") as span:
            span.set_attribute("order.id", order_id)
            span.set_attribute("order.amount", amount)
            # ... do work ...
            return "confirmed"
    ```

    To join these spans to a person or a Session Replay recording, set `posthogDistinctId` and `sessionId` attributes yourself, from the `X-POSTHOG-DISTINCT-ID` and `X-POSTHOG-SESSION-ID` headers that [`tracing_headers`](https://posthog.com/docs/libraries/js/config.md#tracing-headers) sends from the browser.

1.  ## Test your setup

    Checkpoint

    *Confirm spans are reaching PostHog*

    Whichever route you took:

    1.  Run your application and trigger the instrumented code
    2.  Open the PostHog Tracing interface
    3.  Confirm your spans and traces appear

    [View your traces in PostHog](https://app.posthog.com/tracing)

3.  ## Next steps

    Checkpoint

    *What you can do with your traces*

    | Action | Description |
    | --- | --- |
    | **[Why you need distributed tracing](https://posthog.com/docs/distributed-tracing/basics.md)** | What a trace shows you that nothing else does |
    | **Explore traces** | Read a trace as a waterfall to see where time goes |
    | **Filter spans** | Narrow down by service, status, duration, and attributes |
    | **Propagate context** | Pass trace context across services so spans join the same trace |

    [View your traces in PostHog](https://app.posthog.com/tracing)
