# Web traffic views by device type

```sql
SELECT
    breakdown_value AS `context.columns.breakdown_value`,
    tuple(uniq(filtered_person_id), NULL) AS `context.columns.visitors`,
    tuple(sum(filtered_pageview_count), NULL) AS `context.columns.views`,
    divide(`context.columns.visitors`.1, sum(`context.columns.visitors`.1) OVER ()) AS `context.columns.ui_fill_fraction`
FROM
    (SELECT
        any(person_id) AS filtered_person_id,
        count() AS filtered_pageview_count,
        properties.$device_type AS breakdown_value,
        session.session_id AS session_id,
        any(session.$is_bounce) AS is_bounce,
        min(session.$start_timestamp) AS start_timestamp
    FROM
        events
    WHERE
        and(or(and(greaterOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59')))), false), or(equals(event, '$pageview'), equals(event, '$screen')), 1)
    GROUP BY
        session_id,
        breakdown_value)
GROUP BY
    `context.columns.breakdown_value`
HAVING
    notEquals(`context.columns.breakdown_value`, NULL)
ORDER BY
    `context.columns.visitors` DESC,
    `context.columns.views` DESC,
    `context.columns.breakdown_value` ASC
LIMIT 50000
```
