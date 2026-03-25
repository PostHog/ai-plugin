# Instructor LLM analytics installation - Docs

1.  1

    ## Install the PostHog SDK

    Required

    Setting up analytics starts with installing the PostHog SDK for your language. LLM analytics works best with our Python and Node SDKs.

    PostHog AI

    ### Python

    ```bash
    pip install posthog
    ```

    ### Node

    ```bash
    npm install @posthog/ai posthog-node
    ```

2.  2

    ## Install Instructor and OpenAI SDKs

    Required

    Install Instructor and the OpenAI SDK. PostHog instruments your LLM calls by wrapping the OpenAI client, which Instructor uses under the hood.

    PostHog AI

    ### Python

    ```bash
    pip install instructor openai
    ```

    ### Node

    ```bash
    npm install @instructor-ai/instructor openai zod@3
    ```

3.  3

    ## Initialize PostHog and Instructor

    Required

    Initialize PostHog with your project token and host from [your project settings](https://app.posthog.com/settings/project), then create a PostHog OpenAI wrapper and pass it to Instructor.

    PostHog AI

    ### Python

    ```python
    import instructor
    from pydantic import BaseModel
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
    client = instructor.from_openai(openai_client)
    ```

    ### Node

    ```typescript
    import Instructor from '@instructor-ai/instructor'
    import { OpenAI } from '@posthog/ai'
    import { PostHog } from 'posthog-node'
    import { z } from 'zod'
    const phClient = new PostHog(
      '<ph_project_token>',
      { host: 'https://us.i.posthog.com' }
    );
    const openai = new OpenAI({
      apiKey: 'your_openai_api_key',
      posthog: phClient,
    });
    const client = Instructor({ client: openai, mode: 'TOOLS' })
    ```

    **How this works**

    PostHog's `OpenAI` wrapper is a proper subclass of `openai.OpenAI`, so it works directly with `instructor.from_openai()`. PostHog captures `$ai_generation` events automatically without proxying your calls.

4.  4

    ## Use Instructor with structured outputs

    Required

    Now use Instructor to extract structured data from LLM responses. PostHog automatically captures an `$ai_generation` event for each call.

    PostHog AI

    ### Python

    ```python
    class UserInfo(BaseModel):
        name: str
        age: int
    user = client.chat.completions.create(
        model="gpt-5-mini",
        response_model=UserInfo,
        messages=[
            {"role": "user", "content": "John Doe is 30 years old."}
        ],
        posthog_distinct_id="user_123",
        posthog_trace_id="trace_123",
        posthog_properties={"conversation_id": "abc123"},
    )
    print(f"{user.name} is {user.age} years old")
    ```

    ### Node

    ```typescript
    const UserInfo = z.object({
      name: z.string(),
      age: z.number(),
    })
    const user = await client.chat.completions.create({
      model: 'gpt-5-mini',
      response_model: { schema: UserInfo, name: 'UserInfo' },
      messages: [
        { role: 'user', content: 'John Doe is 30 years old.' }
      ],
      posthogDistinctId: 'user_123',
      posthogTraceId: 'trace_123',
      posthogProperties: { conversation_id: 'abc123' },
    })
    console.log(`${user.name} is ${user.age} years old`)
    phClient.shutdown()
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