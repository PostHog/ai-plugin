# React Native logs installation - Docs

PostHog's React Native SDK has built-in support for capturing structured logs. Unlike other languages where you wire OpenTelemetry directly, the SDK handles the OTLP encoding, batching, persistence, and lifecycle for you. You just call `posthog.captureLog(...)` or `posthog.logger.{trace,debug,info,warn,error,fatal}(...)`.

> **JavaScript layer only.** Logs are captured from the JavaScript side of your app. Native logs from your iOS or Android code (e.g. `os_log`, `Log.d`) are not collected.

> **Minimum version:** `posthog-react-native@4.44.0` or later. Run `npx expo install posthog-react-native` (Expo) or your package manager's equivalent to update.

1.  1

    ## Install posthog-react-native

    Required

    If you haven't already, install and initialize `posthog-react-native` using the steps below. For full details, see the [React Native SDK guide](/docs/libraries/react-native.md).

    Our React Native enables you to integrate PostHog with your React Native project. For React Native projects built with Expo, there are no mobile native dependencies outside of supported Expo packages.

    To install, add the `posthog-react-native` package to your project as well as the required peer dependencies.

    #### Expo apps

    Terminal

    PostHog AI

    ```bash
    npx expo install posthog-react-native expo-file-system expo-application expo-device expo-localization
    ```

    #### React Native apps

    Terminal

    PostHog AI

    ```bash
    yarn add posthog-react-native @react-native-async-storage/async-storage react-native-device-info react-native-localize
    # or
    npm i -s posthog-react-native @react-native-async-storage/async-storage react-native-device-info react-native-localize
    ```

    #### React Native Web and macOS

    If you're using [React Native Web](https://github.com/necolas/react-native-web) or [React Native macOS](https://github.com/microsoft/react-native-macos), do not use the [expo-file-system](https://github.com/expo/expo/tree/master/packages/expo-file-system) package since the Web and macOS targets aren't supported, use the [@react-native-async-storage/async-storage](https://github.com/react-native-async-storage/async-storage) package instead.

    ### Configuration

    #### With the PosthogProvider

    The recommended way to set up PostHog for React Native is to use the `PostHogProvider`. This utilizes the Context API to pass the PostHog client around, and enables [autocapture](/docs/product-analytics/autocapture.md).

    To set up `PostHogProvider`, add it to your `App.js` or `App.ts` file:

    App.js

    PostHog AI

    ```jsx
    // App.(js|ts)
    import { usePostHog, PostHogProvider } from 'posthog-react-native'
    ...
    export function MyApp() {
        return (
            <PostHogProvider apiKey="<ph_project_token>" options={{
                // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
                host: 'https://us.i.posthog.com',
            }}>
                <MyComponent />
            </PostHogProvider>
        )
    }
    ```

    Then you can access PostHog using the `usePostHog()` hook:

    React Native

    PostHog AI

    ```jsx
    const MyComponent = () => {
        const posthog = usePostHog()
        useEffect(() => {
            posthog.capture("event_name")
        }, [posthog])
    }
    ```

    #### Without the PosthogProvider

    If you prefer not to use the provider, you can initialize PostHog in its own file and import the instance from there:

    posthog.ts

    PostHog AI

    ```jsx
    import PostHog from 'posthog-react-native'
    export const posthog = new PostHog('<ph_project_token>', {
      // usually 'https://us.i.posthog.com' or 'https://eu.i.posthog.com'
      host: 'https://us.i.posthog.com'
    })
    ```

    Then you can access PostHog by importing your instance:

    React Native

    PostHog AI

    ```jsx
    import { posthog } from './posthog'
    export function MyApp1() {
        useEffect(() => {
            posthog.capture('event_name')
        }, [])
        return <View>Your app code</View>
    }
    ```

    You can even use this instance with the PostHogProvider:

    React Native

    PostHog AI

    ```jsx
    import { posthog } from './posthog'
    export function MyApp() {
      return <PostHogProvider client={posthog}>{/* Your app code */}</PostHogProvider>
    }
    ```

2.  2

    ## Configure logs in your PostHog options

    Required

    Add a `logs` block to your PostHog initialization. All fields are optional; defaults are tuned for mobile (cellular bandwidth, battery, OS lifecycle).

    React Native

    PostHog AI

    ```jsx
    import PostHog from 'posthog-react-native'
    const posthog = new PostHog('<ph_project_token>', {
      host: 'https://us.i.posthog.com',
      logs: {
        serviceName: 'my-app',          // OTLP service.name – shown in the Logs UI
        environment: 'production',      // OTLP deployment.environment
        serviceVersion: '1.2.3',        // OTLP service.version
      },
    })
    ```

3.  3

    ## Capture logs

    Required

    Use `posthog.logger` for the per-level convenience API, or `posthog.captureLog` for full control over level, attributes, and trace context.

    React Native

    PostHog AI

    ```jsx
    // Per-level convenience methods
    posthog.logger.info('checkout completed', { order_id: 'ord_789', amount_cents: 4999 })
    posthog.logger.warn('payment retry', { attempt: 2 })
    posthog.logger.error('payment failed', { code: 'E001' })
    // Lower-level API for custom severity / trace context
    posthog.captureLog({
      body: 'checkout failed',
      level: 'error',
      attributes: { order_id: 'ord_789', step: 'auth' },
      trace_id: '4bf92f3577b34da6a3ce929d0e0e4736',  // optional W3C trace context
      span_id: '00f067aa0ba902b7',
    })
    ```

    Records are buffered, batched, persisted to disk, and flushed automatically – every 10 seconds, on AppState change (foreground ↔ background), on buffer fill, or on `posthog.shutdown()`. For an immediate drain, call `await posthog.flushLogs()`.

    Each record is automatically tagged with the user's distinct ID, session ID, current screen, app foreground/background state, and active feature flags at the moment of capture.

4.  4

    ## Test your setup

    Recommended

    1.  Capture a test log from your app:

        React Native

        PostHog AI

        ```jsx
        posthog.logger.info('hello from RN')
        await posthog.flushLogs()
        ```

    2.  Open the [PostHog Logs UI](https://app.posthog.com/logs).
    3.  Filter by `service.name = 'my-app'` (or whatever value you set above).

    You should see your record arrive within a few seconds.

    [View your logs in PostHog](https://app.posthog.com/logs)

5.  5

    ## Tune buffering, rate cap, and filtering

    Optional

    The `logs` config has knobs for high-volume apps:

    React Native

    PostHog AI

    ```jsx
    const posthog = new PostHog('<ph_project_token>', {
      logs: {
        serviceName: 'my-app',
        flushIntervalMs: 5000,                       // default 10000ms
        maxBufferSize: 200,                          // default 100
        rateCap: { maxLogs: 5000, windowMs: 60000 }, // default 500/10s
        beforeSend: (record) =>
          record.body.includes('secret') ? null : record, // redact or drop
      },
    })
    ```

    Full configuration reference:

    | Field | Default | What it does |
    | --- | --- | --- |
    | serviceName | 'unknown_service' | OTLP service.name resource attribute |
    | serviceVersion | undefined | OTLP service.version resource attribute |
    | environment | undefined | OTLP deployment.environment resource attribute |
    | resourceAttributes | {} | Extra OTLP resource attributes |
    | flushIntervalMs | 10000 | Periodic flush interval in ms |
    | maxBufferSize | 100 | Max records held in memory before eviction |
    | maxBatchRecordsPerPost | 50 | Max records per outbound POST (halved on 413) |
    | rateCap.maxLogs | 500 | Max records per windowMs window |
    | rateCap.windowMs | 10000 | Rate-cap window length in ms |
    | beforeSend | undefined | Pre-send filter (return null to drop) |

    Defaults are tuned for cellular-aware mobile apps (~50 logs/sec ceiling, ~16KB max queue file). Raise `rateCap.maxLogs` and `maxBufferSize` for high-volume scenarios.

6.  6

    ## Filtering with beforeSend

    Optional

    The `beforeSend` hook runs synchronously before the rate cap, so dropped records don't consume the per-interval budget. Use it for redaction, sampling, or filtering by level:

    React Native

    PostHog AI

    ```jsx
    const posthog = new PostHog('<ph_project_token>', {
      host: 'https://us.i.posthog.com',
      logs: {
        serviceName: 'my-app',
        beforeSend: (record) => {
          // Drop debug logs in production
          if (record.level === 'debug') return null
          // Redact secrets in the body
          return {
            ...record,
            body: record.body.replace(/api_key=\S+/g, 'api_key=[REDACTED]'),
          }
        },
      },
    })
    ```

    You can also pass an array of functions to form a chain (evaluated left-to-right). A `null` return from any link short-circuits and drops the record. A throwing filter is caught and skipped – the chain continues with the previous return value, so a buggy filter degrades to a no-op rather than crashing your app.

8.  ## Next steps

    Checkpoint

    *What you can do with your logs*

    | Action | Description |
    | --- | --- |
    | [Why you need logs](/docs/logs/basics.md) | What logs show you that nothing else does |
    | [Search logs](/docs/logs/search.md) | Use the search interface to find specific log entries |
    | Filter by level | Filter by INFO, WARN, ERROR, etc. |
    | [Link session replay](/docs/logs/link-session-replay.md) | Connect logs to users and session replays by passing posthogDistinctId and sessionId |
    | [Link logs to a person](/docs/logs/link-person.md) | Surface every log emitted on behalf of a user on their PostHog person profile |
    | [Logging best practices](/docs/logs/best-practices.md) | Learn what to log, how to structure logs, and patterns that make logs useful in production |

    [Troubleshoot common issues](/docs/logs/troubleshooting.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better