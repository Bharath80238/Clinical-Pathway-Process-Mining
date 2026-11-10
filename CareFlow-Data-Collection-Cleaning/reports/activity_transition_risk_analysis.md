# Activity Transition Frequency and Risk Analysis

## 1. Objective

The objective of this analysis is to evaluate the frequency and time gaps between consecutive clinical activities in the CareFlow event log.

## 2. Analysis Performed

- Identified consecutive activity transitions within each case.
- Calculated the frequency of each transition.
- Measured the number of affected cases.
- Calculated average and median waiting times.
- Evaluated P90 and maximum waiting times.
- Identified transitions requiring further investigation.

## 3. SQL Concepts Used

- LEAD() window function
- Common Table Expressions (CTEs)
- COUNT() and AVG()
- PERCENTILE_CONT()
- GROUP BY and ORDER BY
- Timestamp and interval calculations

## 4. Business Importance

This analysis helps compare activity transitions based on their frequency and recorded time gaps. It can help identify transitions that deserve further investigation from a process performance perspective.

## 5. Conclusion

Activity transition analysis provides insights into the time taken between consecutive recorded clinical activities. Combining transition frequency with waiting-time metrics helps prioritize areas for further process investigation.

## 6. Results

Actual numerical findings and observations will be added after executing the SQL query and reviewing the results.

**Note:** The calculated waiting time represents the elapsed time between recorded events. It does not automatically indicate actual patient waiting time or a confirmed clinical delay. Events with identical timestamps also require reliable ordering information for accurate sequence interpretation.
