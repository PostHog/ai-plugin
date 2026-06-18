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
    and(less($start_timestamp, toDateTime('2026-06-18 07:48:46.044728')), greater($start_timestamp, toDateTime('2026-06-17 07:48:41.045500')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
