# Node.js Feature Flags installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog Node.js library using your package manager:

    PostHog AI

    ### npm

    ```bash
    npm install posthog-node
    ```

    ### yarn

    ```bash
    yarn add posthog-node
    ```

    ### pnpm

    ```bash
    pnpm add posthog-node
    ```

2.  2

    ## Initialize PostHog

    Required

    Initialize the PostHog client with your project token:

    Node.js

    PostHog AI

    ```javascript
    import { PostHog } from 'posthog-node'
    const client = new PostHog(
        '<ph_project_token>',
        {
            host: 'https://us.i.posthog.com'
        }
    )
    ```

3.  3

    ## Send an event

    Recommended

    Once installed, you can manually send events to test your integration:

    Node.js

    PostHog AI

    ```javascript
    client.capture({
        distinctId: 'distinct_id_of_the_user',
        event: 'event_name',
        properties: {
            property1: 'value',
            property2: 'value',
        },
    })
    ```

4.  4

    ## Evaluate boolean feature flags

    Required

    Check if a feature flag is enabled:

    ```javascript
    const isFeatureFlagEnabled = await client.isFeatureEnabled('flag-key', 'distinct_id_of_your_user')
    if (isFeatureFlagEnabled) {
        // Your code if the flag is enabled
        // Optional: fetch the payload
        const matchedFlagPayload = await client.getFeatureFlagPayload('flag-key', 'distinct_id_of_your_user', isFeatureFlagEnabled)
    }
    ```

5.  5

    ## Evaluate multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    ```javascript
    const enabledVariant = await client.getFeatureFlag('flag-key', 'distinct_id_of_your_user')
    if (enabledVariant === 'variant-key') {  // replace 'variant-key' with the key of your variant
        // Do something differently for this user
        // Optional: fetch the payload
        const matchedFlagPayload = await client.getFeatureFlagPayload('flag-key', 'distinct_id_of_your_user', enabledVariant)
    }
    ```

6.  6

    ## Include feature flag information in events

    Required

    If you want to use your feature flag to breakdown or filter events in your insights, you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

    **Note:** This step is only required for events captured using our server-side SDKs or API.

    ## Set sendFeatureFlags (recommended)

    Set `sendFeatureFlags` to `true` in your capture call:

    Node.js

    PostHog AI

    ```javascript
    client.capture({
        distinctId: 'distinct_id_of_your_user',
        event: 'event_name',
        sendFeatureFlags: true,
    })
    ```

    ## Include $feature property

    Include the `$feature/feature_flag_name` property in your event properties:

    Node.js

    PostHog AI

    ```javascript
    client.capture({
        distinctId: 'distinct_id_of_your_user',
        event: 'event_name',
        properties: {
            '$feature/feature-flag-key': 'variant-key' // replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
        },
    })
    ```

7.  7

    ## Override server properties

    Optional

    Sometimes, you may want to evaluate feature flags using properties that haven't been ingested yet, or were set incorrectly earlier. You can provide properties to evaluate the flag with:

    ```javascript
    await client.getFeatureFlag(
        'flag-key',
        'distinct_id_of_the_user',
        {
            personProperties: {
                'property_name': 'value'
            },
            groups: {
                "your_group_type": "your_group_id",
                "another_group_type": "your_group_id",
            },
            groupProperties: {
                'your_group_type': {
                    'group_property_name': 'value'
                },
                'another_group_type': {
                    'group_property_name': 'value'
                },
            },
        }
    )
    ```

8.  8

    ## Running experiments

    Optional

    Experiments run on top of our feature flags. Once you've implemented the flag in your code, you run an experiment by creating a new experiment in the PostHog dashboard.

9.  9

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