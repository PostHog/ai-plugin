# smolagents LLM analytics installation - Docs

1.  1

    ## Install the PostHog SDK

    Required

    Setting up analytics starts with installing the PostHog SDK. The smolagents integration uses PostHog's OpenAI wrapper.

    ```bash
    pip install posthog
    ```

2.  2

    ## Install smolagents and OpenAI

    Required

    Install smolagents and the OpenAI SDK. PostHog instruments your LLM calls by wrapping the OpenAI client, which you can pass to smolagents' `OpenAIServerModel`.

    ```bash
    pip install smolagents openai
    ```

3.  3

    ## Initialize PostHog and smolagents

    Required

    Initialize PostHog with your project token and host from [your project settings](https://app.posthog.com/settings/project), then create a PostHog OpenAI wrapper and pass it to smolagents' `OpenAIServerModel`.

    ```python
    from smolagents import CodeAgent, OpenAIServerModel
    from posthog.ai.openai import OpenAI
    from posthog import Posthog
    posthog = Posthog(
        "<ph_project_token>",
        host="https://us.i.posthog.com"
    )
    openai_client = OpenAI(
        api_key="your_openai_api_key",
        posthog_client=posthog
    )
    model = OpenAIServerModel(
        model_id="gpt-5-mini",
        client=openai_client,
    )
    ```

    **How this works**

    PostHog's `OpenAI` wrapper is a drop-in replacement for `openai.OpenAI`. By passing it as the `client` to `OpenAIServerModel`, all LLM calls made by smolagents are automatically captured as `$ai_generation` events.

4.  4

    ## Run your agent

    Required

    Use smolagents as normal. PostHog automatically captures an `$ai_generation` event for each LLM call made through the wrapped OpenAI client.

    ```python
    agent = CodeAgent(
        tools=[],
        model=model,
    )
    result = agent.run(
        "What is a fun fact about hedgehogs?"
    )
    print(result)
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