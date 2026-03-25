# OpenAI LLM analytics installation - Docs

1.  1

    ## Install the PostHog SDK

    Required

    Setting up analytics starts with installing the PostHog SDK for your language. LLM analytics works best with our Python and Node SDKs.

    PostHog AI

    ### Python

    ```bash
    pip install posthog
    ```

    ### Node

    ```bash
    npm install @posthog/ai posthog-node
    ```

2.  2

    ## Install the OpenAI SDK

    Required

    Install the OpenAI SDK. The PostHog SDK instruments your LLM calls by wrapping the OpenAI client. The PostHog SDK **does not** proxy your calls.

    PostHog AI

    ### Python

    ```bash
    pip install openai
    ```

    ### Node

    ```bash
    npm install openai
    ```

3.  3

    ## Initialize PostHog and OpenAI client

    Required

    Initialize PostHog with your project token and host from [your project settings](https://app.posthog.com/settings/project), then pass it to our OpenAI wrapper.

    PostHog AI

    ### Python

    ```python
    from posthog.ai.openai import OpenAI
    from posthog import Posthog
    posthog = Posthog(
        "<ph_project_token>",
        host="https://us.i.posthog.com"
    )
    client = OpenAI(
        api_key="your_openai_api_key",
        posthog_client=posthog # This is an optional parameter. If it is not provided, a default client will be used.
    )
    ```

    ### Node

    ```typescript
    import { OpenAI } from '@posthog/ai'
    import { PostHog } from 'posthog-node'
    const phClient = new PostHog(
      '<ph_project_token>',
      { host: 'https://us.i.posthog.com' }
    );
    const openai = new OpenAI({
      apiKey: 'your_openai_api_key',
      posthog: phClient,
    });
    // ... your code here ...
    // IMPORTANT: Shutdown the client when you're done to ensure all events are sent
    phClient.shutdown()
    ```

    > **Note:** This also works with the `AsyncOpenAI` client.

    **Proxy note**

    These SDKs **do not** proxy your calls. They only fire off an async call to PostHog in the background to send the data. You can also use LLM analytics with other SDKs or our API, but you will need to capture the data in the right format. See the schema in the [manual capture section](/docs/llm-analytics/installation/manual-capture.md) for more details.

4.  4

    ## Call OpenAI LLMs

    Required

    Now, when you use the OpenAI SDK to call LLMs, PostHog automatically captures an `$ai_generation` event. You can enrich the event with additional data such as the trace ID, distinct ID, custom properties, groups, and privacy mode options.

    PostHog AI

    ### Python

    ```python
    response = client.responses.create(
        model="gpt-5-mini",
        input=[
            {"role": "user", "content": "Tell me a fun fact about hedgehogs"}
        ],
        posthog_distinct_id="user_123", # optional
        posthog_trace_id="trace_123", # optional
        posthog_properties={"conversation_id": "abc123", "paid": True}, # optional
        posthog_groups={"company": "company_id_in_your_db"},  # optional
        posthog_privacy_mode=False # optional
    )
    print(response.output_text)
    ```

    ### Node

    ```typescript
    const completion = await openai.responses.create({
        model: "gpt-5-mini",
        input: [{ role: "user", content: "Tell me a fun fact about hedgehogs" }],
        posthogDistinctId: "user_123", // optional
        posthogTraceId: "trace_123", // optional
        posthogProperties: { conversation_id: "abc123", paid: true }, // optional
        posthogGroups: { company: "company_id_in_your_db" }, // optional
        posthogPrivacyMode: false // optional
    });
    console.log(completion.output_text)
    ```

    > **Notes:**
    >
    > -   We also support the old `chat.completions` API.
    > -   This works with responses where `stream=True`.
    > -   If you want to capture LLM events anonymously, **don't** pass a distinct ID to the request.
    >
    > See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

    You can expect captured `$ai_generation` events to have the following properties:

5.  5

    ## Capture embeddings

    Optional

    PostHog can also capture embedding generations as `$ai_embedding` events. Just make sure to use the same `posthog.ai.openai` client to do so:

    ```python
    response = client.embeddings.create(
        input="The quick brown fox",
        model="text-embedding-3-small",
        posthog_distinct_id="user_123", # optional
        posthog_trace_id="trace_123",   # optional
        posthog_properties={"key": "value"} # optional
        posthog_groups={"company": "company_id_in_your_db"}  # optional
        posthog_privacy_mode=False # optional
    )
    ```

6.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **LLM analytics**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/llm-analytics/generations)

7.  6

    ## Next steps

    Recommended

    Now that you're capturing AI conversations, continue with the resources below to learn what else LLM Analytics enables within the PostHog platform.

    | Resource | Description |
    | --- | --- |
    | [Basics](/docs/llm-analytics/basics.md) | Learn the basics of how LLM calls become events in PostHog. |
    | [Generations](/docs/llm-analytics/generations.md) | Read about the $ai_generation event and its properties. |
    | [Traces](/docs/llm-analytics/traces.md) | Explore the trace hierarchy and how to use it to debug LLM calls. |
    | [Spans](/docs/llm-analytics/spans.md) | Review spans and their role in representing individual operations. |
    | [Anaylze LLM performance](/docs/llm-analytics/dashboard.md) | Learn how to create dashboards to analyze LLM performance. |

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better