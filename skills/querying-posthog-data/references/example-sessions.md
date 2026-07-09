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
    and(less($start_timestamp, toDateTime('2026-07-09 09:12:32.773152')), greater($start_timestamp, toDateTime('2026-07-08 09:12:27.773994')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
