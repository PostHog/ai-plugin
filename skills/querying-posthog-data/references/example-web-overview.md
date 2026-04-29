# Web overview (visitors, page views, sessions, session duration, bounce rate)

```sql
SELECT
    uniq(session_person_id) AS unique_users,
    NULL AS previous_unique_users,
    sum(filtered_pageview_count) AS total_filtered_pageview_count,
    NULL AS previous_total_filtered_pageview_count,
    uniq(session_id) AS unique_sessions,
    NULL AS previous_unique_sessions,
    avg(session_duration) AS avg_duration_s,
    NULL AS previous_avg_duration_s,
    avg(is_bounce) AS bounce_rate,
    NULL AS previous_bounce_rate
FROM
    (SELECT
        any(events.person_id) AS session_person_id,
        session.session_id AS session_id,
        min(session.$start_timestamp) AS start_timestamp,
        any(session.$session_duration) AS session_duration,
        countIf(or(equals(event, '$pageview'), equals(event, '$screen'))) AS filtered_pageview_count,
        any(session.$is_bounce) AS is_bounce
    FROM
        events
    WHERE
        and(notEquals(events.$session_id, NULL), or(equals(event, '$pageview'), equals(event, '$screen')), or(and(greaterOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59')))), false), 1)
    GROUP BY
        session_id
    HAVING
        or(and(greaterOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-03 00:00:00'))), lessOrEquals(start_timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59')))), false))
LIMIT 50000
```
