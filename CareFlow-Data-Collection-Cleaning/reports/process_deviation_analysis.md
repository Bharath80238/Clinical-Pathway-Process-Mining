# Process Deviation Analysis

## 1. Objective

The objective of this analysis is to identify variations in recorded clinical workflows by comparing individual case sequences with the most frequently observed process variant.

## 2. Analysis Performed

- Identified the most common process variant.
- Calculated the number of cases following each variant.
- Measured the percentage of cases following different pathways.
- Identified cases following alternative process variants.
- Calculated the overall process deviation percentage.

## 3. SQL Concepts Used

- Common Table Expressions (CTEs)
- ROW_NUMBER()
- STRING_AGG()
- COUNT()
- CASE statements
- CROSS JOIN
- Percentage calculations

## 4. Business Importance

This analysis helps understand how consistently cases follow commonly observed activity sequences. It also highlights alternative pathways that may require further investigation.

## 5. Conclusion

Process deviation analysis provides insights into variations across recorded healthcare workflows. These findings can support further investigation of unusual activity sequences and potential process improvements.

## 6. Results

Actual numerical findings and observations will be added after executing the SQL query and reviewing the results.

**Note:** The most frequent observed variant is used as a comparison baseline, not as an officially approved clinical pathway. Different activity sequences do not automatically indicate errors or clinical problems.
