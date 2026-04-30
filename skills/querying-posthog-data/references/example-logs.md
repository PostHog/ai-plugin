# Logs (filtering by severity and searching for a term)

```sql
SELECT
    uuid,
    hex(tryBase64Decode(trace_id)),
    hex(tryBase64Decode(span_id)),
    body,
    attributes,
    timestamp,
    observed_timestamp,
    severity_text,
    severity_number,
    severity_text AS level,
    resource_attributes,
    resource_fingerprint,
    instrumentation_scope,
    event_name,
    (SELECT
            min(max_observed_timestamp)
        FROM
            logs_kafka_metrics) AS live_logs_checkpoint
FROM
    logs
WHERE
    and(and(greaterOrEquals(toStartOfDay(time_bucket), toStartOfDay(assumeNotNull(toDateTime('2025-12-09 00:00:00')))), lessOrEquals(toStartOfDay(time_bucket), toStartOfDay(assumeNotNull(toDateTime('2025-12-10 00:00:00'))))), 1, greaterOrEquals(timestamp, toDateTime('2025-12-09 00:00:00.000000')), indexHint(like(lower(body), '%timeout%')), ilike(toString(body), '%timeout%'), in(severity_text, tuple('warn', 'error', 'fatal')))
ORDER BY
    timestamp DESC,
    uuid DESC
LIMIT 101
OFFSET 0
```
