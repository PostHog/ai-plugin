# React Native error tracking installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog React Native library and its dependencies:

    PostHog AI

    ### Expo

    ```bash
    npx expo install posthog-react-native expo-file-system expo-application expo-device expo-localization
    ```

    ### yarn

    ```bash
    yarn add posthog-react-native @react-native-async-storage/async-storage react-native-device-info react-native-localize
    # for iOS
    cd ios && pod install
    ```

    ### npm

    ```bash
    npm i -s posthog-react-native @react-native-async-storage/async-storage react-native-device-info react-native-localize
    # for iOS
    cd ios && pod install
    ```

2.  2

    ## Configure PostHog

    Required

    PostHog is most easily used via the `PostHogProvider` component. Wrap your app with the provider:

    App.tsx

    PostHog AI

    ```jsx
    import { PostHogProvider } from 'posthog-react-native'
    export function MyApp() {
        return (
            <PostHogProvider
                apiKey="<ph_project_token>"
                options={{
                    host: "https://us.i.posthog.com",
                }}
            >
                <RestOfApp />
            </PostHogProvider>
        )
    }
    ```

3.  3

    ## Send events

    Recommended

    Once installed, PostHog will automatically start capturing events. You can also manually send events using the `usePostHog` hook:

    Component.tsx

    PostHog AI

    ```jsx
    import { usePostHog } from 'posthog-react-native'
    function MyComponent() {
        const posthog = usePostHog()
        const handlePress = () => {
            posthog.capture('button_pressed', {
                button_name: 'signup'
            })
        }
        return <Button onPress={handlePress} title="Sign Up" />
    }
    ```

4.  4

    ## Set up exception autocapture

    Recommended

    **Client-side configuration only**

    Support for remote configuration in the [error tracking settings](https://app.posthog.com/settings/project-error-tracking#exception-autocapture) requires SDK version 4.35.0 or higher.

    You can autocapture exceptions by configuring the `errorTracking` when setting up PostHog:

    React Native

    PostHog AI

    ```jsx
    export const posthog = new PostHog('<ph_project_token>', {
      errorTracking: {
        autocapture: {
          uncaughtExceptions: true,
          unhandledRejections: true,
          console: ['error', 'warn'],
          nativeCrashes: true, // native iOS/Android crashes (see below)
        },
      },
    })
    ```

    **Configuration options:**

    | Option | Description |
    | --- | --- |
    | uncaughtExceptions | Captures Uncaught exceptions (ReactNativeGlobal.ErrorUtils.setGlobalHandler) |
    | unhandledRejections | Captures Unhandled rejections (ReactNativeGlobal.onunhandledrejection) |
    | console | Captures console logs as errors according to the reported LogLevel |
    | nativeCrashes | Captures native iOS/Android crashes. Requires @posthog/react-native-plugin and uploaded native symbols (see below) |

    **Capturing native crashes**

    `nativeCrashes` captures native iOS and Android crashes that the JavaScript layer can't see. Beyond the config above, it needs:

    1.  The optional native plugin installed — `npx expo install @posthog/react-native-plugin` (Expo) or `npm i @posthog/react-native-plugin` (bare React Native). If it's missing, native capture is a no-op and your JS-level autocapture is unaffected.
    2.  Your project's **Enable exception autocapture** setting enabled in [error tracking settings](https://app.posthog.com/settings/project-error-tracking#exception-autocapture) — the same server-side setting that gates JavaScript autocapture.
    3.  Native debug symbols uploaded at build time, so crash stack traces are readable. See [native crash symbolication](/docs/error-tracking/upload-source-maps/react-native.md#native-crash-symbolication).

5.  5

    ## Set up error boundaries

    Optional

    You can use the `PostHogErrorBoundary` component to capture rendering errors thrown by components:

    React Native

    PostHog AI

    ```jsx
    import { PostHogProvider, PostHogErrorBoundary } from 'posthog-react-native'
    import { View, Text } from 'react-native'
    const App = () => {
      return (
        <PostHogProvider apiKey="<ph_project_token>">
          <PostHogErrorBoundary
            fallback={YourFallbackComponent}
            additionalProperties={{ screen: "home" }}
          >
            <YourApp />
          </PostHogErrorBoundary>
        </PostHogProvider>
      )
    }
    const YourFallbackComponent = ({ error, componentStack }) => {
      return (
        <View>
          <Text>Something went wrong!</Text>
          <Text>{error instanceof Error ? error.message : String(error)}</Text>
        </View>
      )
    }
    ```

    **Duplicate errors with console capture**

    If you have both `PostHogErrorBoundary` and `console` capture enabled in your `errorTracking` config, render errors will be captured twice. This is because React logs all errors to the console by default. To avoid this, set `console: []` on `errorTracking.autocapture` (for example, `errorTracking: { autocapture: { console: [] } }`) when using `PostHogErrorBoundary`.

    **Dev mode behavior**

    In development mode, React propagates all errors to the global error handler even when they are caught by an error boundary. This means you may see errors reported twice in dev builds. This is expected React behavior and does not occur in production builds.

6.  6

    ## Manually capture exceptions

    Optional

    You can manually capture exceptions using the `captureException` method:

    React Native

    PostHog AI

    ```jsx
    try {
      // Your awesome code that may throw
      someRiskyOperation();
    } catch (error) {
      posthog.captureException(error)
    }
    ```

    This is helpful if you've built your own error handling logic or want to capture exceptions that are handled by your application code.

7.  7

    ## Future features

    Optional

    We currently don't support the following features:

    -   No automatic source map uploads on React Native web

    This will be added in a future release. We recommend you stay up to date with the latest version of the PostHog React Native SDK.

8.  ## Verify error tracking

    Recommended

    *Confirm events are being sent to PostHog*

    Before proceeding, let's make sure exception events are being captured and sent to PostHog. You should see events appear in the activity feed.

    ![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_ouxl_f788dd8cd2.png)![Activity feed with events](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250729_owae_7c3490822c.png)

    [Check for exceptions in PostHog](https://app.posthog.com/activity/explore)

9.  8

    ## Upload source maps & native symbols

    Required

    Great, you're capturing exceptions! The next step is to upload source maps (for JavaScript stack traces) and native symbols (for native iOS/Android crash symbolication) so PostHog can generate accurate stack traces.

    Let's continue to the next section.

    [Upload source maps & native symbols](/docs/error-tracking/upload-source-maps/react-native.md)

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better