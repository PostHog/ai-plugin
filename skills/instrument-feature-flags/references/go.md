# Go feature flags installation - Docs

1.  1

    ## Install the package

    Required

    Install the PostHog Go library:

    Terminal

    PostHog AI

    ```bash
    go get "github.com/posthog/posthog-go"
    ```

2.  2

    ## Configure PostHog

    Required

    Initialize the PostHog client with your project token and host:

    main.go

    PostHog AI

    ```go
    package main
    import (
        "github.com/posthog/posthog-go"
    )
    func main() {
        client, _ := posthog.NewWithConfig("<ph_project_token>", posthog.Config{Endpoint: "https://us.i.posthog.com"})
        defer client.Close()
    }
    ```

3.  3

    ## Send events

    Recommended

    Once installed, you can manually send events to test your integration:

    Go

    PostHog AI

    ```go
    client.Enqueue(posthog.Capture{
        DistinctId: "user_123",
        Event: "button_clicked",
        Properties: posthog.NewProperties().
            Set("button_name", "signup"),
    })
    ```

4.  4

    ## Evaluate boolean feature flags

    Required

    Check if a feature flag is enabled:

    ```go
    isMyFlagEnabled, err := client.IsFeatureEnabled(posthog.FeatureFlagPayload{
        Key:        "flag-key",
        DistinctId: "distinct_id_of_your_user",
    })
    if err != nil {
        // Handle error (e.g. capture error and fallback to default behaviour)
    }
    if isMyFlagEnabled == true {
        // Do something differently for this user
    }
    ```

5.  5

    ## Evaluate multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    ```go
    enabledVariant, err := client.GetFeatureFlag(posthog.FeatureFlagPayload{
        Key:        "flag-key",
        DistinctId: "distinct_id_of_your_user",
    })
    if err != nil {
        // Handle error (e.g. capture error and fallback to default behaviour)
    }
    if enabledVariant == "variant-key" { // replace 'variant-key' with the key of your variant
        // Do something differently for this user
    }
    ```

6.  6

    ## Include feature flag information in events

    Required

    If you want to use your feature flag to breakdown or filter events in your insights, you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

    **Note:** This step is only required for events captured using our server-side SDKs or API.

    ## Set SendFeatureFlags (recommended)

    Set `SendFeatureFlags` to `true` in your capture call:

    Go

    PostHog AI

    ```go
    client.Enqueue(posthog.Capture{
        DistinctId: "distinct_id_of_your_user",
        Event:      "event_name",
        SendFeatureFlags: true,
    })
    ```

    ## Include $feature property

    Include the `$feature/feature_flag_name` property in your event properties:

    Go

    PostHog AI

    ```go
    client.Enqueue(posthog.Capture{
        DistinctId: "distinct_id_of_your_user",
        Event:      "event_name",
        Properties: posthog.NewProperties().
            Set("$feature/feature-flag-key", "variant-key"), // replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
    })
    ```

7.  7

    ## Override server properties

    Optional

    Sometimes, you may want to evaluate feature flags using properties that haven't been ingested yet, or were set incorrectly earlier. You can provide properties to evaluate the flag with:

    ```go
    enabledVariant, err := client.GetFeatureFlag(
        FeatureFlagPayload{
            Key:        "flag-key",
            DistinctId: "distinct_id_of_the_user",
            Groups: posthog.NewGroups().
                Set("your_group_type", "your_group_id").
                Set("another_group_type", "your_group_id"),
            PersonProperties: posthog.NewProperties().
                Set("property_name", "value"),
            GroupProperties: map[string]map[string]interface{}{
                "your_group_type": {
                    "group_property_name": "value",
                },
                "another_group_type": {
                    "group_property_name": "value",
                },
            },
        },
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