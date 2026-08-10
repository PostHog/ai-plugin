# CrewAI observability installation - Docs

Copy page

# CrewAI observability installation - Docs

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_9608fcca70)

![](https://res.cloudinary.com/dmukukwp6/image/upload/texture_tan_dark_a92b0e022d)

Let AI instrument your LLM calls for you

Skip the manual setup — run this in your project and the wizard installs the SDK and wires up AI Observability for you.

`npx @posthog/wizard ai-observability`

[Learn more](/wizard.md)

![PostHog Wizard hedgehog](https://res.cloudinary.com/dmukukwp6/image/upload/wizard_3f8bb7a240.png)

![](https://res.cloudinary.com/dmukukwp6/image/upload/wizard_3f8bb7a240.png)Let AI instrument your LLM calls for you

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
    from crewai import Agent, Task, Crew, LLM
    # Set PostHog environment variables
    os.environ["POSTHOG_API_KEY"] = "<ph_project_token>"
    os.environ["POSTHOG_API_URL"] = "https://us.i.posthog.com"
    # Enable PostHog callbacks in LiteLLM
    litellm.success_callback = ["posthog"]
    litellm.failure_callback = ["posthog"]
    ```

    **How this works**

    CrewAI can route LLM calls either through its own provider clients or through LiteLLM. PostHog hooks into LiteLLM's callback system, so you need `is_litellm=True` on the `LLM` you pass to your agents. With it, PostHog captures every call as an `$ai_generation` event, without proxying your calls.

4.  4

    ## Run your crew

    Required

    Run your CrewAI agents as normal. PostHog automatically captures an `$ai_generation` event for each LLM call. LiteLLM's callback does not see the tools your agents call. Capture a tool's own execution as a span from inside the tool itself instead, as `my_tool` does below.

    ```python
    from posthog import Posthog
    from crewai.tools import tool
    import time, uuid
    posthog = Posthog("<ph_project_token>", host="https://us.i.posthog.com")
    trace_id = str(uuid.uuid4())
    @tool
    def my_tool(query: str) -> str:
        """Describe what your tool does."""
        start = time.time()
        result = run_tool(query)
        posthog.capture(
            distinct_id="user_123",
            event="$ai_span",
            properties={
                "$ai_trace_id": trace_id,
                "$ai_session_id": "conversation-abc",
                "$ai_span_id": str(uuid.uuid4()),
                "$ai_span_name": "my_tool",
                "$ai_input_state": {"query": query},
                "$ai_output_state": result,
                "$ai_latency": time.time() - start,
            },
        )
        return result
    # is_litellm=True routes calls through LiteLLM so the PostHog
    # callback fires. Without it, CrewAI uses its own provider client
    # and no events are captured.
    llm = LLM(
        model="gpt-4o-mini",
        is_litellm=True,
        metadata={
            "user_id": "user_123",
            "$ai_session_id": "conversation-abc",
            "$ai_trace_id": trace_id,
        },
    )
    researcher = Agent(
        role="Researcher",
        goal="Find the weather in a city",
        backstory="You are an expert wildlife researcher.",
        llm=llm,
        tools=[my_tool],
    )
    task = Task(
        description="Find the weather in Paris.",
        expected_output="The weather in Paris.",
        agent=researcher,
    )
    crew = Crew(agents=[researcher], tasks=[task])
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
    | [[...]](/docs/ai-observability/generations.md#event-properties) | See [full list](/docs/ai-observability/generations.md#event-properties) of properties |

5.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **AI Observability**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/ai-observability/generations)

6.  5

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

### Community questions

Ask a question

### Was this page useful?

HelpfulCould be better