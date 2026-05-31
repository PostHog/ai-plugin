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
    and(less($start_timestamp, toDateTime('2026-05-30 16:41:46.527433')), greater($start_timestamp, toDateTime('2026-05-29 16:41:41.528168')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
