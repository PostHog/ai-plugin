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
    and(less($start_timestamp, toDateTime('2026-09-06 09:19:21.250701')), greater($start_timestamp, toDateTime('2026-09-05 09:19:16.251095')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
