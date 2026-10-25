# CareFlow — Clinical Pathway Process Mining Findings
## 1. Project Overview
This project analyzes clinical event records to explore activity frequencies, patient-case timelines, intervals between events, repeated activities, and available clinical measurements.
The analysis uses the `events_analysis` table in `data/processed/careflow.db`. SQL queries and a Streamlit dashboard support exploratory analysis and visualization.
## 2. Dataset Summary
- Total event records: 15,213
- Distinct cases: 1,050
- Distinct activities: 16
- Average events per case: approximately 14.49
- Exact duplicate rows in the analysis table: 0 (one exact duplicate was retained in the raw table and removed during preparation).
- Invalid timestamps detected: 0
## 3. Data Quality Assessment
The inspected dataset contains no missing case IDs, activity names, or timestamps. No exact duplicate rows or invalid timestamps were detected by the validation script.
Clinical measurement fields contain substantial missing data:
| Field | Missing records | Missing percentage |
|---|---:|---:|
| Leucocytes | 11,853 | 77.9% |
| CRP | 12,090 | 79.5% |
| Lactic acid | 13,759 | 90.4% |
These missing values limit the completeness of clinical measurement analysis. Missing measurements should not be interpreted as normal results or as proof that a test was unnecessary.
**Case-ID limitation:** The literal case ID `"NA"` appears in 24 event records, spanning 10 November 2014 to 22 November 2014. The identifier's meaning has not been verified. Current SQL groups these records under one case ID, which may affect case counts, case-duration statistics, and inter-event interval calculations. These records have been retained pending clarification of the source data's identifier semantics.
## 4. Activity Frequency Analysis
The most frequent activities in the SQL results were:
| Activity | Event count |
|---|---:|
| Leucocytes | 3,382 |
| CRP | 3,262 |
| LacticAcid | 1,466 |
| Admission NC | 1,182 |
| ER Triage | 1,053 |
| ER Registration | 1,050 |
| ER Sepsis Triage | 1,049 |
| IV Antibiotics | 823 |
| IV Liquid | 753 |
| Release A | 671 |
Laboratory-related activities account for many recorded events. This indicates that measurement and testing activities are prominent in the event log. Event frequency alone does not establish clinical importance, care quality, or unnecessary testing.
## 5. Case Duration Analysis
Case duration was calculated as the time between the earliest and latest recorded event for each case.
| Metric | Result |
|---|---:|
| Number of cases | 1,050 |
| Mean duration | 683.26 hours |
| Median duration | 128.24 hours |
| 75th percentile | 431.92 hours |
| 90th percentile | 2,225.62 hours |
| Maximum duration | 10,135.77 hours |
| Cases exceeding 24 hours | 778 |
| Cases exceeding 30 days | 207 |
| Cases exceeding 90 days | 109 |
The mean is substantially greater than the median, indicating a right-skewed duration distribution with some very long case timelines.
These values represent the span of recorded events associated with each case ID. They should not automatically be treated as hospital length of stay because a case may include separated encounters or returns to care.
## 6. Inter-Event Interval Analysis
Intervals were calculated between consecutive recorded events within each case.
| Metric | Result |
|---|---:|
| Number of calculated intervals | 14,163 |
| Mean interval | 3,039.30 minutes |
| Median interval | 6.57 minutes |
| 75th percentile | 435 minutes |
| 90th percentile | 2,880 minutes |
| 95th percentile | 4,320 minutes |
| Intervals exceeding 24 hours | 2,125 |
| Intervals exceeding 7 days | 299 |
| Maximum interval | 600,855.30 minutes |
The difference between the mean and median indicates a strongly right-skewed interval distribution. The maximum interval is exceptionally large and warrants investigation.
Long intervals may reflect gaps between separate encounters, discharge followed by return, missing events, or other data characteristics. They must not be labeled clinical delays without further validation.
## 7. Repeated Activity Analysis
The repeated-activity SQL query returned 1,864 case-activity combinations with more than one occurrence.
Leucocytes and CRP appeared frequently among the repeated activities in the query results.
Repeated events may reflect routine monitoring, changes in clinical condition, or other workflow patterns. Additional clinical and temporal context is needed before concluding that repeated activities are unnecessary or inefficient.
## 8. Process Mining and Pathway Variation
The project includes event-level analysis and visualizations of activity frequency, case event counts, case durations, event intervals, and repeated activities.
A complete pathway-variation analysis should additionally identify common ordered activity sequences and compare their frequencies. This finding should be finalized only after the sequence analysis has been run and validated.
## 9. Dashboard
The Streamlit dashboard provides:
- KPI cards for event counts, case counts, activities, and median duration.
- Activity frequency and events-per-case charts.
- Case duration and inter-event interval distributions.
- Repeated-activity analysis.
- Descriptive summaries of available clinical measurements.
- Sidebar filters and filtered-record CSV export.
- A data-quality summary and interpretation limitations.
Dashboard metrics should be compared with independent SQL results before the dashboard is used for formal reporting.
## 10. Limitations
1. Clinical measurements have high rates of missing values.
2. Long case timelines may combine distinct encounters or returns to care.
3. Long inter-event intervals do not independently prove workflow bottlenecks.
4. Repeated activities do not necessarily indicate unnecessary care.
5. Descriptive associations cannot establish clinical causation.
6. Pathway variation and bottleneck conclusions require further sequence-level and clinical validation.
7. Findings apply to the available dataset and its recorded fields.
## 11. Recommendations
1. Investigate unusually long case durations and event intervals at the individual case level.
2. Determine whether case IDs represent continuous episodes or may span multiple encounters.
3. Report missingness for each clinical measurement and account for it when interpreting results.
4. Complete sequence-frequency analysis to identify common and less common pathways.
5. Validate dashboard KPIs against independent SQL calculations.
6. Describe potential bottlenecks as hypotheses until supported by event-level evidence and appropriate clinical context.
7. Document data-cleaning decisions, analytical assumptions, and reproducible execution steps.
## 12. Conclusion
The analysis covers 15,213 event records across 1,050 cases and 16 activities. It identifies frequent laboratory activities, a strongly right-skewed case-duration distribution, substantial missingness in clinical measurements, and unusually long intervals that warrant further investigation.
The dashboard provides an exploratory view of these patterns. Final conclusions about pathway efficiency or clinical bottlenecks require additional validation of encounter boundaries, event sequences, and clinical context.


## Common Clinical Pathway Sequences
### Objective
Identify the most frequent complete sequences of clinical activities across cases to understand common patient journeys.
### Method
- Sorted events by case ID, event timestamp, and activity.
- Grouped events by case ID to create ordered activity sequences.
- Counted how often each complete sequence occurred.
- Saved the 20 most frequent sequences to `reports/common_pathways.csv`.
### Key Findings
- The most frequent complete sequence was **ER Registration → ER Triage → ER Sepsis Triage → CRP → Leucocytes**, observed in 46 cases.
- The sequence **ER Registration → ER Triage → ER Sepsis Triage → CRP → LacticAcid → Leucocytes → IV Liquid → IV Antibiotics** occurred in 41 cases.
- The sequence **ER Registration → ER Triage → ER Sepsis Triage** occurred in 35 cases.
- Several frequent pathways included IV treatment, admission, repeated laboratory tests, and release activities.
### Interpretation and Limitations
The results show that cases can follow different activity sequences. Repeated laboratory tests may represent clinical monitoring rather than unnecessary repetition. Complete-sequence counts do not, by themselves, establish treatment quality, delays, or clinical outcomes.
Events were ordered by timestamp, with activity used as a tie-breaker when timestamps matched. The literal `NA` case ID remains included and is grouped as one identifier, even though it may represent an unknown case. These factors should be considered when interpreting pathway results.
### Output
The top 20 complete activity sequences are available in `reports/common_pathways.csv`.
