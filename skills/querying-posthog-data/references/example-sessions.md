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
    and(less($start_timestamp, toDateTime('2026-07-23 10:39:03.881155')), greater($start_timestamp, toDateTime('2026-07-22 10:38:58.881511')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
