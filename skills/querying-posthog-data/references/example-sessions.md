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
    and(less($start_timestamp, toDateTime('2026-09-17 11:59:09.948151')), greater($start_timestamp, toDateTime('2026-09-16 11:59:04.948499')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
