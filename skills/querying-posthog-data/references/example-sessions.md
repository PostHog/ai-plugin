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
    and(less($start_timestamp, toDateTime('2026-06-13 11:33:57.601548')), greater($start_timestamp, toDateTime('2026-06-12 11:33:52.602372')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
