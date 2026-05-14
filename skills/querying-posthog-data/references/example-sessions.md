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
    and(less($start_timestamp, toDateTime('2026-05-14 11:47:53.227730')), greater($start_timestamp, toDateTime('2026-05-13 11:47:48.228426')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
