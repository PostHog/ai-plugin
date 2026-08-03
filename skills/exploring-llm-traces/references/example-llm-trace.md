# LLM Trace query

This query might return a very large blob of JSON data. You should either only include data you need in case it's minimal or dump the results to a file and use bash commands to explore it.
This query must always have time ranges set. You can calculate the time range as -30 to +30 minutes from the source event.
The typical order of event capture for a trace is: $ai_span -> $ai_generation/$ai_embedding -> $ai_trace.
Explore `$ai\_\*`-prefixed properties to find data related to traces, generations, embeddings, spans, feedback, and metric.
Key properties of the $ai_generation event: $ai_input and $ai_output_choices.

**IMPORTANT:** The `$ai_input`, `$ai_input_state`, and `$ai_output_state` properties can be extremely large (containing full conversation histories, system prompts, or application state). When your query selects these properties, you MUST dump the results to a file and use bash commands to explore the output. Never output them directly into the conversation.

This content lives only on `posthog.ai_events` (read it directly by `trace_id`), not on `events.properties` — see [where heavy content lives](./events-and-properties.md#where-heavy-content-lives-events-vs-ai_events).

```sql
SELECT
    deduped.trace_id AS id,
    any(deduped.session_id) AS ai_session_id,
    min(deduped.timestamp) AS first_timestamp,
    max(deduped.timestamp) AS last_timestamp,
    ifNull(nullIf(argMinIf(deduped.distinct_id, deduped.timestamp, equals(deduped.event, '$ai_trace')), ''), argMin(deduped.distinct_id, deduped.timestamp)) AS first_distinct_id,
    round(if(and(equals(countIf(and(greater(deduped.latency, 0), notEquals(deduped.event, '$ai_generation'))), 0), greater(countIf(and(greater(deduped.latency, 0), equals(deduped.event, '$ai_generation'))), 0)), sumIf(deduped.latency, and(equals(deduped.event, '$ai_generation'), greater(deduped.latency, 0))), sumIf(deduped.latency, or(equals(deduped.parent_id, NULL), equals(deduped.parent_id, deduped.trace_id)))), 2) AS total_latency,
    nullIf(sumIf(deduped.input_tokens, in(deduped.event, tuple('$ai_generation', '$ai_embedding'))), 0) AS input_tokens,
    nullIf(sumIf(deduped.output_tokens, in(deduped.event, tuple('$ai_generation', '$ai_embedding'))), 0) AS output_tokens,
    nullIf(round(sumIf(deduped.input_cost_usd, in(deduped.event, tuple('$ai_generation', '$ai_embedding'))), 10), 0) AS input_cost,
    nullIf(round(sumIf(deduped.output_cost_usd, in(deduped.event, tuple('$ai_generation', '$ai_embedding'))), 10), 0) AS output_cost,
    nullIf(round(sumIf(deduped.total_cost_usd, in(deduped.event, tuple('$ai_generation', '$ai_embedding'))), 10), 0) AS total_cost,
    arrayDistinct(arraySort(x -> x.3, groupArrayIf(tuple(deduped.uuid, deduped.event, deduped.timestamp, deduped.properties, deduped.input, deduped.output, deduped.output_choices, deduped.input_state, deduped.output_state, deduped.tools), notEquals(deduped.event, '$ai_trace')))) AS events,
    argMinIf(deduped.input_state, deduped.timestamp, equals(deduped.event, '$ai_trace')) AS input_state,
    argMinIf(deduped.output_state, deduped.timestamp, equals(deduped.event, '$ai_trace')) AS output_state,
    ifNull(argMinIf(ifNull(nullIf(deduped.span_name, ''), nullIf(deduped.trace_name, '')), deduped.timestamp, equals(deduped.event, '$ai_trace')), argMin(ifNull(nullIf(deduped.span_name, ''), nullIf(deduped.trace_name, '')), deduped.timestamp)) AS trace_name
FROM
    (SELECT
        uuid,
        event,
        timestamp,
        distinct_id,
        properties,
        trace_id,
        session_id,
        parent_id,
        span_name,
        trace_name,
        latency,
        input_tokens,
        output_tokens,
        input_cost_usd,
        output_cost_usd,
        total_cost_usd,
        input,
        output,
        output_choices,
        input_state,
        output_state,
        tools
    FROM
        ai_events
    WHERE
        and(in(event, tuple('$ai_span', '$ai_generation', '$ai_embedding', '$ai_metric', '$ai_feedback', '$ai_trace')), and(greaterOrEquals(ai_events.timestamp, assumeNotNull(toDateTime('2025-12-09 23:35:41'))), lessOrEquals(ai_events.timestamp, assumeNotNull(toDateTime('2025-12-17 00:15:41'))), equals(trace_id, '79955c94-7453-488f-a84a-eabb6f084e4c')))
    LIMIT 1  BY uuid) AS deduped
GROUP BY
    deduped.trace_id
LIMIT 1
```
