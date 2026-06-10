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
    and(less($start_timestamp, toDateTime('2026-06-10 07:18:32.846710')), greater($start_timestamp, toDateTime('2026-06-09 07:18:27.847409')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
