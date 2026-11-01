# CareFlow Dimensional Data Warehouse (Star-Schema Architecture) Report

**Project**: CareFlow: Clinical Pathway Process Mining  
**Module**: Dimensional Modeling & Star-Schema Data Warehouse Design  
**Author**: Amit Prajapati (Member 3 — Process Mining Analyst)  
**Date**: November 1, 2026  
**Artifact References**: `reports/star_schema/`, `reports/star_schema_summary.json`, `reports/figures/process_maps/star_schema_entity_relationship.png`

---

## 1. Executive Summary & Architectural Motivation

While process mining algorithms discover intricate topological pathways, Directly-Follows Graphs, and Petri nets, executive stakeholders and Business Intelligence (BI) dashboards (e.g. Power BI, Streamlit, Tableau) require structured, query-optimized dimensional data structures.

To facilitate high-performance slice-and-dice analytics and support **Member 4's** dashboard integration, I developed a formal **Enterprise Star-Schema Data Warehouse model**. This architecture decouples raw chronological event logging into:
- A high-density **Fact Table** capturing every operational transition, duration metric, and SLA flag.
- Four normalized **Dimension Tables** capturing patient cohort attributes, clinical activity classifications, organizational departments, and SLA time tiers.

The model was implemented in `src/star_schema_export.py` and exported both as flat CSV dimensions and as a unified SQLite warehouse (`reports/star_schema/careflow_star_schema.db`).

---

## 2. Dimensional Architecture & Entity-Relationship Schema

The entity-relationship diagram below summarizes the star-schema topology:

```
                          ┌───────────────────────────┐
                          │    DIM_PATIENT_COHORT     │
                          │        (1,050 rows)       │
                          ├───────────────────────────┤
                          │ [PK] patient_cohort_key   │
                          │   •  case_id              │
                          │   •  age & age_bracket    │
                          │   •  is_geriatric         │
                          │   •  infection_suspected  │
                          │   •  sirs_criteria        │
                          │   •  care_archetype       │
                          │   •  has_readmission      │
                          └─────────────┬─────────────┘
                                        │ 1
                                        │
                                        │ N
┌───────────────────────────┐           │           ┌───────────────────────────┐
│       DIM_ACTIVITY        │           │           │      DIM_DEPARTMENT       │
│         (16 rows)         │ 1       N ▼         1 │         (26 rows)         │
├───────────────────────────┼────►┌───────────────┐◄────┼───────────────────────────┤
│ [PK] activity_key         │     │     FACT_     │     │ [PK] department_key       │
│   •  activity_name        │     │CLINICAL_EVENTS│     │   •  org_code             │
│   •  clinical_phase       │     │(15,213 rows)  │     │   •  department_name      │
│   •  is_normative_step    │     └───────┬───────┘     │   •  clinical_division    │
│   •  is_diagnostic_lab    │             ▲ N           │   •  service_tier         │
└───────────────────────────┘             │             │   •  is_critical_care     │
                                          │ 1           └───────────────────────────┘
                               ┌──────────┴───────────┐
                               │   DIM_TIME_BUCKET    │
                               │       (5 rows)       │
                               ├──────────────────────┤
                               │ [PK] time_bucket_key │
                               │   •  bucket_name     │
                               │   •  min/max_minutes │
                               │   •  sla_compliance  │
                               └──────────────────────┘
```

---

## 3. Data Dictionary & Table Specifications

### 3.1. Fact Table: `fact_clinical_events` (15,213 Rows)
- **Granularity**: Exactly one row per discrete clinical activity execution within a patient encounter.
- **Surrogate Primary Key**: `event_surrogate_key` (Unique sequence 1 to 15,213).
- **Foreign Keys**:
  - `patient_cohort_key` $\to$ `DIM_PATIENT_COHORT`
  - `activity_key` $\to$ `DIM_ACTIVITY`
  - `department_key` $\to$ `DIM_DEPARTMENT`
  - `time_bucket_key` $\to$ `DIM_TIME_BUCKET`
- **Quantitative Metrics & Measures**:
  - `step_sequence`: Chronological event index within the patient's trace (1 to $N$).
  - `timestamp`: ISO-8601 UTC timestamp.
  - `transition_duration_minutes`: Elapsed duration from the preceding clinical step (minutes).
  - `transition_duration_hours`: Elapsed duration from the preceding clinical step (hours).
  - `elapsed_from_start_hours`: Cumulative time from patient ER intake to this step.
  - `is_repeat_activity`: Binary flag ($1/0$) indicating diagnostic re-testing or rework.
  - `is_sla_delayed`: Binary flag ($1/0$) indicating whether an antibiotic order breached the 60-min Golden Hour SLA.

### 3.2. Dimension: `dim_patient_cohort` (1,050 Rows)
- **Surrogate Primary Key**: `patient_cohort_key` (1 to 1,050).
- **Attributes**: `case_id`, `age`, `age_bracket` (`<40`, `40-64`, `65-79`, `80+`), `is_geriatric`, `infection_suspected`, `sirs_criteria`, `organ_dysfunction`, `care_archetype` (Archetype 1: Rapid ER, Archetype 2: Standard Ward, Archetype 3: Critical ICU), `has_icu_admission`, `has_ward_admission`, `has_antibiotics`, `has_readmission`, `total_stay_days`, `total_event_count`, `is_extended_stay` ($\ge 7$ days).

### 3.3. Dimension: `dim_activity` (16 Rows)
- **Surrogate Primary Key**: `activity_key` (1 to 16).
- **Attributes**: `activity_name`, `clinical_phase` (Intake, Triage, Diagnostics, Therapeutics, Inpatient, Discharge, Readmission), `is_normative_step`, `is_diagnostic_lab`, `is_admission_step`, `is_discharge_step`.

### 3.4. Dimension: `dim_department` (26 Rows)
- **Surrogate Primary Key**: `department_key` (1 to 26).
- **Attributes**: `org_code`, `department_name`, `clinical_division` (Emergency Care, Diagnostics, Inpatient Ward, Critical Care, Administration), `service_tier` (Primary, Secondary, Tertiary, Ancillary), `is_critical_care`, `is_diagnostic_unit`.

### 3.5. Dimension: `dim_time_bucket` (5 Rows)
- **Surrogate Primary Key**: `time_bucket_key` (1 to 5).
- **Tiers**:
  1. *Immediate ($\le 15$ min)*: Optimal triage response.
  2. *Rapid (15 – 30 min)*: Standard emergency flow.
  3. *Standard SLA (30 – 60 min)*: Golden Hour compliant boundary.
  4. *Delayed (60 – 180 min)*: Mild operational delay.
  5. *Prolonged ($> 180$ min)*: Severe queueing bottleneck.

---

## 4. Referential Integrity & Verification

The star-schema was verified using an automated test suite (`tests/test_star_schema.py`):
- **100% Referential Integrity**: Every foreign key in `fact_clinical_events` resolves to a valid record in its parent dimension.
- **Zero Orphaned Records**: Exactly 0 orphaned foreign keys.
- **Strict Surrogate Uniqueness**: 15,213 distinct keys with zero null values.
- **Complete Population Alignment**: 1,050 patients and 15,213 events perfectly preserved.

---

## 5. Ready-to-Use SQL Query Recipes for Dashboard Hand-off (Member 4)

Below are three high-performance analytical SQL queries provided to Member 4 for dashboard and Power BI report authoring:

### Query 1: Golden Hour SLA Compliance by Care Archetype
```sql
SELECT 
    p.care_archetype,
    COUNT(DISTINCT p.patient_cohort_key) AS total_patients,
    SUM(f.is_sla_delayed) AS delayed_antibiotic_orders,
    ROUND(100.0 * (1.0 - (SUM(f.is_sla_delayed) * 1.0 / COUNT(DISTINCT p.patient_cohort_key))), 2) AS golden_hour_compliance_pct
FROM fact_clinical_events f
JOIN dim_patient_cohort p ON f.patient_cohort_key = p.patient_cohort_key
JOIN dim_activity a ON f.activity_key = a.activity_key
WHERE a.activity_name = 'IV Antibiotics'
GROUP BY p.care_archetype;
```

### Query 2: Laboratory Diagnostic Workload & Turnaround by Assay
```sql
SELECT 
    a.activity_name AS diagnostic_assay,
    COUNT(f.event_surrogate_key) AS total_tests_performed,
    SUM(f.is_repeat_activity) AS repeat_rework_orders,
    ROUND(AVG(f.transition_duration_minutes), 2) AS avg_turnaround_minutes
FROM fact_clinical_events f
JOIN dim_activity a ON f.activity_key = a.activity_key
WHERE a.is_diagnostic_lab = 1
GROUP BY a.activity_name;
```

### Query 3: Readmission Incidence by Inpatient Length-of-Stay Tier
```sql
SELECT 
    CASE 
        WHEN p.total_stay_days < 1.0 THEN 'Under 24 Hours (ER Discharge)'
        WHEN p.total_stay_days < 7.0 THEN '1 to 6 Days (Acute Stay)'
        ELSE '7+ Days (Extended Stay)'
    END AS stay_bracket,
    COUNT(p.patient_cohort_key) AS cohort_size,
    SUM(p.has_readmission) AS readmitted_patients,
    ROUND(100.0 * AVG(p.has_readmission), 2) AS readmission_rate_pct
FROM dim_patient_cohort p
GROUP BY 1
ORDER BY readmission_rate_pct ASC;
```
