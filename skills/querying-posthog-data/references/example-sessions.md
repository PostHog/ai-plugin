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
    and(less($start_timestamp, toDateTime('2026-06-24 05:42:58.272368')), greater($start_timestamp, toDateTime('2026-06-23 05:42:53.273129')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
