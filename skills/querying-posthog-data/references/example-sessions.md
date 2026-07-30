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
    and(less($start_timestamp, toDateTime('2026-07-30 11:07:53.217929')), greater($start_timestamp, toDateTime('2026-07-29 11:07:48.218256')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
