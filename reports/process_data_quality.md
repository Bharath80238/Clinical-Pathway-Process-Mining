# CareFlow — Process Mining Data Quality & Trace Validation Report

**Author:** Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project:** CareFlow: Clinical Pathway Process Mining  
**Date:** 2026-10-21 (Day 2 Validation Milestone)  
**Assigned Branch:** `Amit-Prajapati`  

---

## 1. Executive Summary

Process mining algorithms (e.g. Directly-Follows Graphs, Petri Nets, Heuristic Mining, and Token Replay) impose strict structural requirements on event data beyond standard relational database checks. Unlike general business intelligence queries that aggregate counts, process mining relies on **strict temporal ordering**, **deterministic tie-breaking**, and **trace boundary identification**.

This report documents the validation, hygiene checks, and normalization procedures implemented in `src/validate_process_log.py` and `src/trace_metrics.py` for the Sepsis Cases Event Log.

---

## 2. Event Log Health Audit

The analysis table in `data/processed/careflow.db` was evaluated across all 15,213 event records:

| Quality Dimension | Value | Process Mining Significance |
| :--- | :---: | :--- |
| **Total Event Records** | 15,213 | 100% complete; 1 duplicate removed in preprocessing. |
| **Distinct Patient Cases** | 1,050 | Discrete clinical encounters tracked from presentation. |
| **Null / Missing Case IDs** | 0 | Every activity is strictly mapped to an identifier. |
| **Null / Unknown Activities** | 0 | All activities map to the 16 approved clinical states. |
| **Null / Invalid Timestamps** | 0 | Timestamps parsed to ISO-8601 with UTC timezone offsets. |
| **Single-Event Traces** | 0 | No trivial cases; every trace exhibits transition structure. |
| **Chronological Inversions** | 0 | Log is strictly non-decreasing ($t_i \ge t_{i-1}$) per case. |
| **Simultaneous Events ($t_i = t_{i-1}$)** | 4,446 | Resolved using deterministic clinical priority rules. |
| **Traces Starting with ER Registration** | 995 (94.76%) | Standard entry point for majority of patients. |
| **Traces Ending with Release (A–E)** | 486 (46.29%) | Formal discharge / release pathways. |
| **Traces Ending with Return ER** | 291 (27.71%) | Unplanned emergency readmission events. |

---

## 3. Resolution of Simultaneous (Same-Second) Events

### The Problem
In healthcare electronic health records (EHR), diagnostic orders (e.g., `CRP`, `Leucocytes`, and `LacticAcid`) or resuscitation orders (`IV Antibiotics` and `IV Liquid`) are routinely registered under identical timestamps (e.g. batch laboratory processing at `11:27:00`). If unaddressed, process mining engines produce arbitrary reciprocal loops ($A \rightarrow B$ and $B \rightarrow A$).

### The Solution: Clinical Precedence Hierarchy
We implemented a clinical priority tie-breaker in `src/validate_process_log.py` that sorts identical timestamps into an intra-second millisecond cascade:

1. **Intake & Triage:** `ER Registration` $\rightarrow$ `ER Triage` $\rightarrow$ `ER Sepsis Triage`
2. **Diagnostic Sampling:** `CRP` $\rightarrow$ `Leucocytes` $\rightarrow$ `LacticAcid`
3. **Medical Intervention:** `IV Liquid` $\rightarrow$ `IV Antibiotics`
4. **Inpatient Placement:** `Admission NC` $\rightarrow$ `Admission IC`
5. **Outcome & Discharge:** `Release A–E`
6. **Readmission:** `Return ER`

*Result:* Same-second simultaneous timestamps were reduced from **4,446 to 0**, producing completely deterministic directed edges.

---

## 4. Patient Encounter Lifecycle Categorization

Cases were classified into three clinical outcome states (exported in `reports/case_completeness_summary.json` and `reports/trace_level_metrics.csv`):

```
┌─────────────────────────────────┬───────────┬────────────┐
│ Lifecycle Category              │ Cases     │ Percentage │
├─────────────────────────────────┼───────────┼────────────┤
│ Completed Normal Encounter      │ 488       │ 46.48%     │
│ Readmission Encounter           │ 294       │ 28.00%     │
│ Truncated / Open Encounter      │ 268       │ 25.52%     │
├─────────────────────────────────┼───────────┼────────────┤
│ Total                           │ 1,050     │ 100.00%    │
└─────────────────────────────────┴───────────┴────────────┘
```

- **Completed Normal Encounter (46.5%):** Patients who progressed from emergency presentation to formal discharge (`Release A` through `Release E`).
- **Readmission Encounter (28.0%):** High-risk sepsis patients who re-presented to the emergency department (`Return ER`) within the observation window.
- **Truncated / Open Encounter (25.5%):** Cases whose final recorded event was an inpatient ward transfer, ICU admission, or medication without an explicit release event (censored / continuing care).

---

## 5. Trace Length & Duration Distribution

Trace metrics computed in `src/trace_metrics.py`:

### Trace Length (Events per Case)
- **Minimum:** 3 events
- **25th Percentile:** 9 events
- **Median:** 13 events
- **Mean:** 14.49 events ($\sigma = 11.47$)
- **75th Percentile:** 16 events
- **90th Percentile:** 23 events
- **95th Percentile:** 30 events
- **Maximum:** 185 events (complex, multi-week ICU cases with extensive lab monitoring)

### Case Duration
- **Minimum:** 0.0 days (same-day discharge)
- **Median:** 5.34 days
- **Mean:** 28.47 days ($\sigma = 60.54$)
- **90th Percentile:** 92.73 days
- **Maximum:** 422.32 days (long-term readmission cycle)

---

## 6. Artifacts & Deliverables Generated Today

1. `src/validate_process_log.py`: Automated diagnostic and tie-breaker script.
2. `src/trace_metrics.py`: Trace length, case duration, and variance calculation module.
3. `tests/test_process_validation.py`: 4 automated unit tests verifying pipeline stability.
4. `reports/trace_level_metrics.csv`: Patient-level metrics table for 1,050 cases.
5. `reports/trace_summary_statistics.json`: Statistical distribution export.
6. `reports/case_completeness_summary.json`: Encounter classification summary.
7. `reports/figures/process_maps/trace_duration_vs_events.png`: Multi-panel visualization of trace length and duration distributions.
