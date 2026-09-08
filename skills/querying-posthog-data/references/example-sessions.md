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
    and(less($start_timestamp, toDateTime('2026-09-08 12:06:31.658752')), greater($start_timestamp, toDateTime('2026-09-07 12:06:26.659226')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
