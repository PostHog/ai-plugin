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
    and(less($start_timestamp, toDateTime('2026-09-21 12:04:03.763781')), greater($start_timestamp, toDateTime('2026-09-20 12:03:58.764107')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
