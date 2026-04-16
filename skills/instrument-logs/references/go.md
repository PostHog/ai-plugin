# Go logs installation - Docs

1.  1

    ## Install OpenTelemetry packages

    Required

    Terminal

    PostHog AI

    ```bash
    go get go.opentelemetry.io/otel/sdk/log
    go get go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploghttp
    ```

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate log requests. This is the same key you use for capturing events and exceptions with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/project/settings).

3.  3

    ## Configure the SDK

    Required

    Set up the OpenTelemetry SDK to send logs to PostHog.

    Go

    PostHog AI

    ```go
    package main
    import (
        "os"
        "context"
        "log"
        "log/slog"
        "go.opentelemetry.io/otel/exporters/otlp/otlplog/otlploghttp"
        "go.opentelemetry.io/otel/exporters/stdout/stdoutlog"
        "go.opentelemetry.io/contrib/bridges/otelslog"
        otellog "go.opentelemetry.io/otel/sdk/log"
        "go.opentelemetry.io/otel/log/global"
    )
    func main() {
        ctx := context.Background()
        // Create OTLP HTTP exporter
        exporter, err := otlploghttp.New(ctx,
            otlploghttp.WithEndpoint("us.i.posthog.com"),
            otlploghttp.WithURLPath("/i/v1/logs"),
            otlploghttp.WithHeaders(map[string]string{
                "Authorization": "Bearer <ph_project_token>",
            }),
        )
        if err != nil {
            panic(err)
        }
        // you could also set this outside your application
        os.Setenv("OTEL_SERVICE_NAME", "my-service")
        stdoutExporter, _ := stdoutlog.New()
        // Create logger provider
        loggerProvider := otellog.NewLoggerProvider(
            otellog.WithProcessor(otellog.NewBatchProcessor(exporter)),
            // optional, also log to stdout
            otellog.WithProcessor(otellog.NewSimpleProcessor(stdoutExporter)),
        )
        defer func() {
            loggerProvider.Shutdown(context.Background())
        }()
        global.SetLoggerProvider(loggerProvider)
        slog.SetDefault(otelslog.NewLogger(""))
        log.Println("this is a log line")
    }
    ```

    Alternatively, you can pass the API key as a query parameter by modifying the URL path:

    Go

    PostHog AI

    ```go
    otlploghttp.WithURLPath("/i/v1/logs?token=<ph_project_token>")
    ```

4.  4

    ## Use OpenTelemetry logging

    Required

    Now you can start logging with OpenTelemetry:

    Go

    PostHog AI

    ```go
    import (
        "go.opentelemetry.io/otel/log"
    )
    logger := otel.GetLoggerProvider().Logger("my-app")
    logger.Info(ctx, "User action",
        log.String("userId", "123"),
        log.String("action", "login"),
    )
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