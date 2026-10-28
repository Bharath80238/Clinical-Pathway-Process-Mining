\# Week 3: Patient Pathway Bottleneck Analysis



\## 1. Objective

Analyze the clinical event log to identify long patient transitions, estimate waiting times, and summarize pathway performance.



\## 2. Dataset Overview

\- Original dataset shape: 15,214 rows and 32 columns.

\- Case identifier: `case:concept:name`

\- Activity column: `concept:name`

\- Timestamp column: `time:timestamp`

\- Rows removed during cleaning: 24

\- Negative transitions removed: 0

\- Total patients: 1,049

\- Total events after cleaning: 15,190

\- Unique activities: 16

\- Total transitions: 14,141



\## 3. Key Findings



\### Highest Average Transition Times

\- Release E → Return ER: 162,368.33 minutes (1 transition).

\- Release A → Return ER: 118,569.67 minutes (276 transitions).

\- Release C → Return ER: 98,113.62 minutes (6 transitions).

\- Release D → Return ER: 80,062.77 minutes (10 transitions).



The Release A → Return ER transition has the largest number of cases among the top four transitions. These intervals require further investigation to determine whether they represent genuine pathway delays or returns occurring long after an earlier release.



\### Overall KPIs

\- Average transition time: 3,042.76 minutes.

\- Longest transition time: 600,855.30 minutes.

\- Total transitions: 14,141.



\## 4. Data Quality Considerations

The longest transition is approximately 417 days. Such a large interval should be validated before being interpreted as a clinical bottleneck. Check event timestamps, case boundaries, and the meaning of release and return activities. Large intervals can substantially increase the average transition time.



\## 5. Outputs

\- `bottleneck\_summary.csv`

\- `week3\_kpis.csv`

\- `cleaned\_event\_log.csv`

\- `patient\_transitions.csv`

\- `bottleneck\_chart.png`



\## 6. Conclusion

Week 3 analysis identified long intervals between release and return activities, along with other diagnostic and admission transitions. The findings provide starting points for further investigation. The largest intervals should be validated before recommending process changes.



\## 7. Next Steps

\- Validate unusually long transition intervals.

\- Review the bottleneck chart and transition summary.

\- Document findings and data limitations.

\- Prepare the validated results for dashboard and reporting work.

