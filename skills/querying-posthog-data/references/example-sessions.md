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
    and(less($start_timestamp, toDateTime('2026-10-02 11:59:50.845393')), greater($start_timestamp, toDateTime('2026-10-01 11:59:45.845703')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
