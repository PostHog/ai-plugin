# AutoGen LLM analytics installation - Docs

1.  1

    ## Install dependencies

    Required

    **Full working examples**

    See the complete [Python example](https://github.com/PostHog/posthog-python/tree/master/examples/example-ai-autogen) on GitHub. If you're using the PostHog SDK wrapper instead of OpenTelemetry, see the [Python wrapper example](https://github.com/PostHog/posthog-python/tree/7223c52/examples/example-ai-autogen).

    Install the OpenTelemetry SDK, the OpenAI instrumentation, and AutoGen.

    ```bash
    pip install autogen-agentchat "autogen-ext[openai]" openai opentelemetry-sdk posthog[otel] opentelemetry-instrumentation-openai-v2
    ```

2.  2

    ## Set up OpenTelemetry tracing

    Required

    Configure OpenTelemetry to auto-instrument OpenAI SDK calls and export traces to PostHog. PostHog converts `gen_ai.*` spans into `$ai_generation` events automatically.

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

3.  3

    ## Run your agents

    Required

    Use AutoGen as normal. PostHog automatically captures an `$ai_generation` event for each LLM call made through the OpenAI SDK that AutoGen uses internally.

    ```python
    import asyncio
    from autogen_agentchat.agents import AssistantAgent
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key="your_openai_api_key",
    )
    agent = AssistantAgent("assistant", model_client=model_client)
    async def main():
        result = await agent.run(task="Say 'Hello World!'")
        print(result)
        await model_client.close()
    asyncio.run(main())
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
    | [[...]](/docs/llm-analytics/generations.md#event-properties) | See [full list](/docs/llm-analytics/generations.md#event-properties) of properties |

4.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **LLM analytics**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/llm-analytics/generations)

5.  4

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