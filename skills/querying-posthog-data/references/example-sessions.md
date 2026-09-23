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
    and(less($start_timestamp, toDateTime('2026-09-23 12:07:12.242587')), greater($start_timestamp, toDateTime('2026-09-22 12:07:07.243015')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
