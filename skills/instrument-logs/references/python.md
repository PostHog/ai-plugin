# Python logs installation - Docs

1.  1

    ## Install OpenTelemetry packages

    Required

    Terminal

    PostHog AI

    ```bash
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
    ```

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate log requests. This is the same key you use for capturing events and exceptions with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/settings).

3.  3

    ## Configure the SDK

    Required

    Set up the OpenTelemetry SDK to send logs to PostHog.

    Python

    PostHog AI

    ```python
    from opentelemetry import logs
    from opentelemetry.sdk.logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk.logs.export import BatchLogRecordProcessor
    from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
    # Configure the logger provider
    logger_provider = LoggerProvider()
    logs.set_logger_provider(logger_provider)
    # Create OTLP exporter with API key in header
    otlp_exporter = OTLPLogExporter(
        endpoint="https://us.i.posthog.com/i/v1/logs",
        headers={"Authorization": "Bearer <ph_project_token>"}
    )
    # Add processor
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(otlp_exporter)
    )
    # Get logger
    logger = logs.get_logger("my-app")
    ```

    Alternatively, you can pass the API key as a query parameter:

    Python

    PostHog AI

    ```python
    otlp_exporter = OTLPLogExporter(
        endpoint="https://us.i.posthog.com/i/v1/logs?token=<ph_project_token>"
    )
    ```

4.  4

    ## Use OpenTelemetry logging

    Required

    Now you can start logging with OpenTelemetry:

    Python

    PostHog AI

    ```python
    import logging
    # Configure logging to use OpenTelemetry
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().addHandler(LoggingHandler())
    # Use standard Python logging
    logger = logging.getLogger("my-app")
    logger.info("User action", extra={"userId": "123", "action": "login"})
    logger.warning("Deprecated API used", extra={"endpoint": "/old-api"})
    logger.error("Database connection failed", extra={"error": "Connection timeout"})
    ```

5.  5

    ## Test your setup

    Recommended

    Once everything is configured, test that logs are flowing into PostHog:

    1.  Send a test log from your application
    2.  Check the PostHog logs interface for your log entries
    3.  Verify the logs appear in your project

    [View your logs in PostHog](https://app.posthog.com/logs)

7.  ## Next steps

    Checkpoint

    *What you can do with your logs*

    | Action | Description |
    | --- | --- |
    | [Why you need logs](/docs/logs/basics.md) | What logs show you that nothing else does |
    | [Search logs](/docs/logs/search.md) | Use the search interface to find specific log entries |
    | Filter by level | Filter by INFO, WARN, ERROR, etc. |
    | [Link session replay](/docs/logs/link-session-replay.md) | Connect logs to users and session replays by passing posthogDistinctId and sessionId |
    | [Logging best practices](/docs/logs/best-practices.md) | Learn what to log, how to structure logs, and patterns that make logs useful in production |

    [Troubleshoot common issues](/docs/logs/troubleshooting.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better