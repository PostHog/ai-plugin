> AI agents: this is one page from PostHog's docs. Full index of Markdown docs for LLMs: https://posthog.com/llms.txt

# Anthropic AI Observability installation

Canonical URL: https://posthog.com/docs/ai-observability/installation/anthropic

> **Cloud region:** This page uses US Cloud hosts. For an EU Cloud project, use `https://eu.i.posthog.com` instead of `https://us.i.posthog.com` (ingestion host).

## On this page

- [Copy your project token](#copy-your-project-token)
- [Choose how to send traces](#choose-how-to-send-traces)
- [Call Claude and see the trace](#call-claude-and-see-the-trace)
- [Users and sessions](#users-and-sessions)
- [Keep an eye on your agent](#keep-an-eye-on-your-agent)
- [Troubleshooting](#troubleshooting)
- [Install dependencies](#install-dependencies)
- [Configure PostHog](#configure-posthog)
- [Call Anthropic](#call-anthropic)
- [Capture tool calls as spans](#capture-tool-calls-as-spans)
- [Verify traces and generations](#verify-traces-and-generations)
- [Next steps](#next-steps)
- [If you just landed here, welcome](#if-you-just-landed-here-welcome)

## Claude Platform Beta

Claude Platform+PostHog

### Become a trace explorer

Send OpenTelemetry traces from Claude to PostHog with no extra code. Add PostHog as a destination in the Claude Console and run evals on live traces and ship fixes that actually make a difference.

100K free events, every month

![Explorer hedgehog holding a folded map](https://posthog.com/images/docs/ai-observability/explorer-hedgehog.png)

Click the map

1.  1

    ## Copy your project token

    Required

    Log in to see your project token here

    [Log in to PostHog](https://app.posthog.com/login)[or open your project settings](https://app.posthog.com/settings/project#variables)

    A personal API key (`phx_...`) won't work here.

2.  2

    ## Choose how to send traces

    Required

    The Claude Platform can send traces from two places. Pick one for each PostHog project. If you use both, each request reaches PostHog twice.

    -   **SDK tracing:** you set it up in your code with the Claude SDK. It covers the calls your app makes and the tools it runs itself. You can link traces to your users and add custom properties.
    -   **Console destination:** you add PostHog in the Claude Console, with no code changes. It covers your Messages API requests, server tools such as web search, and Managed Agents sessions.

    ## SDK tracing

    Install the Claude SDK with the steps in Anthropic's [OpenTelemetry guide](https://platform.claude.com/docs/en/manage-claude/opentelemetry/sdk#install-the-sdk). Then install the OpenTelemetry packages. PostHog has a span processor for Python, Node, and Go. Java and Ruby use the standard OTLP exporter.

    ### Python

    ```bash
    pip install "posthog[otel]"
    ```

    ### Node

    ```bash
    npm install @posthog/ai @opentelemetry/sdk-trace-node @opentelemetry/resources @opentelemetry/exporter-trace-otlp-http
    ```

    ### Go

    ```bash
    go get github.com/posthog/posthog-go/otel go.opentelemetry.io/otel go.opentelemetry.io/otel/sdk
    ```

    ### Java

    ```kotlin
    dependencies {
        implementation(platform("io.opentelemetry:opentelemetry-bom:1.57.0"))
        implementation("io.opentelemetry:opentelemetry-sdk")
        implementation("io.opentelemetry:opentelemetry-exporter-otlp")
    }
    ```

    ### Ruby

    ```bash
    bundle add opentelemetry-sdk opentelemetry-exporter-otlp
    ```

    Register a tracer provider before your first Claude call. Set the content mode to see prompts and responses, because the SDK sends metadata only by default:

    ### Python

    ```python
    from anthropic import Anthropic
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from posthog.ai.otel import PostHogSpanProcessor
    
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
    
    client = Anthropic(open_telemetry={"traces": {"content_mode": "content"}})
    
    message = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Tell me about hedgehogs"}],
    )
    
    # Flush the batched spans before a script exits.
    provider.shutdown()
    ```

    ### Node

    ```typescript
    import Anthropic from '@anthropic-ai/sdk'
    import { resourceFromAttributes } from '@opentelemetry/resources'
    import { NodeTracerProvider } from '@opentelemetry/sdk-trace-node'
    import { PostHogSpanProcessor } from '@posthog/ai/otel'
    
    const provider = new NodeTracerProvider({
      resource: resourceFromAttributes({
        'service.name': 'my-app',
        'posthog.distinct_id': 'user_123', // optional: identifies the user in PostHog
        foo: 'bar', // custom properties are passed through
      }),
      spanProcessors: [
        new PostHogSpanProcessor({
          projectToken: '<ph_project_token>',
          host: 'https://us.i.posthog.com',
        }),
      ],
    })
    provider.register()
    
    const client = new Anthropic({ openTelemetry: { traces: { contentMode: 'content' } } })
    
    const message = await client.messages.create({
      model: 'claude-opus-5',
      max_tokens: 1024,
      messages: [{ role: 'user', content: 'Tell me about hedgehogs' }],
    })
    
    // Flush the batched spans before a script exits.
    await provider.shutdown()
    ```

    ### Go

    ```go
    package main
    
    import (
        "context"
        "fmt"
    
        "github.com/anthropics/anthropic-sdk-go"
        "github.com/anthropics/anthropic-sdk-go/option"
        posthogotel "github.com/posthog/posthog-go/otel"
        "go.opentelemetry.io/otel"
        "go.opentelemetry.io/otel/attribute"
        "go.opentelemetry.io/otel/propagation"
        sdkresource "go.opentelemetry.io/otel/sdk/resource"
        sdktrace "go.opentelemetry.io/otel/sdk/trace"
    )
    
    func main() {
        ctx := context.Background()
    
        processor, err := posthogotel.NewSpanProcessor(ctx, "<ph_project_token>",
            posthogotel.WithHost("https://us.i.posthog.com"),
        )
        if err != nil {
            panic(err)
        }
    
        resource := sdkresource.NewWithAttributes("",
            attribute.String("service.name", "my-app"),
            attribute.String("posthog.distinct_id", "user_123"), // optional: identifies the user in PostHog
            attribute.String("foo", "bar"), // custom properties are passed through
        )
        provider := sdktrace.NewTracerProvider(
            sdktrace.WithResource(resource),
            sdktrace.WithSpanProcessor(processor),
        )
        // Flush the batched spans before the program exits.
        defer provider.Shutdown(ctx)
        otel.SetTracerProvider(provider)
        otel.SetTextMapPropagator(propagation.TraceContext{})
    
        client := anthropic.NewClient(
            option.WithOpenTelemetryTracesContentMode(option.OpenTelemetryContentModeContent),
        )
    
        message, err := client.Messages.New(ctx, anthropic.MessageNewParams{
            Model:     anthropic.ModelClaudeOpus5,
            MaxTokens: 1024,
            Messages: []anthropic.MessageParam{
                anthropic.NewUserMessage(anthropic.NewTextBlock("Tell me about hedgehogs")),
            },
        })
        if err != nil {
            panic(err)
        }
        fmt.Println(message.StopReason)
    }
    ```

    ### Java

    ```java
    import com.anthropic.client.okhttp.AnthropicOkHttpClient;
    import com.anthropic.core.opentelemetry.OpenTelemetryContentMode;
    import com.anthropic.core.opentelemetry.OpenTelemetryOptions;
    import com.anthropic.models.messages.MessageCreateParams;
    import com.anthropic.models.messages.Model;
    import io.opentelemetry.api.common.AttributeKey;
    import io.opentelemetry.api.common.Attributes;
    import io.opentelemetry.api.trace.propagation.W3CTraceContextPropagator;
    import io.opentelemetry.context.propagation.ContextPropagators;
    import io.opentelemetry.exporter.otlp.http.trace.OtlpHttpSpanExporter;
    import io.opentelemetry.sdk.OpenTelemetrySdk;
    import io.opentelemetry.sdk.resources.Resource;
    import io.opentelemetry.sdk.trace.SdkTracerProvider;
    import io.opentelemetry.sdk.trace.export.BatchSpanProcessor;
    
    public class Main {
        public static void main(String[] args) {
            var exporter = OtlpHttpSpanExporter.builder()
                .setEndpoint("https://us.i.posthog.com/i/v0/ai/otel")
                .addHeader("Authorization", "Bearer <ph_project_token>")
                .build();
    
            var resource = Resource.getDefault().merge(Resource.create(Attributes.of(
                AttributeKey.stringKey("service.name"), "my-app",
                AttributeKey.stringKey("posthog.distinct_id"), "user_123", // optional: identifies the user in PostHog
                AttributeKey.stringKey("foo"), "bar"))); // custom properties are passed through
    
            var tracerProvider = SdkTracerProvider.builder()
                .setResource(resource)
                .addSpanProcessor(BatchSpanProcessor.builder(exporter).build())
                .build();
            OpenTelemetrySdk.builder()
                .setTracerProvider(tracerProvider)
                .setPropagators(ContextPropagators.create(W3CTraceContextPropagator.getInstance()))
                .buildAndRegisterGlobal();
    
            var envOptions = OpenTelemetryOptions.fromEnv();
            var client = AnthropicOkHttpClient.builder()
                .fromEnv()
                .openTelemetry(envOptions.toBuilder()
                    .traces(envOptions.traces().toBuilder()
                        .contentMode(OpenTelemetryContentMode.CONTENT)
                        .build())
                    .build())
                .build();
    
            var message = client.messages().create(MessageCreateParams.builder()
                .model(Model.CLAUDE_OPUS_5)
                .maxTokens(1024)
                .addUserMessage("Tell me about hedgehogs")
                .build());
    
            // Flush the batched spans before the program exits.
            tracerProvider.close();
        }
    }
    ```

    ### Ruby

    ```ruby
    require "anthropic"
    require "opentelemetry/sdk"
    require "opentelemetry/exporter/otlp"
    
    OpenTelemetry::SDK.configure do |config|
      config.resource = OpenTelemetry::SDK::Resources::Resource.create(
        "service.name" => "my-app",
        "posthog.distinct_id" => "user_123", # optional: identifies the user in PostHog
        "foo" => "bar" # custom properties are passed through
      )
      config.add_span_processor(
        OpenTelemetry::SDK::Trace::Export::BatchSpanProcessor.new(
          OpenTelemetry::Exporter::OTLP::Exporter.new(
            endpoint: "https://us.i.posthog.com/i/v0/ai/otel",
            headers: {"Authorization" => "Bearer <ph_project_token>"}
          )
        )
      )
    end
    
    client = Anthropic::Client.new(open_telemetry: {traces: {content_mode: :content}})
    
    message = client.messages.create(
      model: Anthropic::Model::CLAUDE_OPUS_5,
      max_tokens: 1024,
      messages: [{role: "user", content: "Tell me about hedgehogs"}]
    )
    
    # Flush the batched spans before a script exits.
    OpenTelemetry.tracer_provider.shutdown
    ```

    You can also set the content mode with the `ANTHROPIC_OPEN_TELEMETRY_TRACES_CONTENT_MODE=content` environment variable.

    To group several calls into one session, set a conversation ID on the client or the request, as described in [Configure the SDK](https://platform.claude.com/docs/en/manage-claude/opentelemetry/sdk#configure-the-sdk). PostHog uses it as the session ID.

    ## Console destination

    API tracing does not yet support person identification or custom properties. Anthropic is exploring ways to support this in the future.

    In the Claude Console, open the [OpenTelemetry settings](https://platform.claude.com/settings/telemetry-destinations) of your organization and click **Add destination**. You need an admin role.

    1.  **Provider:** PostHog.
    2.  **Region:** US if you log in at `us.posthog.com`, EU if you log in at `eu.posthog.com`.
    3.  **Project token:** paste your `phc_` token.
    4.  **Content mode:** pick **Full content** to see every prompt and response in PostHog. **Metadata only** sends tokens, costs, and timing without the messages.
    5.  **Workspaces:** choose which workspaces send their traces to PostHog: **All**, **Selected**, or **All except**.

    ![The Add destination form in the Claude Console with PostHog selected as the provider](https://posthog.com/images/docs/ai-observability/claude-platform-add-destination.png)

    Click **Add destination**. Your code doesn't change.

    Anthropic's [OpenTelemetry guide](https://platform.claude.com/docs/en/manage-claude/opentelemetry) covers workspaces, delivery health, and every span and attribute.

3.  3

    ## Call Claude and see the trace

    Required

    Call Claude the way you already do, then open [AI Observability](https://app.posthog.com/ai-observability/traces). Each request shows up as an `anthropic.messages.create` trace, with its cost, tokens, and messages.

    -   **SDK tracing:** if you use the tool runner, each tool it runs gets its own span.
    -   **Console destination:** the trace holds an `anthropic.model_request` span for each model request. A request can have more than one, for example when the model uses web search.

    **Using Managed Agents?** A Console destination also sends your sessions, with a span for each turn, model request, and tool use:

    ![A Managed Agents trace in PostHog: session turns with model requests and bash tool uses on a timeline, and the turn input and output](https://posthog.com/images/docs/ai-observability/claude-platform-managed-agents-trace.png)

    The turn holds the agent's input and output, each model request holds its tokens and cost, and each tool use holds its arguments and result. A session can span several traces. To follow one session, filter by `anthropic.session.id`.

4.  4

    ## Users and sessions

    Recommended

    This step applies to SDK tracing in Python, Node, and Go.

    A server usually handles requests for many users, so a resource attribute can't say who each trace belongs to. Wrap each request in a PostHog context instead. The PostHog span processor adds the context's distinct ID and properties to every AI span started inside it. Other span processors and exporters on the same provider don't see them.

    Set `$ai_session_id` if your product has multi-turn conversations, so the Sessions tab can group their traces. Workloads that finish in a single trace, like batch jobs or one-shot generation, don't need it.

    ### Python

    ```python
    # Requires posthog 7.70.0 or later
    import posthog
    
    with posthog.new_context():
        posthog.identify_context(user_id)
        posthog.tag("$ai_session_id", conversation_id)
        posthog.tag("plan", "pro")  # custom properties work too
    
        reply = handle_turn(user_message)
    ```

    ### Node

    ```typescript
    // Requires @posthog/ai 8.14.0 and posthog-node 5.15.0 or later
    import { PostHog } from 'posthog-node'
    
    const posthog = new PostHog('<ph_project_token>', { host: 'https://us.i.posthog.com' })
    
    const provider = new NodeTracerProvider({
      // ...the rest of your setup from the earlier step
      spanProcessors: [
        new PostHogSpanProcessor({
          projectToken: '<ph_project_token>',
          host: 'https://us.i.posthog.com',
          client: posthog,
        }),
      ],
    })
    
    const reply = await posthog.withContext(
      {
        distinctId: userId,
        properties: {
          $ai_session_id: conversationId,
          plan: 'pro', // custom properties work too
        },
      },
      () => handleTurn(userMessage)
    )
    ```

    ### Go

    ```go
    // Requires github.com/posthog/posthog-go/otel v1.35.0 or later
    import "github.com/posthog/posthog-go"
    
    ctx = posthog.WithRequestContext(ctx, posthog.RequestContext{
        DistinctId: userID,
        Properties: posthog.Properties{
            "$ai_session_id": conversationID,
            "plan":           "pro", // custom properties work too
        },
    })
    
    reply := handleTurn(ctx, userMessage)
    ```

    On Node, install `posthog-node` and pass the client as the `client` option of your `PostHogSpanProcessor`. Without it, the processor doesn't read the context.

    In Go, `posthog.NewRequestContextMiddleware` fills the context for each HTTP request from the `X-PostHog-Distinct-Id` and `X-PostHog-Session-Id` headers. The session header sets the web session ID (`$session_id`), not `$ai_session_id`, so set `$ai_session_id` in `Properties` to group traces in the Sessions tab.

    A distinct ID set this way takes priority over a `posthog.distinct_id` resource attribute, so you can keep the resource attribute as the fallback for work outside a request. If your instrumentation already sets the `gen_ai.conversation.id` attribute, PostHog uses it as the session ID, and an explicit `$ai_session_id` takes priority over it.

5.  5

    ## Keep an eye on your agent

    Recommended

    Your traces are in. Now put them to work.

    Evaluations

    Quickly monitor how your agent is doing. Score every response for helpfulness, hallucinations, or tone, and see when quality drops.

    [Set up evaluations](https://posthog.com/docs/ai-evals.md)

    Dashboard

    Follow cost, usage, and latency over time, broken down by model or workspace.

    [Explore the dashboard](https://posthog.com/docs/ai-observability/dashboard.md)

    Clusters

    Group similar conversations to see what people ask your agent most.

    [Find patterns](https://posthog.com/docs/ai-observability/clusters.md)

    Sentiment

    See how users feel while they talk to your agent.

    [Track sentiment](https://posthog.com/docs/ai-observability/sentiment.md)

6.  6

    ## Troubleshooting

    Optional

    -   **Delivery shows Failing with a 401:** the token in the Claude Console is a personal API key. Use your project token.
    -   **Delivery shows Healthy, but PostHog is empty:** check that the token comes from this project and that the region matches your PostHog cloud.
    -   **No traces from a Console destination:** check that the destination's **Workspaces** setting covers the workspace of your API key. Traces can take up to a minute to arrive.
    -   **No traces from the Claude SDK:** register the tracer provider before the first Claude call. `ANTHROPIC_OPEN_TELEMETRY=false` turns the spans off.
    -   **Traces stop at the end of a script:** shut down the tracer provider before the script exits, as the samples do, so the last batch is sent.
    -   **No prompts or responses:** in the Claude Console, the destination uses **Metadata only**. Organizations with a data-handling restriction, such as HIPAA, always export metadata only. With the Claude SDK, set the content mode to `content` on the client.
    -   **Each request appears twice:** a Claude Console destination and the Claude SDK both send this project the same requests. Remove one of the two.

    For other questions, see [AI Observability troubleshooting](https://posthog.com/docs/ai-observability/troubleshooting.md).

## Tab

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

    See the complete [Node.js](https://github.com/PostHog/posthog-js/tree/main/examples/example-ai-anthropic) and [Python](https://github.com/PostHog/posthog-python/tree/master/examples/example-ai-anthropic) examples on GitHub.

    Install the PostHog SDK and the Anthropic SDK.

    ### Python

    ```bash
    pip install posthog anthropic
    ```

    ### Node

    ```bash
    npm install @posthog/ai posthog-node @anthropic-ai/sdk
    ```

    ### Go

    ```prose
    PostHog doesn't have a Go wrapper for this SDK yet. Use the [OpenTelemetry integration](https://posthog.com/docs/ai-observability/installation/opentelemetry) instead.
    ```

2.  2

    ## Configure PostHog

    Required

    Create a PostHog client, then swap in PostHog's Anthropic wrapper.

    ### Python

    ```python
    from posthog import Posthog
    from posthog.ai.anthropic import Anthropic
    import time, uuid
    
    posthog = Posthog("<ph_project_token>", host="https://us.i.posthog.com")
    
    client = Anthropic(
        api_key="sk-ant-api...",
        posthog_client=posthog,
    )
    ```

    ### Node

    ```typescript
    import { Anthropic } from '@posthog/ai/anthropic'
    import { PostHog } from 'posthog-node'
    
    const posthog = new PostHog('<ph_project_token>', { host: 'https://us.i.posthog.com' })
    
    const client = new Anthropic({
      apiKey: 'sk-ant-api...',
      posthog,
    })
    ```

3.  3

    ## Call Anthropic

    Required

    When you use the wrapped client to call Anthropic, PostHog automatically captures an `$ai_generation` event.

    ### Python

    ```python
    trace_id = str(uuid.uuid4())
    
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": "What's the weather in Paris?"}],
        tools=tools,
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
    
    const response = await client.messages.create({
      model: 'claude-sonnet-4-5',
      max_tokens: 1024,
      messages: [{ role: 'user', content: "What's the weather in Paris?" }],
      tools,
      posthogDistinctId: 'user_123',
      posthogTraceId: traceId,
      posthogProperties: {
        $ai_session_id: 'conversation-abc',
      },
    })
    ```

    > **Note:** If you want to capture LLM events anonymously, omit `posthog_distinct_id` from the call. See our docs on [anonymous vs identified events](https://posthog.com/docs/data/anonymous-vs-identified-events.md) to learn more.

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

    ## Capture tool calls as spans

    Optional

    For standard responses, the posthog client captures it as a generation. For all tool calls, you must manually capture them as `$ai_span` events.

    ### Python

    ```python
    for block in response.content:
        if block.type != "tool_use":
            continue
    
        start = time.time()
        result = run_tool(block.name, block.input)
    
        posthog.capture(
            distinct_id="user_123",
            event="$ai_span",
            properties={
                "$ai_trace_id": trace_id,
                "$ai_session_id": "conversation-abc",
                "$ai_span_id": str(uuid.uuid4()),
                "$ai_span_name": block.name,
                "$ai_input_state": block.input,
                "$ai_output_state": result,
                "$ai_latency": time.time() - start,
            },
        )
    ```

    ### Node

    ```typescript
    for (const block of response.content) {
      if (block.type !== 'tool_use') continue
    
      const start = Date.now()
      const result = await runTool(block.name, block.input)
    
      posthog.capture({
        distinctId: 'user_123',
        event: '$ai_span',
        properties: {
          $ai_trace_id: traceId,
          $ai_session_id: 'conversation-abc',
          $ai_span_id: crypto.randomUUID(),
          $ai_span_name: block.name,
          $ai_input_state: block.input,
          $ai_output_state: result,
          $ai_latency: (Date.now() - start) / 1000,
        },
      })
    }
    ```

    See [spans](https://posthog.com/docs/ai-observability/spans.md) for the full list of span properties.

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

Tourist info

## If you just landed here, welcome

PostHog is the context layer for your product. And since we're advertising anyway: 97% of companies use it for free.

[Get started](https://app.posthog.com/signup)[Read the docs](https://posthog.com/docs.md)

A hedgehog tourist holding a map and a suitcase
