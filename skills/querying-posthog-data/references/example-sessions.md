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
    and(less($start_timestamp, toDateTime('2026-05-27 21:04:05.708136')), greater($start_timestamp, toDateTime('2026-05-26 21:04:00.708886')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
