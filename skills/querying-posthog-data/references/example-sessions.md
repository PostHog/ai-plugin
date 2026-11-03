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
    and(less($start_timestamp, toDateTime('2026-11-03 12:00:33.190778')), greater($start_timestamp, toDateTime('2026-11-02 12:00:28.191182')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
