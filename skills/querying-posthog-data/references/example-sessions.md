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
    and(less($start_timestamp, toDateTime('2026-09-02 11:49:44.983061')), greater($start_timestamp, toDateTime('2026-09-01 11:49:39.983400')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
