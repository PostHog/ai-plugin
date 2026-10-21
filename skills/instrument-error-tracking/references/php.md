> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# PHP Error Tracking installation

Canonical URL: https://posthog.com/docs/error-tracking/installation/php

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install the PHP SDK](#install-the-php-sdk)
- [Initialize the client](#initialize-the-client)
- [Capture exceptions](#capture-exceptions)
- [Enable automatic capture](#enable-automatic-capture)
- [Identify users and attach request context](#identify-users-and-attach-request-context)
- [Configure error tracking options](#configure-error-tracking-options)
- [Verify error tracking](#verify-error-tracking)
- [Link releases](#link-releases)

1.  1

    ## Install the PHP SDK

    Required

    Install the [PostHog PHP SDK](https://posthog.com/docs/libraries/php.md) via Composer:

    ```bash
    composer require posthog/posthog-php
    ```

2.  2

    ## Initialize the client

    Required

    Set your project token and instance address before making any calls:

    ```php
    PostHog\PostHog::init(
        '<ph_project_token>',
        ['host' => 'https://us.i.posthog.com']
    );
    ```

    You can find your project token and instance address in the [project settings](https://app.posthog.com/settings/project) page in PostHog.

3.  3

    ## Capture exceptions

    Required

    Use `captureException` to manually capture exceptions and send them to PostHog as `$exception` events with full stack traces.

    ### Basic usage

    ```php
    try {
        // Your code that might throw
        riskyOperation();
    } catch (\Throwable $e) {
        PostHog\PostHog::captureException($e, 'user_distinct_id');
    }
    ```

    ### With additional properties

    You can pass extra properties to include with the exception event:

    ```php
    try {
        processOrder($orderId);
    } catch (\Throwable $e) {
        PostHog\PostHog::captureException($e, 'user_distinct_id', [
            'order_id' => $orderId,
            'environment' => 'production',
        ]);
    }
    ```

    You can also pass a plain string if you want to send an error message without a `Throwable`.

4.  4

    ## Enable automatic capture

    Recommended

    Automatic capture is opt-in for PHP. When enabled, the SDK installs handlers for uncaught exceptions. With the default `capture_errors: true`, it also captures PHP errors and fatal shutdown errors.

    ```php
    PostHog\PostHog::init(
        '<ph_project_token>',
        [
            'host' => 'https://us.i.posthog.com',
            'error_tracking' => [
                'enabled' => true,
            ],
        ]
    );
    ```

    **Existing handlers are preserved**

    The SDK chains existing exception and error handlers instead of replacing your app's behavior.

5.  5

    ## Identify users and attach request context

    Recommended

    By default, automatically captured errors are anonymous. Use `context_provider` to attach a `distinctId` and request metadata to every automatically captured error event.

    ```php
    PostHog\PostHog::init(
        '<ph_project_token>',
        [
            'host' => 'https://us.i.posthog.com',
            'error_tracking' => [
                'enabled' => true,
                'context_provider' => static function (array $payload): array {
                    return [
                        'distinctId' => $_SESSION['user_id'] ?? null,
                        'properties' => [
                            '$current_url' => $_SERVER['REQUEST_URI'] ?? null,
                            '$request_method' => $_SERVER['REQUEST_METHOD'] ?? null,
                            '$exception_source' => $payload['source'] ?? null,
                        ],
                    ];
                },
            ],
        ]
    );
    ```

    If `distinctId` is omitted, PostHog sends the event with an auto-generated ID and sets `$process_person_profile` to `false`.

6.  6

    ## Configure error tracking options

    Optional

    ```php
    PostHog\PostHog::init(
        '<ph_project_token>',
        [
            'host' => 'https://us.i.posthog.com',
            'error_tracking' => [
                'enabled' => true,
                'capture_errors' => true,
                'excluded_exceptions' => [
                    \InvalidArgumentException::class,
                ],
                'max_frames' => 20,
                'context_provider' => static function (array $payload): array {
                    return [
                        'distinctId' => $_SESSION['user_id'] ?? null,
                        'properties' => [],
                    ];
                },
            ],
        ]
    );
    ```

    | Option | Type | Default | Description |
    | --- | --- | --- | --- |
    | `enabled` | boolean | `false` | Enables automatic error tracking handlers. Manual `captureException` works regardless. |
    | `capture_errors` | boolean | `true` | When enabled, also captures PHP errors and fatal shutdown errors in addition to uncaught exceptions. |
    | `excluded_exceptions` | array of class strings | `[]` | Throwable classes to skip during automatic capture. |
    | `max_frames` | integer | `20` | Maximum number of stack frames included in `$exception_list`. |
    | `context_provider` | callable or `null` | `null` | Callback that returns `distinctId` and extra event properties for automatic captures. |

7.  ## Verify error tracking

    Recommended

    Trigger a test exception to confirm events are being sent to PostHog. You should see them appear in the [Error Tracking](https://app.posthog.com/error_tracking) tab.

    ```php
    PostHog\PostHog::init(
        '<ph_project_token>',
        [
            'host' => 'https://us.i.posthog.com',
            'error_tracking' => [
                'enabled' => true,
            ],
        ]
    );
    
    try {
        throw new \Exception('Test exception from PHP');
    } catch (\Throwable $e) {
        PostHog\PostHog::captureException($e, 'test_user');
    }
    ```

8.  7

    ## Link releases

    Optional

    Great, you're capturing exceptions! To see which release each exception comes from, give your app the release ID when you deploy.

    [Link releases](https://posthog.com/docs/error-tracking/link-releases/php.md)
