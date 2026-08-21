> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Vercel AI SDK observability installation - Docs

Copy page

# Vercel AI SDK observability installation - Docs

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

    Use Node.js 22.22 or later. Install the PostHog AI package, the Vercel AI SDK, its OpenTelemetry integration, the OpenTelemetry SDK, and Zod for defining tool schemas.

    ```bash
    npm install @posthog/ai@^8.7.0 @ai-sdk/openai @ai-sdk/otel ai @opentelemetry/sdk-node @opentelemetry/resources zod
    ```

2.  2

    ## Set up the OpenTelemetry exporter

    Required

    Create `instrumentation.ts`. Initialize the OpenTelemetry SDK with PostHog's `PostHogSpanProcessor`, then register the Vercel AI SDK integration. Both setup calls must finish before the first AI SDK call. Their relative order does not matter because the integration obtains a lazy OpenTelemetry tracer.

    ```typescript
    import { OpenTelemetry } from '@ai-sdk/otel'
    import { NodeSDK } from '@opentelemetry/sdk-node'
    import { resourceFromAttributes } from '@opentelemetry/resources'
    import { PostHogSpanProcessor } from '@posthog/ai/otel'
    import { registerTelemetry } from 'ai'
    export const posthogSpanProcessor = new PostHogSpanProcessor({
      projectToken: '<ph_project_token>',
      host: 'https://us.i.posthog.com',
    })
    const sdk = new NodeSDK({
      resource: resourceFromAttributes({
        'service.name': 'my-app',
      }),
      spanProcessors: [posthogSpanProcessor],
    })
    sdk.start()
    registerTelemetry(
      new OpenTelemetry({
        enrichSpan: ({ runtimeContext }) => ({
          environment:
            typeof runtimeContext?.properties === 'object' &&
            runtimeContext.properties !== null &&
            'environment' in runtimeContext.properties &&
            typeof runtimeContext.properties.environment === 'string'
              ? runtimeContext.properties.environment
              : undefined,
          'posthog.distinct_id':
            typeof runtimeContext?.distinctId === 'string'
              ? runtimeContext.distinctId
              : undefined,
          '$ai_session_id':
            typeof runtimeContext?.sessionId === 'string'
              ? runtimeContext.sessionId
              : undefined,
          '$ai_trace_name':
            typeof runtimeContext?.traceName === 'string'
              ? runtimeContext.traceName
              : undefined,
          '$groups':
            typeof runtimeContext?.groups === 'object' &&
            runtimeContext.groups !== null &&
            !Array.isArray(runtimeContext.groups)
              ? JSON.stringify(runtimeContext.groups)
              : undefined,
        }),
      })
    )
    ```

    > **Request-scoped runtimes:** Keep the processor reference and await `posthogSpanProcessor.forceFlush()` before the request lifecycle ends, or attach the promise to a supported lifecycle hook such as `waitUntil`. Long-running services can flush during graceful shutdown instead.

    > **Vercel AI SDK versions:** This OpenTelemetry integration is the supported path for Vercel AI SDK v7. The legacy PostHog `withTracing` wrapper supports the v5 and v6 provider interfaces and rejects v7 models.

3.  3

    ## Call Vercel AI with telemetry enabled

    Required

    Pass request data through `runtimeContext`, then select the fields that the telemetry integration can receive with `telemetry.includeRuntimeContext`. Define `tools` the same way you normally would, with an `execute` function, as `get_weather` does below.

    ```typescript
    import { generateText, tool, stepCountIs } from 'ai'
    import { openai } from '@ai-sdk/openai'
    import { z } from 'zod'
    import { posthogSpanProcessor } from './instrumentation'
    async function runWeatherAgent(): Promise<string> {
      const result = await generateText({
        model: openai('gpt-5-mini'),
        prompt: "What's the weather in Paris?",
        tools: {
          get_weather: tool({
            description: 'Get the weather for a city',
            inputSchema: z.object({ city: z.string() }),
            execute: async ({ city }) => `It's always sunny in ${city}!`,
          }),
        },
        stopWhen: stepCountIs(5), // let the model see the tool result and respond
        runtimeContext: {
          distinctId: 'user_123',
          sessionId: 'conversation-abc',
          traceName: 'weather-agent',
          groups: {
            company: 'company_123',
          },
          properties: {
            environment: 'production',
          },
        },
        telemetry: {
          functionId: 'my-ai-function',
          includeRuntimeContext: {
            distinctId: true,
            sessionId: true,
            traceName: true,
            groups: true,
            properties: true,
          },
        },
      })
      return result.text
    }
    try {
      console.log(await runWeatherAgent())
    } finally {
      // Spans are still queued in the batch processor when this script exits,
      // so without this flush they never reach PostHog.
      await posthogSpanProcessor.forceFlush()
    }
    ```

    > **Identity:** Provide `distinctId` for stable user attribution. Omitting it does not make capture anonymous. PostHog assigns fallback IDs when no distinct ID is present.

    > **Groups and custom properties:** PostHog ingestion converts the JSON-string `$groups` attribute into native group associations. Other scalar attributes returned by `enrichSpan`, such as `environment`, remain filterable custom properties.

    > **Trace and session names:** `$ai_session_id` groups calls in AI observability. Trace names are not configurable on the v7 OpenTelemetry path yet. PostHog derives the displayed trace name from the OpenTelemetry span name, which takes precedence over `$ai_trace_name`. `functionId` is emitted as `gen_ai.agent.name` and does not set the trace name either.

    > **Runtime context support:** Current `@ai-sdk/otel` releases pass `runtimeContext` to `enrichSpan` for `generateText` and `streamText`. Object generation, embeddings, and reranking do not pass runtime context yet.

    > **Privacy:** Vercel AI SDK v7 records prompts and outputs by default. Set `recordInputs: false` or `recordOutputs: false` in `telemetry` to disable either field. The OpenTelemetry path does not have a separate PostHog privacy switch for text content, so these flags are the control for prompt and output recording.

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

### Still have questions?

Ask PostHog AI

### Was this page useful?

HelpfulCould be better