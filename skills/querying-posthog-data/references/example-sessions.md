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
    and(less($start_timestamp, toDateTime('2026-09-27 11:57:43.179461')), greater($start_timestamp, toDateTime('2026-09-26 11:57:38.179837')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
