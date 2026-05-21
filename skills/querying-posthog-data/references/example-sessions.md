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
    and(less($start_timestamp, toDateTime('2026-05-19 23:15:24.163869')), greater($start_timestamp, toDateTime('2026-05-18 23:15:19.164870')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
