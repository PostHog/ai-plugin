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
    and(less($start_timestamp, toDateTime('2026-10-18 11:18:52.147605')), greater($start_timestamp, toDateTime('2026-10-17 11:18:47.147980')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
