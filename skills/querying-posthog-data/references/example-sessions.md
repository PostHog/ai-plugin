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
    and(less($start_timestamp, toDateTime('2026-10-10 11:45:40.816465')), greater($start_timestamp, toDateTime('2026-10-09 11:45:35.816880')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
