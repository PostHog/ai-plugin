> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# LiteLLM AI Observability installation - Docs

Copy page

# LiteLLM AI Observability installation - Docs

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_9608fcca70)

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_dark_a92b0e022d)

Let AI instrument your LLM calls for you

Skip the manual setup — run this in your project and the wizard installs the SDK and wires up AI Observability for you.

`npx @posthog/wizard ai-observability`

[Learn more](/wizard.md)

![PostHog Wizard hedgehog](https://res.cloudinary.com/dmukukwp6/image/upload/wizard_3f8bb7a240.png)

![](https://res.cloudinary.com/dmukukwp6/image/upload/wizard_3f8bb7a240.png)Let AI instrument your LLM calls for you

1.  1

    ## LiteLLM Requirements

    Required

    > **Note:** Use LiteLLM as a Python SDK or as a proxy server. PostHog observability requires LiteLLM version 1.77.3 or higher.

2.  2

    ## Install LiteLLM

    Required

    Choose your installation method based on how you want to use LiteLLM:

    PostHog AI

    ### SDK

    ```bash
    pip install litellm
    ```

    ### Proxy

    ```bash
    # Install via pip
    pip install 'litellm[proxy]'
    # Or run via Docker
    docker run --rm -p 4000:4000 ghcr.io/berriai/litellm:latest
    ```

3.  3

    ## Configure PostHog observability

    Required

    Configure PostHog by setting your project token and host as well as adding `posthog` to your LiteLLM callback handlers. You can find your project token in [your project settings](https://app.posthog.com/settings/project).

    PostHog AI

    ### SDK

    ```python
    import os
    import litellm
    # Set environment variables
    os.environ["POSTHOG_API_KEY"] = "<ph_project_token>"
    os.environ["POSTHOG_API_URL"] = "https://us.i.posthog.com"  # Optional, defaults to https://app.posthog.com
    # Enable PostHog callbacks
    litellm.success_callback = ["posthog"]
    litellm.failure_callback = ["posthog"]  # Optional: also log failures
    ```

    ### Proxy

    ```yaml
    # config.yaml
    model_list:
    - model_name: gpt-5-mini
      litellm_params:
        model: gpt-5-mini
    litellm_settings:
      success_callback: ["posthog"]
      failure_callback: ["posthog"]  # Optional: also log failures
    environment_variables:
      POSTHOG_API_KEY: "<ph_project_token>"
      POSTHOG_API_URL: "https://us.i.posthog.com"  # Optional
    ```

4.  4

    ## Call LLMs through LiteLLM

    Required

    When you use LiteLLM to call an LLM provider, PostHog automatically captures an `$ai_generation` event. Identity and trace data travel through `metadata`, since LiteLLM has no dedicated `posthog_trace_id` parameter.

    PostHog AI

    ### SDK

    ```python
    from posthog import Posthog
    import time, uuid, json
    posthog = Posthog("<ph_project_token>", host="https://us.i.posthog.com")
    trace_id = str(uuid.uuid4())
    response = litellm.completion(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": "What's the weather in Paris?"}],
        tools=tools,
        metadata={
            "user_id": "user_123",                # Maps to PostHog distinct_id
            "company": "company_id_in_your_db",   # Custom property
            "$ai_session_id": "conversation-abc",
            "$ai_trace_id": trace_id,
        },
    )
    ```

    ### Proxy

    ```bash
    # Start the proxy (if not already running)
    litellm --config config.yaml
    # Make a request to the proxy
    curl -X POST http://localhost:4000/chat/completions                                       -H "Content-Type: application/json"                                       -d '{
        "model": "gpt-5-mini",
        "messages": [
          {"role": "user", "content": "Tell me a fun fact about hedgehogs"}
        ],
        "metadata": {
          "user_id": "user_123",
          "company": "company_id_in_your_db", # Custom property
          "$ai_session_id": "conversation-abc" # Groups calls into one session
        }
      }'
    ```

    > **Notes:**
    >
    > -   This works with streaming responses by setting `stream=True`.
    > -   To disable logging for specific requests, add `{"no-log": true}` to metadata.
    > -   Pass `$ai_session_id` in metadata to group calls from the same conversation into one PostHog session.
    > -   If you want to capture LLM events anonymously, **do not** pass a `user_id` in metadata.
    >
    > See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

    You can expect captured `$ai_generation` events to have the following properties:

    | Property | Description |
    | --- | --- |
    | $ai_model | The specific model, like gpt-5-mini or claude-4-sonnet |
    | $ai_latency | The latency of the LLM call in seconds |
    | $ai_time_to_first_token | Time to first token in seconds (streaming only) |
    | $ai_tools | Tools and functions available to the LLM |
    | $ai_input | List of messages sent to the LLM |
    | $ai_input_tokens | The number of tokens in the input (often found in response.usage) |
    | $ai_output_choices | List of response choices from the LLM |
    | $ai_output_tokens | The number of tokens in the output (often found in response.usage) |
    | $ai_total_cost_usd | The total cost in USD (input + output) |
    | [[...]](/docs/ai-observability/generations.md#event-properties) | See [full list](/docs/ai-observability/generations.md#event-properties) of properties |

5.  5

    ## Capture tool calls as spans

    Optional

    Capture each tool call as a span yourself, as the example below does right after the generation that triggered it.

    ```python
    for call in response.choices[0].message.tool_calls or []:
        start = time.time()
        result = run_tool(call.function.name, json.loads(call.function.arguments))
        posthog.capture(
            distinct_id="user_123",
            event="$ai_span",
            properties={
                "$ai_trace_id": trace_id,
                "$ai_session_id": "conversation-abc",
                "$ai_span_id": str(uuid.uuid4()),
                "$ai_span_name": call.function.name,
                "$ai_input_state": call.function.arguments,
                "$ai_output_state": result,
                "$ai_latency": time.time() - start,
            },
        )
    ```

    See [spans](/docs/ai-observability/spans.md) for the full list of span properties.

6.  6

    ## Capture embeddings

    Optional

    PostHog can also capture embedding generations as `$ai_embedding` events through LiteLLM:

    PostHog AI

    ### SDK

    ```python
    response = litellm.embedding(
        input="The quick brown fox",
        model="text-embedding-3-small",
        metadata={
            "user_id": "user_123",  # Maps to PostHog distinct_id
            "company": "company_id_in_your_db"  # Custom property
        }
    )
    ```

    ### Proxy

    ```bash
    # Make an embeddings request to the proxy
    curl -X POST http://localhost:4000/embeddings                                       -H "Content-Type: application/json"                                       -d '{
        "input": "The quick brown fox",
        "model": "text-embedding-3-small",
        "metadata": {
          "user_id": "user_123",
          "company": "company_id_in_your_db" # Custom property
        }
      }'
    ```

7.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **AI Observability**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/ai-observability/generations)

8.  7

    ## Next steps

    Recommended

    Now that you're capturing AI conversations, continue with the resources below to learn what else AI Observability enables within the PostHog platform.

    | Resource | Description |
    | --- | --- |
    | [Basics](/docs/ai-observability/basics.md) | Learn the basics of how LLM calls become events in PostHog. |
    | [Generations](/docs/ai-observability/generations.md) | Read about the $ai_generation event and its properties. |
    | [Traces](/docs/ai-observability/traces.md) | Explore the trace hierarchy and how to use it to debug LLM calls. |
    | [Spans](/docs/ai-observability/spans.md) | Review spans and their role in representing individual operations. |
    | [Anaylze LLM performance](/docs/ai-observability/dashboard.md) | Learn how to create dashboards to analyze LLM performance. |

### Was this page useful?

HelpfulCould be better