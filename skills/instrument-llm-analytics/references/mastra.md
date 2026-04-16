# Mastra LLM analytics installation - Docs

1.  1

    ## Install dependencies

    Required

    **Full working examples**

    See the complete [Node.js example](https://github.com/PostHog/posthog-js/tree/main/examples/example-ai-mastra) on GitHub. If you're using the PostHog SDK wrapper instead, see the [Node.js wrapper example](https://github.com/PostHog/posthog-js/tree/e08ff1be/examples/example-ai-mastra).

    Install Mastra with the official `@mastra/posthog` exporter. Mastra's observability system sends traces to PostHog as `$ai_generation` events automatically.

    ```bash
    npm install @mastra/core @mastra/observability @mastra/posthog
    ```

2.  2

    ## Configure Mastra with the PostHog exporter

    Required

    Initialize Mastra with an `Observability` config that uses the `PosthogExporter`. Pass your PostHog project token and host from [your project settings](https://app.posthog.com/settings/project).

    ```typescript
    import { Mastra } from '@mastra/core'
    import { Agent } from '@mastra/core/agent'
    import { Observability } from '@mastra/observability'
    import { PosthogExporter } from '@mastra/posthog'
    const weatherAgent = new Agent({
      id: 'weather-agent',
      name: 'Weather Agent',
      instructions: 'You are a helpful assistant with access to weather data.',
      model: { id: 'openai/gpt-4o-mini' },
    })
    const mastra = new Mastra({
      agents: { weatherAgent },
      observability: new Observability({
        configs: {
          posthog: {
            serviceName: 'my-app',
            exporters: [
              new PosthogExporter({
                apiKey: '<ph_project_token>',
                host: 'https://us.i.posthog.com',
                defaultDistinctId: 'user_123', // fallback if no userId in metadata
              }),
            ],
          },
        },
      }),
    })
    ```

3.  3

    ## Run your agent

    Required

    Use Mastra as normal. The `PosthogExporter` automatically captures `$ai_generation` events for each LLM call, including token usage, cost, latency, and the full conversation.

    Pass `tracingOptions.metadata` to `generate()` to attach per-request metadata. The `userId` field maps to PostHog's distinct ID, `sessionId` maps to `$ai_session_id`, and any other keys are passed through as custom event properties.

    ```typescript
    const agent = mastra.getAgent('weatherAgent')
    const result = await agent.generate("What's the weather in Dublin?", {
      tracingOptions: {
        metadata: {
          userId: 'user_123', // becomes distinct_id
          sessionId: 'session_abc', // becomes $ai_session_id
          conversation_id: 'abc-123', // custom property
        },
      },
    })
    console.log(result.text)
    ```

    > **Note:** If you want to capture LLM events anonymously, omit `userId` from `tracingOptions.metadata` and don't set `defaultDistinctId`. See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

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