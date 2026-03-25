# Pydantic AI LLM analytics installation - Docs

1.  1

    ## Install the PostHog SDK

    Required

    Setting up analytics starts with installing the PostHog SDK. The Pydantic AI integration uses PostHog's OpenAI wrapper.

    ```bash
    pip install posthog
    ```

2.  2

    ## Install Pydantic AI

    Required

    Install Pydantic AI with OpenAI support. PostHog instruments your LLM calls by wrapping the OpenAI client that Pydantic AI uses.

    ```bash
    pip install 'pydantic-ai[openai]'
    ```

3.  3

    ## Initialize PostHog and Pydantic AI

    Required

    Initialize PostHog with your project token and host from [your project settings](https://app.posthog.com/settings/project), then create a PostHog `AsyncOpenAI` wrapper, pass it to an `OpenAIProvider`, and use that with Pydantic AI's `OpenAIChatModel`.

    ```python
    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIChatModel
    from pydantic_ai.providers.openai import OpenAIProvider
    from posthog.ai.openai import AsyncOpenAI
    from posthog import Posthog
    posthog = Posthog(
        "<ph_project_token>",
        host="https://us.i.posthog.com"
    )
    openai_client = AsyncOpenAI(
        api_key="your_openai_api_key",
        posthog_client=posthog
    )
    provider = OpenAIProvider(openai_client=openai_client)
    model = OpenAIChatModel(
        "gpt-5-mini",
        provider=provider
    )
    ```

    **How this works**

    PostHog's `AsyncOpenAI` wrapper is a proper subclass of `openai.AsyncOpenAI`, so it works directly as the client for Pydantic AI's `OpenAIProvider`. PostHog captures `$ai_generation` events automatically without proxying your calls.

4.  4

    ## Run your agent

    Required

    Create a Pydantic AI agent with the model and run it. PostHog automatically captures an `$ai_generation` event for each LLM call.

    ```python
    agent = Agent(
        model,
        system_prompt="You are a helpful assistant.",
    )
    result = agent.run_sync(
        "Tell me a fun fact about hedgehogs.",
        # Pass PostHog metadata via the OpenAI client's extra params
    )
    print(result.output)
    ```

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