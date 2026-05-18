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
    and(less($start_timestamp, toDateTime('2026-05-15 16:37:01.205420')), greater($start_timestamp, toDateTime('2026-05-14 16:36:56.206003')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
