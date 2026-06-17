# Azure OpenAI observability installation - Docs

1.  1

    ## Install dependencies

    Required

    **Full working examples**

    See the complete [Node.js](https://github.com/PostHog/posthog-js/tree/main/examples/example-ai-azure-openai) and [Python](https://github.com/PostHog/posthog-python/tree/master/examples/example-ai-azure-openai) examples on GitHub. If you're using the PostHog SDK wrapper instead of OpenTelemetry, see the [Node.js wrapper](https://github.com/PostHog/posthog-js/tree/e08ff1be/examples/example-ai-azure-openai) and [Python wrapper](https://github.com/PostHog/posthog-python/tree/7223c52/examples/example-ai-azure-openai) examples.

    Install the OpenTelemetry SDK, the OpenAI instrumentation, and the OpenAI SDK.

    PostHog AI

    ### Python

    ```bash
    pip install openai opentelemetry-sdk "posthog[otel]" opentelemetry-instrumentation-openai-v2
    ```

    ### Node

    ```bash
    npm install openai @posthog/ai @opentelemetry/sdk-node @opentelemetry/resources @opentelemetry/instrumentation-openai
    ```

2.  2

    ## Set up OpenTelemetry tracing

    Required

    Configure OpenTelemetry to auto-instrument OpenAI SDK calls and export traces to PostHog. PostHog converts `gen_ai.*` spans into `$ai_generation` events automatically.

    PostHog AI

    ### Python

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

    ### Node

    ```typescript
    import { NodeSDK } from '@opentelemetry/sdk-node'
    import { resourceFromAttributes } from '@opentelemetry/resources'
    import { PostHogSpanProcessor } from '@posthog/ai/otel'
    import { OpenAIInstrumentation } from '@opentelemetry/instrumentation-openai'
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
      instrumentations: [new OpenAIInstrumentation()],
    })
    sdk.start()
    ```

3.  3

    ## Call Azure OpenAI

    Required

    Now, when you call Azure OpenAI, PostHog automatically captures `$ai_generation` events via the OpenTelemetry instrumentation.

    PostHog AI

    ### Python

    ```python
    import openai
    client = openai.AzureOpenAI(
        api_key="<azure_openai_api_key>",
        api_version="2024-10-21",
        azure_endpoint="https://<your-resource>.openai.azure.com",
    )
    response = client.chat.completions.create(
        model="<your-deployment-name>",
        messages=[
            {"role": "user", "content": "Tell me a fun fact about hedgehogs"}
        ],
    )
    print(response.choices[0].message.content)
    ```

    ### Node

    ```typescript
    import { AzureOpenAI } from 'openai'
    const client = new AzureOpenAI({
      apiKey: '<azure_openai_api_key>',
      apiVersion: '2024-10-21',
      endpoint: 'https://<your-resource>.openai.azure.com',
    })
    const response = await client.chat.completions.create({
      model: '<your-deployment-name>',
      messages: [{ role: 'user', content: 'Tell me a fun fact about hedgehogs' }],
    })
    console.log(response.choices[0].message.content)
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

## .NET support

`PostHog.AI` adds AI observability for .NET applications using Azure OpenAI. It is currently pre-release, so expect breaking changes before a stable release.

Install the packages:

Terminal

PostHog AI

```bash
dotnet add package PostHog.AI
dotnet add package Azure.AI.OpenAI
```

When using dependency injection, register PostHog first, then register an Azure OpenAI client with the PostHog handler:

C#

PostHog AI

```csharp
using System.ClientModel.Primitives;
using Azure;
using Azure.AI.OpenAI;
using Microsoft.Extensions.DependencyInjection;
using PostHog.AI;
using PostHog.Config;
var services = new ServiceCollection();
services.AddPostHog(options =>
{
    options.PostConfigure(posthogOptions =>
    {
        posthogOptions.ProjectToken = "<ph_project_token>";
        posthogOptions.HostUrl = new Uri("https://us.i.posthog.com");
    });
});
services.AddPostHogAI();
services
    .AddHttpClient("PostHogAzureOpenAIClient")
    .AddPostHogOpenAIHandler();
services.AddSingleton<AzureOpenAIClient>(sp =>
{
    var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
    var httpClient = httpClientFactory.CreateClient("PostHogAzureOpenAIClient");
    var options = new AzureOpenAIClientOptions
    {
        Transport = new HttpClientPipelineTransport(httpClient),
    };
    return new AzureOpenAIClient(
        new Uri("<azure_openai_endpoint>"),
        new AzureKeyCredential("<azure_openai_api_key>"),
        options);
});
var serviceProvider = services.BuildServiceProvider();
var azureOpenAIClient = serviceProvider.GetRequiredService<AzureOpenAIClient>();
```

Use `PostHogAIContext` to attach trace, session, span, and user context to AI calls made inside a scope:

C#

PostHog AI

```csharp
using PostHog.AI;
using (PostHogAIContext.BeginScope(
    distinctId: "user-123",
    traceId: "trace-abc",
    sessionId: "session-xyz",
    spanId: "span-1",
    spanName: "summarize_text",
    parentId: null))
{
    var chatClient = azureOpenAIClient.GetChatClient("<deployment_name>");
    await chatClient.CompleteChatAsync("Summarize this text");
}
```

The integration captures `$ai_generation` and `$ai_embedding` events with model, latency, token, error, trace, session, and span properties. For more .NET SDK details, see the [.NET library docs](/docs/libraries/dotnet.md#ai-observability).

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better