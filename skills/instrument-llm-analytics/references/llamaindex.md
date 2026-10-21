> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# LlamaIndex AI Observability installation

Canonical URL: https://posthog.com/docs/ai-observability/installation/llamaindex

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host), and use `https://eu.posthog.com` instead of `https://app.posthog.com` (app host for links).

## On this page

- [Install dependencies](#install-dependencies)
- [Set up OpenTelemetry tracing](#set-up-opentelemetry-tracing)
- [Query with LlamaIndex](#query-with-llamaindex)
- [Users and sessions](#users-and-sessions)
- [Verify traces and generations](#verify-traces-and-generations)
- [Next steps](#next-steps)

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_9608fcca70)

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_dark_a92b0e022d)

Let AI instrument your LLM calls for you

Skip the manual setup — run this in your project and the wizard installs the SDK and wires up AI Observability for you.

`npx @posthog/wizard ai-observability`

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

    This instruments the OpenAI calls LlamaIndex makes underneath, so you get one `$ai_generation` per LLM call. Retrieval and query-engine steps are not captured as spans. To record those, capture `$ai_span` events yourself with a shared `$ai_trace_id`. See [manual capture](https://posthog.com/docs/ai-observability/installation/manual-capture.md).

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

    > **Note:** To capture LLM events anonymously, omit the `posthog.distinct_id` resource attribute and don't set a distinct ID in the PostHog context. See our docs on [anonymous vs identified events](https://posthog.com/docs/data/anonymous-vs-identified-events.md) to learn more.

    You can expect captured `$ai_generation` events to have the following properties:

    | Property | Description |
    | --- | --- |
    | `$ai_model` | The specific model, like `gpt-5-mini` or `claude-4-sonnet` |
    | `$ai_latency` | The latency of the LLM call in seconds |
    | `$ai_time_to_first_token` | Time to first token in seconds (streaming only) |
    | `$ai_tools` | Tools and functions available to the LLM |
    | `$ai_input` | List of messages sent to the LLM |
    | `$ai_input_tokens` | The number of tokens in the input (often found in response.usage) |
    | `$ai_output_choices` | List of response choices from the LLM |
    | `$ai_output_tokens` | The number of tokens in the output (often found in `response.usage`) |
    | `$ai_total_cost_usd` | The total cost in USD (input + output) |
    | [\[...\]](https://posthog.com/docs/ai-observability/generations.md#event-properties) | See [full list](https://posthog.com/docs/ai-observability/generations.md#event-properties) of properties |

4.  4

    ## Users and sessions

    Recommended

    A server usually handles requests for many users, so a resource attribute can't say who each trace belongs to. Wrap each request in a PostHog context instead. The PostHog span processor adds the context's distinct ID and properties to every AI span started inside it. Other span processors and exporters on the same provider don't see them.

    Set `$ai_session_id` if your product has multi-turn conversations, so the Sessions tab can group their traces. Workloads that finish in a single trace, like batch jobs or one-shot generation, don't need it.

    Python

    ```python
    # Requires posthog 7.70.0 or later
    import posthog
    
    with posthog.new_context():
        posthog.identify_context(user_id)
        posthog.tag("$ai_session_id", conversation_id)
        posthog.tag("plan", "pro")  # custom properties work too
    
        reply = handle_turn(user_message)
    ```

    A distinct ID set this way takes priority over a `posthog.distinct_id` resource attribute, so you can keep the resource attribute as the fallback for work outside a request. If your instrumentation already sets the `gen_ai.conversation.id` attribute, PostHog uses it as the session ID, and an explicit `$ai_session_id` takes priority over it.

5.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **AI Observability**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)

    [Check for LLM events in PostHog](https://app.posthog.com/ai-observability/generations)

6.  5

    ## Next steps

    Recommended

    Now that you're capturing AI conversations, continue with the resources below to learn what else AI Observability enables within the PostHog platform.

    | Resource | Description |
    | --- | --- |
    | [Basics](https://posthog.com/docs/ai-observability/basics.md) | Learn the basics of how LLM calls become events in PostHog. |
    | [Generations](https://posthog.com/docs/ai-observability/generations.md) | Read about the `$ai_generation` event and its properties. |
    | [Traces](https://posthog.com/docs/ai-observability/traces.md) | Explore the trace hierarchy and how to use it to debug LLM calls. |
    | [Spans](https://posthog.com/docs/ai-observability/spans.md) | Review spans and their role in representing individual operations. |
    | [Anaylze LLM performance](https://posthog.com/docs/ai-observability/dashboard.md) | Learn how to create dashboards to analyze LLM performance. |
