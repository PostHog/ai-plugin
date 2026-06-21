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
    and(less($start_timestamp, toDateTime('2026-06-20 10:38:33.494220')), greater($start_timestamp, toDateTime('2026-06-19 10:38:28.494928')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
