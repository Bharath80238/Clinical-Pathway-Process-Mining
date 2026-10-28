# Day 11 - SQL-Based Data Analysis

## Objective

Analyze healthcare event-log data using PostgreSQL queries to understand case activity counts and event durations.

## Work Completed

- Analyzed the number of events recorded for individual cases.
- Calculated event counts for each activity.
- Identified cases with the longest recorded event durations.
- Calculated overall case-duration statistics using SQL.

## Case Duration Summary

| Metric           |      Result |
| ---------------- | ----------: |
| Total cases      |       1,050 |
| Average duration |  28.47 days |
| Maximum duration | 422.32 days |
| Minimum duration |      0 days |

## Observations

- The dataset contains 1,050 unique cases and 16 unique activities.
- Leucocytes and CRP were among the most frequently recorded activities.
- The longest observed case duration was approximately 422.32 days.
- The minimum observed duration was 0 days.

## Interpretation Note

Case duration represents the elapsed time between the first and last recorded event for each case. It should not automatically be interpreted as hospital length of stay.

## Outcome

Completed initial SQL-based case and activity analysis using PostgreSQL. The results provide a starting point for further clinical process and bottleneck analysis.
