# Process Performance Comparison

## 1. Objective

The objective of this analysis is to compare the performance of different process variants in the CareFlow healthcare event log.

## 2. Analysis Performed

- Compared the number of cases following each process variant.
- Calculated the average number of activities per case.
- Measured the average recorded duration of each variant.
- Calculated median and 90th-percentile durations.
- Identified variants with longer recorded durations.

## 3. SQL Concepts Used

- Common Table Expressions (CTEs)
- STRING_AGG()
- COUNT() and AVG()
- PERCENTILE_CONT()
- GROUP BY and ORDER BY
- Timestamp calculations

## 4. Business Importance

This analysis helps compare different recorded clinical workflows based on their activity counts and durations. It can help identify process variants that deserve further investigation.

## 5. Conclusion

Process performance comparison provides a better understanding of differences between recorded patient journeys. The results can support further investigation into workflow complexity and potential delays.

## 6. Results

Actual numerical findings and observations will be added after executing the SQL query and reviewing the results.

**Note:** Duration represents the time between the first and last recorded events, not necessarily the patient's actual hospital stay. Activity ordering for identical timestamps also requires validation.
