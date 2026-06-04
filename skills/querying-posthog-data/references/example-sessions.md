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
    and(less($start_timestamp, toDateTime('2026-06-04 11:31:44.192433')), greater($start_timestamp, toDateTime('2026-06-03 11:31:39.193195')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
