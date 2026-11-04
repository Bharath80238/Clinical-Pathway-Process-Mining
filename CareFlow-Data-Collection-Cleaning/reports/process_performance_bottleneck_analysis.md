# Process Performance and Bottleneck Analysis

## 1. Objective

The objective of this analysis is to evaluate the temporal performance of clinical processes by measuring the time gaps between consecutive activities within each case. The analysis aims to identify activities associated with long waiting intervals and recurring transitions that may require further investigation.

## 2. Business Problem

In healthcare workflows, delays between recorded activities can affect process efficiency and the timely progression of patient cases. However, a high activity count alone cannot explain where delays occur.

This analysis examines event timestamps and activity sequences to identify potentially significant waiting intervals and support evidence-based process improvement.

## 3. Analytical Approach

The analysis uses PostgreSQL features, including:

- **Common Table Expressions (CTEs):** Organize intermediate analysis steps.
- **Window Functions:** Use `LEAD()` to identify the next activity and its timestamp within each case.
- **Time Interval Calculation:** Measure elapsed time between consecutive events.
- **Percentile Analysis:** Calculate the median and 90th-percentile waiting intervals.
- **Transition Analysis:** Compare waiting times across activity transitions.

## 4. SQL Query: Activity Transition Performance

```sql
WITH ordered_events AS (
    SELECT
        "case:concept:name" AS case_id,
        "concept:name" AS current_activity,
        "time:timestamp" AS current_timestamp,

        LEAD("concept:name") OVER (
            PARTITION BY "case:concept:name"
            ORDER BY "time:timestamp"
        ) AS next_activity,

        LEAD("time:timestamp") OVER (
            PARTITION BY "case:concept:name"
            ORDER BY "time:timestamp"
        ) AS next_timestamp

    FROM public.events
),

transition_gaps AS (
    SELECT
        case_id,
        current_activity,
        next_activity,
        EXTRACT(
            EPOCH FROM (next_timestamp - current_timestamp)
        ) / 3600.0 AS waiting_hours

    FROM ordered_events
    WHERE next_timestamp IS NOT NULL
      AND next_timestamp >= current_timestamp
),

transition_metrics AS (
    SELECT
        current_activity,
        next_activity,
        COUNT(*) AS transition_count,
        ROUND(AVG(waiting_hours)::numeric, 2)
            AS avg_waiting_hours,
        ROUND(
            (PERCENTILE_CONT(0.5)
                WITHIN GROUP (ORDER BY waiting_hours))::numeric,
            2
        ) AS median_waiting_hours,
        ROUND(
            (PERCENTILE_CONT(0.9)
                WITHIN GROUP (ORDER BY waiting_hours))::numeric,
            2
        ) AS p90_waiting_hours,
        ROUND(MAX(waiting_hours)::numeric, 2)
            AS max_waiting_hours

    FROM transition_gaps
    GROUP BY current_activity, next_activity
)

SELECT *
FROM transition_metrics
WHERE transition_count >= 20
ORDER BY p90_waiting_hours DESC;
```

## 5. Key Performance Indicators

The following KPIs will be calculated from the query results:

| KPI                  | Purpose                                                                                  |
| -------------------- | ---------------------------------------------------------------------------------------- |
| Transition Count     | Measures how often an activity transition occurs                                         |
| Average Waiting Time | Measures the mean elapsed time between consecutive events                                |
| Median Waiting Time  | Represents the middle waiting-time observation                                           |
| P90 Waiting Time     | Identifies the waiting-time threshold below which approximately 90% of observations fall |
| Maximum Waiting Time | Identifies the largest observed interval for a transition                                |

## 6. Bottleneck Identification Strategy

Transitions with high P90 waiting times will be prioritized for investigation, provided they occur frequently enough to support meaningful comparisons.

The analysis will consider both waiting-time magnitude and transition frequency. A long interval observed only once should not automatically be treated as a systematic bottleneck.

## 7. Data Quality and Interpretation

- Events are ordered within each case using their recorded timestamps.
- Intervals with missing next events are excluded.
- Negative time intervals are excluded from the transition calculations.
- The minimum transition count of 20 is an analytical filtering threshold selected for this project, not an official clinical standard.
- Elapsed time between recorded events does not necessarily represent staff inactivity, patient waiting time, or a confirmed clinical delay.
- If multiple activities have identical timestamps, a deterministic secondary ordering field may be required for reliable sequence analysis.

## 8. Expected Business Value

This analysis can help stakeholders:

- Identify activity transitions associated with extended elapsed times.
- Compare typical waiting times with unusually long intervals.
- Prioritize process transitions for further investigation.
- Support the design of process performance dashboards.
- Develop evidence-based recommendations after validating the findings with clinical and operational context.

## 9. Conclusion

Transition-level performance analysis provides a deeper understanding of recorded clinical workflows than simple activity-frequency analysis. By combining sequence information, elapsed-time metrics, and percentile-based comparisons, the analysis establishes a foundation for investigating potential bottlenecks and process inefficiencies.

**Status:** SQL analysis prepared. Final findings and recommendations must be added after executing the query and reviewing the actual results.
