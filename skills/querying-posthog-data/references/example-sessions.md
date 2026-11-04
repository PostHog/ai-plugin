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
    and(less($start_timestamp, toDateTime('2026-11-04 11:54:11.885154')), greater($start_timestamp, toDateTime('2026-11-03 11:54:06.885450')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
