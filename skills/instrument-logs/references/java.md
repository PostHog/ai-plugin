# Java logs installation - Docs

1.  1

    ## Install OpenTelemetry packages

    Required

    Add the following dependencies to your `pom.xml`:

    XML

    PostHog AI

    ```xml
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-api</artifactId>
        <version>1.32.0</version>
    </dependency>
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-sdk</artifactId>
        <version>1.32.0</version>
    </dependency>
    <dependency>
        <groupId>io.opentelemetry</groupId>
        <artifactId>opentelemetry-exporter-otlp</artifactId>
        <version>1.32.0</version>
    </dependency>
    ```

2.  2

    ## Get your project token

    Required

    You'll need your PostHog project token to authenticate log requests. This is the same key you use for capturing events and exceptions with the PostHog SDK.

    > **Important:** Use your **project token** which starts with `phc_`. Do **not** use a personal API key (which starts with `phx_`).

    You can find your project token in [Project Settings](https://app.posthog.com/settings/project).

3.  3

    ## Configure the SDK

    Required

    Set up the OpenTelemetry SDK to send logs to PostHog.

    Java

    PostHog AI

    ```java
    import io.opentelemetry.api.logs.GlobalLoggerProvider;
    import io.opentelemetry.sdk.logs.SdkLoggerProvider;
    import io.opentelemetry.sdk.logs.export.BatchLogRecordProcessor;
    import io.opentelemetry.exporter.otlp.logs.OtlpHttpLogRecordExporter;
    SdkLoggerProvider loggerProvider = SdkLoggerProvider.builder()
        .addLogRecordProcessor(
            BatchLogRecordProcessor.builder(
                OtlpHttpLogRecordExporter.builder()
                    .setEndpoint("https://us.i.posthog.com/i/v1/logs")
                    .addHeader("Authorization", "Bearer <ph_project_token>")
                    .build()
            ).build()
        )
        .build();
    GlobalLoggerProvider.set(loggerProvider);
    ```

    Alternatively, you can pass the API key as a query parameter:

    Java

    PostHog AI

    ```java
    OtlpHttpLogRecordExporter.builder()
        .setEndpoint("https://us.i.posthog.com/i/v1/logs?token=<ph_project_token>")
        .build()
    ```

4.  4

    ## Use OpenTelemetry logging

    Required

    Now you can start logging with OpenTelemetry:

    Java

    PostHog AI

    ```java
    import io.opentelemetry.api.logs.Logger;
    Logger logger = GlobalLoggerProvider.get().get("my-app");
    logger.logRecordBuilder()
        .setBody("User action")
        .setAttributes(Attributes.of(
            AttributeKey.stringKey("userId"), "123",
            AttributeKey.stringKey("action"), "login"
        ))
        .emit();
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