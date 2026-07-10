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
    and(less($start_timestamp, toDateTime('2026-07-10 09:34:30.705829')), greater($start_timestamp, toDateTime('2026-07-09 09:34:25.706177')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
