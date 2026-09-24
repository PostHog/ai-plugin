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
    and(less($start_timestamp, toDateTime('2026-09-24 12:03:20.411270')), greater($start_timestamp, toDateTime('2026-09-23 12:03:15.411795')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
