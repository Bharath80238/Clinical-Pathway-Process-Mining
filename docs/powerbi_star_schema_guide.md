# CareFlow Power BI Star-Schema & Dashboard Implementation Guide

**Author**: Tanisha Kumari (Member 4 — BI Dashboard Specialist)  
**Project**: CareFlow: Clinical Pathway Process Mining  
**DataSource Location**: `reports/star_schema/`  
**Power BI File**: `dashboard/CareFlow_Dashboard.pbix`  

---

## 1. Overview of Data Warehouse Integration

To power the **CareFlow Executive Overview Dashboard**, the process mining outputs from Member 3 were transformed into an enterprise **Dimensional Star-Schema Data Warehouse**. 

This allows Power BI to create cross-filtering slicers, drill-down hierarchies, and real-time KPI card calculations without recalculating path loops.

---

## 2. Star-Schema Tables & Relationship Mapping

Connect Power BI to the CSV files in `reports/star_schema/` and configure the following 1-to-Many ($1 : N$) single-directional relationships in the Model View:

```
┌──────────────────────────────────────┐          ┌──────────────────────────────────────┐
│          DIM_PATIENT_COHORT          │          │             DIM_ACTIVITY             │
│        (dim_patient_cohort.csv)      │          │          (dim_activity.csv)          │
│        1,050 Patient Encounters      │          │       16 Clinical Activities         │
└──────────────────┬───────────────────┘          └──────────────────┬───────────────────┘
                   │ 1                                               │ 1
                   │                                                 │
                   │ N                                               │ N
                   ▼                                                 ▼
     ┌─────────────────────────────────────────────────────────────────────┐
     │                        FACT_CLINICAL_EVENTS                         │
     │                    (fact_clinical_events.csv)                       │
     │                      15,213 Transition Rows                         │
     └─────────────────────────────────────────────────────────────────────┘
                   ▲                                                 ▲
                   │ N                                               │ N
                   │                                                 │
                   │ 1                                               │ 1
┌──────────────────┴───────────────────┐          ┌──────────────────┴───────────────────┐
│            DIM_DEPARTMENT            │          │           DIM_TIME_BUCKET            │
│        (dim_department.csv)          │          │        (dim_time_bucket.csv)         │
│     26 Organizational Units          │          │       5 SLA Compliance Tiers         │
└──────────────────────────────────────┘          └──────────────────────────────────────┘
```

### Relationship Keys:
1. `dim_patient_cohort[patient_cohort_key]` $\longrightarrow$ `fact_clinical_events[patient_cohort_key]`
2. `dim_activity[activity_key]` $\longrightarrow$ `fact_clinical_events[activity_key]`
3. `dim_department[department_key]` $\longrightarrow$ `fact_clinical_events[department_key]`
4. `dim_time_bucket[time_bucket_key]` $\longrightarrow$ `fact_clinical_events[time_bucket_key]`

---

## 3. Key DAX Measures for Dashboard Cards & Visuals

Add these standard DAX measures in Power BI:

### 3.1. Total Patient Cohort
```dax
Total Patients = DISTINCTCOUNT(dim_patient_cohort[case_id])
```

### 3.2. Total Clinical Transitions
```dax
Total Transitions = COUNTROWS(fact_clinical_events)
```

### 3.3. Sepsis Golden Hour Compliance Rate (%)
```dax
Golden Hour Compliance Rate = 
VAR TotalAbx = CALCULATE(COUNTROWS(fact_clinical_events), dim_activity[activity_name] = "IV Antibiotics")
VAR DelayedAbx = CALCULATE(SUM(fact_clinical_events[is_sla_delayed]), dim_activity[activity_name] = "IV Antibiotics")
RETURN
IF(TotalAbx > 0, 1.0 - (DelayedAbx / TotalAbx), 0)
```

### 3.4. Unplanned ER Readmission Rate (%)
```dax
Readmission Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(dim_patient_cohort), dim_patient_cohort[has_readmission] = 1),
    COUNTROWS(dim_patient_cohort),
    0
)
```

### 3.5. Central Diagnostic Lab Workload Share (%)
```dax
Lab Workload Share = 
DIVIDE(
    CALCULATE(COUNTROWS(fact_clinical_events), dim_department[org_code] = "B"),
    COUNTROWS(fact_clinical_events),
    0
)
```

---

## 4. Multi-Page Dashboard Layout Structure

1. **Page 1: Executive Overview & KPI Cards**:
   - 6 top metric cards (Total Patients, Transitions, SLA Compliance, Readmissions, Stay Length, Lab Workload).
   - Care Archetype pie chart (`dashboard/dashboard_archetype_metrics.csv`).
   - Monthly intake volume area chart.
2. **Page 2: Process Discovery & Pathway Flows**:
   - Dominant Happy Path diagram (`reports/figures/process_maps/happy_path.png`).
   - Variant distribution Pareto curve (`reports/figures/process_maps/variant_distribution.png`).
   - Top 15 frequent clinical pathways table (`reports/variant_analysis.csv`).
3. **Page 3: Clinical Bottlenecks & SLA Compliance**:
   - Transition duration heatmap (`reports/figures/process_maps/bottleneck_heatmap.png`).
   - Sepsis Golden Hour SLA breakdown (`reports/figures/process_maps/sepsis_golden_hour_sla.png`).
   - Lab diagnostic turnaround distributions (`reports/figures/process_maps/diagnostic_turnaround_distribution.png`).
4. **Page 4: Hospital Departments & Readmission Risk**:
   - Department workload bar chart (`reports/figures/process_maps/org_workload_distribution.png`).
   - Cross-department handoff matrix (`reports/figures/process_maps/org_handoff_heatmap.png`).
   - Readmission risk factors forest plot (`reports/figures/process_maps/readmission_risk_factors.png`).
   - CDSS Risk & Bed Allocation Matrix (`reports/figures/process_maps/clinical_decision_support_matrix.png`).
