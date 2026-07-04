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
    and(less($start_timestamp, toDateTime('2026-07-04 11:32:14.112957')), greater($start_timestamp, toDateTime('2026-07-03 11:32:09.113740')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
