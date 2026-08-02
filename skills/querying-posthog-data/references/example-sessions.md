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
    and(less($start_timestamp, toDateTime('2026-08-02 11:02:03.027028')), greater($start_timestamp, toDateTime('2026-08-01 11:01:58.027368')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
