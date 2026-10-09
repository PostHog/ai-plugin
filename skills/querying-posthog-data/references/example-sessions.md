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
    and(less($start_timestamp, toDateTime('2026-10-09 11:59:58.207114')), greater($start_timestamp, toDateTime('2026-10-08 11:59:53.207519')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
