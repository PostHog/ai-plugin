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
    and(less($start_timestamp, toDateTime('2026-10-05 11:49:13.050081')), greater($start_timestamp, toDateTime('2026-10-04 11:49:08.050388')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
