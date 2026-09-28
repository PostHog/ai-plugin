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
    and(less($start_timestamp, toDateTime('2026-09-28 12:08:13.631266')), greater($start_timestamp, toDateTime('2026-09-27 12:08:08.631531')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
