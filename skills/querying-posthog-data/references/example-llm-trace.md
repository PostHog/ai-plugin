# LLM Trace query

This query might return a very large blob of JSON data. You should either only include data you need in case it's minimal or dump the results to a file and use bash commands to explore it.
This query must always have time ranges set. You can calculate the time range as -30 to +30 minutes from the source event.
The typical order of event capture for a trace is: $ai_span -> $ai_generation/$ai_embedding -> $ai_trace.
Explore `$ai\_\*`-prefixed properties to find data related to traces, generations, embeddings, spans, feedback, and metric.
Key properties of the $ai_generation event: $ai_input and $ai_output_choices.

**IMPORTANT:** The `$ai_input`, `$ai_input_state`, and `$ai_output_state` properties can be extremely large (containing full conversation histories, system prompts, or application state). When your query selects these properties, you MUST dump the results to a file and use bash commands to explore the output. Never output them directly into the conversation.

```sql
SELECT
    trace_id AS id,
    any(session_id) AS ai_session_id,
    min(timestamp) AS first_timestamp,
    max(timestamp) AS last_timestamp,
    ifNull(nullIf(argMinIf(distinct_id, timestamp, equals(event, '$ai_trace')), ''), argMin(distinct_id, timestamp)) AS first_distinct_id,
    round(if(and(equals(countIf(and(greater(latency, 0), notEquals(event, '$ai_generation'))), 0), greater(countIf(and(greater(latency, 0), equals(event, '$ai_generation'))), 0)), sumIf(latency, and(equals(event, '$ai_generation'), greater(latency, 0))), sumIf(latency, or(equals(parent_id, NULL), equals(parent_id, trace_id)))), 2) AS total_latency,
    nullIf(sumIf(input_tokens, in(event, tuple('$ai_generation', '$ai_embedding'))), 0) AS input_tokens,
    nullIf(sumIf(output_tokens, in(event, tuple('$ai_generation', '$ai_embedding'))), 0) AS output_tokens,
    nullIf(round(sumIf(input_cost_usd, in(event, tuple('$ai_generation', '$ai_embedding'))), 10), 0) AS input_cost,
    nullIf(round(sumIf(output_cost_usd, in(event, tuple('$ai_generation', '$ai_embedding'))), 10), 0) AS output_cost,
    nullIf(round(sumIf(total_cost_usd, in(event, tuple('$ai_generation', '$ai_embedding'))), 10), 0) AS total_cost,
    arrayDistinct(arraySort(x -> x.3, groupArrayIf(tuple(uuid, event, timestamp, properties, input, output, output_choices, input_state, output_state, tools), notEquals(event, '$ai_trace')))) AS events,
    argMinIf(input_state, timestamp, equals(event, '$ai_trace')) AS input_state,
    argMinIf(output_state, timestamp, equals(event, '$ai_trace')) AS output_state,
    ifNull(argMinIf(ifNull(nullIf(span_name, ''), nullIf(trace_name, '')), timestamp, equals(event, '$ai_trace')), argMin(ifNull(nullIf(span_name, ''), nullIf(trace_name, '')), timestamp)) AS trace_name
FROM
    ai_events
WHERE
    and(in(event, tuple('$ai_span', '$ai_generation', '$ai_embedding', '$ai_metric', '$ai_feedback', '$ai_trace')), and(greaterOrEquals(ai_events.timestamp, toDateTime('2025-12-09 23:35:41.000000')), lessOrEquals(ai_events.timestamp, toDateTime('2025-12-10 00:15:41.000000')), equals(trace_id, '79955c94-7453-488f-a84a-eabb6f084e4c')))
GROUP BY
    trace_id
LIMIT 1
```
