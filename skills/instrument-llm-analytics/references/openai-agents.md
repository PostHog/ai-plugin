# OpenAI Agents SDK observability installation - Docs

Copy page

# OpenAI Agents SDK observability installation - Docs

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

    Setting up analytics starts with installing the PostHog Python SDK.

    ```bash
    pip install posthog
    ```

2.  2

    ## Install the OpenAI Agents SDK

    Required

    Install the OpenAI Agents SDK. PostHog instruments your agent runs by registering a tracing processor. The PostHog SDK **does not** proxy your calls.

    ```bash
    pip install openai-agents
    ```

    **Proxy note**

    These SDKs **do not** proxy your calls. They only fire off an async call to PostHog in the background to send the data. You can also use AI observability with other SDKs or our API, but you will need to capture the data in the right format. See the schema in the [manual capture section](/docs/ai-observability/installation/manual-capture.md) for more details.

3.  3

    ## Initialize PostHog tracing

    Required

    Initialize PostHog with your project token and host from [your project settings](https://app.posthog.com/settings/project). Then call `instrument()` to register PostHog tracing with the OpenAI Agents SDK. This automatically captures all agent traces, spans, and LLM generations.

    ```python
    from posthog import Posthog
    from posthog.ai.openai_agents import instrument
    posthog = Posthog(
        "<ph_project_token>",
        host="https://us.i.posthog.com"
    )
    instrument(
        client=posthog,
        distinct_id=lambda trace: (trace.metadata or {}).get("posthog_distinct_id"),
        privacy_mode=False, # optional
        groups={"company": "company_id_in_your_db"}, # optional
    )
    ```

    > **Note:** If you want to capture LLM events anonymously, **do not** pass a distinct ID — here or per run. See our docs on [anonymous vs identified events](/docs/data/anonymous-vs-identified-events.md) to learn more.

4.  4

    ## Run your agents

    Required

    Run your OpenAI agents as normal. PostHog automatically captures `$ai_generation` events for LLM calls and `$ai_span` events for agent execution, tool calls, and handoffs. Pass the user and conversation on the run's `RunConfig`:

    -   `group_id` groups the run's traces into a conversation — it becomes `$ai_session_id`.
    -   `trace_metadata["posthog_distinct_id"]` attributes the run's events to a user — the `distinct_id` lambda from the previous step reads it off each trace. Any other `trace_metadata` keys land on the trace as `$ai_trace_metadata`.

    The example below defines a tool and lets the agent call it.

    ```python
    from agents import Agent, Runner, RunConfig, function_tool
    @function_tool
    def get_weather(city: str) -> str:
        """Get the weather for a city."""
        return f"The weather in {city} is sunny, 72F"
    agent = Agent(
        name="Assistant",
        instructions="You are a helpful assistant.",
        tools=[get_weather],
    )
    result = Runner.run_sync(
        agent,
        "What's the weather in Paris?",
        run_config=RunConfig(
            group_id="conversation_abc",
            trace_metadata={"posthog_distinct_id": "user_123"},
        ),
    )
    print(result.final_output)
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

5.  5

    ## Multi-agent and tool usage

    Optional

    PostHog captures the full trace hierarchy for complex agent workflows, including handoffs between multiple agents.

    ```python
    from agents import Agent, Runner, function_tool
    @function_tool
    def get_weather(city: str) -> str:
        """Get the weather for a city."""
        return f"The weather in {city} is sunny, 72F"
    weather_agent = Agent(
        name="WeatherAgent",
        instructions="You help with weather queries.",
        tools=[get_weather]
    )
    triage_agent = Agent(
        name="TriageAgent",
        instructions="Route weather questions to the weather agent.",
        handoffs=[weather_agent]
    )
    result = Runner.run_sync(triage_agent, "What's the weather in San Francisco?")
    ```

    This captures:

    -   Agent spans for `TriageAgent` and `WeatherAgent`
    -   Handoff spans showing the routing between agents
    -   Tool spans for `get_weather` function calls
    -   Generation spans for all LLM calls

    As with the single-agent example above, PostHog captures every span in that list automatically. You write no extra code for the handoff itself.

6.  ## Verify traces and generations

    Recommended

    *Confirm LLM events are being sent to PostHog*

    Let's make sure LLM events are being captured and sent to PostHog. Under **AI Observability**, you should see rows of data appear in the **Traces** and **Generations** tabs.

    ![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syne_ecd0801880.png)![LLM generations in PostHog](https://res.cloudinary.com/dmukukwp6/image/upload/SCR_20250807_syjm_5baab36590.png)

    [Check for LLM events in PostHog](https://app.posthog.com/ai-observability/generations)

7.  6

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