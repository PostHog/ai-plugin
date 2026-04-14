# Event taxonomy (properties of an event, with sample values)

All properties for a given event, with up to 5 sample values each:

```sql
SELECT
    key,
    arraySlice(arrayDistinct(groupArray(value)), 1, 5) AS values,
    count(DISTINCT value) AS total_count
FROM
    (SELECT
        JSONExtractKeysAndValues(properties, 'String') AS kv
    FROM
        events
    WHERE
        and(greaterOrEquals(timestamp, minus(now(), toIntervalDay(30))), equals(event, '$pageview'))
    ORDER BY
        timestamp DESC
    LIMIT 100)
ARRAY JOIN (kv).1 AS key, (kv).2 AS value
WHERE
    not(match(key, '(\\$set|\\$time|\\$set_once|\\$sent_at|distinct_id|\\$ip|\\$feature\\/|\\$feature_enrollment\\/|\\$feature_interaction\\/|\\$product_tour|__|survey_dismiss|survey_responded|phjs|partial_filter_chosen|changed_action|window-id|changed_event|partial_filter)'))
GROUP BY
    key
ORDER BY
    total_count DESC
LIMIT 50000
```

Specific properties only (faster, skips the omit filter):

```sql
SELECT
    key,
    arraySlice(arrayDistinct(groupArray(value)), 1, 5) AS values,
    count(DISTINCT value) AS total_count
FROM
    (SELECT
        key,
        value,
        count() AS count
    FROM
        (SELECT
            [tuple('$browser', JSONExtractString(properties, '$browser')), tuple('$os', JSONExtractString(properties, '$os'))] AS kv
        FROM
            events
        WHERE
            and(greaterOrEquals(timestamp, minus(now(), toIntervalDay(30))), equals(event, '$pageview'), or(notEquals(JSONExtractString(properties, '$browser'), ''), notEquals(JSONExtractString(properties, '$os'), ''))))
    ARRAY JOIN (kv).1 AS key, (kv).2 AS value
    WHERE
        notEquals(value, '')
    GROUP BY
        key,
        value
    ORDER BY
        count DESC)
GROUP BY
    key
ORDER BY
    total_count DESC,
    key ASC
LIMIT 50000
```
