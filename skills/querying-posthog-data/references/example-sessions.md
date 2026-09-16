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
    and(less($start_timestamp, toDateTime('2026-09-16 11:58:22.233302')), greater($start_timestamp, toDateTime('2026-09-15 11:58:17.233727')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
