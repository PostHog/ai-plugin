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
    and(less($start_timestamp, toDateTime('2026-06-07 11:18:18.008107')), greater($start_timestamp, toDateTime('2026-06-06 11:18:13.008942')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
