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
    and(less($start_timestamp, toDateTime('2026-05-09 01:25:44.964556')), greater($start_timestamp, toDateTime('2026-05-08 01:25:39.965353')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
