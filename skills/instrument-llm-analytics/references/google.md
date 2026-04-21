# Google LLM analytics installation - Docs

1.  1

    ## Install dependencies

    Required

    **Full working examples**

    See the complete [Node.js](https://github.com/PostHog/posthog-js/tree/main/examples/example-ai-gemini) and [Python](https://github.com/PostHog/posthog-python/tree/main/examples/example-ai-gemini) examples on GitHub. If you're using the PostHog SDK wrapper instead of OpenTelemetry, see the [Node.js wrapper](https://github.com/PostHog/posthog-js/tree/e08ff1be/examples/example-ai-gemini) and [Python wrapper](https://github.com/PostHog/posthog-python/tree/0fdbc2e9/examples/example-ai-gemini) examples.

    Install the OpenTelemetry SDK, the Google Gen AI instrumentation, and the Google Gen AI SDK.

    PostHog AI

    ### Python

    ```bash
    pip install google-genai opentelemetry-sdk posthog[otel] opentelemetry-instrumentation-google-generativeai
    ```

    ### Node

    ```bash
    npm install @google/genai @posthog/ai @opentelemetry/sdk-node @opentelemetry/resources @traceloop/instrumentation-google-generativeai
    ```

2.  2

    ## Set up OpenTelemetry tracing

    Required

    Configure OpenTelemetry to auto-instrument Google Gen AI SDK calls and export traces to PostHog. PostHog converts `gen_ai.*` spans into `$ai_generation` events automatically.

    PostHog AI

    ### Python

    ```python
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from posthog.ai.otel import PostHogSpanProcessor
    from opentelemetry.instrumentation.google_generativeai import GoogleGenerativeAiInstrumentor
    resource = Resource(attributes={
        SERVICE_NAME: "my-app",
        "posthog.distinct_id": "user_123", # optional: identifies the user in PostHog
        "foo": "bar", # custom properties are passed through
    })
    provider = TracerProvider(resource=resource)
    provider.add_span_processor(
        PostHogSpanProcessor(
            api_key="<ph_project_token>",
            host="https://us.i.posthog.com",
        )
    )
    trace.set_tracer_provider(provider)
    GoogleGenerativeAiInstrumentor().instrument()
    ```

    ### Node

    ```typescript
    import { NodeSDK } from '@opentelemetry/sdk-node'
    import { resourceFromAttributes } from '@opentelemetry/resources'
    import { PostHogSpanProcessor } from '@posthog/ai/otel'
    import { GenAIInstrumentation } from '@traceloop/instrumentation-google-generativeai'
    const sdk = new NodeSDK({
      resource: resourceFromAttributes({
        'service.name': 'my-app',
        'posthog.distinct_id': 'user_123', // optional: identifies the user in PostHog
        foo: 'bar', // custom properties are passed through
      }),
      spanProcessors: [
        new PostHogSpanProcessor({
          apiKey: '<ph_project_token>',
          host: 'https://us.i.posthog.com',
        }),
      ],
      instrumentations: [new GenAIInstrumentation()],
    })
    sdk.start()
    ```

3.  3

    ## Call Google Gen AI LLMs

    Required

    Now, when you use the Google Gen AI SDK to call Gemini, PostHog automatically captures `$ai_generation` events via the OpenTelemetry instrumentation.

    PostHog AI

    ### Python

    ```python
    from google import genai
    client = genai.Client(api_key="your_gemini_api_key")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[{"role": "user", "parts": [{"text": "Tell me a fun fact about hedgehogs"}]}],
    )
    print(response.text)
    ```

    ### Node

    ```typescript
    import { GoogleGenAI } from '@google/genai'
    const client = new GoogleGenAI({ apiKey: 'your_gemini_api_key' })
    const response = await client.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: 'Tell me a fun fact about hedgehogs',
    })
    console.log(response.text)
    ```

    > **Note:** This integration also works with Vertex AI via Google Cloud Platform. Initialize the Google Gen AI client with `vertexai=True, project=..., location=...` (Python) or `{ vertexai: true, project: '...', location: '...' }` (Node) and the OpenTelemetry instrumentation will capture those calls the same way.

    > **Note:** If you want to capture LLM events anonymously, omit the `posthog.distinct_id` resource attribute. See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

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
    | [[...]](/docs/llm-analytics/generations.md#event-properties) | See [full list](/docs/llm-analytics/generations.md#event-properties) of properties |

4.  4

    ## Capture embeddings

    Optional

    PostHog can also capture embedding generations as `$ai_embedding` events. The OpenTelemetry instrumentation automatically captures these when you use the `embed_content` API:

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

5.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **LLM analytics**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/llm-analytics/generations)

6.  5

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