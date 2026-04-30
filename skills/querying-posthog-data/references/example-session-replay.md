# Session replay (listing recordings with activity filters)

```sql
SELECT
    s.session_id,
    any(s.team_id),
    any(s.distinct_id),
    min(s.min_first_timestamp) AS start_time,
    max(s.max_last_timestamp) AS end_time,
    dateDiff('SECOND', start_time, end_time) AS duration,
    argMinMerge(s.first_url) AS first_url,
    sum(s.click_count) AS click_count,
    sum(s.keypress_count) AS keypress_count,
    sum(s.mouse_activity_count) AS mouse_activity_count,
    divide(sum(s.active_milliseconds), 1000) AS active_seconds,
    minus(duration, active_seconds) AS inactive_seconds,
    sum(s.console_log_count) AS console_log_count,
    sum(s.console_warn_count) AS console_warn_count,
    sum(s.console_error_count) AS console_error_count,
    max(s.retention_period_days) AS retention_period_days,
    plus(dateTrunc('DAY', start_time), toIntervalDay(coalesce(retention_period_days, 30))) AS expiry_time,
    date_diff('DAY', toDateTime('2025-12-10 00:00:00.000000'), expiry_time) AS recording_ttl,
    greaterOrEquals(max(s._timestamp), toDateTime('2025-12-09 23:55:00.000000')) AS ongoing,
    round(multiply(divide(plus(plus(plus(divide(sum(s.active_milliseconds), 1000), sum(s.click_count)), sum(s.keypress_count)), sum(s.console_error_count)), plus(plus(plus(plus(sum(s.mouse_activity_count), dateDiff('SECOND', start_time, end_time)), sum(s.console_error_count)), sum(s.console_log_count)), sum(s.console_warn_count))), 100), 2) AS activity_score
FROM
    raw_session_replay_events AS s
WHERE
    and(greaterOrEquals(s.min_first_timestamp, toDateTime('2025-12-07 00:00:00.000000')), lessOrEquals(s.min_first_timestamp, toDateTime('2025-12-10 00:00:00.000000')))
GROUP BY
    session_id
HAVING
    and(greaterOrEquals(expiry_time, toDateTime('2025-12-10 00:00:00.000000')), equals(max(s.is_deleted), 0), greater(active_seconds, 5.0))
ORDER BY
    start_time DESC,
    session_id DESC
LIMIT 50000
```
