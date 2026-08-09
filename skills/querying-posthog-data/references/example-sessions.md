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
    and(less($start_timestamp, toDateTime('2026-08-03 16:02:24.633563')), greater($start_timestamp, toDateTime('2026-08-02 16:02:19.633873')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
