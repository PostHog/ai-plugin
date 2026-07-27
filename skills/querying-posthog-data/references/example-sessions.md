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
    and(less($start_timestamp, toDateTime('2026-07-27 11:28:05.620192')), greater($start_timestamp, toDateTime('2026-07-26 11:28:00.620461')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
