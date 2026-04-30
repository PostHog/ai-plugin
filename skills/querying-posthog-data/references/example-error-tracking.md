# Error tracking (search for a value in an error and filtering by custom properties)

```sql
SELECT
    e.issue_id AS id,
    max(timestamp) AS last_seen,
    min(timestamp) AS first_seen,
    argMax(properties.$exception_functions.-1, timestamp) AS function,
    argMax(properties.$exception_sources.-1, timestamp) AS source,
    count(DISTINCT uuid) AS occurrences,
    count(DISTINCT nullIf($session_id, '')) AS sessions,
    count(DISTINCT coalesce(nullIf(toString(person_id), '00000000-0000-0000-0000-000000000000'), distinct_id)) AS users,
    sumForEach(arrayMap(bin -> if(and(greater(timestamp, bin), lessOrEquals(dateDiff('seconds', bin, timestamp), divide(dateDiff('seconds', toDateTime(toDateTime('2025-12-09 00:00:00.000000')), toDateTime(toDateTime('2025-12-10 00:00:00.000000'))), 20))), 1, 0), arrayMap(i -> dateAdd(toDateTime(toDateTime('2025-12-09 00:00:00.000000')), toIntervalSecond(multiply(i, divide(dateDiff('seconds', toDateTime(toDateTime('2025-12-09 00:00:00.000000')), toDateTime(toDateTime('2025-12-10 00:00:00.000000'))), 20)))), range(0, 20)))) AS volumeRange,
    argMin(tuple(uuid, distinct_id, timestamp, properties), timestamp) AS first_event,
    argMax(properties.$lib, timestamp) AS library
FROM
    events AS e
WHERE
    and(equals(event, '$exception'), isNotNull(e.issue_id), equals(properties.tag, 'max_ai'), greaterOrEquals(timestamp, toDateTime(toDateTime('2025-12-09 00:00:00.000000'))), lessOrEquals(timestamp, toDateTime(toDateTime('2025-12-10 00:00:00.000000'))), or(greater(position(lower(properties.$exception_types), lower('constant')), 0), greater(position(lower(properties.$exception_values), lower('constant')), 0), greater(position(lower(properties.$exception_sources), lower('constant')), 0), greater(position(lower(properties.$exception_functions), lower('constant')), 0), greater(position(lower(properties.email), lower('constant')), 0), greater(position(lower(person.properties.email), lower('constant')), 0)))
GROUP BY
    id
ORDER BY
    last_seen DESC
LIMIT 50000
```
