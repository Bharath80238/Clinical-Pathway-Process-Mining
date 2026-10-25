# CareFlow — Mid-Project Review Milestone & Algorithm Verification Report

**Author:** Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project:** CareFlow: Clinical Pathway Process Mining (Infotact Solutions)  
**Evaluation Stage:** MID Review Milestone (Weeks 1–2 Completion)  
**Date:** 2026-10-25  
**Assigned Branch:** `Amit-Prajapati`  

---

## 1. Executive Summary & Milestone Defense

As Member 3 (Process Mining Analyst), my primary objective for the **Mid-Project Review Milestone** was to reconstruct the true, unvarnished clinical reality of patient journeys through the hospital, identify hidden operational bottlenecks, quantify clinical guideline conformance, and prove the mathematical soundness of all underlying process mining algorithms.

Over Weeks 1 and 2, I developed **11 specialized analytical scripts**, generated **11 publication-grade process diagrams**, exported **10 structured data deliverables**, integrated a **3-tab interactive Streamlit dashboard UI**, and established an **automated unit testing suite** with 100% passing test coverage.

---

## 2. Proof of Algorithmic Soundness & Mathematical Rigor

In accordance with the project assignment and curriculum expectations, each process mining model was algorithmically validated:

### 2.1. Directly-Follows Graph (DFG) Mining
- **Implementation:** `src/process_mining.py`
- **Verification:** Evaluated across all 15,213 chronological events.
- **Result:** Successfully mapped all 16 clinical activities. Identified dominant transitions ($\ge 100$) for the **Happy Path** and the unfiltered transition network for the **Spaghetti Diagram**.

### 2.2. Formal Petri Net Discovery (Inductive Miner)
- **Implementation:** `src/petri_net_mining.py`
- **Format:** Exported to standard XML format in `reports/models/sepsis_petri_net.pnml`.
- **Structural Properties:**
  - **Places ($P$):** 39 places
  - **Transitions ($T$):** 50 transitions (16 clinical activities + 34 silent routing $\tau$)
  - **Directed Arcs ($F$):** 116 arcs
  - **Initial Marking:** `['source']`
  - **Final Marking:** `['sink']`
- **Soundness Verification:** Proved mathematically sound as a Workflow Net (WF-net); deadlock-free and terminating at the sink marking.

### 2.3. Heuristic Causal Net Mining (Noise & Dependency Thresholding)
- **Implementation:** `src/heuristic_mining.py`
- **Causal Metric:**
  $$D(a, b) = \frac{|a \rightarrow b| - |b \rightarrow a|}{|a \rightarrow b| + |b \rightarrow a| + 1} \in [-1.0, 1.0]$$
- **Verification:** Exported full matrix to `reports/heuristic_dependency_matrix.csv`.
- **Finding:** Filtered out infrequent noise edges ($D(a, b) \ge 0.5$, $n \ge 50$) to reveal core causal backbones (e.g. `ER Sepsis Triage` $\rightarrow$ `CRP` with $D=0.998$, `IV Antibiotics` $\rightarrow$ `Admission NC` with $D=0.990$).

### 2.4. Trace Variant Clustering (Care Archetypes)
- **Implementation:** `src/variant_clustering.py`
- **Methodology:** Reduced **691 unmanageable trace variants** into **3 actionable Clinical Care Archetypes**:
  1. *Archetype 1: Rapid ER Evaluation & Outpatient Release* (21.05%, 221 cases, median stay 45 min, 0.0% readmission).
  2. *Archetype 2: Standard Inpatient Ward Acute Recovery* (46.00%, 483 cases, median stay 4.85 days, 8.9% readmission).
  3. *Archetype 3: Critical ICU Escalation & Readmission* (32.95%, 346 cases, median stay 44.7 days, 72.5% readmission).

---

## 3. Core Clinical Findings for Hospital Stakeholders

```
┌───────────────────────────────────────────────┬─────────────────────────────┐
│ Key Performance Indicator (KPI)               │ Observed Empirical Finding  │
├───────────────────────────────────────────────┼─────────────────────────────┤
│ Total Analyzed Patient Cohort                 │ 1,050 discrete cases        │
│ Total Recorded Clinical Events                │ 15,213 events               │
│ Overall Pathway Guideline Conformance Score   │ 94.6% average hospital score│
│ Sepsis Golden Hour Antibiotic SLA (<=60 min)  │ 84.8% compliance            │
│ Surviving Sepsis 3-Hour Bundle Mandate        │ 96.5% compliance            │
│ Median Emergency to Antibiotics Latency       │ 44.0 minutes                │
│ Central Diagnostic Lab (Group B) Event Share  │ 53.31% (8,110 events)       │
│ Unplanned Emergency Readmissions (Return ER)  │ 294 patients (28.00%)       │
│ ICU Patient Readmission Hazard Rate           │ 42.73% of ICU survivors     │
└───────────────────────────────────────────────┴─────────────────────────────┘
```

---

## 4. Complete Deliverable Inventory (Mid-Review Package)

### Analytics Code Modules (`src/`)
1. `src/prepare_data.py`: Raw multi-format ingestion and database enrichment.
2. `src/process_mining.py`: Core PM4Py DFG miner, Happy Path & Spaghetti generator.
3. `src/validate_process_log.py`: Log health auditor and simultaneous event tie-breaker.
4. `src/trace_metrics.py`: Trace length, case duration, and variance calculator.
5. `src/bottleneck_analysis.py`: Node-to-node transition matrix and Golden Hour SLA analyzer.
6. `src/rework_analysis.py`: Diagnostic testing repeat loops and readmission detector.
7. `src/conformance_checking.py`: Normative sepsis pathway guideline conformance auditor.
8. `src/org_mining.py`: Departmental mapping and cross-department handoff matrix.
9. `src/cohort_analysis.py`: Infection, ICU, SIRS, and Geriatric cohort segmentation.
10. `src/pathway_filter.py`: Dynamic clinical slicing and multi-criteria trace filtering.
11. `src/petri_net_mining.py`: Inductive Miner Petri Net discoverer and PNML exporter.
12. `src/variant_clustering.py`: 3-archetype behavioral clustering engine.
13. `src/export_master_summary.py`: Master executive JSON data bundle generator.
14. `app.py`: Integrated Streamlit dashboard with 3 dedicated process mining tabs.

### Automated Unit Test Suites (`tests/`)
1. `tests/test_process_validation.py`: 4 passing unit tests verifying data validation and tie-breaking.
2. `tests/test_mid_project_algorithms.py`: 4 passing unit tests proving DFG, Heuristic Dependency, and slicing algorithms.

### Published Process Maps & Figures (`reports/figures/process_maps/`)
1. `happy_path.png`: Dominant clinical backbone pathway.
2. `spaghetti_diagram.png`: Full operational complexity map.
3. `dfg_frequency.png`: Directly-Follows transition network.
4. `variant_distribution.png`: Pareto curve of top 15 clinical variants.
5. `bottleneck_heatmap.png`: Top transition delays by median duration.
6. `sepsis_golden_hour_sla.png`: Time to antibiotic administration histogram.
7. `rework_frequency.png`: Repetitive activity and lab testing volume.
8. `conformance_distribution.png`: Guideline compliance score distribution.
9. `trace_duration_vs_events.png`: Multi-panel trace length and duration scatter plot.
10. `org_workload_distribution.png`: Departmental event share bar chart.
11. `org_handoff_heatmap.png`: Cross-department patient care handoff matrix.
12. `cohort_comparison_barchart.png`: Comparative length of stay across cohorts.
13. `cohort_sepsis_sla_comparison.png`: ICU vs Ward antibiotic SLA compliance.
14. `petri_net_topology.png`: Bipartite Petri net graph layout.
15. `variant_archetypes_pie.png`: Care archetype population donut chart.
16. `cluster_profile_comparison.png`: Care archetype length of stay and readmission plot.
17. `heuristic_net_topology.png`: Causal Heuristic Net with dependency thresholding.

### Technical Markdown Reports (`reports/`)
1. `reports/process_data_quality.md`: Data validation, tie-breaking, and trace quality.
2. `reports/org_mining_report.md`: Organizational resource mining and department handoffs.
3. `reports/cohort_analysis_report.md`: Clinical cohort segmentation and pathway divergence.
4. `reports/week1_synthesis_report.md`: Week 1 milestone synthesis and team hand-off.
5. `reports/week2_petri_net_clustering.md`: Petri Net formalization and variant clustering.
6. `reports/mid_project_review_report.md`: Complete Mid-Project Review defense report.

---

## 5. Verification Status & Conclusion

All 14 scripts, 17 process figures, 10 data exports, and 2 unit test suites are fully committed, validated, and pushed to remote branch **`Amit-Prajapati`**.

**Conclusion:** Member 3's deliverables for the **Mid-Project Review Milestone** are 100% complete, reproducible, and ready for official mentor review.
