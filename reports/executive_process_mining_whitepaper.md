# CareFlow: Clinical Pathway Process Mining & Hospital Operational Intelligence
## Executive Whitepaper & Strategic Clinical Decision Architecture

**Author**: Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project**: CareFlow: Clinical Pathway Process Mining  
**Institutional Milestone**: Executive Synthesis & Advanced Decision Architecture (Day 18)  
**Date**: November 4, 2026  
**Artifact References**: `reports/careflow_process_mining_master_summary.json`, `reports/models/sepsis_petri_net.pnml`, `reports/star_schema/`

---

## 1. Executive Abstract

Hospital-acquired sepsis remains one of the leading causes of inpatient mortality and resource strain across global healthcare networks. While contemporary Hospital Information Systems (HIS) collect granular event timestamps, conventional descriptive Business Intelligence tools fail to capture the sequential causality, operational rework, and cross-departmental queueing dynamics that govern real-world patient outcomes.

In this study, formal **Process Mining techniques** were deployed across a cohort of **1,050 sepsis patients** comprising **15,213 clinical events** and **16 discrete care activities**. Through the integration of Directly-Follows Graph (DFG) mining, Inductive Petri Net discovery, Token-Based Replay (TBR) simulation, and Dimensional Data Warehousing, this investigation reconstructs the unvarnished reality of clinical execution.

### Key Empirical Findings
- **Sepsis Golden Hour Compliance**: **84.8%** of septic patients receive IV Antibiotics within the 60-minute therapeutic window (median: **44.0 minutes**). However, **15.2% exceed this threshold**.
- **The Diagnostic Lab Bottleneck**: **Central Diagnostic Laboratory (B)** executes **53.31% of all hospital events (8,110 events)**. The 90th percentile turnaround time for critical biomarkers (`CRP`, `Leucocytes`, `LacticAcid`) reaches **49.6 minutes**, directly contributing to the antibiotic administration delay.
- **Structural Model Soundness**: Token-Based Replay verified **100.0% structural language acceptance** across all 1,050 patient traces ($p = c = 49,273; m = 0, r = 0$) on a 39-place, 50-transition Workflow Net.
- **Unplanned Readmission Hazard**: **28.00% of all sepsis patients (294 cases)** suffer an emergency return (`Return ER`). Patients hospitalized for $\ge 7$ days experience an **Odds Ratio of 104.96** for readmission.

---

## 2. Process Architecture & Pipeline Engineering

### 2.1. Deterministic Timestamp Tie-Breaking
Emergency departments frequently record multiple concurrent entries. Across the cohort, **4,446 events possessed identical same-second timestamps**. To prevent synthetic cycles and causal inversions, an automated clinical precedence engine was established:

$$\text{Intake} \longrightarrow \text{Triage} \longrightarrow \text{Diagnostics} \longrightarrow \text{Therapeutics} \longrightarrow \text{Admission} \longrightarrow \text{Discharge}$$

This pipeline achieved 100% data hygiene, resolving all timestamp inversions while preserving raw clinical validity.

### 2.2. Complexity Reduction: The 3 Care Archetypes
Unfiltered mining generated a dense **Spaghetti Diagram** encompassing **691 distinct trace variants**. To make operational management feasible, patients were clustered into three distinct Care Archetypes:
1. **Archetype 1: Rapid ER Evaluation (21.05%, 221 cases)**: Median stay 45 minutes; 0.0% readmission.
2. **Archetype 2: Standard Inpatient Ward Acute Recovery (46.00%, 483 cases)**: Median stay 4.85 days; 8.9% readmission.
3. **Archetype 3: Critical ICU Escalation & Readmission (32.95%, 346 cases)**: Median stay 44.7 days; **72.5% readmission rate**.

---

## 3. Bottleneck Quantification & Laboratory Queueing

### 3.1. Diagnostic Turnaround Time (TAT) Analysis
To resolve the root cause of the 15.2% Golden Hour breaches, turnaround time from ER triage to verified laboratory availability was quantified:

| Biomarker Assay | Tested Cohort | Total Draws | Median TAT | 90th %ile TAT | Repeat Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **C-Reactive Protein (`CRP`)** | 1,007 | 3,262 | 24.30 min | 46.60 min | 68.72% |
| **Leucocytes Count (`Leucocytes`)** | 1,012 | 3,382 | 24.41 min | 46.64 min | 66.90% |
| **Lactic Acid (`LacticAcid`)** | 860 | 1,466 | 24.97 min | 49.55 min | 20.00% |

Physicians demonstrated a propensity to await automated laboratory verification before initiating broad-spectrum antimicrobial infusions. During peak intake periods, the 49.6-minute laboratory queue pushed total time-to-antibiotics past the 60-minute SLA boundary.

### 3.2. Inter-Ward Patient Transfer Latencies
- **ER to Normal Care Ward**: Median 1.60 hours ($p_{90}: 4.57$ hours).
- **Ward to ICU Escalation**: Median **5.01 hours** ($p_{90}: 13.82$ hours). Delays in recognizing clinical deterioration on general wards contributed to late intensive care transfers.

---

## 4. Formal Verification: Inductive Petri Net & Token Replay

To ensure mathematical validity, the process was modeled as a formal **Workflow Petri Net (WF-net)** using PM4Py's Inductive Miner:
- **Structural Properties**: 39 Places ($P$), 50 Transitions ($T$, 16 visible, 34 silent $\tau$), 116 Directed Arcs ($F$).
- **Token Accounting Invariants**:
  $$p = c = 49,273 \quad \land \quad m = r = 0 \implies \text{Fitness} = 1.000$$
This empirical proof confirms that the discovered model is strictly sound, deadlock-free, and terminates cleanly at the sink place across all 1,050 clinical traces.

---

## 5. Readmission Root-Cause Mining (`Return ER`)

Statistical odds ratios identified the primary risk factors driving the 28.0% hospital return rate:
1. **Extended Stay ($\ge 7$ Days)**: $OR = 104.96$ ($63.82\%$ readmitted vs $1.65\%$ unexposed).
2. **Repetitive Lab Testing ($\ge 2$ Draws)**: $OR = 7.57$ ($37.40\%$ readmitted vs $7.32\%$ unexposed).
3. **SIRS Criteria $\ge 2$**: $OR = 2.61$ ($31.07\%$ readmitted vs $14.72\%$ unexposed).
4. **ICU Admission**: $OR = 2.09$ ($42.73\%$ readmitted vs $26.28\%$ unexposed).

---

## 6. Sepsis Clinical Decision Support System (CDSS) & Action Plan

To translate process mining discoveries into active clinical practice, an automated decision engine was constructed (`src/clinical_decision_support.py`):

### 6.1. Sepsis Pathway Escalation Score (SPES)
A 10-point multi-factorial scoring algorithm evaluating:
- Infection suspicion (+2), SIRS $\ge 2$ (+2), Organ dysfunction (+3), Age $\ge 65$ (+1), Repeat lab instability (+1), ICU requirement (+1).

### 6.2. Stratification & Recommended Care Pathways
- **Low Risk (Score 0–2, 18.29%, 192 pts)**: ER Observation unit; outpatient discharge evaluation within 4–6 hours.
- **Moderate Risk (Score 3–5, 30.00%, 315 pts)**: Mandatory 60-min Golden Hour antibiotics; Normal Care Ward admission; serial 24h CRP monitoring.
- **Critical Risk (Score 6–10, 51.71%, 543 pts)**: Accelerated 30-min Golden Hour antibiotics; immediate fluid resuscitation; pre-emptive ICU consult and telemetry bed allocation.

### 6.3. Institutional Recommendations
1. **Decouple Empiric Antibiotics from Lab Verification**: Update ER protocol to authorize immediate antibiotic delivery upon clinical suspicion, prior to automated lab counters.
2. **Bedside Point-of-Care Testing (POCT) for Lactic Acid**: Deploy handheld analyzers in triage to compress turnaround from 25 min to $< 5$ min.
3. **Post-ICU Transitional Telehealth Protocol**: Implement mandatory 48-hour phone triage for discharged ICU patients to mitigate the 72.5% readmission rate.
4. **Dimensional Data Warehouse Hand-off**: The complete 5-table Star-Schema (`reports/star_schema/`) is finalized to support Member 4's executive dashboard deployment.
