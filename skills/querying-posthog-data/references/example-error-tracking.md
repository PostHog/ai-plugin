# Error tracking (search for a value in an error and filtering by custom properties)

```sql
SELECT
    fp_state.issue_id AS id,
    any(fp_state.issue_status) AS status,
    any(fp_state.issue_name) AS name,
    any(fp_state.issue_description) AS description,
    any(fp_state.assigned_user_id) AS assignee_user_id,
    any(fp_state.assigned_role_id) AS assignee_role_id,
    min(fp_state.first_seen) AS first_seen,
    max(ev.last_seen_fp) AS last_seen,
    argMaxMerge(ev.function_state) AS function,
    argMaxMerge(ev.source_state) AS source,
    sum(ev.occ) AS occurrences,
    uniqMerge(ev.sessions_state) AS sessions,
    uniqMerge(ev.users_state) AS users,
    sumForEach(arrayMap(i -> if(equals(ev.bin_idx, i), ev.occ, _toUInt64(0)), range(0, 20))) AS volumeRange,
    argMaxMerge(ev.library_state) AS library
FROM
    (SELECT
        cityHash64(e.properties.$exception_fingerprint) AS fp_hash,
        max(timestamp) AS last_seen_fp,
        argMaxState(properties.$exception_functions.-1, timestamp) AS function_state,
        argMaxState(properties.$exception_sources.-1, timestamp) AS source_state,
        argMaxState(properties.$lib, timestamp) AS library_state,
        least(19, intDiv(dateDiff('seconds', toDateTime(toDateTime('2026-07-07 08:02:52.944511')), timestamp), greatest(1, intDiv(dateDiff('seconds', toDateTime(toDateTime('2026-07-07 08:02:52.944511')), toDateTime(toDateTime('2026-07-08 08:02:52.945115'))), 20)))) AS bin_idx,
        count() AS occ,
        uniqState(nullIf(e.$session_id, '')) AS sessions_state,
        uniqState(coalesce(nullIf(toString(e.person_id), '00000000-0000-0000-0000-000000000000'), e.distinct_id)) AS users_state
    FROM
        events AS e
    WHERE
        and(equals(e.event, '$exception'), isNotNull(e.properties.$exception_fingerprint), true, greaterOrEquals(e.timestamp, toDateTime(toDateTime('2026-07-07 08:02:52.944511'))), lessOrEquals(e.timestamp, toDateTime(toDateTime('2026-07-08 08:02:52.945115'))), or(greater(position(lower(e.properties.$exception_types), lower('constant')), 0), greater(position(lower(e.properties.$exception_values), lower('constant')), 0), greater(position(lower(e.properties.$exception_sources), lower('constant')), 0), greater(position(lower(e.properties.$exception_functions), lower('constant')), 0), greater(position(lower(e.properties.email), lower('constant')), 0), greater(position(lower(e.person.properties.email), lower('constant')), 0)), equals(properties.tag, 'max_ai'))
    GROUP BY
        fp_hash,
        bin_idx) AS ev
    INNER JOIN error_tracking_fingerprint_issue_state AS fp_state ON equals(ev.fp_hash, fp_state.fp_hash)
WHERE
    isNotNull(fp_state.issue_id)
GROUP BY
    id
ORDER BY
    last_seen DESC
LIMIT 50000
```
