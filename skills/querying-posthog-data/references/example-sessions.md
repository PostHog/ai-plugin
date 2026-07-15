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
    and(less($start_timestamp, toDateTime('2026-07-15 06:23:48.782076')), greater($start_timestamp, toDateTime('2026-07-14 06:23:43.782420')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
