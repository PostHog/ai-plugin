# Person property taxonomy (sample values for person properties)

Sample values for specific person properties:

```sql
SELECT
    groupArray(5)(prop),
    count(),
    prop_index
FROM
    (SELECT
        DISTINCT prop_index,
        toString(prop_value) AS prop
    FROM
        persons
    ARRAY JOIN arrayEnumerate([toString(properties.email), toString(properties.$initial_browser)]) AS prop_index, [toString(properties.email), toString(properties.$initial_browser)] AS prop_value
    WHERE
        isNotNull(prop_value)
    ORDER BY
        created_at DESC)
GROUP BY
    prop_index
ORDER BY
    prop_index ASC
LIMIT 50000
```
