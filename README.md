# CareFlow: Clinical Pathway Process Mining
[![Project Status: Complete](https://img.shields.io/badge/Status-Final%20Release%20v1.0.0-success.svg)](README.md)
[![Test Suite](https://img.shields.io/badge/Unit%20Tests-51%20Passing-brightgreen.svg)](tests/)
[![Batch](https://img.shields.io/badge/Infotact%20Solutions-Batch--22.1-blue.svg)](https://infotact.in)
[![Role](https://img.shields.io/badge/Analyst-Member%203%20(Process%20Mining)-orange.svg)](reports/final_project_submission_manifest.md)

## Project Overview
**CareFlow** is an enterprise-grade clinical process mining and healthcare analytics platform designed to analyze, discover, and optimize hospital sepsis treatment pathways. Built upon real-world electronic health record (EHR) event logs (Eindhoven / MIMIC-aligned benchmark), CareFlow transforms millions of clinical data points into mathematically verified Petri Nets, identifies hospital operational bottlenecks, assesses clinical guideline compliance (Surviving Sepsis Campaign Golden Hour SLA), and provides an automated Clinical Decision Support System (CDSS) with a 5-table Star-Schema Data Warehouse.

Developed for the **Infotact Solutions 1-Month Data Analytics Internship (Batch-22.1)** by **Amit Prajapati (Member 3 — Process Mining Analyst)**.

---

## Final Review & Submission Status (Batch-22.1)
| Requirement | Criteria | Member 3 Status | Audit Evidence |
| :--- | :--- | :---: | :--- |
| **1. Select your project** | Choose assigned team project | **Done** | CareFlow: Clinical Pathway Process Mining |
| **2. Connect GitHub repo** | Link active fork and working branch | **Done** | `Bharath80238/Clinical-Pathway-Process-Mining` (`Amit-Prajapati`) |
| **3. Commit on 20 different days** | Min. 20 distinct calendar days ($\ge 50$ chars/commit) | **20 / 20 Days** | Oct 18 – Nov 6, 2026 (100% Verified) |
| **4. Submit 4 weekly write-ups** | Detailed progress per stage | **4 / 4 Write-ups** | Weeks 1, 2, 3, 4 submitted |
| **Overall Eligibility** | Final project review checklist | **UNLOCKED** | Ready for Final Evaluation |

---

## Key Clinical Findings & Quantitative Discoveries

1. **Sepsis Golden Hour SLA Compliance:**
   - **84.8%** of evaluated patients receive intravenous antibiotics within the 60-minute Golden Hour SLA window (median time: **44.0 minutes**).
   - **96.5%** achieve compliance within the Surviving Sepsis 3-hour bundle target.
   - **15.2%** exceed 60 minutes, with the primary delay attributed to Central Diagnostic Laboratory verification queues.

2. **Central Diagnostic Laboratory Workload Concentration:**
   - **Central Diagnostic Lab (B)** executes **53.31% of all recorded events** hospital-wide (8,110 / 15,213 events), serving 96.5% of all cohort patients.
   - Diagnostic Turnaround Time (TAT): CRP median 24.3 min (p90 46.6 min), Leucocytes median 24.4 min (p90 46.6 min), Lactic Acid median 25.0 min (p90 49.6 min).

3. **Inpatient Escalation & Bed Transfer Latencies:**
   - ER to Inpatient Ward (`Admission NC`): Median **1.60 hours** (p90 4.57 hours).
   - Ward-to-ICU Escalation (`Admission NC` $\to$ `Admission IC`): Median **5.01 hours** (p90 13.82 hours) — the hospital's primary critical care transfer bottleneck.
   - ICU Step-Down Delay (`Admission IC` $\to$ `Admission NC`): Median **7.35 hours** (p90 14.64 hours).

4. **Unplanned Readmission Risk Factors (`Return ER`):**
   - Baseline cohort readmission rate: **28.00%** (294 / 1,050 patients).
   - **Prolonged Inpatient Stay ($\ge 7$ days)** is the dominant predictor: **$OR = 104.96\times$** (63.82% readmission rate in $\ge 7$d vs 1.65% in < 7d).
   - Repeat Diagnostic Orders ($\ge 2$ repeat batches): **$OR = 7.57\times$** (37.40% vs 7.32%).
   - SIRS Criteria $\ge 2$: **$OR = 2.61\times$** (31.07% vs 14.72%).

5. **Formal Process Soundness & Conformance:**
   - Formal Inductive Petri Net (WF-Net) model generated with 39 places, 50 transitions, and 116 arcs (`reports/models/sepsis_petri_net.pnml`).
   - Token-Based Replay simulation across all 1,050 traces achieved **100.0% mean trace fitness** ($p = c = 49,273; m = 0, r = 0$).

6. **Clinical Decision Support System (CDSS):**
   - Automated Sepsis Pathway Escalation Score (SPES, 0–10 scale) triaged the cohort into Low Risk (18.3%), Moderate Risk (30.0%), and Critical High Risk (**51.7%, 543 patients** requiring stat antibiotics and ICU bed reservation).

---

## Dimensional Star-Schema Data Warehouse (`reports/star_schema/`)
Engineered specifically for Member 4's executive Power BI and Streamlit dashboards:
- **`fact_clinical_events`** (15,213 rows, 12 columns, 4 foreign keys)
- **`dim_patient_cohort`** (1,050 rows, 16 clinical attributes)
- **`dim_activity`** (16 rows, clinical categories & SLA flags)
- **`dim_department`** (26 rows, organizational unit mappings)
- **`dim_time_bucket`** (5 tiers, clinical shift distributions)
- **`careflow_star_schema.db`** (SQLite relational warehouse with 100% verified foreign key integrity)

---

## 20-Day Analytical Milestone Roadmap

```
Week 1: Data Ingestion, Hygiene Audit & Deterministic Precedence Resolution
├── Day 1-2: Multi-format ingestion (Excel/Parquet), schema harmonization, careflow.db SQLite setup
├── Day 3-4: Null audit, timestamp chronological verification, identifying 4,446 simultaneous events
└── Day 5: Deterministic clinical tie-breaking engine (15,213 events resolved to 0 timestamp conflicts)

Week 2: Process Mining, Transition Matrices & Clinical Bottlenecks
├── Day 6-7: Directly-Follows Graph (DFG) discovery, Happy Path extraction (32.8% prevalence)
├── Day 8-9: Trace duration metrics (median 5.34d), stay distribution, rework loops (CRP 68.7%)
└── Day 10: Sepsis Golden Hour SLA engine (84.8% compliance) & Department B workload analysis (53.31%)

Week 3: Advanced Mining, Formal Petri Nets & Conformance Checking
├── Day 11-12: Inductive Miner formal Workflow Net (39 places, 50 transitions, 116 arcs)
├── Day 13-14: Heuristic Causal Miner (dependency >= 0.5) & 3 Care Archetype clustering
└── Day 15: Token-Based Replay simulation (100% fitness, 49,273 tokens conserved, 0 missing)

Week 4: Risk Modeling, Star-Schema Warehouse, CDSS & Final Defense
├── Day 16: Inter-ward transfer latencies & Central Diagnostic Laboratory TAT benchmarks
├── Day 17: Readmission risk factor mining (Stay >= 7d OR=104.96x) & 5-table Star-Schema export
├── Day 18: Automated Clinical Decision Support System (SPES score, 543 high-risk patients)
├── Day 19: Executive Defense Presentation Guide & milestone roadmap visualization
└── Day 20: Final end-to-end regression verification suite, institutional sign-off & v1.0.0 release
```

---

## Project Structure
```text
Clinical-Pathway-Process-Mining/
├── README.md                                    # Master project documentation
├── app.py                                       # Streamlit interactive application
├── requirements.txt                             # Production environment dependencies
├── src/                                         # 25 Process Mining & Analytics Modules
│   ├── prepare_data.py                          # Data preparation & SQLite ingestion
│   ├── validate_process_log.py                  # Log health audit & clinical tie-breaking
│   ├── process_mining.py                        # DFG mining & Happy Path extraction
│   ├── trace_metrics.py                         # Duration & trace length distribution
│   ├── bottleneck_analysis.py                   # Transition latency & Golden Hour SLA
│   ├── rework_analysis.py                       # Diagnostic repeat testing loops
│   ├── org_mining.py                            # Organizational mining & handoffs
│   ├── cohort_analysis.py                       # Cohort pathway segmentation
│   ├── pathway_filter.py                        # Multi-criteria clinical trace slicing
│   ├── petri_net_mining.py                      # Inductive Miner formal Petri Net
│   ├── heuristic_mining.py                      # Heuristic Causal Net discovery
│   ├── variant_clustering.py                    # 3 Care Archetype clustering engine
│   ├── token_replay.py                          # Token-Based Replay conformance checker
│   ├── inter_ward_transfers.py                  # Bed-to-bed transfer latency calculator
│   ├── diagnostic_turnaround.py                 # Central Lab TAT benchmarks
│   ├── readmission_risk_mining.py               # Risk factor mining & Odds Ratios
│   ├── star_schema_export.py                    # 5-table Star-Schema exporter
│   ├── clinical_decision_support.py             # CDSS SPES risk triage engine
│   ├── presentation_metrics_generator.py        # Executive presentation metrics
│   ├── export_master_summary.py                 # Master summary JSON bundle compiler
│   └── verify_final_submission.py               # Final institutional release auditor
├── tests/                                       # 10 Test Suites (51 passing unit tests)
│   ├── test_process_validation.py
│   ├── test_advanced_process_mining.py
│   ├── test_clinical_kpis.py
│   ├── test_star_schema_export.py
│   ├── test_decision_support.py
│   ├── test_presentation_readiness.py
│   └── test_final_release_verification.py
├── reports/                                     # Analytical Reports & Whitepapers
│   ├── executive_process_mining_whitepaper.md   # Executive institutional whitepaper
│   ├── final_defense_presentation_guide.md      # Slide-by-slide defense guide
│   ├── final_project_submission_manifest.md     # Official delivery manifest & sign-off
│   ├── careflow_final_audit_certificate.json    # Cryptographic audit verification
│   ├── careflow_process_mining_master_summary.json # Master analytical bundle
│   ├── models/sepsis_petri_net.pnml             # Formal XML Workflow Net
│   ├── star_schema/                             # 5 Star-Schema dimensional tables
│   └── figures/process_maps/                    # 24 high-resolution process maps
└── docs/
    └── MEMBER3_PROCESS_MINING_TECHNICAL_GUIDE.md # Technical implementation architecture
```

---

## Quickstart & Verification

### 1. Environment Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Execute Automated Verification Suite (51 Unit Tests)
```powershell
python -m unittest discover tests
```

### 3. Generate Final Audit Certificate
```powershell
python src/verify_final_submission.py
```

### 4. Launch Interactive Application
```powershell
streamlit run app.py
```

---

## Author & Acknowledgements
- **Author:** Amit Prajapati (Member 3 — Process Mining Analyst)
- **GitHub:** [`amit20055`](https://github.com/amit20055)
- **Branch:** `Amit-Prajapati`
- **Program:** Infotact Solutions Data Analytics Internship (Batch-22.1)
- **Repository:** [`Bharath80238/Clinical-Pathway-Process-Mining`](https://github.com/Bharath80238/Clinical-Pathway-Process-Mining)
