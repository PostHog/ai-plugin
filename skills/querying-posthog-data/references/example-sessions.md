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
    and(less($start_timestamp, toDateTime('2026-07-08 08:03:04.219548')), greater($start_timestamp, toDateTime('2026-07-07 08:02:59.220461')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
