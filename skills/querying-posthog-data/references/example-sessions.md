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
    and(less($start_timestamp, toDateTime('2026-09-20 08:33:39.780640')), greater($start_timestamp, toDateTime('2026-09-19 08:33:34.781001')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
