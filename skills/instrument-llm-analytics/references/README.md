# PostHog.AI

This package provides AI Observability for .NET applications using PostHog. It currently supports intercepting and tracing requests to OpenAI and Azure OpenAI.

> [!WARNING]  
> This package is currently in a pre-release stage. We're making it available publicly to solicit
> feedback. While we always strive to maintain a high level of quality, use this package at your own
> risk. There *will* be many breaking changes until we reach a stable release.

## Installation

Install the `PostHog.AI` package via NuGet:

```bash
dotnet add package PostHog.AI
```

## Usage

### Dependency Injection (Recommended)

The easiest way to use `PostHog.AI` is via the `AddPostHogOpenAIClient` extension method. This registers an `OpenAIClient` that is automatically configured to use PostHog for observability.

```csharp
using PostHog;
using PostHog.AI;
using OpenAI;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = Host.CreateApplicationBuilder(args);

// 1. Configure PostHog
builder.Services.AddPostHog(options =>
{
    options.ProjectToken = "YOUR_PROJECT_TOKEN";
    options.HostUrl = new Uri("https://us.i.posthog.com"); // or eu.i.posthog.com
});

// 2. Register OpenAI Client with PostHog integration
// This registers OpenAIClient as a Singleton and configures it to use the PostHog interceptor.
// You can also chain additional HTTP handlers here (e.g., for resilience).
builder.Services.AddPostHogOpenAIClient("YOUR_OPENAI_API_KEY", options => 
{
    // Optional: Configure OpenAIClientOptions here
});

var host = builder.Build();

// 3. Inject and use OpenAIClient
var openAIClient = host.Services.GetRequiredService<OpenAIClient>();
// ... use client
```

> **Note:** `AddPostHogOpenAIClient` overrides the `Transport` property of `OpenAIClientOptions` to inject the PostHog handler. If you need a custom Transport implementation (rare), you should manually configure the client as shown below.

### Manual Configuration (Advanced)

If you need more control or are not using the helper method:

```csharp
using PostHog.AI;
using OpenAI;
using System.ClientModel;
using System.ClientModel.Primitives;

// 1. Register PostHog AI services
builder.Services.AddPostHogAI();

// 2. Configure OpenAI Client with the intercepting handler manually
builder.Services.AddHttpClient("PostHogOpenAI") // Named client
    .AddPostHogOpenAIHandler();

builder.Services.AddSingleton<OpenAIClient>(sp =>
{
    var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();
    var httpClient = httpClientFactory.CreateClient("PostHogOpenAI");
    
    // Explicitly set the transport
    var options = new OpenAIClientOptions
    {
        Transport = new HttpClientPipelineTransport(httpClient)
    };
    
    return new OpenAIClient(new ApiKeyCredential("YOUR_OPENAI_API_KEY"), options);
});
```

## Supported Features

-   **Trace Capture**: Automatically captures `$ai_generation` and `$ai_embedding` events.
-   **Token Usage**: Captures prompt, completion, and total token usage.
-   **Model Parameters**: Tracks model configuration including temperature, max_tokens, stream, and tools.
-   **Latency**: Measures and records request latency in seconds.
-   **Streaming**: Supports capturing content from streamed responses (Server-Sent Events).
-   **Embeddings**: Automatically detects and captures `$ai_embedding` events for embedding requests.
-   **Error Handling**: Captures error messages and HTTP status codes.
-   **Span and Session Tracking**: Supports grouping events with session IDs, span IDs, and parent-child relationships via `PostHogAIContext`.
-   **Cache Tracking**: Captures cache token usage when available in API responses.

## Captured Event Properties

The handler automatically extracts and captures the following properties from OpenAI API requests and responses:

### Core Properties

- `$ai_trace_id` - Unique identifier (UUID) for grouping AI events
- `$ai_provider` - AI service provider (e.g., "openai")
- `$ai_lib` - Library identifier ("posthog-dotnet")
- `$ai_model` - Model name used for the generation
- `$ai_latency` - Request latency in seconds
- `$ai_base_url` - Base URL of the API endpoint
- `$ai_request_url` - Full URL of the API request
- `$ai_http_status` - HTTP status code of the response

### Model Parameters

- `$ai_temperature` - Temperature parameter used in the request
- `$ai_max_tokens` - Maximum tokens setting
- `$ai_stream` - Whether the response was streamed
- `$ai_tools` - Tools/functions available to the model
- `$ai_model_parameters` - Dictionary of other model parameters (top_p, frequency_penalty, presence_penalty, stop, etc.)

### Input/Output

- `$ai_input` - Input messages, prompt, or input data
- `$ai_output_choices` - Response choices from the LLM (for generation events)
- `$ai_input_tokens` - Number of tokens in the input
- `$ai_output_tokens` - Number of tokens in the output
- `$ai_total_tokens` - Total number of tokens used

### Context-Based Properties

These properties can be set via `PostHogAIContext` (see below):

- `$ai_session_id` - Groups related traces together
- `$ai_span_id` - Unique identifier for this generation
- `$ai_span_name` - Name given to this generation
- `$ai_parent_id` - Parent span ID for tree view grouping

### Cache Properties

- `$ai_cache_read_input_tokens` - Number of tokens read from cache (when available)
- `$ai_cache_creation_input_tokens` - Number of tokens written to cache (when available)

### Error Properties

- `$ai_is_error` - Boolean indicating if the request was an error
- `$ai_error` - Error message or object

## Using PostHogAIContext

`PostHogAIContext` allows you to set additional context for AI events within a scope, including session tracking, span tracking, and custom properties.

### Basic Usage

```csharp
using PostHog.AI;

// Begin a scope with context
using (PostHogAIContext.BeginScope(
    distinctId: "user-123",
    traceId: "trace-abc",
    sessionId: "session-xyz",
    spanId: "span-1",
    spanName: "summarize_text",
    parentId: null))
{
    // All OpenAI API calls within this scope will include the context
    var chatClient = openAIClient.GetChatClient("gpt-4");
    var response = await chatClient.CompleteChatAsync("Summarize this text");
}
// Context is automatically restored when the scope ends
```

### Span Tracking Example

```csharp
using PostHog.AI;

// Parent span
using (PostHogAIContext.BeginScope(
    traceId: "trace-123",
    spanId: "span-parent",
    spanName: "process_document"))
{
    // Child span 1
    using (PostHogAIContext.BeginScope(
        traceId: "trace-123", // Same trace
        spanId: "span-child-1",
        spanName: "extract_summary",
        parentId: "span-parent")) // Link to parent
    {
        // First AI call
        var chatClient = openAIClient.GetChatClient("gpt-4");
        await chatClient.CompleteChatAsync("Summarize the document");
    }

    // Child span 2
    using (PostHogAIContext.BeginScope(
        traceId: "trace-123",
        spanId: "span-child-2",
        spanName: "extract_keywords",
        parentId: "span-parent"))
    {
        // Second AI call
        var chatClient = openAIClient.GetChatClient("gpt-4");
        await chatClient.CompleteChatAsync("Extract keywords from the document");
    }
}
```

### Custom Properties

You can add custom properties that will be merged into the event properties:

```csharp
using PostHog.AI;

var customProperties = new Dictionary<string, object>
{
    { "workflow_id", "workflow-123" },
    { "feature_flag", "new-model-v2" },
    { "$ai_session_id", "override-session" } // Can override context properties
};

using (PostHogAIContext.BeginScope(
    sessionId: "default-session",
    properties: customProperties))
{
    // Properties dictionary takes precedence over context properties
    // In this case, $ai_session_id will be "override-session"
    var chatClient = openAIClient.GetChatClient("gpt-4");
    await chatClient.CompleteChatAsync("Hello");
}
```

### Property Precedence

Properties are applied in the following order (later values override earlier ones):

1. Context properties (`SessionId`, `SpanId`, etc.)
2. Properties dictionary (can override context properties)

This allows you to set default context properties via `BeginScope` and override them for specific events via the Properties dictionary.

## Configuration

The handler uses the configured `IPostHogClient` to send events. Ensure your PostHog client is correctly configured with your API key and host URL.
