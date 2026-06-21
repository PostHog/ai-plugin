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
    and(less($start_timestamp, toDateTime('2026-06-21 11:20:24.480974')), greater($start_timestamp, toDateTime('2026-06-20 11:20:19.481756')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
