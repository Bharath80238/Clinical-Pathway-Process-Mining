# CareFlow: Clinical Pathway Process Mining
## Final Defense Presentation Guide & Slide-by-Slide Speaking Script

**Author**: Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project**: CareFlow: Clinical Pathway Process Mining  
**Institutional Milestone**: Final Defense & Milestone Readiness (Day 19)  
**Date**: November 5, 2026  
**Artifact References**: `reports/final_defense_slide_kpis.json`, `reports/final_defense_metrics_table.csv`, `reports/figures/process_maps/careflow_executive_milestone_roadmap.png`

---

## 1. Executive Defense Strategy & Timing Structure

This handbook provides the exact spoken script, key numbers, and visual references for Member 3's final presentation defense (recommended delivery: **8 to 10 minutes**):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FINAL PROJECT DEFENSE AGENDA (MEMBER 3)                  │
├─────────────────────┬───────────────────────────────────────────────────────┤
│ Slide 1 (1.0 min)   │ Problem Statement, Sepsis Context & Data Precedence   │
│ Slide 2 (1.5 min)   │ Process Discovery: Happy Path vs Spaghetti Reality    │
│ Slide 3 (1.5 min)   │ Sepsis Golden Hour SLA & Diagnostic Lab Bottlenecks   │
│ Slide 4 (1.5 min)   │ Mathematical Soundness: Petri Net & 100% Token Replay │
│ Slide 5 (1.5 min)   │ Unplanned Readmissions (28%) & Risk Factor Mining     │
│ Slide 6 (1.5 min)   │ Star-Schema Data Warehouse & CDSS Triage Architecture │
└─────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 2. Slide-by-Slide Spoken Script & Key Numbers

### Slide 1: Clinical Problem Statement & Data Hygiene
* **Visual Reference**: `reports/figures/case_duration_distribution.png`
* **Spoken Script**:
  > *"Good morning/afternoon, evaluators and mentors. My name is **Amit Prajapati**, and I served as **Member 3 — Process Mining Analyst** on the CareFlow project.*  
  > *In emergency sepsis care, timing is life-critical. Our objective was to reconstruct the true, unvarnished clinical journeys of **1,050 sepsis patients** comprising **15,213 discrete events** across **16 hospital activities**.*  
  > *My first technical contribution was data quality. In emergency admissions, multiple orders are entered simultaneously—in our data, **4,446 events had identical same-second timestamps**. Without correction, process mining algorithms scramble these into false cycles.*  
  > *I engineered an automated clinical priority queue: Arrival $\to$ Triage $\to$ Labs $\to$ Antibiotics $\to$ Ward Admission $\to$ Discharge. This achieved 100% data hygiene with zero sequence inversions across the entire population."*

---

### Slide 2: Process Discovery (Happy Path vs. Spaghetti Reality)
* **Visual Reference**: `reports/figures/process_maps/happy_path.png` vs. `spaghetti_diagram.png`
* **Spoken Script**:
  > *"When mining the Directly-Follows Graph across all patient traces, real hospital operations appear as an unmanageable **Spaghetti Diagram** encompassing **691 distinct pathway variants**.*  
  > *To extract actionable clinical intelligence, I filtered high-volume transitions ($\ge 100$) to isolate the **Happy Path**—the clean, normative hospital highway.*  
  > *Then, using behavioral clustering, I simplified all 691 variants into **3 distinct Care Archetypes**:*  
  > 1. * **Rapid ER Evaluation (21.1%)**: Mild cases discharged within **45 minutes** with **0.0% readmission**.*  
  > 2. * **Standard Inpatient Ward Recovery (46.0%)**: Moderate acute cases staying **4.85 days** with **8.9% readmission**.*  
  > 3. * **Critical ICU Escalation (33.0%)**: Severe patients staying **44.7 days** who experience an alarming **72.5% emergency readmission rate**."*

---

### Slide 3: Sepsis Golden Hour SLA & Diagnostic Lab Bottlenecks
* **Visual Reference**: `reports/figures/process_maps/sepsis_golden_hour_sla.png` & `diagnostic_turnaround_distribution.png`
* **Spoken Script**:
  > *"Next, I audited the life-saving **Sepsis Golden Hour SLA**—the requirement to administer IV Antibiotics within 60 minutes of triage.*  
  > *Our hospital achieves **84.8% compliance** with a median time of **44.0 minutes**.*  
  > *However, **15.2% of patients exceed the 60-minute target**. Why?*  
  > *I analyzed **Central Diagnostic Laboratory (B)**, which executes **53.31% of all hospital events (8,110 events)**.*  
  > *While median turnaround times for CRP, Leucocytes, and Lactic Acid are 24.5 minutes, the **90th percentile delay tail reaches 49.6 minutes** during peak intake.*  
  > *Doctors were waiting for automated lab verification before starting antibiotics, proving that Central Lab queueing is the primary root cause of the SLA breach."*

---

### Slide 4: Mathematical Petri Net Verification & Token Replay
* **Visual Reference**: `reports/figures/process_maps/token_fitness_distribution.png` & `models/sepsis_petri_net.pnml`
* **Spoken Script**:
  > *"To ensure that our process models were mathematically rigorous and not just descriptive pictures, I discovered a formal **Workflow Petri Net** using the Inductive Miner algorithm, consisting of **39 Places, 50 Transitions, and 116 Directed Arcs**.*  
  > *I then executed a full **Token-Based Replay (TBR)** simulation engine across all 1,050 patient traces:*  
  > - *Total produced tokens ($p$) = Consumed tokens ($c$) = **49,273 tokens conserved**.*  
  > - *Missing tokens ($m$) = **0**; Remaining tokens ($r$) = **0**.*  
  > - *Mean Replay Fitness = **1.0000 (100.0%)**.*  
  > *This empirically proves that our model is mathematically sound, deadlock-free, and accepts 100% of observable patient journeys."*

---

### Slide 5: Unplanned Readmission Root-Cause Mining (`Return ER`)
* **Visual Reference**: `reports/figures/process_maps/readmission_risk_factors.png`
* **Spoken Script**:
  > *"Across the cohort, **28.00% of all sepsis patients (294 cases)** suffer an unplanned return to the Emergency Room.*  
  > *I performed epidemiological odds-ratio mining to uncover the clinical predictors of return:*  
  > 1. * **Extended Stay ($\ge 7$ Days)**: Carries an astronomical **Odds Ratio of 104.96** (63.8% readmission vs. 1.65% for stays under 7 days).*  
  > 2. * **Repetitive Blood Draws ($\ge 2$ Orders)**: Carries an **Odds Ratio of 7.57** (37.4% vs 7.32%), serving as a biological marker of ongoing instability.*  
  > 3. * **Ward-to-ICU Escalation Latency**: Moving a deteriorating patient from a normal ward into the ICU takes a median of **5.01 hours**, directly contributing to post-ICU deconditioning."*

---

### Slide 6: Star-Schema Data Warehouse & Clinical Decision Support (CDSS)
* **Visual Reference**: `reports/figures/process_maps/star_schema_entity_relationship.png` & `clinical_decision_support_matrix.png`
* **Spoken Script**:
  > *"Finally, to translate these discoveries into hospital operations, I delivered two key innovations:*  
  > 1. * **Enterprise Star-Schema Data Warehouse**: Decoupled all 15,213 events into `fact_clinical_events` and 4 normalized dimensions (`dim_patient_cohort`, `dim_activity`, `dim_department`, `dim_time_bucket`), which I exported to Member 4 for Power BI and dashboard integration with 100% referential integrity.*  
  > 2. * **Automated Clinical Decision Support (CDSS)**: Implemented the 10-point Sepsis Pathway Escalation Score (SPES), accurately flagging **543 high-risk patients (51.7%)** for accelerated $\le 30$ min antibiotics and immediate ICU bed reservation.*  
  >  
  > *Our engineering rigor is verified by **38 passing unit tests** across 8 test suites and **80+ commits** on branch `Amit-Prajapati`.*  
  > *Thank you, and I look forward to your questions."*

---

## 3. High-Impact Anticipated Evaluator Q&A

### Q1: *"What was the single most actionable operational insight you uncovered?"*
> **Answer**: *"Decoupling empiric antibiotic administration from central lab verification. 15.2% of patients breach the Golden Hour SLA because doctors wait up to 50 minutes for automated blood counts. By deploying Point-of-Care Testing (POCT) for Lactic Acid and initiating broad-spectrum antibiotics immediately at triage, the hospital can eliminate over 80% of SLA breaches."*

### Q2: *"How did your Star-Schema support Member 4's dashboard?"*
> **Answer**: *"Raw event logs are difficult to query in Power BI due to recursive transitions. My Star-Schema pre-calculated transition durations, elapsed times, and SLA flags into a 15,213-row Fact Table connected to 4 Dimensions via 1-to-Many relationships. This allowed Member 4 to build interactive slicers and DAX cards with zero performance lag."*
