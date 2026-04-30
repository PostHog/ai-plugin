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
    and(less($start_timestamp, toDateTime('2025-12-10 00:00:05.000000')), greater($start_timestamp, toDateTime('2025-12-09 00:00:00.000000')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
