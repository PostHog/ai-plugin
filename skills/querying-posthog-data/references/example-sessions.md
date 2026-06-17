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
    and(less($start_timestamp, toDateTime('2026-06-17 04:14:46.833041')), greater($start_timestamp, toDateTime('2026-06-16 04:14:41.833806')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
