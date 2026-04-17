# API Feature Flags installation - Docs

1.  1

    ## Evaluate the feature flag value using flags

    Required

    `flags` is the endpoint used to determine if a given flag is enabled for a certain user or not.

    PostHog AI

    ### Basic request (flags only)

    ```bash
    curl -v -L --header "Content-Type: application/json" -d '{
        "token": "<ph_project_token>",
        "distinct_id": "distinct_id_of_your_user",
        "groups" : {
            "group_type": "group_id"
        }
    }' "https://us.i.posthog.com/flags?v=2"
    ```

    ### Python

    ```python
    import requests
    import json
    url = "https://us.i.posthog.com/flags?v=2"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "token": "<ph_project_token>",
        "distinct_id": "user distinct id",
        "groups": {
            "group_type": "group_id"
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response.json())
    ```

    ### Node.js

    ```javascript
    const response = await fetch("https://us.i.posthog.com/flags?v=2", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            token: "<ph_project_token>",
            distinct_id: "user distinct id",
            groups: {
                group_type: "group_id",
            },
        }),
    });
    const data = await response.json();
    console.log(data);
    ```

    **Note:** The `groups` key is only required for group-based feature flags. If you use it, replace `group_type` and `group_id` with the values for your group such as `company: "Twitter"`.

2.  2

    ## Include feature flag information when capturing events

    Required

    If you want to use your feature flag to breakdown or filter events in your insights, you'll need to include feature flag information in those events. This ensures that the feature flag value is attributed correctly to the event.

    **Note:** This step is only required for events captured using our server-side SDKs or API.

    PostHog AI

    ### Terminal

    ```bash
    curl -v -L --header "Content-Type: application/json" -d '{
        "token": "<ph_project_token>",
        "event": "your_event_name",
        "distinct_id": "distinct_id_of_your_user",
        "properties": {
            "$feature/feature-flag-key": "variant-key"
        }
    }' https://us.i.posthog.com/i/v0/e/
    ```

    ### Python

    ```python
    import requests
    import json
    url = "https://us.i.posthog.com/i/v0/e/"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "token": "<ph_project_token>",
        "event": "your_event_name",
        "distinct_id": "distinct_id_of_your_user",
        "properties": {
            "$feature/feature-flag-key": "variant-key"
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response)
    ```

3.  3

    ## Send a $feature\_flag\_called event

    Optional

    To track usage of your feature flag and view related analytics in PostHog, submit the `$feature_flag_called` event whenever you check a feature flag value in your code.

    You need to include two properties with this event:

    1.  `$feature_flag_response`: This is the name of the variant the user has been assigned to e.g., "control" or "test"
    2.  `$feature_flag`: This is the key of the feature flag in your experiment.

    PostHog AI

    ### Terminal

    ```bash
    curl -v -L --header "Content-Type: application/json" -d '{
        "token": "<ph_project_token>",
        "event": "$feature_flag_called",
        "distinct_id": "distinct_id_of_your_user",
        "properties": {
            "$feature_flag": "feature-flag-key",
            "$feature_flag_response": "variant-name"
        }
    }' https://us.i.posthog.com/i/v0/e/
    ```

    ### Python

    ```python
    import requests
    import json
    url = "https://us.i.posthog.com/i/v0/e/"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "token": "<ph_project_token>",
        "event": "$feature_flag_called",
        "distinct_id": "distinct_id_of_your_user",
        "properties": {
            "$feature_flag": "feature-flag-key",
            "$feature_flag_response": "variant-name"
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    print(response)
    ```

4.  4

    ## Running experiments

    Optional

    Experiments run on top of our feature flags. Once you've implemented the flag in your code, you run an experiment by creating a new experiment in the PostHog dashboard.

5.  5

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