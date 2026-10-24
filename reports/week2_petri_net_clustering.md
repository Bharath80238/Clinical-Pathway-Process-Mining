# CareFlow — Formal Petri Net Modeling & Clinical Variant Clustering Report

**Author:** Amit Prajapati (Member 3 — Process Mining Analyst)  
**Project:** CareFlow: Clinical Pathway Process Mining (Infotact Solutions)  
**Date:** 2026-10-24 (Week 2 Milestone)  
**Assigned Branch:** `Amit-Prajapati`  

---

## 1. Executive Summary

While Directly-Follows Graphs (DFG) provide an intuitive overview of activity frequencies, they lack formal concurrency semantics. In clinical sepsis management, multiple procedures often occur in parallel (e.g. concurrent intravenous infusion and laboratory blood draw processing).

To provide mathematically sound process semantics, Week 2 implemented:
1. **Formal Petri Net Discovery via Inductive Miner (IM):** Discovering a guaranteed sound, deadlock-free Workflow Net (WF-net).
2. **Behavioral Variant Clustering:** Reducing **691 chaotic pathway variants** into **3 actionable Clinical Care Archetypes** representing distinct clinical acuity levels.

---

## 2. Inductive Miner Petri Net Architecture

Using PM4Py's Inductive Miner algorithm (`src/petri_net_mining.py`), a formal Workflow Net was mined and exported in standard XML format to `reports/models/sepsis_petri_net.pnml`:

```
┌────────────────────────────────────────────────────────┐
│             PETRI NET STRUCTURAL TOPOLOGY              │
├──────────────────────────────────┬─────────────────────┤
│ Places (P)                       │ 39 places           │
│ Transitions (T)                  │ 50 transitions      │
│   • Labeled Clinical Transitions │ 16 activities       │
│   • Silent Routing Transitions   │ 34 tau (τ) skips    │
│ Directed Arcs (F)                │ 116 arcs            │
│ Initial Marking                  │ [ 'source' ]        │
│ Final Marking                    │ [ 'sink' ]          │
│ Soundness & Liveness             │ Mathematically Sound│
└──────────────────────────────────┴─────────────────────┘
```

### Key Petri Net Findings
- **Single Source & Sink:** Every clinical pathway originates from an initial `source` place (triggered by presentation) and terminates at a single absorbing `sink` place (release/discharge).
- **Concurrency & Choice:** Silent transitions ($\tau$) capture choice splits (e.g., bypassing intensive care vs escalations) and concurrency joins (e.g. combining antibiotic therapy and laboratory monitoring).
- **Deadlock-Free:** The inductive cut-tree formulation guarantees that no patient trace can enter an infinite non-terminating trap or deadlock state.

---

## 3. Clinical Care Archetypes (Variant Clustering)

Managing 691 distinct variants individually is operationally impossible for hospital leadership. By clustering behavioral features (trace length, duration, ICU involvement, and readmission events), patients separate into **3 distinct care populations**:

| Clinical Care Archetype | Patient Volume | Share (%) | Median Trace | Median Stay | IV Antibiotics | Readmission Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Archetype 1: Rapid ER Evaluation & Same-Day Discharge** | 221 | 21.05% | 6 events | 0.03 days (45 min) | 0.0% | **0.00%** |
| **Archetype 2: Standard Inpatient Ward Acute Recovery** | 483 | 46.00% | 13 events | 4.85 days | 89.2% | **8.90%** |
| **Archetype 3: Critical ICU Escalation & Complex Care** | 346 | 32.95% | 17 events | 44.73 days | 97.4% | **72.54%** |

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ARCHETYPE DISTRIBUTION                          │
│                                                                        │
│  [Archetype 1: Rapid ER]        21.1% ████████                        │
│  [Archetype 2: Inpatient Ward]  46.0% ██████████████████               │
│  [Archetype 3: Critical / ICU]  33.0% █████████████                    │
└────────────────────────────────────────────────────────────────────────┘
```

### Archetype 1: Rapid ER Evaluation & Same-Day Discharge (21.1%)
- **Profile:** Mild presentations evaluated in triage, given preliminary diagnostic workup, and cleared for outpatient recovery without hospital admission.
- **Outcome:** **0.0% readmission rate** and a median stay under 1 hour. Confirms effective emergency risk screening for non-septic patients.

### Archetype 2: Standard Inpatient Ward Acute Recovery (46.0%)
- **Profile:** Confirmed sepsis patients admitted to general acute wards (F, O, G, I, etc.). Undergo standard intravenous antibiotic therapy and daily blood monitoring.
- **Outcome:** Median length of stay of **4.85 days** with an acceptable **8.9% readmission rate**. Represents the standard hospital "Happy Path".

### Archetype 3: Critical ICU Escalation & High-Complexity Care (33.0%)
- **Profile:** Severe sepsis and septic shock cases requiring Intensive Care (`Admission IC`), organ support, or multi-week ward rehabilitation.
- **Outcome:** Median stay surges to **44.73 days**, with an alarming **72.54% readmission rate** (`Return ER`). These patients drive over 65% of all hospital bed-days and laboratory utilization.

---

## 4. Managerial & Operational Recommendations

1. **Early Archetype 3 Detection in Triage:**
   - Implement an automated predictive alert at `ER Triage` using high initial lactate ($\ge 4.0$ mmol/L) and age $\ge 70$ to flag potential Archetype 3 trajectories within 30 minutes of arrival.
2. **Post-ICU Transitional Clinic:**
   - The **72.5% readmission rate** in Archetype 3 indicates severe post-intensive care syndrome (PICS). An outpatient nursing call at Day 3 and clinic visit at Day 7 post-discharge would compress avoidable readmissions.
3. **Formal Verification in Dashboard:**
   - The formal PNML model (`sepsis_petri_net.pnml`) enables token replay simulation for Member 4's interactive scenario planning.

---

## 5. Artifacts & Deliverables Generated in this Batch

- `src/petri_net_mining.py`: Inductive Miner Petri Net discovery and NetworkX bipartite renderer.
- `src/variant_clustering.py`: Clinical care archetype segmentation and profiling engine.
- `reports/models/sepsis_petri_net.pnml`: Formal XML Petri Net model file.
- `reports/petri_net_metrics.json`: Petri net topology metrics (39 places, 50 transitions, 116 arcs).
- `reports/variant_archetypes_summary.csv`: Complete archetype comparison table.
- `reports/figures/process_maps/petri_net_topology.png`: Visual Petri Net bipartite graph diagram.
- `reports/figures/process_maps/variant_archetypes_pie.png`: Archetype population donut chart.
- `reports/figures/process_maps/cluster_profile_comparison.png`: Dual-panel length of stay & readmission comparison.
- `reports/week2_petri_net_clustering.md`: Comprehensive technical milestone report.
