# React Native Feature Flags installation - Docs

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

    ## Use feature flags

    Required

    PostHog provides hooks to make it easy to use feature flags in your React Native app. Use `useFeatureFlagEnabled` for boolean flags:

    Component.tsx

    PostHog AI

    ```jsx
    import { usePostHog } from 'posthog-react-native'
    function MyComponent() {
        const posthog = usePostHog()
        const isMyFlagEnabled = posthog.isFeatureEnabled('flag-key')
        if (isMyFlagEnabled) {
            // Do something differently for this user
            // Optional: fetch the payload
            const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
        }
        return <View>...</View>
    }
    ```

    ### Multivariate flags

    For multivariate flags, use `getFeatureFlag`:

    Component.tsx

    PostHog AI

    ```jsx
    import { usePostHog } from 'posthog-react-native'
    function MyComponent() {
        const posthog = usePostHog()
        const enabledVariant = posthog.getFeatureFlag('flag-key')
        if (enabledVariant === 'variant-key') { // replace 'variant-key' with the key of your variant
            // Do something differently for this user
            // Optional: fetch the payload
            const matchedFlagPayload = posthog.getFeatureFlagPayload('flag-key')
        }
        return <View>...</View>
    }
    ```

5.  5

    ## Running experiments

    Optional

    Experiments run on top of our feature flags. Once you've implemented the flag in your code, you run an experiment by creating a new experiment in the PostHog dashboard.

6.  6

    ## Next steps

    Recommended

    Now that you're evaluating flags, continue with the resources below to learn what else Feature Flags enables within the PostHog platform.

    | Resource | Description |
    | --- | --- |
    | [Creating a feature flag](/docs/feature-flags/creating-feature-flags.md) | How to create a feature flag in PostHog |
    | [Adding feature flag code](/docs/feature-flags/adding-feature-flag-code.md) | How to check flags in your code for all platforms |
    | [Framework-specific guides](/docs/feature-flags/tutorials.md#framework-guides) | Setup guides for React Native, Next.js, Flutter, and other frameworks |
    | [How to do a phased rollout](/tutorials/phased-rollout.md) | Gradually roll out features to minimize risk |
    | [More tutorials](/docs/feature-flags/tutorials.md) | Other real-world examples and use cases |

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better