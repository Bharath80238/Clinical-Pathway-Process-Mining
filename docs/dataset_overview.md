
# CareFlow — Dataset Overview

## Project and purpose

CareFlow: Clinical Pathway Process Mining explores event sequences and elapsed
time between recorded hospital activities. This overview reports measurements
from the workbook currently present in the repository; it does not infer
clinical causes or recommend care.

## Dataset inspected

- **File:** `data/raw/events.xlsx`, worksheet `Sheet1`
- **Size:** 15,214 event rows and 32 columns
- **Event-log fields:** `case:concept:name` (case ID),
  `concept:name` (activity), and `time:timestamp` (event timestamp)
- **Date range:** 2013-11-07 08:18:29 to 2015-06-05 12:25:11
- **Cases with a case ID:** 1,049
- **Distinct activities:** 16

For cleaned names, the three event-log fields are `case_concept_name`,
`concept_name`, and `time_timestamp`, respectively. Cleaning changes names
only; it does not change event values.

## Verified data-quality findings

- 24 rows have no case ID. No activity values or timestamps are missing.
- All non-missing timestamps can be parsed as datetimes.
- One exact duplicate row is present.
- Seven rows beyond the first occurrences repeat a
  case/activity/timestamp key, including the exact duplicate noted above.
  These are flagged for review and are not removed automatically.
- Many clinical attributes are event-specific and sparse. For example, the
  `Age` and clinical indicator fields each have 14,164 missing values.
  Missing attribute values should not be interpreted as negative findings.

## Activity frequencies

The most frequent activities in the full event table are:

| Activity | Events |
|---|---:|
| Leucocytes | 3,383 |
| CRP | 3,262 |
| LacticAcid | 1,466 |
| Admission NC | 1,182 |
| ER Triage | 1,053 |

## Patient journeys and elapsed times

Journeys are reconstructed by sorting complete case/activity/timestamp records
by case ID and timestamp. The 24 rows without a case ID are excluded from
journey reconstruction. The 1,049 reconstructed journeys have a median of 13
events; the mean is 14.48, with a range of 3 to 185 events. The most frequent
complete activity sequence occurs in 35 cases:
`ER Registration → ER Triage → ER Sepsis Triage`.

There are 14,141 consecutive-event intervals across these journeys. Their
median is 6.53 minutes; the mean is 3,042.76 minutes (about 50.7 hours), and
the 90th percentile is 2,880 minutes (48 hours). There are 4,441 zero-minute
intervals. The large difference between median and mean indicates a strongly
right-skewed distribution; the maximum is 600,855.3 minutes (about 417 days).

These are elapsed times between recorded event timestamps, not verified
clinical waiting times. Same-time events and unusually long gaps are retained
in the analysis; inspect them in context before interpreting bottlenecks.

## Reproducing the exploration

From the repository root, run `python -m src.member4_event_exploration`.
The module reads `data/raw/events.xlsx` by default and prints quality checks,
the most frequent activities, and waiting-time summary statistics. An
alternative CSV or Excel file can be passed as the first argument.
