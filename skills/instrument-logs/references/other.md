# Other languages logs installation - Docs

PostHog logs works with any OpenTelemetry-compatible client. Check the [OpenTelemetry documentation](https://opentelemetry.io/docs/) for your specific language or framework.

1.  1

    ## Install OpenTelemetry packages

    Required

    The key requirements are:

    -   Use OTLP (OpenTelemetry Protocol) for log export over HTTP
    -   Send logs to your PostHog logs endpoint (see configuration step below)
    -   Include your project token in the Authorization header or as a `?token=` query parameter

    Find the OpenTelemetry SDK for your language in the [official registry](https://opentelemetry.io/ecosystem/registry/).

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate log requests. This is the same key you use for capturing events and exceptions with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/settings).

3.  3

    ## Configure the SDK

    Required

    Configure your OpenTelemetry SDK to send logs to PostHog.

    **Endpoint:**

    PostHog AI

    ```
    https://us.i.posthog.com/i/v1/logs
    ```

    **Authentication:** Include your project token either as an `Authorization` header:

    PostHog AI

    ```
    Authorization: Bearer <ph_project_token>
    ```

    Or as a query parameter on the endpoint:

    PostHog AI

    ```
    https://us.i.posthog.com/i/v1/logs?token=<ph_project_token>
    ```

4.  4

    ## Test your setup

    Recommended

    Once everything is configured, test that logs are flowing into PostHog:

    1.  Send a test log from your application
    2.  Check the PostHog logs interface for your log entries
    3.  Verify the logs appear in your project

    [View your logs in PostHog](https://app.posthog.com/logs)

6.  ## Next steps

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