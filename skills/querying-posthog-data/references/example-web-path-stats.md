# Web path stats

In this view you can validate all of the paths that were accessed in your application, regardless of when they were accessed through the lifetime of a user session.

The bounce rate indicates the percentage of users who left your page immediately after visiting without capturing any event.

```sql
SELECT
    counts.breakdown_value AS `context.columns.breakdown_value`,
    tuple(counts.visitors, counts.previous_visitors) AS `context.columns.visitors`,
    tuple(counts.views, counts.previous_views) AS `context.columns.views`,
    tuple(bounce.bounce_rate, bounce.previous_bounce_rate) AS `context.columns.bounce_rate`,
    divide(`context.columns.visitors`.1, sum(`context.columns.visitors`.1) OVER ()) AS `context.columns.ui_fill_fraction`
FROM
    (SELECT
        breakdown_value,
        uniqIf(filtered_person_id, and(greaterOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))))) AS visitors,
        uniqIf(filtered_person_id, false) AS previous_visitors,
        sumIf(filtered_pageview_count, and(greaterOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))))) AS views,
        sumIf(filtered_pageview_count, false) AS previous_views
    FROM
        (SELECT
            any(person_id) AS filtered_person_id,
            count() AS filtered_pageview_count,
            events.properties.$pathname AS breakdown_value,
            session.session_id AS session_id,
            min(session.$start_timestamp) AS start_timestamp
        FROM
            events
        WHERE
            and(or(equals(events.event, '$pageview'), equals(events.event, '$screen')), or(and(greaterOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59')))), false), 1, 1)
        GROUP BY
            session_id,
            breakdown_value)
    GROUP BY
        breakdown_value) AS counts
    LEFT JOIN (SELECT
        breakdown_value,
        avgIf(is_bounce, and(greaterOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))))) AS bounce_rate,
        avgIf(is_bounce, false) AS previous_bounce_rate
    FROM
        (SELECT
            session.$entry_pathname AS breakdown_value,
            any(session.$is_bounce) AS is_bounce,
            session.session_id AS session_id,
            min(session.$start_timestamp) AS start_timestamp
        FROM
            events
        WHERE
            and(or(equals(events.event, '$pageview'), equals(events.event, '$screen')), or(and(greaterOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59')))), false), 1, 1)
        GROUP BY
            session_id,
            breakdown_value)
    GROUP BY
        breakdown_value) AS bounce ON equals(counts.breakdown_value, bounce.breakdown_value)
WHERE
    notEquals(counts.breakdown_value, NULL)
ORDER BY
    `context.columns.visitors` DESC,
    `context.columns.views` DESC,
    `context.columns.breakdown_value` ASC
LIMIT 50000
```
