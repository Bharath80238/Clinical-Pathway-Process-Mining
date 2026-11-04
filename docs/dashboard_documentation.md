# CareFlow Power BI & Streamlit Dashboard Documentation

**Author**: Tanisha Kumari (Member 4 — BI Dashboard Specialist)  
**Project**: CareFlow: Clinical Pathway Process Mining  
**Power BI Report File**: `dashboard/CareFlow_Dashboard.pbix`  
**Web Dashboard**: `app.py`  
**Data Warehouse Source**: `reports/star_schema/`  

---

## 1. Project Overview & Role Definition
As Member 4 (BI Dashboard Specialist), my primary objective is to translate Member 3's advanced process mining outputs, Petri net models, and bottleneck analytics into an intuitive, high-impact **Executive Business Intelligence Dashboard**.

The dashboard provides clinical leadership with real-time visibility into patient journey flows, Sepsis Golden Hour SLA compliance, laboratory diagnostic queues, and readmission risk.

---

## 2. Integrated Data Architecture (Star-Schema)
The dashboard directly connects to the **CareFlow Dimensional Star-Schema Data Warehouse** located in `reports/star_schema/`:
- **Fact Table**: `fact_clinical_events.csv` (15,213 records with transition latency and SLA flags)
- **Dimension 1**: `dim_patient_cohort.csv` (1,050 cases with age, SIRS, and Care Archetypes)
- **Dimension 2**: `dim_activity.csv` (16 clinical activities with functional phase classifications)
- **Dimension 3**: `dim_department.csv` (26 organizational units with clinical division groupings)
- **Dimension 4**: `dim_time_bucket.csv` (5 standardized SLA performance tiers)

For complete modeling details and DAX measures, refer to the [Power BI Star-Schema Guide](file:///c:/Users/amitp/OneDrive/Desktop/data%20analytice%20project%20infotact/docs/powerbi_star_schema_guide.md).

---

## 3. Four Core Dashboard Pages

### Page 1: Executive Overview & Headline KPIs
- **Headline Cards**: Total Patients (1,050), Total Events (15,213), Golden Hour Compliance (84.8%), Unplanned Readmissions (28.0%), Median Stay (5.34 days), Central Lab Workload (53.31%).
- **Patient Cohort Segmentation**: Care Archetype distribution (Rapid ER 21%, Standard Ward 46%, Critical ICU 33%).
- **Summary Metrics**: Powered by `dashboard/dashboard_kpi_cards.csv` and `dashboard/dashboard_archetype_metrics.csv`.

### Page 2: Clinical Pathway Discovery
- **Topological Process Maps**: Dominant Happy Path vs. Unfiltered Spaghetti Diagram.
- **Variant Analysis**: Cumulative patient coverage Pareto curve across 691 pathway variations.

### Page 3: Bottleneck Analytics & Sepsis Golden Hour SLA
- **Step-by-Step Latency Matrix**: Node-to-node transition durations identifying ICU escalation delays (median 5.01 hours).
- **Golden Hour SLA Compliance**: Time-to-antibiotics distribution highlighting the 15.2% delayed cohort.
- **Diagnostic Laboratory Queueing**: Turnaround time (TAT) distributions for CRP, Leucocytes, and Lactic Acid.

### Page 4: Department Workload & Readmission Risk
- **Organizational Analysis**: Central Diagnostic Lab workload share and cross-department handoff matrix.
- **Readmission Root-Cause Mining**: Odds ratio forest plot identifying high-risk cohorts (extended stay $\ge 7$ days $OR=104.96$).
- **Clinical Decision Support (CDSS)**: Automated triage scoring and recommended bed allocations.

---

## 4. Automated Data Loading & Verification
The dashboard data pipeline is automated via `src/member4_dashboard_data_loader.py` and validated by unit tests in `tests/test_member4_dashboard_data.py`.
