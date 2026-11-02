# Patient Cohort Analysis

## 1. Objective

The objective of this analysis is to group patient cases based on the duration between their first and last recorded activities. This helps us compare short-duration, medium-duration, and long-duration cases.

## 2. Analysis Performed

Using PostgreSQL, I calculated the duration of each case and grouped cases into three categories:

- **Short:** Less than 7 days
- **Medium:** 7 days to less than 30 days
- **Long:** 30 days or more

These duration thresholds are selected for this project’s analytical purposes and are not official clinical classifications.

## 3. SQL Query

```sql
WITH case_duration AS (
    SELECT
        "case:concept:name" AS case_id,
        EXTRACT(
            EPOCH FROM (
                MAX("time:timestamp") - MIN("time:timestamp")
            )
        ) / 86400 AS duration_days
    FROM public.events
    GROUP BY "case:concept:name"
)
SELECT
    CASE
        WHEN duration_days < 7 THEN 'Short'
        WHEN duration_days < 30 THEN 'Medium'
        ELSE 'Long'
    END AS duration_group,
    COUNT(*) AS total_cases,
    ROUND(AVG(duration_days)::numeric, 2) AS avg_duration_days
FROM case_duration
GROUP BY duration_group
ORDER BY avg_duration_days;
```

## 4. Purpose of the Analysis

This analysis helps us:

- Understand how cases are distributed across different duration groups.
- Compare the average recorded duration of each group.
- Identify groups that may require further investigation.
- Support future process analysis and dashboard development.

## 5. Important Note

The calculated duration represents the time between the first and last recorded events for each case. It does not necessarily represent the patient's actual hospital stay or treatment duration.

## 6. Conclusion

Patient cohort analysis provides a simple way to compare cases based on their recorded durations. The results can support further investigation of activity sequences, waiting times, and potential process bottlenecks.

**Status:** SQL analysis prepared. Query results must be reviewed before recording specific findings.
