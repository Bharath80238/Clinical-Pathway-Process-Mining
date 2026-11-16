"""
CareFlow: Clinical Pathway Process Mining
Executive Clinical Intelligence Dashboard
Authors: Tanisha Kumari (Member 4 - BI Specialist) & Amit Prajapati (Member 3 - Process Mining Analyst)
Project: Infotact Solutions Batch-22.1 Data Analytics Project
"""

import json
import os
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="CareFlow | Clinical Intelligence Command Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Impact Professional CSS Styling (Fully Dark/Light Adaptive)
st.markdown(
    """
    <style>
    /* Global styles */
    .hero-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%);
        color: #ffffff;
        padding: 24px 32px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 20px -5px rgba(30, 58, 138, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .hero-banner h1 {
        color: #ffffff !important;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: -0.02em;
    }
    .hero-banner p {
        color: #e0e7ff !important;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    .hero-pill {
        background: rgba(255, 255, 255, 0.18);
        color: #ffffff !important;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 10px;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }
    
    /* Executive KPI Grid */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 14px;
        margin-bottom: 24px;
    }
    @media (max-width: 1200px) {
        .kpi-grid { grid-template-columns: repeat(3, 1fr); }
    }
    @media (max-width: 768px) {
        .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    }
    
    .kpi-card {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 14px;
        padding: 16px 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s, border-color 0.2s;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #60a5fa !important;
    }
    .kpi-header {
        color: #94a3b8 !important;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-value {
        color: #ffffff !important;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 10px;
        font-feature-settings: "tnum";
    }
    .kpi-badge {
        font-size: 0.72rem;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 6px;
        display: inline-block;
        width: fit-content;
    }
    .badge-emerald { background: rgba(16, 185, 129, 0.2); color: #34d399 !important; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa !important; border: 1px solid rgba(59, 130, 246, 0.4); }
    .badge-amber { background: rgba(245, 158, 11, 0.2); color: #fbbf24 !important; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc !important; border: 1px solid rgba(168, 85, 247, 0.4); }
    .badge-coral { background: rgba(248, 113, 113, 0.2); color: #f87171 !important; border: 1px solid rgba(248, 113, 113, 0.4); }

    /* Streamlit Native Metric Fixes for Dark Mode */
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.25) !important;
    }
    div[data-testid="stMetricLabel"] * {
        color: #94a3b8 !important;
        font-size: 0.80rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetricValue"] * {
        color: #ffffff !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stMetricDelta"] * {
        font-weight: 600 !important;
    }

    /* Clinical Decision Support Metric Cards */
    .metric-card {
        background-color: #1e293b !important;
        border-radius: 12px;
        padding: 22px;
        border: 1px solid #334155;
        border-left: 6px solid #3b82f6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 16px;
    }
    .metric-card h3 {
        color: #ffffff !important;
        margin-top: 0;
        margin-bottom: 12px;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .metric-card p, .metric-card li {
        color: #e2e8f0 !important;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .metric-card.success { border-left-color: #10b981 !important; background: rgba(16, 185, 129, 0.08) !important; }
    .metric-card.warning { border-left-color: #f59e0b !important; background: rgba(245, 158, 11, 0.08) !important; }
    .metric-card.danger { border-left-color: #ef4444 !important; background: rgba(239, 68, 68, 0.08) !important; }
    
    /* Archetype Mini Cards */
    .archetype-box {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .archetype-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .archetype-title {
        color: #ffffff;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .archetype-meta {
        color: #94a3b8;
        font-size: 0.82rem;
        line-height: 1.4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_DIR / "data" / "processed" / "careflow.db"
REPORTS_DIR = PROJECT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"
STAR_SCHEMA_DIR = REPORTS_DIR / "star_schema"

# ---------------------------------------------------------
# Data Loading & Caching Engine
# ---------------------------------------------------------
@st.cache_data
def load_master_metrics():
    """Load pre-aggregated master executive bundle."""
    master_path = REPORTS_DIR / "careflow_process_mining_master_summary.json"
    if master_path.exists():
        with open(master_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_patient_dimension():
    """Load dim_patient_cohort table from Star-Schema."""
    pt_path = STAR_SCHEMA_DIR / "dim_patient_cohort.csv"
    if pt_path.exists():
        return pd.read_csv(pt_path)
    return pd.DataFrame()

@st.cache_data
def load_fact_events():
    """Load fact_clinical_events table from Star-Schema."""
    fact_path = STAR_SCHEMA_DIR / "fact_clinical_events.csv"
    if fact_path.exists():
        return pd.read_csv(fact_path)
    return pd.DataFrame()

@st.cache_data
def load_cdss_recommendations():
    """Load automated CDSS risk stratification recommendations."""
    cdss_path = REPORTS_DIR / "clinical_decision_recommendations.csv"
    if cdss_path.exists():
        return pd.read_csv(cdss_path)
    return pd.DataFrame()

@st.cache_data
def load_trace_metrics():
    """Load trace-level duration and metrics."""
    trace_path = REPORTS_DIR / "trace_level_metrics.csv"
    if trace_path.exists():
        return pd.read_csv(trace_path)
    return pd.DataFrame()

# Load all cached datasets
master_data = load_master_metrics()
df_patients = load_patient_dimension()
df_facts = load_fact_events()
df_cdss = load_cdss_recommendations()
df_traces = load_trace_metrics()

# ---------------------------------------------------------
# Sidebar Navigation & Global Filters
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/fluency/96/hospital-3.png", width=70)
st.sidebar.title("CareFlow Analytics")
st.sidebar.caption("Infotact Solutions Batch-22.1 | CareFlow BI")

page = st.sidebar.radio(
    "Navigation Views",
    [
        "📊 Executive KPI Overview",
        "🗺️ Clinical Pathway Discovery",
        "⏱️ Bottleneck & Golden Hour SLA",
        "🛏️ Inter-Ward Queues & Lab TAT",
        "🩺 Live CDSS Triage & Risk Calculator",
        "📦 Star-Schema Data Warehouse"
    ],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("Cohort Filters")

# Care Archetype Filter
archetype_options = ["All Archetypes", "Rapid ER Discharge (21%)", "Standard Ward Care (46%)", "Critical ICU Escalation (33%)"]
selected_archetype = st.sidebar.selectbox("Patient Care Archetype", archetype_options)

# Sepsis Golden Hour SLA Filter
sla_filter = st.sidebar.selectbox("Sepsis Golden Hour Status", ["All Patients", "SLA Compliant (<=60m)", "SLA Delayed (>60m)"])

# Age Filter
min_age, max_age = 18, 95
if not df_patients.empty and "age" in df_patients.columns:
    min_age = int(df_patients["age"].min())
    max_age = int(df_patients["age"].max())
selected_age_range = st.sidebar.slider("Patient Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **Role:** Member 4 — BI Dashboard Specialist  
    **Collaborator:** Member 3 — Process Mining Analyst  
    **Data Model:** 5-Table Star Schema Data Warehouse
    """
)

# ---------------------------------------------------------
# Header Banner
# ---------------------------------------------------------
st.markdown(
    """
    <div class="hero-banner">
        <h1>🏥 CareFlow: Clinical Intelligence Center</h1>
        <p>Interactive process mining, hospital bottleneck diagnostics, and clinical decision support for sepsis treatment pathways.</p>
        <span class="hero-pill">⚡ Live Star-Schema Integration</span>
        <span class="hero-pill" style="margin-left: 8px;">🎯 Sepsis Golden Hour SLA: 84.8%</span>
        <span class="hero-pill" style="margin-left: 8px;">🛡️ Token Replay Fitness: 100%</span>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# VIEW 1: Executive KPI Overview
# ---------------------------------------------------------
if page == "📊 Executive KPI Overview":
    st.subheader("Executive Clinical & Operational KPIs")
    st.markdown("High-level summary of hospital throughput, guideline conformance, and patient risk across **1,050 cohort encounters**.")

    kpis = master_data.get("executive_kpis", {})

    # Custom HTML KPI Grid with Guaranteed Dark/Light Contrast
    kpi_html = f"""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-header">👥 TOTAL PATIENTS</div>
            <div class="kpi-value">{kpis.get('total_patient_cases', 1050):,}</div>
            <div class="kpi-badge badge-blue">1,050 Sepsis Cohort</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-header">📋 RECORDED EVENTS</div>
            <div class="kpi-value">{kpis.get('total_recorded_events', 15213):,}</div>
            <div class="kpi-badge badge-purple">16 Activities</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-header">⚡ GOLDEN HOUR SLA</div>
            <div class="kpi-value">{kpis.get('sepsis_antibiotics_golden_hour_compliance_pct', 84.8):.1f}%</div>
            <div class="kpi-badge badge-emerald">↑ 84.8% &le; 60m SLA</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-header">🛡️ 3-HOUR SSC BUNDLE</div>
            <div class="kpi-value">{kpis.get('sepsis_antibiotics_three_hour_bundle_compliance_pct', 96.5):.1f}%</div>
            <div class="kpi-badge badge-emerald">Surviving Sepsis</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-header">🔄 UNPLANNED READMIT</div>
            <div class="kpi-value">{kpis.get('unplanned_er_readmission_rate_pct', 28.0):.1f}%</div>
            <div class="kpi-badge badge-coral">294 Return ER Cases</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-header">🧪 CENTRAL LAB (B)</div>
            <div class="kpi-value">53.31%</div>
            <div class="kpi-badge badge-amber">8,110 Diagnostic Orders</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)

    st.markdown("---")

    col_arch, col_workload = st.columns([1, 1])

    with col_arch:
        st.subheader("Care Archetype Segmentation")
        st.markdown("Process mining variant clustering revealed **3 distinct clinical archetypes** within the sepsis cohort:")

        archetypes = master_data.get("care_archetypes", {})
        arch1 = archetypes.get("archetype_1_rapid_er", {"prevalence_pct": 21.05, "cases": 221, "median_stay_days": 0.03, "readmission_pct": 0.0})
        arch2 = archetypes.get("archetype_2_inpatient_ward", {"prevalence_pct": 46.0, "cases": 483, "median_stay_days": 4.85, "readmission_pct": 8.9})
        arch3 = archetypes.get("archetype_3_critical_icu", {"prevalence_pct": 32.95, "cases": 346, "median_stay_days": 44.7, "readmission_pct": 72.5})

        st.markdown(
            f"""
            <div class="archetype-box">
                <div class="archetype-header">
                    <span class="archetype-title">🟢 1. Rapid ER Discharge</span>
                    <span class="kpi-badge badge-emerald">{arch1['prevalence_pct']}% ({arch1['cases']} pts)</span>
                </div>
                <div class="archetype-meta">Median stay: <b>{arch1['median_stay_days']} days</b> | Readmissions: <b>{arch1['readmission_pct']}%</b><br>Mild infection ruled out; patients discharged home from emergency unit.</div>
            </div>
            
            <div class="archetype-box">
                <div class="archetype-header">
                    <span class="archetype-title">🟡 2. Standard Inpatient Ward</span>
                    <span class="kpi-badge badge-amber">{arch2['prevalence_pct']}% ({arch2['cases']} pts)</span>
                </div>
                <div class="archetype-meta">Median stay: <b>{arch2['median_stay_days']} days</b> | Readmissions: <b>{arch2['readmission_pct']}%</b><br>Confirmed sepsis; admission to normal care ward (Admission NC) with IV antibiotics.</div>
            </div>
            
            <div class="archetype-box">
                <div class="archetype-header">
                    <span class="archetype-title">🔴 3. Critical ICU Escalation</span>
                    <span class="kpi-badge badge-coral">{arch3['prevalence_pct']}% ({arch3['cases']} pts)</span>
                </div>
                <div class="archetype-meta">Median stay: <b>{arch3['median_stay_days']} days</b> | Readmissions: <b>{arch3['readmission_pct']}%</b><br>Severe sepsis with organ dysfunction; ICU escalation and prolonged inpatient stay.</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        arch_img = FIGURES_DIR / "variant_archetypes_pie.png"
        if arch_img.exists():
            st.image(str(arch_img), use_container_width=True)

    with col_workload:
        st.subheader("Hospital Department Workload Concentration")
        st.markdown("Distribution of clinical activities processed across hospital administrative & diagnostic divisions:")

        workload = master_data.get("workload_by_department", {
            "Central Diagnostic Laboratory (B)": "53.31% (8,110 events, 96.5% reach)",
            "Emergency Clinical Staff (A & L)": "24.16% (3,675 events, 95.2% reach)",
            "General Inpatient Wards (F, O, G, etc.)": "7.82% (1,189 events, 80.9% reach)",
            "Emergency Triage Unit (C)": "6.92% (1,053 events, 100.0% reach)",
            "Discharge Administration (E)": "5.14% (782 events, 74.5% reach)",
            "Emergency Readmission (?)": "1.93% (294 events, 28.0% reach)",
            "Intensive Care Units (P, W, J, K)": "0.72% (110 events, 10.5% reach)"
        })

        wl_df = pd.DataFrame([
            {"Hospital Division": k, "Volume Share & Reach": v}
            for k, v in workload.items()
        ])
        st.dataframe(wl_df, use_container_width=True, hide_index=True)

        wl_img = FIGURES_DIR / "org_workload_distribution.png"
        if wl_img.exists():
            st.image(str(wl_img), use_container_width=True)

# ---------------------------------------------------------
# VIEW 2: Clinical Pathway Discovery
# ---------------------------------------------------------
elif page == "🗺️ Clinical Pathway Discovery":
    st.subheader("Process Discovery: Dominant Pathways vs Hospital Complexity")
    st.markdown("Interactive comparison between the clinical guideline **Happy Path** and the unfiltered **Spaghetti Process Map**.")

    view_mode = st.radio(
        "Select Process Mining Map View",
        [
            "🌟 Dominant Happy Path (32.8% of Cohort)",
            "🍝 Unfiltered Spaghetti Process Map (691 Variants)",
            "🔬 Inductive Petri Net (WF-Net with 39 Places)",
            "⚡ Heuristic Causal Net (Dependency >= 0.5)"
        ],
        horizontal=True
    )

    if "Happy Path" in view_mode:
        col_img, col_txt = st.columns([3, 2])
        with col_img:
            img_path = FIGURES_DIR / "happy_path.png"
            if img_path.exists():
                st.image(str(img_path), caption="Happy Path: Clean admission -> diagnostic triage -> release sequence", use_container_width=True)
        with col_txt:
            st.markdown("### Clinical Protocol Conformance")
            st.markdown(
                """
                - **Pathway:** `ER Registration` → `ER Triage` → `ER Sepsis Triage` → `CRP/Leucocytes` → `IV Antibiotics` → `Admission NC` → `Release A`.
                - **Prevalence:** Traversed by **344 patients (32.8%)** with zero pathway deviations.
                - **Median Duration:** **4.85 days**.
                - **Readmission Risk:** Only **8.9%** for patients strictly adhering to the standard sequence.
                """
            )
    elif "Spaghetti" in view_mode:
        img_path = FIGURES_DIR / "spaghetti_diagram.png"
        if img_path.exists():
            st.image(str(img_path), caption="Full Hospital Spaghetti Diagram: High-entropy repeat loops and non-standard transfers", use_container_width=True)
        st.warning("⚠️ High visual complexity indicates extensive repeated laboratory diagnostics, inter-ward transfers, and unstructured readmission loops.")

    elif "Petri Net" in view_mode:
        col_pn, col_pn_info = st.columns([3, 2])
        with col_pn:
            img_path = FIGURES_DIR / "petri_net_topology.png"
            if img_path.exists():
                st.image(str(img_path), caption="Inductive Petri Net WF-Net Topology (reports/models/sepsis_petri_net.pnml)", use_container_width=True)
        with col_pn_info:
            st.markdown("### Mathematical Soundness & Replay")
            st.markdown(
                """
                - **Topology:** 39 places, 50 transitions (16 clinical, 34 silent tau), 116 directed arcs.
                - **Token-Based Replay (TBR):** **100.0% mean trace fitness** across all 1,050 cases.
                - **Token Conservation:** 49,273 tokens produced and consumed with **0 missing** and **0 remaining**.
                """
            )
            tbr_img = FIGURES_DIR / "token_fitness_distribution.png"
            if tbr_img.exists():
                st.image(str(tbr_img), use_container_width=True)

    else:
        img_path = FIGURES_DIR / "heuristic_net_topology.png"
        if img_path.exists():
            st.image(str(img_path), caption="Heuristic Causal Net: Robust dependencies with D >= 0.5 thresholding", use_container_width=True)

    st.markdown("---")
    st.subheader("Top Clinical Pathway Variants")
    variant_csv = REPORTS_DIR / "variant_analysis.csv"
    if variant_csv.exists():
        df_variants = pd.read_csv(variant_csv)
        st.dataframe(df_variants.head(20), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# VIEW 3: Bottleneck & Golden Hour SLA
# ---------------------------------------------------------
elif page == "⏱️ Bottleneck & Golden Hour SLA":
    st.subheader("Sepsis Golden Hour SLA Compliance & Operational Bottlenecks")
    st.markdown("Tracking hospital adherence to the **Surviving Sepsis Campaign (SSC)** 1-hour antibiotic administration target.")

    col_sla1, col_sla2, col_sla3 = st.columns(3)
    with col_sla1:
        st.metric("Median Time to Antibiotics", "44.0 minutes", "-16.0 min vs SLA Limit", delta_color="normal")
    with col_sla2:
        st.metric("Golden Hour Compliance", "84.8%", "446 / 526 evaluated cases", delta_color="normal")
    with col_sla3:
        st.metric("Delayed Beyond 60 min", "15.2%", "80 patients delayed", delta_color="inverse")

    col_sla_img, col_bn_img = st.columns(2)
    with col_sla_img:
        sla_img = FIGURES_DIR / "sepsis_golden_hour_sla.png"
        if sla_img.exists():
            st.image(str(sla_img), caption="Time from ER Sepsis Triage to IV Antibiotics Distribution", use_container_width=True)
    with col_bn_img:
        bn_img = FIGURES_DIR / "bottleneck_heatmap.png"
        if bn_img.exists():
            st.image(str(bn_img), caption="Clinical Step Bottlenecks Ranked by Median Delay Hours", use_container_width=True)

    st.subheader("Top Identified Hospital Bottlenecks")
    bottlenecks = master_data.get("top_clinical_bottlenecks", [
        {"step": "Admission NC -> Admission IC", "median_delay_hours": 5.01, "severity": "High (ICU Escalation Latency)"},
        {"step": "Admission IC -> Admission NC", "median_delay_hours": 7.35, "severity": "Moderate (Step-Down Bed Wait)"},
        {"step": "CRP -> CRP (Repeat Lab)", "median_delay_hours": 24.0, "severity": "Routine Inpatient Cycle (68.7% Patients)"},
        {"step": "Leucocytes -> Leucocytes", "median_delay_hours": 24.0, "severity": "Routine Inpatient Cycle (66.9% Patients)"},
        {"step": "ER Sepsis Triage -> IV Antibiotics", "median_delay_hours": 0.73, "severity": "Clinical SLA Target: <=1.0h (15.2% Exceeding)"}
    ])
    st.dataframe(pd.DataFrame(bottlenecks), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Diagnostic Rework & Repetitive Testing Loops")
    rework_img = FIGURES_DIR / "rework_frequency.png"
    if rework_img.exists():
        st.image(str(rework_img), caption="Repeat Testing Rates: CRP (68.7%), Leucocytes (66.9%), Lactic Acid (20.0%)", use_container_width=True)

# ---------------------------------------------------------
# VIEW 4: Inter-Ward Queues & Lab TAT
# ---------------------------------------------------------
elif page == "🛏️ Inter-Ward Queues & Lab TAT":
    st.subheader("Bed-to-Bed Transfer Latencies & Diagnostic Laboratory Turnaround")
    st.markdown("Quantifying transfer bottlenecks between hospital care units and diagnostic turnaround performance in Central Lab B.")

    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
    with col_t1:
        st.metric("ER to Ward Transfer", "1.60 hrs", "p90: 4.57 hrs")
    with col_t2:
        st.metric("Ward to ICU Escalation", "5.01 hrs", "p90: 13.82 hrs (Primary Delay)", delta_color="inverse")
    with col_t3:
        st.metric("ICU Step-Down Delay", "7.35 hrs", "p90: 14.64 hrs", delta_color="inverse")
    with col_t4:
        st.metric("Lab B Median TAT", "24.5 min", "p90: 49.6 min (95% <= 60m)")

    col_tat_img, col_tr_img = st.columns(2)
    with col_tat_img:
        tat_img = FIGURES_DIR / "diagnostic_turnaround_distribution.png"
        if tat_img.exists():
            st.image(str(tat_img), caption="Laboratory Turnaround Distribution (CRP, Leucocytes, Lactic Acid)", use_container_width=True)
    with col_tr_img:
        tr_img = FIGURES_DIR / "inter_ward_transfer_delays.png"
        if tr_img.exists():
            st.image(str(tr_img), caption="Inter-Ward Transfer Latency and Patient Transition Counts", use_container_width=True)

    col_tat_tbl, col_tr_tbl = st.columns(2)
    with col_tat_tbl:
        tat_csv = REPORTS_DIR / "diagnostic_turnaround_metrics.csv"
        if tat_csv.exists():
            st.markdown("#### Diagnostic Turnaround Metrics Table")
            st.dataframe(pd.read_csv(tat_csv), use_container_width=True, hide_index=True)
    with col_tr_tbl:
        tr_csv = REPORTS_DIR / "inter_ward_transfer_metrics.csv"
        if tr_csv.exists():
            st.markdown("#### Inter-Ward Transfer Latency Table")
            st.dataframe(pd.read_csv(tr_csv), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# VIEW 5: Live CDSS Triage & Risk Calculator
# ---------------------------------------------------------
elif page == "🩺 Live CDSS Triage & Risk Calculator":
    st.subheader("Automated Clinical Decision Support System (CDSS)")
    st.markdown("Real-time **Sepsis Pathway Escalation Score (SPES, 0–10 scale)** calculation and cohort escalation tracking.")

    st.markdown("### 🧮 Interactive Patient Risk Stratifier")
    st.markdown("Simulate patient admission parameters to determine clinical risk tier, protocol escalation, and bed allocation:")

    calc_col1, calc_col2 = st.columns([1, 1])

    with calc_col1:
        st.markdown("#### Patient Clinical Parameters")
        input_age = st.slider("Patient Age", 18, 95, 68)
        input_sirs = st.radio("SIRS Criteria Met", [0, 1, 2, 3, 4], index=2, horizontal=True)
        input_dysfunction = st.checkbox("Suspected Organ Dysfunction (SOFA / Shock)", value=True)
        input_repeats = st.slider("Diagnostic Testing Repeat Batches", 1, 8, 3)
        input_icu = st.checkbox("Requires Intensive Care Unit (ICU) Bed", value=False)
        input_lactate = st.number_input("Serum Lactic Acid (mmol/L)", min_value=0.5, max_value=12.0, value=2.8, step=0.1)

    # Calculate SPES Score dynamically
    spes_score = 0
    if input_age >= 65: spes_score += 1
    if input_sirs >= 2: spes_score += 2
    if input_dysfunction: spes_score += 3
    if input_repeats >= 2: spes_score += 1
    if input_icu: spes_score += 2
    if input_lactate >= 2.0: spes_score += 1
    spes_score = min(spes_score, 10)

    with calc_col2:
        st.markdown("#### Real-Time Evaluated Risk & Actionable Protocol")
        if spes_score <= 2:
            st.markdown(
                f"""
                <div class="metric-card success">
                    <h3>🟢 LOW RISK (SPES Score: {spes_score}/10)</h3>
                    <p><b>Recommended Clinical Protocol:</b></p>
                    <ul>
                        <li>Ambulatory observation / Outpatient discharge candidate</li>
                        <li>Routine oral antibiotics if localized infection confirmed</li>
                        <li>No intensive monitoring or inpatient escalation required</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif spes_score <= 5:
            st.markdown(
                f"""
                <div class="metric-card warning">
                    <h3>🟡 MODERATE RISK (SPES Score: {spes_score}/10)</h3>
                    <p><b>Recommended Clinical Protocol:</b></p>
                    <ul>
                        <li>Admit to General Inpatient Ward (Admission NC)</li>
                        <li>Administer IV Antibiotics within 60 minutes (Golden Hour SLA)</li>
                        <li>Order 24-hour repeat CRP and Leucocyte testing</li>
                        <li>Serial lactate monitoring every 6 hours</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div class="metric-card danger">
                    <h3>🔴 CRITICAL HIGH RISK (SPES Score: {spes_score}/10)</h3>
                    <p><b>Recommended Clinical Protocol (STAT):</b></p>
                    <ul>
                        <li><b>STAT IV Antibiotics (&le; 30 minutes)</b></li>
                        <li><b>Immediate ICU Escalation Bed Reservation (Admission IC)</b></li>
                        <li>Fluid resuscitation: 30 mL/kg crystalloid for hypotension/lactate &ge; 4.0</li>
                        <li>Repeat serum lactate within 2 hours</li>
                        <li>Continuous arterial line & hemodynamic monitoring</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.subheader("Cohort High-Risk Queue (543 Patients Identified)")
    st.markdown("Searchable registry of all cohort patients identified as **High Risk** requiring protocolized intervention:")

    if not df_cdss.empty:
        search_case = st.text_input("Search by Case ID (e.g. 'A', 'B', 'BA')", "")
        filtered_cdss = df_cdss
        if search_case:
            filtered_cdss = filtered_cdss[filtered_cdss["case_id"].astype(str).str.contains(search_case, case=False)]

        st.dataframe(filtered_cdss.head(30), use_container_width=True, hide_index=True)
        
        csv_bytes = df_cdss.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export High-Risk Patient Registry (CSV)",
            data=csv_bytes,
            file_name="careflow_high_risk_patients.csv",
            mime="text/csv"
        )

# ---------------------------------------------------------
# VIEW 6: Star-Schema Data Warehouse
# ---------------------------------------------------------
elif page == "📦 Star-Schema Data Warehouse":
    st.subheader("Dimensional Star-Schema Data Warehouse")
    st.markdown("Direct inspection of the 5 relational tables engineered for enterprise Power BI and analytics reporting.")

    schema_img = FIGURES_DIR / "star_schema_entity_relationship.png"
    if schema_img.exists():
        st.image(str(schema_img), caption="Star Schema Architecture: fact_clinical_events (15,213 rows) connected to 4 dimension tables", use_container_width=True)

    tab_fact, tab_pt, tab_act, tab_dept, tab_time = st.tabs([
        "fact_clinical_events (15,213 rows)",
        "dim_patient_cohort (1,050 rows)",
        "dim_activity (16 rows)",
        "dim_department (26 rows)",
        "dim_time_bucket (5 tiers)"
    ])

    with tab_fact:
        st.markdown("**Fact Table: Clinical Events with Transition Duration & SLA Flags**")
        if not df_facts.empty:
            st.dataframe(df_facts.head(25), use_container_width=True, hide_index=True)
            st.caption(f"Total Rows: {len(df_facts):,} | Foreign Keys: patient_cohort_key, activity_key, department_key, time_bucket_key")

    with tab_pt:
        st.markdown("**Dimension Table: Patient Demographics, Clinical Status & Care Archetypes**")
        if not df_patients.empty:
            st.dataframe(df_patients.head(25), use_container_width=True, hide_index=True)
            st.caption(f"Total Cohort Patients: {len(df_patients):,}")

    with tab_act:
        act_csv = STAR_SCHEMA_DIR / "dim_activity.csv"
        if act_csv.exists():
            st.markdown("**Dimension Table: Clinical Activities & Workflow Phases**")
            st.dataframe(pd.read_csv(act_csv), use_container_width=True, hide_index=True)

    with tab_dept:
        dept_csv = STAR_SCHEMA_DIR / "dim_department.csv"
        if dept_csv.exists():
            st.markdown("**Dimension Table: Hospital Departments & Organizational Divisions**")
            st.dataframe(pd.read_csv(dept_csv), use_container_width=True, hide_index=True)

    with tab_time:
        time_csv = STAR_SCHEMA_DIR / "dim_time_bucket.csv"
        if time_csv.exists():
            st.markdown("**Dimension Table: Transition Duration SLA Tiers**")
            st.dataframe(pd.read_csv(time_csv), use_container_width=True, hide_index=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption("CareFlow: Clinical Pathway Process Mining | Infotact Solutions Batch-22.1 | Member 3 (Process Mining) & Member 4 (BI Specialist)")
