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
    and(less($start_timestamp, toDateTime('2026-06-14 10:27:20.549787')), greater($start_timestamp, toDateTime('2026-06-13 10:27:15.550699')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
