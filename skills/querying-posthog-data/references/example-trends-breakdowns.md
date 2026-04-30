# Trends (total event count, specific week)

```sql
SELECT
    groupArray(1)(date)[1] AS date,
    arrayFold((acc, x) -> arrayMap(i -> plus(acc[i], x[i]), range(1, plus(length(date), 1))), groupArray(ifNull(total, 0)), arrayWithConstant(length(date), reinterpretAsFloat64(0))) AS total,
    arrayMap(i -> if(ifNull(greaterOrEquals(row_number, 25), 0), '$$_posthog_breakdown_other_$$', i), breakdown_value) AS breakdown_value
FROM
    (SELECT
        arrayMap(number -> plus(toStartOfInterval(assumeNotNull(toDateTime('2025-12-03 00:00:00')), toIntervalDay(1)), toIntervalDay(number)), range(0, plus(coalesce(dateDiff('day', toStartOfInterval(assumeNotNull(toDateTime('2025-12-03 00:00:00')), toIntervalDay(1)), toStartOfInterval(assumeNotNull(toDateTime('2025-12-10 23:59:59')), toIntervalDay(1)))), 1))) AS date,
        arrayMap(_match_date -> arraySum(arraySlice(groupArray(ifNull(count, 0)), indexOf(groupArray(day_start) AS _days_for_count, _match_date) AS _index, plus(minus(arrayLastIndex(x -> equals(x, _match_date), _days_for_count), _index), 1))), date) AS total,
        breakdown_value AS breakdown_value,
        rowNumberInAllBlocks() AS row_number
    FROM
        (WITH
            min_max AS (SELECT
                    count() AS total,
                    toStartOfDay(timestamp) AS day_start,
                    ifNull(nullIf(left(toString(properties.$browser), 400), ''), '$$_posthog_breakdown_null_$$') AS breakdown_value_1,
                    properties.$browser_version AS breakdown_value_2
                FROM
                    events AS e
                WHERE
                    and(greaterOrEquals(timestamp, toStartOfInterval(assumeNotNull(toDateTime('2025-12-03 00:00:00')), toIntervalDay(1))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))), equals(event, '$pageview'))
                GROUP BY
                    day_start,
                    breakdown_value_1,
                    breakdown_value_2)
        SELECT
            sum(total) AS count,
            day_start,
            [breakdown_value_1, if(empty(arrayFilter(x -> and(lessOrEquals(x[1], breakdown_value_2), less(breakdown_value_2, x[2])), buckets[1])[1]), '$$_posthog_breakdown_null_$$', ifNull(nullIf(left(toString(arrayFilter(x -> and(lessOrEquals(x[1], breakdown_value_2), less(breakdown_value_2, x[2])), buckets[1])[1]), 400), ''), '$$_posthog_breakdown_null_$$'))] AS breakdown_value
        FROM
            (SELECT
                count() AS total,
                toStartOfDay(timestamp) AS day_start,
                ifNull(nullIf(left(toString(properties.$browser), 400), ''), '$$_posthog_breakdown_null_$$') AS breakdown_value_1,
                properties.$browser_version AS breakdown_value_2,
                (SELECT
                        [max(breakdown_value_2)]
                    FROM
                        min_max) AS max_nums,
                (SELECT
                        [min(breakdown_value_2)]
                    FROM
                        min_max) AS min_nums,
                arrayMap((max_num, min_num) -> minus(max_num, min_num), arrayZip(max_nums, min_nums)) AS diff,
                [10] AS bins,
                arrayMap(i -> arrayMap(x -> [plus(multiply(divide(diff[i], bins[i]), x), min_nums[i]), plus(plus(multiply(divide(diff[i], bins[i]), plus(x, 1)), min_nums[i]), if(equals(plus(x, 1), bins[i]), 0.01, 0))], range(bins[i])), range(1, 2)) AS buckets
            FROM
                events AS e
            WHERE
                and(greaterOrEquals(timestamp, toStartOfInterval(assumeNotNull(toDateTime('2025-12-03 00:00:00')), toIntervalDay(1))), lessOrEquals(timestamp, assumeNotNull(toDateTime('2025-12-10 23:59:59'))), equals(event, '$pageview'))
            GROUP BY
                day_start,
                breakdown_value_1,
                breakdown_value_2)
        GROUP BY
            day_start,
            breakdown_value
        ORDER BY
            day_start ASC,
            breakdown_value ASC)
    GROUP BY
        breakdown_value
    ORDER BY
        if(has(breakdown_value, '$$_posthog_breakdown_other_$$'), 2, if(has(breakdown_value, '$$_posthog_breakdown_null_$$'), 1, 0)) ASC,
        arraySum(total) DESC,
        breakdown_value ASC)
WHERE
    arrayExists(x -> isNotNull(x), breakdown_value)
GROUP BY
    breakdown_value
ORDER BY
    if(has(breakdown_value, '$$_posthog_breakdown_other_$$'), 2, if(has(breakdown_value, '$$_posthog_breakdown_null_$$'), 1, 0)) ASC,
    arraySum(total) DESC,
    breakdown_value ASC
LIMIT 50000
```
