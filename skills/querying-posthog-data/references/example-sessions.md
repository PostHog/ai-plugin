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
    and(less($start_timestamp, toDateTime('2026-09-03 11:46:07.477242')), greater($start_timestamp, toDateTime('2026-09-02 11:46:02.477503')))
ORDER BY
    $start_timestamp DESC
LIMIT 50000
```
