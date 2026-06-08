# Sessions (listing sessions with duration, pageviews, and bounce rate)

```sql
SELECT
    session_id,
    $start_timestamp,
    $end_timestamp,
    $session_duration,
    $pageview_count,
    $is_bounce,
    $entry_current_url,
    $end_current_url
FROM
    sessions
WHERE
    and(less($start_timestamp, toDateTime('2026-06-08 12:32:04.100378')), greater($start_timestamp, toDateTime('2026-06-07 12:31:59.101030')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
