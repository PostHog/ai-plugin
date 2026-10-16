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
    and(less($start_timestamp, toDateTime('2026-10-15 12:05:12.578040')), greater($start_timestamp, toDateTime('2026-10-14 12:05:07.578345')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
