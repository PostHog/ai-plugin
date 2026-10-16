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
    and(less($start_timestamp, toDateTime('2026-10-16 11:58:36.633342')), greater($start_timestamp, toDateTime('2026-10-15 11:58:31.633864')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
