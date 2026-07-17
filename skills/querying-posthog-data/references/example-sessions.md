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
    and(less($start_timestamp, toDateTime('2026-07-17 08:01:11.985593')), greater($start_timestamp, toDateTime('2026-07-16 08:01:06.985950')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
