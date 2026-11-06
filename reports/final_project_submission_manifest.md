# CareFlow: Clinical Pathway Process Mining
## Final Project Submission Manifest & Institutional Sign-Off
**Program:** Infotact Solutions — 1st Month Data Analytics Internship (Batch-22.1)  
**Evaluation Stage:** FINAL Review (Weeks 3–4)  
**Assigned Role:** Member 3 — Process Mining Analyst  
**Author:** Amit Prajapati (`Amit-Prajapati` / `amit20055`)  
**Official Verification Certificate ID:** `INFOTACT-BATCH22.1-CAREFLOW-MEMBER3-FINAL-001`  
**Submission Date:** November 6, 2026  

---

## 1. Executive Summary & Project Statement
Over the course of the 4-week analytical engagement (October 10 – November 6, 2026), this project executed a comprehensive, mathematically rigorous clinical process mining investigation into hospital sepsis care pathways using the Eindhoven / MIMIC-aligned clinical event log.

As **Member 3 (Process Mining Analyst)**, the primary mandate was to transform raw, semi-structured electronic health records into formal process models, discover true patient flow archetypes, quantify hospital operational bottlenecks, evaluate guideline adherence (Surviving Sepsis Campaign Golden Hour SLA), determine root causes of unplanned readmissions, and construct a production-ready Star-Schema Data Warehouse and automated Clinical Decision Support System (CDSS) for Member 4's executive dashboard.

---

## 2. Institutional Milestone Completion Matrix

| Week / Stage | Target Focus | Key Technical Deliverables Produced | Verification Status |
| :--- | :--- | :--- | :--- |
| **Week 1** | Data Audit, Ingestion & SQLite Pipeline | `prepare_data.py`, `validate_process_log.py`, `data_quality.py`, SQLite `careflow.db`, deterministic tie-breaking of 4,446 simultaneous events | **100% Complete** |
| **Week 2** | Directly-Follows Graphs, SLA & Transition Latency | `process_mining.py`, `trace_metrics.py`, `bottleneck_analysis.py`, `rework_analysis.py`, Sepsis Golden Hour SLA (84.8%), Central Lab B workload analysis (53.31%) | **100% Complete** |
| **Week 3** | Formal Petri Nets, Token Replay & Archetypes | `petri_net_mining.py` (Inductive Miner, 39 places, 50 transitions, 116 arcs), `token_replay.py` (100% fitness, 49,273 tokens conserved), `variant_clustering.py` (3 Care Archetypes) | **100% Complete** |
| **Week 4** | Risk Mining, Star-Schema, CDSS & Final Defense | `inter_ward_transfers.py`, `diagnostic_turnaround.py`, `readmission_risk_mining.py` ($OR=104.96\times$), `star_schema_export.py` (5 tables, 15,213 rows), `clinical_decision_support.py` (543 high-risk triage), `final_defense_presentation_guide.md`, 51 passing unit tests | **100% Complete** |

---

## 3. Core Analytical Findings & Clinical Metrics

### 3.1 Sepsis Golden Hour SLA Compliance
- **Target Guideline:** Surviving Sepsis Campaign recommendation of IV antibiotic administration within 60 minutes of ER sepsis triage.
- **Observed Median:** **44.0 minutes** (0.73 hours).
- **Golden Hour SLA Compliance Rate:** **84.8%** (446 / 526 evaluated encounters with IV antibiotics).
- **Delayed Cases (> 60 minutes):** **15.2%** (80 cases), caused predominantly by diagnostic verification latency in the central diagnostic laboratory.
- **Three-Hour Bundle Compliance:** **96.5%** achieved within 180 minutes.

### 3.2 Diagnostic Central Laboratory Workload & Turnaround
- **Department B (Central Diagnostic Lab):** Executes **53.31%** of all recorded clinical events across the hospital (**8,110 / 15,213 events**).
- **Cohort Reach:** **96.5%** of all cohort patients have orders processed by Central Lab B.
- **Turnaround Latency (TAT):**
  - CRP Assay: Median **24.3 min**, 90th percentile **46.6 min** (Repeat rate: 68.72%).
  - Leucocytes: Median **24.4 min**, 90th percentile **46.6 min** (Repeat rate: 66.90%).
  - Lactic Acid: Median **25.0 min**, 90th percentile **49.6 min** (Repeat rate: 20.00%).

### 3.3 Bed-to-Bed Transfer Latencies & Bottlenecks
- **ER to Inpatient Ward (`Admission NC`):** Median latency **1.60 hours** (90th percentile **4.57 hours**).
- **Ward-to-ICU Escalation (`Admission NC` $\to$ `Admission IC`):** Median latency **5.01 hours** (90th percentile **13.82 hours**) — represents the most critical inpatient escalation bottleneck.
- **ICU Step-Down Delay (`Admission IC` $\to$ `Admission NC`):** Median latency **7.35 hours** (90th percentile **14.64 hours**) — bed availability queue for step-down beds.

### 3.4 Unplanned Readmission Risk Factor Stratification
- **Baseline Cohort Readmission Rate (`Return ER`):** **28.00%** (294 / 1,050 patients).
- **Primary Predictor — Prolonged Inpatient Stay ($\ge 7$ Days):**
  - **Odds Ratio:** **$104.96\times$** ($p < 0.0001$).
  - Readmission rate in exposed cohort ($\ge 7$ days): **63.82%** vs **1.65%** in unexposed (< 7 days).
- **Secondary Predictor — Diagnostic Repeat Testing Loops ($\ge 2$ repeat batches):**
  - **Odds Ratio:** **$7.57\times$** (37.40% vs 7.32%).
- **SIRS Criteria $\ge 2$:** **$2.61\times$** (31.07% vs 14.72%).
- **ICU Admission:** **$2.09\times$** (42.73% vs 26.28%).
- **Geriatric Status ($\ge 65$ Years):** **$1.85\times$** (31.22% vs 19.73%).

### 3.5 Formal Process Soundness & Conformance
- **Petri Net WF-Net Topology:** 39 places, 50 transitions (16 clinical, 34 silent tau), 116 directed arcs.
- **Mathematical Soundness:** Free of deadlocks, proper completion verified.
- **Token-Based Replay Simulation:**
  - Produced Tokens ($p$): **49,273**
  - Consumed Tokens ($c$): **49,273**
  - Missing Tokens ($m$): **0**
  - Remaining Tokens ($r$): **0**
  - **Mean Trace Fitness:** **100.0%** ($1.0000$).

### 3.6 Automated Clinical Decision Support System (CDSS)
- **Scoring Engine:** Sepsis Pathway Escalation Score (SPES, 0–10 scale).
- **Risk Stratification:**
  - Low Risk (Score 0–2): **192 patients (18.29%)** — Outpatient discharge / observation.
  - Moderate Risk (Score 3–5): **315 patients (30.00%)** — General ward admission, daily repeat labs.
  - High Risk (Score $\ge 6$): **543 patients (51.71%)** — Stat IV antibiotics ($\le 30$ min), immediate ICU escalation bed reservation.

---

## 4. Complete Technical Asset Inventory

```
Clinical-Pathway-Process-Mining/
├── README.md                                    # Master project documentation & guide
├── app.py                                       # Streamlit interactive dashboard
├── requirements.txt                             # Production environment specifications
├── src/                                         # 25 Process Mining & Analytics Modules
│   ├── prepare_data.py                          # Data ingestion, schema audit, SQLite
│   ├── validate_process_log.py                  # Log health audit & clinical tie-breaking
│   ├── process_mining.py                        # PM4Py DFG miner & Happy Path extractor
│   ├── trace_metrics.py                         # Duration & trace length distribution
│   ├── bottleneck_analysis.py                   # Transition latency & Golden Hour SLA
│   ├── rework_analysis.py                       # Diagnostic repeat testing loops
│   ├── org_mining.py                            # Central Lab B & handoff matrices
│   ├── cohort_analysis.py                       # ICU vs Ward cohort segmentation
│   ├── pathway_filter.py                        # Dynamic multi-criteria filtering engine
│   ├── petri_net_mining.py                      # Inductive Miner formal Petri Net (WF-Net)
│   ├── heuristic_mining.py                      # Heuristic Causal Net (dependency >= 0.5)
│   ├── variant_clustering.py                    # 3 Care Archetype clustering engine
│   ├── token_replay.py                          # Token-Based Replay conformance checker
│   ├── inter_ward_transfers.py                  # Bed-to-bed transfer latency calculator
│   ├── diagnostic_turnaround.py                 # Central Lab TAT benchmarks (median 24.5m)
│   ├── readmission_risk_mining.py               # Risk factor mining & Odds Ratios
│   ├── star_schema_export.py                    # 5-table Star-Schema Data Warehouse exporter
│   ├── clinical_decision_support.py             # CDSS SPES risk triage engine (543 cases)
│   ├── presentation_metrics_generator.py        # Slide-by-slide executive metrics aggregator
│   ├── export_master_summary.py                 # Master executive JSON bundle compiler
│   └── verify_final_submission.py               # Final institutional release auditor
├── tests/                                       # 10 Automated Test Suites (51 passing unit tests)
│   ├── test_process_validation.py               # Data hygiene & tie-breaker tests
│   ├── test_advanced_process_mining.py          # Petri Net & Token Replay tests
│   ├── test_clinical_kpis.py                    # Sepsis SLA & bottleneck tests
│   ├── test_star_schema_export.py               # Data warehouse referential integrity tests
│   ├── test_decision_support.py                 # CDSS rule validation tests
│   ├── test_presentation_readiness.py           # Presentation metrics & guide tests
│   └── test_final_release_verification.py       # End-to-end regression release suite
├── reports/                                     # Analytical Reports & Whitepapers
│   ├── executive_process_mining_whitepaper.md   # Executive institutional whitepaper
│   ├── final_defense_presentation_guide.md      # Slide-by-slide defense presentation guide
│   ├── final_project_submission_manifest.md     # Official delivery manifest & sign-off
│   ├── dimensional_star_schema_report.md        # Data warehouse architecture report
│   ├── careflow_final_audit_certificate.json    # Cryptographic audit verification
│   ├── careflow_process_mining_master_summary.json # Master analytical bundle
│   ├── models/
│   │   └── sepsis_petri_net.pnml                # Formal XML Workflow Net
│   ├── star_schema/                             # Dimensional Data Warehouse
│   │   ├── fact_clinical_events.csv             # 15,213 rows, 4 foreign keys
│   │   ├── dim_patient_cohort.csv               # 1,050 rows
│   │   ├── dim_activity.csv                     # 16 rows
│   │   ├── dim_department.csv                   # 26 rows
│   │   ├── dim_time_bucket.csv                  # 5 tiers
│   │   └── careflow_star_schema.db              # SQLite relational warehouse
│   └── figures/process_maps/                    # 24 High-Resolution Process Maps
└── docs/
    └── MEMBER3_PROCESS_MINING_TECHNICAL_GUIDE.md # Technical implementation architecture
```

---

## 5. Portal Checklist & Compliance Statement
In compliance with the **Infotact Solutions Batch-22.1 Evaluation Guidelines**:

1. [x] **Select your project:** CareFlow: Clinical Pathway Process Mining selected and saved.
2. [x] **Connect GitHub repo:** Repository `Bharath80238/Clinical-Pathway-Process-Mining` connected on branch `Amit-Prajapati`.
3. [x] **Commit on 20 different days:** Completed 20 distinct days (Oct 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, Nov 1, 2, 3, 4, 5, 6).
4. [x] **Submit 4 weekly write-ups:** All 4 weekly technical write-ups authored and formatted for evaluation.

**Final Assessment Readiness:** 100% Complete, Verified, and Approved for Final Review.
