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
    and(less($start_timestamp, toDateTime('2026-11-10 11:58:58.613201')), greater($start_timestamp, toDateTime('2026-11-09 11:58:53.613445')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
