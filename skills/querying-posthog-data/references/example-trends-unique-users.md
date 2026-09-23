# Daily unique users over the last 30 days

## Native trends insight

First, check the event with `posthog:read-data-schema`. Then call `posthog:query-trends` with this input for a native daily trends insight:

```json
{
  "kind": "TrendsQuery",
  "series": [{ "kind": "EventsNode", "event": "chat with ai", "math": "dau" }],
  "dateRange": { "date_from": "-30d" },
  "interval": "day"
}
```

The omitted `filterTestAccounts` field follows the project's "Filter out internal and test users" setting. Set it only when the request explicitly asks to override that setting.

Use the native insight controls for breakdowns or period comparisons. Do not generate SQL only to render this insight.

## SQL representation

This build-time SQL represents the same aggregation and time range. It cannot inherit the project's test-account setting. Before running or adapting it, apply the project's test-account filters when "Filter out internal and test users" is enabled.

```sql
SELECT
    arrayMap(number -> plus(toStartOfInterval(assumeNotNull(toDateTime('2025-11-10 00:00:00')), toIntervalDay(1)), toIntervalDay(number)), range(0, plus(coalesce(dateDiff('day', toStartOfInterval(assumeNotNull(toDateTime('2025-11-10 00:00:00')), toIntervalDay(1)), toStartOfInterval(assumeNotNull(toDateTime('2025-12-10 23:59:59')), toIntervalDay(1)))), 1))) AS date,
    arrayMap(_match_date -> arraySum(arraySlice(groupArray(ifNull(count, 0)), indexOf(groupArray(day_start) AS _days_for_count, _match_date) AS _index, plus(minus(arrayLastIndex(x -> equals(x, _match_date), _days_for_count), _index), 1))), date) AS total
FROM
    (SELECT
        sum(total) AS count,
        day_start
    FROM
        (SELECT
            count(DISTINCT e.person_id) AS total,
            toStartOfDay(timestamp) AS day_start
        FROM
            events AS e
        WHERE
            and(greaterOrEquals(timestamp, toStartOfInterval(assumeNotNull(toDateTime('2025-11-10 00:00:00')), toIntervalDay(1))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))), equals(event, 'chat with ai'))
        GROUP BY
            day_start)
    GROUP BY
        day_start
    ORDER BY
        day_start ASC)
ORDER BY
    arraySum(total) DESC
LIMIT 50000
```

## Simple aggregate: prefer a typed query when both fit

For "Count `chat with ai` events in the last seven days", either a typed total or SQL can answer the question.
Prefer the typed query for a new analysis when both methods preserve the requested calculation and output.
Use `posthog:query-trends` with `math: "total"`, `compareFilter.compare: true`, `trendsFilter.display: "Metric"`, `trendsFilter.metricSummary: "total"`, and the requested time bounds.
Resolve both rolling bounds to ISO 8601 timestamps and pass them as `date_from` and `date_to` when matching the SQL window below.

The SQL form remains valid when the user requests SQL or an existing SQL query already fits:

```sql
SELECT count() AS event_count
FROM events
WHERE event = 'chat with ai'
  AND timestamp >= now() - INTERVAL 7 DAY
  AND timestamp <= now()
```

Keep test-account filtering consistent. Reuse either valid form when it already fits the task. A single number does not require a method change.
