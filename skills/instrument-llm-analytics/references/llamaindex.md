> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# LlamaIndex AI Observability installation - Docs

Copy page

# LlamaIndex AI Observability installation - Docs

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

    See the complete [Python example](https://github.com/PostHog/posthog-python/tree/master/examples/example-ai-llamaindex) on GitHub. If you use the PostHog SDK wrapper instead of OpenTelemetry, see this example instead: [Python wrapper example](https://github.com/PostHog/posthog-python/tree/7223c52/examples/example-ai-llamaindex).

    Install LlamaIndex, OpenAI, and the OpenTelemetry SDK with the LlamaIndex instrumentation.

    ```bash
    pip install llama-index llama-index-llms-openai opentelemetry-sdk "posthog[otel]" opentelemetry-instrumentation-openai-v2
    ```

2.  2

    ## Set up OpenTelemetry tracing

    Required

    Configure OpenTelemetry to auto-instrument LlamaIndex calls and export traces to PostHog. PostHog converts `gen_ai.*` spans into `$ai_generation` events automatically.

    ```python
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME
    from posthog.ai.otel import PostHogSpanProcessor
    from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
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
    OpenAIInstrumentor().instrument()
    ```

    **What gets captured**

    This instruments the OpenAI calls LlamaIndex makes underneath, so you get one `$ai_generation` per LLM call. Retrieval and query-engine steps are not captured as spans. To record those, capture `$ai_span` events yourself with a shared `$ai_trace_id`. See [manual capture](/docs/ai-observability/installation/manual-capture.md).

3.  3

    ## Query with LlamaIndex

    Required

    Use LlamaIndex as normal. The OpenTelemetry instrumentation automatically captures `$ai_generation` events for each LLM call.

    ```python
    from llama_index.llms.openai import OpenAI
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
    llm = OpenAI(model="gpt-4o-mini", api_key="your_openai_api_key")
    # Load your documents
    documents = SimpleDirectoryReader("data").load_data()
    # Create an index
    index = VectorStoreIndex.from_documents(documents, llm=llm)
    # Query the index
    query_engine = index.as_query_engine(llm=llm)
    response = query_engine.query("What is this document about?")
    print(response)
    ```

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
    | [[...]](/docs/ai-observability/generations.md#event-properties) | See [full list](/docs/ai-observability/generations.md#event-properties) of properties |

4.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **AI Observability**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/ai-observability/generations)

5.  4

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