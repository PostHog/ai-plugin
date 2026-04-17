# Datadog logs installation - Docs

If you're already using Datadog to collect logs, you can forward them to PostHog by configuring your existing Datadog log exporters (like the Datadog Agent) to send logs to PostHog's Datadog-compatible endpoint.

1.  1

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate log requests. This is the same key you use for capturing events and exceptions with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal token (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/settings/project).

2.  2

    ## Configure Datadog Agent

    Required

    Set the Datadog logs URL to point to PostHog's Datadog-compatible endpoint. The endpoint format is:

    PostHog AI

    ```
    https://us.i.posthog.com/i/v1/logs/datadog/<ph_project_token>
    ```

    For the **Datadog Agent**, set the `DD_LOGS_CONFIG_LOGS_DD_URL` environment variable:

    Terminal

    PostHog AI

    ```bash
    export DD_LOGS_CONFIG_LOGS_DD_URL="https://us.i.posthog.com/i/v1/logs/datadog/<ph_project_token>"
    ```

    Alternatively, you can set this in your `datadog.yaml` configuration file:

    YAML

    PostHog AI

    ```yaml
    logs_config:
      logs_dd_url: "https://us.i.posthog.com/i/v1/logs/datadog/<ph_project_token>"
    ```

3.  3

    ## Other Datadog log exporters

    Optional

    If you're using other Datadog log exporters or forwarders, configure them to send logs to the same endpoint:

    PostHog AI

    ```
    https://us.i.posthog.com/i/v1/logs/datadog/<ph_project_token>
    ```

    The endpoint accepts logs in the standard Datadog log format, so existing integrations should work without additional changes.

4.  4

    ## Test your setup

    Recommended

    Once everything is configured, test that logs are flowing into PostHog:

    1.  Restart the Datadog Agent (or your log forwarder) to apply the configuration
    2.  Generate some log entries in your application
    3.  Check the PostHog Logs interface for your log entries
    4.  Verify the logs appear in your project

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