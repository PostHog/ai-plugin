# Google AI Observability installation - Docs

Copy page

# Google AI Observability installation - Docs

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_9608fcca70)

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_dark_a92b0e022d)

Let AI instrument your LLM calls for you

Skip the manual setup — run this in your project and the wizard installs the SDK and wires up AI Observability for you.

`npx @posthog/wizard ai-observability`

[Learn more](/wizard.md)

![PostHog Wizard hedgehog](https://res.cloudinary.com/dmukukwp6/image/upload/wizard_3f8bb7a240.png)

![](https://res.cloudinary.com/dmukukwp6/image/upload/wizard_3f8bb7a240.png)Let AI instrument your LLM calls for you

1.  1

    ## Install dependencies

    Required

    **Full working examples**

    See the complete [Node.js](https://github.com/PostHog/posthog-js/tree/main/examples/example-ai-gemini) and [Python](https://github.com/PostHog/posthog-python/tree/main/examples/example-ai-gemini) examples on GitHub.

    Install the PostHog SDK and the Google Gen AI SDK.

    PostHog AI

    ### Python

    ```bash
    pip install posthog google-genai
    ```

    ### Node

    ```bash
    npm install @posthog/ai posthog-node @google/genai
    ```

2.  2

    ## Configure PostHog

    Required

    Create a PostHog client, then swap in PostHog's Google Gen AI wrapper.

    PostHog AI

    ### Python

    ```python
    from posthog import Posthog
    from posthog.ai.gemini import Client
    import time, uuid
    from google.genai import types
    posthog = Posthog("<ph_project_token>", host="https://us.i.posthog.com")
    client = Client(
        api_key="your_gemini_api_key",
        posthog_client=posthog,
    )
    ```

    ### Node

    ```typescript
    import { GoogleGenAI } from '@posthog/ai/gemini'
    import { PostHog } from 'posthog-node'
    const posthog = new PostHog('<ph_project_token>', { host: 'https://us.i.posthog.com' })
    const client = new GoogleGenAI({
      apiKey: 'your_gemini_api_key',
      posthog,
    })
    ```

3.  3

    ## Call Google Gen AI LLMs

    Required

    When you use the wrapped client to call Gemini, PostHog automatically captures an `$ai_generation` event.

    PostHog AI

    ### Python

    ```python
    trace_id = str(uuid.uuid4())
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"role": "user", "parts": [{"text": "What's the weather in Paris?"}]}],
        config=types.GenerateContentConfig(tools=tools),
        posthog_distinct_id="user_123",
        posthog_trace_id=trace_id,
        posthog_properties={
            "$ai_session_id": "conversation-abc",
        },
    )
    ```

    ### Node

    ```typescript
    const traceId = crypto.randomUUID()
    const response = await client.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: "What's the weather in Paris?",
      config: { tools },
      posthogDistinctId: 'user_123',
      posthogTraceId: traceId,
      posthogProperties: {
        $ai_session_id: 'conversation-abc',
      },
    })
    ```

    > **Note:** If you want to capture LLM events anonymously, omit `posthog_distinct_id` from the call. See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

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

4.  4

    ## Capture tool calls as spans

    Optional

    For standard responses, the posthog client captures it as a generation. For all tool calls, you must manually capture them as `$ai_span` events.

    PostHog AI

    ### Python

    ```python
    for call in response.function_calls or []:
        start = time.time()
        result = run_tool(call.name, call.args)
        posthog.capture(
            distinct_id="user_123",
            event="$ai_span",
            properties={
                "$ai_trace_id": trace_id,
                "$ai_session_id": "conversation-abc",
                "$ai_span_id": str(uuid.uuid4()),
                "$ai_span_name": call.name,
                "$ai_input_state": call.args,
                "$ai_output_state": result,
                "$ai_latency": time.time() - start,
            },
        )
    ```

    ### Node

    ```typescript
    for (const call of response.functionCalls ?? []) {
      const start = Date.now()
      const result = await runTool(call.name, call.args)
      posthog.capture({
        distinctId: 'user_123',
        event: '$ai_span',
        properties: {
          $ai_trace_id: traceId,
          $ai_session_id: 'conversation-abc',
          $ai_span_id: crypto.randomUUID(),
          $ai_span_name: call.name,
          $ai_input_state: call.args,
          $ai_output_state: result,
          $ai_latency: (Date.now() - start) / 1000,
        },
      })
    }
    ```

    See [spans](/docs/ai-observability/spans.md) for the full list of span properties.

5.  5

    ## Capture embeddings

    Optional

    PostHog can also capture embedding generations as `$ai_embedding` events. The wrapped client captures these automatically when you use the `embed_content` API:

    PostHog AI

    ### Python

    ```python
    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents="The quick brown fox",
    )
    ```

    ### Node

    ```typescript
    const response = await client.models.embedContent({
      model: 'gemini-embedding-001',
      contents: 'The quick brown fox',
    })
    ```

6.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **AI Observability**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/ai-observability/generations)

7.  6

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

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better