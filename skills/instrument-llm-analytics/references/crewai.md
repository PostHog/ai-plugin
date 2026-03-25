# CrewAI LLM analytics installation - Docs

1.  1

    ## Install the PostHog SDK

    Required

    Setting up analytics starts with installing the PostHog SDK. CrewAI uses LiteLLM under the hood, and PostHog integrates with LiteLLM's callback system.

    ```bash
    pip install posthog
    ```

2.  2

    ## Install CrewAI

    Required

    Install CrewAI. PostHog instruments your LLM calls through LiteLLM's callback system that CrewAI uses natively.

    ```bash
    pip install crewai litellm
    ```

3.  3

    ## Configure PostHog with LiteLLM

    Required

    Set your PostHog project token and host as environment variables, then configure LiteLLM to use PostHog as a callback handler. You can find your project token in [your project settings](https://app.posthog.com/settings/project).

    ```python
    import os
    import litellm
    from crewai import Agent, Task, Crew
    # Set PostHog environment variables
    os.environ["POSTHOG_API_KEY"] = "<ph_project_token>"
    os.environ["POSTHOG_API_URL"] = "https://us.i.posthog.com"
    # Enable PostHog callbacks in LiteLLM
    litellm.success_callback = ["posthog"]
    litellm.failure_callback = ["posthog"]
    ```

    **How this works**

    CrewAI uses LiteLLM under the hood for LLM provider access. By configuring PostHog as a LiteLLM callback, all LLM calls made through CrewAI are automatically captured as `$ai_generation` events without proxying your calls.

4.  4

    ## Run your crew

    Required

    Run your CrewAI agents as normal. PostHog automatically captures generation events for each LLM call.

    ```python
    researcher = Agent(
        role="Researcher",
        goal="Find interesting facts about hedgehogs",
        backstory="You are an expert wildlife researcher.",
    )
    task = Task(
        description="Research three fun facts about hedgehogs.",
        expected_output="A list of three fun facts.",
        agent=researcher,
    )
    crew = Crew(
        agents=[researcher],
        tasks=[task],
    )
    result = crew.kickoff()
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