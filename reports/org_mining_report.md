# CareFlow — Organizational Resource Mining & Departmental Handover Report

**Author:** Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project:** CareFlow: Clinical Pathway Process Mining  
**Date:** 2026-10-22 (Day 3 Milestone)  
**Assigned Branch:** `Amit-Prajapati`  

---

## 1. Executive Summary

Clinical pathway process mining is incomplete without understanding **who** performs which activities and **how care transitions across departments**. In a hospital environment, delays often originate not from the clinical tasks themselves, but at the **organizational handoff boundaries** between separate teams (e.g., Emergency Department to Laboratory, Emergency to Inpatient Wards, or Inpatient Wards to Intensive Care).

This report analyzes the organizational structure recorded in `org:group` across all **15,213 events** and **1,050 patient cases**, uncovering operational silos, workload concentration, and cross-departmental care transfer patterns.

---

## 2. Hospital Department Mapping Taxonomy

The 26 distinct organizational codes in the Sepsis dataset were mapped to their functional clinical units:

| Code (`org:group`) | Functional Hospital Unit | Event Volume | Share (%) | Patient Reach | Primary Clinical Responsibilities |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **B** | Central Diagnostic Laboratory | 8,110 | 53.31% | 1,013 (96.5%) | High-throughput blood draws (`CRP`, `Leucocytes`, `LacticAcid`). |
| **A** | Emergency Clinical Staff (Team A) | 3,462 | 22.76% | 985 (93.8%) | ER intake, sepsis screening, resuscitation fluids (`IV Liquid`, `IV Antibiotics`). |
| **C** | Emergency Triage Assessment Unit | 1,053 | 6.92% | 1,050 (100.0%) | Initial nursing triage and urgency categorization (`ER Triage`). |
| **E** | Discharge & Outpatient Administration | 782 | 5.14% | 782 (74.5%) | Discharge processing and transfer releases (`Release A` through `Release E`). |
| **?** | Emergency Readmission (Unplanned) | 294 | 1.93% | 294 (28.0%) | Post-discharge emergency department re-presentations (`Return ER`). |
| **L** | Emergency Clinical Staff (Team B) | 213 | 1.40% | 65 (6.2%) | Secondary emergency surge team. |
| **F, O, G, I, M, etc.** | General Inpatient Nursing Wards | 1,189 | 7.82% | 850+ (80.9%) | Acute medical bed management and recovery (`Admission NC`). |
| **P, W, J, K** | Intensive Care Units (ICU) | 110 | 0.72% | 108 (10.3%) | Critical organ support and intensive monitoring (`Admission IC`). |

---

## 3. Workload Concentration & Departmental Profiles

```
Workload Distribution:
┌───────────────────────────────────────────────┬────────────┬──────────────┐
│ Department                                    │ Events     │ Percentage   │
├───────────────────────────────────────────────┼────────────┼──────────────┤
│ Central Diagnostic Laboratory (B)             │ 8,110      │ 53.31%       │
│ Emergency Clinical Staff (A & L)              │ 3,675      │ 24.16%       │
│ Emergency Triage Unit (C)                     │ 1,053      │  6.92%       │
│ General Inpatient Wards (F, O, G, I, etc.)    │ 1,189      │  7.82%       │
│ Discharge Administration (E)                  │   782      │  5.14%       │
│ Emergency Readmission (?)                     │   294      │  1.93%       │
│ Intensive Care Units (P, W, J, K)             │   110      │  0.72%       │
└───────────────────────────────────────────────┴────────────┴──────────────┘
```

### Key Departmental Insights
1. **The Diagnostic Heavyweight:** Over **53% of all recorded events** are concentrated in the Central Diagnostic Laboratory (Group B). Complex sepsis inpatients undergo daily or twice-daily repetitive monitoring (averaging **8.0 events per patient**).
2. **Universal Triage Reach:** Team C evaluated **100% of the patient cohort (1,050 cases)**, showing consistent adherence to upfront clinical triage protocols.
3. **Discharge Specialization:** Team E exclusively manages patient exit pathways (`Release A–E`), ensuring formal departure accountability.

---

## 4. Cross-Departmental Handoff of Work Analysis

When analyzing transitions from event $t_i$ to $t_{i+1}$, the top inter-departmental handoffs reveal the primary care flow:

| Rank | Transferring Unit $\rightarrow$ Receiving Unit | Handoff Volume | Operational Significance |
| :---: | :--- | :---: | :--- |
| **1** | `Laboratory (B)` $\rightarrow$ `Laboratory (B)` | 6,111 | Continuous intra-lab test execution cycles. |
| **2** | `Emergency Staff (A)` $\rightarrow$ `Emergency Triage (C)` | 946 | Immediate post-registration triage handoff. |
| **3** | `Emergency Staff (A)` $\rightarrow$ `Emergency Staff (A)` | 929 | Consecutive therapeutic interventions by ER nurses. |
| **4** | `Emergency Staff (A)` $\rightarrow$ `Laboratory (B)` | 869 | ER blood draw sample dispatch to laboratory. |
| **5** | `Emergency Triage (C)` $\rightarrow$ `Emergency Staff (A)` | 863 | Post-triage clinical handoff back to physicians. |
| **6** | `Laboratory (B)` $\rightarrow$ `Emergency Staff (A)` | 686 | Diagnostic results received by ER clinicians to direct therapy. |
| **7** | `Laboratory (B)` $\rightarrow$ `Discharge Admin (E)` | 637 | Lab clearance confirming patient readiness for release. |
| **8** | `Discharge Admin (E)` $\rightarrow$ `Emergency Readmission (?)`| 293 | Unplanned patient return to ER following discharge. |

---

## 5. Organizational Friction & Operational Recommendations

1. **The Lab-ER Communication Loop:** 
   - Over 1,550 handoffs occur back and forth between ER Staff (A) and Diagnostic Lab (B). 
   - *Recommendation:* Introduce Point-of-Care (POC) bedside blood gas and lactate analyzers in the ER to compress the 30–60 minute lab dispatch turnaround time.
2. **Ward Fragmentation:**
   - Inpatient admissions are dispersed across 15 different ward codes (F, O, G, I, M, etc.). Patients frequently experience multiple internal transfers (e.g. Ward G $\rightarrow$ Ward O $\rightarrow$ Ward F), adding transition latency.
   - *Recommendation:* Implement a unified inpatient bed-management dashboard to assign patients directly to definitive wards without intermediate transfers.
3. **High Post-Discharge Readmission Friction:**
   - 293 transitions flow directly from Discharge Administration (E) into Emergency Readmission (?).
   - *Recommendation:* Establish an outpatient follow-up clinic contact within 48–72 hours for discharged sepsis patients to prevent emergency re-presentation.

---

## 6. Artifacts Generated on Day 3

- `src/org_mining.py`: Organizational resource mining and department profiling engine.
- `reports/org_department_profiles.csv`: 26-department workload, case count, and activity table.
- `reports/org_handoff_matrix.csv`: Inter-department handoff transfer network matrix.
- `reports/figures/process_maps/org_workload_distribution.png`: Departmental workload bar chart.
- `reports/figures/process_maps/org_handoff_heatmap.png`: Cross-department patient transfer heatmap.
- `reports/org_mining_report.md`: Complete organizational process mining technical report.
