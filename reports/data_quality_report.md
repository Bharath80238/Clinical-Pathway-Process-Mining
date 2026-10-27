# CareFlow - Initial Data Quality Report
## 1. Objective
Validate the source event log before using it for SQL analysis and clinical pathway process mining. The checks cover source consistency, missing values, duplicate records, timestamps, case identifiers, and preparation of the analysis dataset.
## 2. Dataset source and attribution
- **Dataset:** Sepsis Cases Event Log
- **Dataset creator:** Felix Mannhardt
- **Publication year:** 2016
- **Dataset repository:** https://huggingface.co/datasets/kondratevakate/sepsis-cases-event-log
- **Original data repository:** https://data.4tu.nl/articles/_/12707639/1
- **DOI:** https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460
**Citation:** Mannhardt, F. (2016). *Sepsis Cases Event Log*. 4TU.ResearchData. https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460
The dataset is used for exploratory clinical event-log analysis and process mining. Consult the original repository's terms of use before redistributing the dataset or using it beyond the permitted scope.
The raw source files are retained locally and excluded from Git tracking. Refer to this report for data validation results, cleaning decisions, and analysis limitations.
## 3. Validation results
### 3.1 Source-file comparison
The Excel and Parquet files were compared after normalizing representation differences.
| Check | Excel | Parquet | Result |
|---|---:|---:|---|
| Rows | 15,214 | 15,214 | Match |
| Columns | 32 | 32 | Match |
| Column names and order | Same | Same | Match |
| Exact duplicate rows | 1 | 1 | Match |
| Missing case IDs | 0 | 0 | Match |
| Unique activity labels | 16 | 16 | Match |
| Invalid or missing timestamps | 0 | 0 | Match |
**Comparison outcome:** All values matched after normalization. Boolean values represented as numeric 0/1 in Excel and Boolean values in Parquet were normalized for comparison. Timestamps were converted to a common UTC representation. Missing values were normalized for comparison without treating the literal string `"NA"` as missing.
Timestamp range:
- **Start:** 2013-11-07 08:18:29 UTC
- **End:** 2015-06-05 12:25:11 UTC
### 3.2 Database and preparation results
The preparation pipeline was executed, and the resulting SQLite database was checked.
| Check | Verified result |
|---|---:|
| Rows loaded from source | 15,214 |
| Rows before required-field filtering | 15,214 |
| Rows after required-field filtering | 15,214 |
| Exact duplicates removed from analysis | 1 |
| Final analysis rows | 15,213 |
| Rows in `events_raw` | 15,214 |
| Rows in `events_analysis` | 15,213 |
| Exact duplicates in `events_analysis` | 0 |
| Distinct case-ID values in analysis | 1,050 |
| Missing case IDs in analysis | 0 |
| Missing activities in analysis | 0 |
| Missing timestamps in analysis | 0 |
| Rows with literal case ID `"NA"` | 24 |
The raw table retains all 15,214 source rows. The analysis table contains 15,213 rows after removing one exact duplicate. No rows were removed for missing required fields during the verified run.
The 1,050 distinct case-ID values include the literal string `"NA"`. This should not automatically be interpreted as 1,050 confirmed individual patient cases.
### 3.3 Missing laboratory measurements
The following missing-value counts were observed in the original 15,214-row source dataset.
| Field | Missing values | Approx. missing |
|---|---:|---:|
| Leucocytes | 11,853 | 77.9% |
| CRP | 12,091 | 79.5% |
| LacticAcid | 13,760 | 90.4% |
These measurements are sparsely populated. Analyses using laboratory values may therefore represent only a subset of the event log. Missing measurements must not be interpreted as normal results or zero values.
## 4. Findings
### Confirmed findings
1. The Excel and Parquet copies have the same dimensions and column order.
2. Their values match after normalization of Boolean representations, timestamps, and missing values.
3. Both source copies contain one exact duplicate row.
4. All source rows have a case-ID value, activity value, and valid timestamp under the checks performed.
5. The prepared analysis table contains 15,213 rows and no exact duplicate rows.
6. Laboratory measurements have substantial missingness, particularly LacticAcid.
7. There are 24 events whose case identifier is the literal string `"NA"`.
### Interpretation requiring further investigation
The literal `"NA"` value occurs in the Parquet source and is preserved in the Excel comparison and preparation pipeline. Its intended meaning has not been independently confirmed from the dataset documentation.
It could be a meaningful identifier or a missing identifier encoded as text. Until the source semantics are verified, the 24 events should be flagged as an unresolved case-identity issue. Treating all of them as one genuine case could distort case-duration, pathway, and waiting-time calculations.
## 5. Cleaning and preparation decisions
| Decision | Affected rows | Reason | Original preserved? |
|---|---:|---|---|
| Retain the raw source table | 15,214 retained | Preserve source records for auditability | Yes |
| Remove one exact duplicate from the analysis table | 1 removed | Prevent an exact duplicate from inflating event counts | Yes, in `events_raw` |
| Filter rows with missing required fields | 0 removed in the verified run | Required fields were populated and timestamps were valid | Yes |
| Normalize Excel and Parquet representations for comparison | No source rows removed | Avoid false differences from Boolean and timestamp types | Yes |
| Preserve literal `"NA"` case-ID values | 24 events retained | Do not assume the string means missing without source confirmation | Yes |
| Retain missing laboratory values as missing | No additional rows removed solely for these values | Avoid fabricating clinical measurements or discarding otherwise usable events | Yes |
The raw source files were not modified by the comparison process. The SQLite database contains a raw table and a separate analysis table.
## 6. Limitations and risks
1. **Unresolved case identity:** The meaning of the 24 `"NA"` case-ID events remains unconfirmed. Case-level metrics should be interpreted cautiously until this is resolved.
2. **Missing laboratory data:** High missingness can affect laboratory summaries and comparisons between cases. The available measurements may not be representative of all events.
3. **Case duration is not necessarily hospital length of stay:** A case duration calculated from the first to the last recorded event is an event-log span. It should not automatically be described as an actual hospital length of stay.
4. **Long event intervals:** Large gaps between events may reflect the structure of the event log, missing intermediate events, or case-identity issues. They should not automatically be interpreted as clinical waiting times.
5. **Duplicate policy:** One exact duplicate was excluded from the analysis table. This decision is documented and reproducible, while the raw record remains available.
6. **Source attribution:** The dataset's original publication details should be confirmed against the source documentation before final publication.
## 7. Conclusion
**Status: Ready for analysis with documented limitations.**
The source-file comparison passed, and the preparation pipeline and SQLite row counts were verified. The analysis table is suitable for continued exploratory SQL analysis and preliminary pathway analysis, provided the limitations above are carried forward.
Before finalizing clinical interpretations, verify the meaning of the literal `"NA"` case identifier, confirm the dataset attribution, and document the precise definitions used for case duration and waiting-time KPIs.
