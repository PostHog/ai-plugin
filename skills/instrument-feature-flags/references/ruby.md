# Ruby feature flags installation - Docs

1.  1

    ## Install the gem

    Required

    Add the PostHog Ruby gem to your Gemfile:

    Gemfile

    PostHog AI

    ```ruby
    gem "posthog-ruby"
    ```

2.  2

    ## Configure PostHog

    Required

    Initialize the PostHog client with your project token and host:

    Ruby

    PostHog AI

    ```ruby
    require 'posthog'
    posthog = PostHog::Client.new({
        api_key: "<ph_project_token>",
        host: "https://us.i.posthog.com",
        on_error: Proc.new { |status, msg| print msg }
    })
    ```

3.  3

    ## Send events

    Recommended

    Once installed, you can manually send events to test your integration:

    Ruby

    PostHog AI

    ```ruby
    posthog.capture({
        distinct_id: 'user_123',
        event: 'button_clicked',
        properties: {
            button_name: 'signup'
        }
    })
    ```

4.  4

    ## Evaluate boolean feature flags

    Required

    Check if a feature flag is enabled:

    ```ruby
    is_my_flag_enabled = posthog.is_feature_enabled('flag-key', 'distinct_id_of_your_user')
    if is_my_flag_enabled
        # Do something differently for this user
        # Optional: fetch the payload
        matched_flag_payload = posthog.get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
    end
    ```

5.  5

    ## Evaluate multivariate feature flags

    Optional

    For multivariate flags, check which variant the user has been assigned:

    ```ruby
    enabled_variant = posthog.get_feature_flag('flag-key', 'distinct_id_of_your_user')
    if enabled_variant == 'variant-key' # replace 'variant-key' with the key of your variant
        # Do something differently for this user
        # Optional: fetch the payload
        matched_flag_payload = posthog.get_feature_flag_payload('flag-key', 'distinct_id_of_your_user')
    end
    ```

6.  6

    ## Include feature flag information in events

    Required

    If you want to use your feature flag to breakdown or filter events in your insights, you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

    **Note:** This step is only required for events captured using our server-side SDKs or API.

    ## Set send_feature_flags (recommended)

    Set `send_feature_flags` to `true` in your capture call:

    Ruby

    PostHog AI

    ```ruby
    posthog.capture({
        distinct_id: 'distinct_id_of_your_user',
        event: 'event_name',
        send_feature_flags: true,
    })
    ```

    ## Include $feature property

    Include the `$feature/feature_flag_name` property in your event properties:

    Ruby

    PostHog AI

    ```ruby
    posthog.capture({
        distinct_id: 'distinct_id_of_your_user',
        event: 'event_name',
        properties: {
            '$feature/feature-flag-key': 'variant-key', # replace feature-flag-key with your flag key. Replace 'variant-key' with the key of your variant
        }
    })
    ```

7.  7

    ## Override server properties

    Optional

    Sometimes, you may want to evaluate feature flags using properties that haven't been ingested yet, or were set incorrectly earlier. You can provide properties to evaluate the flag with:

    ```ruby
    posthog.get_feature_flag(
        'flag-key',
        'distinct_id_of_the_user',
        person_properties: {
            'property_name': 'value'
        },
        groups: {
            'your_group_type': 'your_group_id',
            'another_group_type': 'your_group_id',
        },
        group_properties: {
            'your_group_type': {
                'group_property_name': 'value'
            },
            'another_group_type': {
                'group_property_name': 'value'
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