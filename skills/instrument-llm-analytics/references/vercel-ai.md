# Vercel AI SDK LLM analytics installation - Docs

1.  1

    ## Install dependencies

    Required

    Install the PostHog AI package, the Vercel AI SDK, and the OpenTelemetry SDK.

    ```bash
    npm install @posthog/ai @ai-sdk/openai ai @opentelemetry/sdk-node @opentelemetry/resources
    ```

2.  2

    ## Set up the OpenTelemetry exporter

    Required

    Initialize the OpenTelemetry SDK with PostHog's `PostHogSpanProcessor`. This sends `gen_ai.*` spans directly to PostHog's OTLP ingestion endpoint. PostHog converts these into `$ai_generation` events automatically.

    ```typescript
    import { NodeSDK } from '@opentelemetry/sdk-node'
    import { resourceFromAttributes } from '@opentelemetry/resources'
    import { PostHogSpanProcessor } from '@posthog/ai/otel'
    const sdk = new NodeSDK({
      resource: resourceFromAttributes({
        'service.name': 'my-app',
      }),
      spanProcessors: [
        new PostHogSpanProcessor({
          apiKey: '<ph_project_token>',
          host: 'https://us.i.posthog.com',
        }),
      ],
    })
    sdk.start()
    ```

3.  3

    ## Call Vercel AI with telemetry enabled

    Required

    Pass `experimental_telemetry` to your Vercel AI SDK calls. The `posthog_distinct_id` metadata field links events to a specific user in PostHog.

    ```typescript
    import { generateText } from 'ai'
    import { openai } from '@ai-sdk/openai'
    const result = await generateText({
      model: openai('gpt-5-mini'),
      prompt: 'Tell me a fun fact about hedgehogs.',
      experimental_telemetry: {
        isEnabled: true,
        functionId: 'my-ai-function',
        metadata: {
          posthog_distinct_id: 'user_123', // optional
        },
      },
    })
    console.log(result.text)
    ```

    > **Note:** If you want to capture LLM events anonymously, omit the `posthog_distinct_id` metadata field. See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

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