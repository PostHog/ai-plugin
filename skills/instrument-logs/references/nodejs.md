# Node.js logs installation - Docs

1.  1

    ## Install OpenTelemetry packages

    Required

    Terminal

    PostHog AI

    ```bash
    npm install @opentelemetry/sdk-node @opentelemetry/exporter-logs-otlp-http @opentelemetry/api-logs @opentelemetry/resources
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

    JavaScript

    PostHog AI

    ```javascript
    import { NodeSDK } from '@opentelemetry/sdk-node';
    import { OTLPLogExporter } from '@opentelemetry/exporter-logs-otlp-http';
    import { BatchLogRecordProcessor } from '@opentelemetry/sdk-logs';
    import { resourceFromAttributes } from '@opentelemetry/resources';
    const sdk = new NodeSDK({
      resource: resourceFromAttributes({
        'service.name': 'my-node-service',
      }),
      logRecordProcessor: new BatchLogRecordProcessor(
        new OTLPLogExporter({
          url: 'https://us.i.posthog.com/i/v1/logs',
          headers: {
            'Authorization': 'Bearer <ph_project_token>'
          }
        })
      )
    });
    sdk.start();
    ```

    Alternatively, you can pass the API key as a query parameter:

    JavaScript

    PostHog AI

    ```javascript
    const sdk = new NodeSDK({
      logRecordProcessor: new BatchLogRecordProcessor(
        new OTLPLogExporter({
          url: 'https://us.i.posthog.com/i/v1/logs?token=<ph_project_token>'
        })
      )
    });
    ```

4.  4

    ## Use OpenTelemetry logging

    Required

    Now you can start logging with OpenTelemetry:

    JavaScript

    PostHog AI

    ```javascript
    import { logs } from '@opentelemetry/api-logs';
    const logger = logs.getLogger('my-app');
    // Log with different levels and attributes
    logger.emit({ severityText: 'trace', body: 'log data', attributes: {'my_attribute': 'stringValue'} });
    logger.emit({ severityText: 'warn', body: 'log data', attributes: {'warning_count': 3} });
    logger.emit({ severityText: 'error', body: 'log data', attributes: {'json_attribute': [1,2,3]} });
    ```

5.  5

    ## Test your setup

    Recommended

    Once everything is configured, test that logs are flowing into PostHog:

    1.  Send a test log from your application
    2.  Check the PostHog Logs interface for your log entries
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