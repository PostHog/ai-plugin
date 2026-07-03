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
    and(less($start_timestamp, toDateTime('2026-07-03 08:50:54.152679')), greater($start_timestamp, toDateTime('2026-07-02 08:50:49.153529')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
