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
    and(less($start_timestamp, toDateTime('2026-05-22 20:25:50.007785')), greater($start_timestamp, toDateTime('2026-05-21 20:25:45.008598')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
