# CareFlow — Clinical Cohort Segmentation & Pathway Divergence Report

**Author:** Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project:** CareFlow: Clinical Pathway Process Mining  
**Date:** 2026-10-24 (Day 4 Milestone)  
**Assigned Branch:** `Amit-Prajapati`  

---

## 1. Executive Summary

Treating an entire hospital event log as a single homogeneous cohort obscures vital operational insights. Sepsis patients present across a wide spectrum of physiological acuity—from mild outpatients to multi-organ failure ICU cases. 

This report presents a **clinical cohort segmentation analysis** across all **1,050 patient cases**, examining how clinical pathways, transition durations, and emergency readmission hazards diverge based on:
1. **Infection Suspicion Status** (`InfectionSuspected`)
2. **Acuity Level & Critical Care Placement** (`Admission IC` vs `Admission NC`)
3. **Patient Age Demographics** (Geriatric $\ge 65$ years vs Non-Geriatric)
4. **Systemic Inflammatory Response Syndrome (SIRS)** Criteria ($\ge 2$ vs $< 2$)

---

## 2. Cohort Process Performance Summary

```
┌───────────────────────────┬────────┬───────────┬──────────────┬──────────────┬──────────────┐
│ Clinical Cohort           │ Cases  │ Share (%) │ Median Traces│ Median Stay  │ Readmission  │
│                           │        │           │ (Events)     │ (Days)       │ Rate (%)     │
├───────────────────────────┼────────┼───────────┼──────────────┼──────────────┼──────────────┤
│ All Patients              │ 1,050  │ 100.00%   │ 13 events    │  5.34 days   │ 28.00%       │
│ Infection Suspected       │   848  │  80.76%   │ 14 events    │  6.37 days   │ 31.01%       │
│ Infection Not Suspected   │   202  │  19.24%   │  6 events    │  0.10 days   │ 15.35%       │
│ ICU Admitted              │   110  │  10.48%   │ 26 events    │ 19.84 days   │ 42.73%       │
│ Normal Ward Only          │   940  │  89.52%   │ 12 events    │  4.91 days   │ 26.28%       │
│ High SIRS Risk (>=2)      │   853  │  81.24%   │ 14 events    │  6.33 days   │ 31.07%       │
│ Low SIRS Risk             │   197  │  18.76%   │  6 events    │  0.09 days   │ 14.72%       │
│ Geriatric (Age >= 65)     │   756  │  72.00%   │ 13 events    │  6.29 days   │ 31.22%       │
│ Non-Geriatric (Age < 65)  │   294  │  28.00%   │ 12 events    │  3.65 days   │ 19.73%       │
└───────────────────────────┴────────┴───────────┴──────────────┴──────────────┴──────────────┘
```

---

## 3. Key Clinical Findings & Pathway Divergence

### 3.1. Infection Suspected vs. Non-Suspected Pathway Bifurcation
- **Infection Suspected Cohort (848 cases, 80.8%):**
  - **95.87%** receive Intravenous Antibiotics (`IV Antibiotics`).
  - Median hospital stay is **6.37 days** with **14 events** per patient.
  - These patients drive the diagnostic laboratory workload (repeated daily CRP and Leucocyte testing).
- **Infection Not Suspected Cohort (202 cases, 19.2%):**
  - Only **4.95%** receive antibiotics.
  - Median length of stay is **0.10 days (~2.4 hours)**, indicating rapid emergency evaluation and same-day discharge.
  - Readmission rate is less than half that of suspected sepsis patients (**15.35% vs 31.01%**).

### 3.2. Critical Care (ICU) Trajectory & High Readmission Risk
- **ICU Cohort (110 patients, 10.5%):**
  - Patients admitted to Intensive Care (`Admission IC` via teams P, W, J, K) experience a **4x longer length of stay** (median **19.84 days** vs 4.91 days for ward patients).
  - Trace length doubles to a median of **26 events** (up to 185 events).
  - **42.73% of ICU survivors experience an unplanned emergency readmission** (`Return ER`), highlighting severe post-intensive care syndrome and vulnerability after discharge.

### 3.3. Sepsis "Golden Hour" Antibiotic SLA Comparison
The Surviving Sepsis Campaign mandates broad-spectrum intravenous antimicrobials within **1 hour (Golden Hour)** and at most **3 hours (3-hour bundle)** from triage:

| Metric | ICU Cohort ($N=110$) | Normal Ward Cohort ($N=940$) | Clinical Target |
| :--- | :---: | :---: | :---: |
| **Median Time to Antibiotics** | **45.0 minutes** | **44.0 minutes** | $< 60$ minutes |
| **Golden Hour Compliance ($\le 60$ min)** | **80.00%** | **84.81%** | $> 90\%$ |
| **3-Hour Bundle Compliance ($\le 180$ min)**| **96.67%** | **96.39%** | $100\%$ |
| **90th Percentile Delay** | **145.0 minutes** | **137.5 minutes** | $< 120$ minutes |

*Observation:* While median antibiotic timing is under 45 minutes for both groups, approximately **15–20% of patients exceed the 60-minute Golden Hour target**, primarily due to diagnostic blood-draw queuing in the Central Laboratory.

### 3.4. Age & Demographic Impact
- **72% of sepsis admissions are geriatric patients ($\ge 65$ years old)**.
- Geriatric patients exhibit a **31.22% readmission rate** compared to **19.73%** for younger patients.
- Geriatric patients require longer inpatient stabilization (median **6.29 days** vs **3.65 days**).

---

## 4. Operational Recommendations for Hospital Leadership

1. **ICU Transition Follow-up Protocol:**
   - Establish a designated post-ICU outpatient liaison to address the alarming **42.7% readmission rate**.
2. **Bedside Point-of-Care Blood Testing:**
   - Deploy point-of-care lactate and blood gas analyzers in the Emergency Department to compress the 15–20% tail of delayed antibiotic administrations into the 60-minute window.
3. **Geriatric Care Coordination:**
   - Implement dedicated geriatric discharge planning to reduce elderly readmission cycles.

---

## 5. Artifacts Generated on Day 4

- `src/cohort_analysis.py`: Clinical cohort segmentation and comparative analytics engine.
- `reports/cohort_comparison_metrics.csv`: Multi-cohort comparative metrics table.
- `reports/icu_vs_ward_comparison.json`: Detailed ICU vs Ward transition and SLA breakdown.
- `reports/figures/process_maps/cohort_comparison_barchart.png`: Comparative bar chart of length of stay and readmission rates.
- `reports/figures/process_maps/cohort_sepsis_sla_comparison.png`: Golden hour vs 3-hour bundle compliance chart.
- `reports/cohort_analysis_report.md`: Complete clinical cohort segmentation findings report.
