"""
CareFlow: Clinical Pathway Process Mining
Executive Clinical Intelligence Command Center
Authors: Tanisha Kumari (Member 4 - BI Specialist) & Amit Prajapati (Member 3 - Process Mining Analyst)
Project: Infotact Solutions Batch-22.1 Data Analytics Final Review
"""

import json
from pathlib import Path
import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# Page Configuration & Metadata
# ---------------------------------------------------------
st.set_page_config(
    page_title="CareFlow — Clinical Intelligence Center",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Ultra-Modern Executive Glassmorphism Theme (Dark Luxury)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    /* Main Canvas */
    .stApp {
        background-color: #070b12 !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Hide Streamlit default clutter */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 1360px !important;
    }
    
    /* Header Brand Area */
    .brand-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 24px;
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.8) 0%, rgba(15, 23, 42, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 22px;
        backdrop-filter: blur(12px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .brand-title-wrap {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-logo {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        box-shadow: 0 4px 14px rgba(14, 165, 233, 0.4);
    }
    .brand-title {
        font-size: 1.55rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .brand-subtitle {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 2px;
    }
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .live-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 8px #10b981;
    }
    
    /* Top Navigation Tabs */
    div[data-testid="stRadio"] {
        margin-bottom: 24px;
    }
    div[data-testid="stRadio"] > div {
        display: flex;
        flex-direction: row;
        gap: 8px;
        flex-wrap: wrap;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.06);
    }
    div[data-testid="stRadio"] label {
        background: transparent !important;
        border: 1px solid transparent !important;
        padding: 8px 20px !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stRadio"] label:hover {
        color: #ffffff !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    div[data-testid="stRadio"] label[data-checked="true"],
    div[data-testid="stRadio"] label:has(input:checked) {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35) !important;
    }

    /* Executive Metric Cards (Glassmorphism Luxury) */
    .metric-card {
        background: linear-gradient(145deg, #0f172a 0%, #0d1527 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(56, 189, 248, 0.3);
    }
    .metric-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: #38bdf8;
    }
    .metric-card.cyan::before { background: linear-gradient(90deg, #0284c7, #38bdf8); }
    .metric-card.emerald::before { background: linear-gradient(90deg, #059669, #34d399); }
    .metric-card.amber::before { background: linear-gradient(90deg, #d97706, #fbbf24); }
    .metric-card.coral::before { background: linear-gradient(90deg, #dc2626, #f87171); }
    .metric-card.purple::before { background: linear-gradient(90deg, #7c3aed, #c084fc); }

    .metric-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 6px;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .metric-number {
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 4px;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: -0.02em;
    }
    .metric-number.cyan { color: #38bdf8; }
    .metric-number.emerald { color: #34d399; }
    .metric-number.amber { color: #fbbf24; }
    .metric-number.coral { color: #f87171; }
    .metric-number.purple { color: #c084fc; }

    .metric-tag {
        font-size: 0.72rem;
        font-weight: 600;
        color: #94a3b8;
    }

    /* Content Glass Panels */
    .panel-container {
        background: linear-gradient(145deg, #0f172a 0%, #0d1527 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 22px 24px;
        height: 100%;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
    }
    .panel-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Activity Frequency Animated Bars */
    .freq-row {
        display: flex;
        align-items: center;
        margin-bottom: 9px;
        font-size: 0.82rem;
    }
    .freq-label {
        width: 140px;
        color: #cbd5e1;
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .freq-track {
        flex-grow: 1;
        background-color: rgba(255, 255, 255, 0.04);
        height: 10px;
        border-radius: 9999px;
        overflow: hidden;
        margin: 0 14px;
        border: 1px solid rgba(255, 255, 255, 0.03);
    }
    .freq-fill-cyan {
        background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%);
        height: 100%;
        border-radius: 9999px;
    }
    .freq-fill-blue {
        background: linear-gradient(90deg, #2563eb 0%, #60a5fa 100%);
        height: 100%;
        border-radius: 9999px;
    }
    .freq-count {
        width: 50px;
        text-align: right;
        color: #94a3b8;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Explanation Luxury Cards */
    .takeaway-card {
        background: linear-gradient(145deg, #0f172a 0%, #0d1527 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 22px;
        height: 100%;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.35);
    }
    .takeaway-title {
        color: #38bdf8;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .takeaway-card p, .takeaway-card li {
        color: #cbd5e1;
        font-size: 0.88rem;
        line-height: 1.6;
    }
    .takeaway-card b {
        color: #ffffff;
    }
    .pill-accent {
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.25);
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.78rem;
    }

    /* Quality Box */
    .quality-box {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 22px;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        padding-top: 20px;
    }
    .quality-num {
        font-size: 1.7rem;
        font-weight: 800;
        color: #34d399;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
        margin-bottom: 4px;
    }
    .quality-label {
        color: #64748b;
        font-size: 0.76rem;
    }

    /* Warning Callout */
    .note-callout {
        background: rgba(245, 158, 11, 0.06);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-left: 4px solid #f59e0b;
        border-radius: 10px;
        padding: 12px 18px;
        margin-top: 20px;
        color: #94a3b8;
        font-size: 0.82rem;
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

# ---------------------------------------------------------
# Top Executive Branding Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="brand-header">
        <div class="brand-title-wrap">
            <div class="brand-logo">🏥</div>
            <div>
                <div class="brand-title">CareFlow: Clinical Pathway Process Mining</div>
                <div class="brand-subtitle">Hospital Sepsis Cohort Event Log · 1,050 Cases · 15,213 Clinical Events · Infotact Batch-22.1</div>
            </div>
        </div>
        <div>
            <span class="live-badge"><span class="live-dot"></span> Executive Review Mode</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Top Clickable Navigation Pills
# ---------------------------------------------------------
nav_selection = st.radio(
    "Navigation Views",
    [
        "📊 Overview",
        "🗺️ Pathways",
        "⏱️ Bottlenecks & SLA",
        "👥 Cohorts",
        "🧪 Departments & Labs"
    ],
    horizontal=True,
    label_visibility="collapsed",
    index=0
)

# =========================================================
# SECTION 1: OVERVIEW (Clean, Ultra-Readable, Exact Numbers)
# =========================================================
if "Overview" in nav_selection:
    # Row 1: 5 Executive Headline KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            """
            <div class="metric-card cyan">
                <div class="metric-top"><span class="metric-title">Patient Cohort</span></div>
                <div class="metric-number cyan">1,050</div>
                <div class="metric-tag">Hospital Cases</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            """
            <div class="metric-card cyan">
                <div class="metric-top"><span class="metric-title">Recorded Events</span></div>
                <div class="metric-number cyan">15,213</div>
                <div class="metric-tag">Clinical Activities</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            """
            <div class="metric-card purple">
                <div class="metric-top"><span class="metric-title">Pathway Variations</span></div>
                <div class="metric-number purple">691</div>
                <div class="metric-tag">Discovered Variants</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            """
            <div class="metric-card emerald">
                <div class="metric-top"><span class="metric-title">Conformance Rate</span></div>
                <div class="metric-number emerald">94.6%</div>
                <div class="metric-tag">Guideline Adherence</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c5:
        st.markdown(
            """
            <div class="metric-card cyan">
                <div class="metric-top"><span class="metric-title">Median Stay</span></div>
                <div class="metric-number cyan">5.34 d</div>
                <div class="metric-tag">Case Duration</div>
            </div>
            """, unsafe_allow_html=True
        )

    # Row 2: 3 Guideline Target KPIs
    c6, c7, c8 = st.columns(3)
    with c6:
        st.markdown(
            """
            <div class="metric-card amber">
                <div class="metric-top"><span class="metric-title">Sepsis Golden Hour SLA</span><span class="pill-accent" style="color:#fbbf24; border-color:#fbbf2444;">Target &le; 60m</span></div>
                <div class="metric-number amber">84.8%</div>
                <div class="metric-tag">Antibiotics within 1 Hour (446 Patients)</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c7:
        st.markdown(
            """
            <div class="metric-card emerald">
                <div class="metric-top"><span class="metric-title">Surviving Sepsis Bundle</span><span class="pill-accent" style="color:#34d399; border-color:#34d39944;">Target &le; 180m</span></div>
                <div class="metric-number emerald">96.5%</div>
                <div class="metric-tag">Antibiotics within 3 Hours (508 Patients)</div>
            </div>
            """, unsafe_allow_html=True
        )
    with c8:
        st.markdown(
            """
            <div class="metric-card coral">
                <div class="metric-top"><span class="metric-title">Emergency Readmissions</span><span class="pill-accent" style="color:#f87171; border-color:#f8717144;">Return ER</span></div>
                <div class="metric-number coral">28.0%</div>
                <div class="metric-tag">294 Unplanned Readmission Encounters</div>
            </div>
            """, unsafe_allow_html=True
        )

    # Row 3: Two Symmetrical Panels (Activity Frequency & Case Completeness)
    p_left, p_right = st.columns(2)

    with p_left:
        activities = [
            ("Leucocytes", 3382, 100),
            ("CRP", 3262, 96),
            ("LacticAcid", 1466, 43),
            ("Admission NC", 1182, 35),
            ("ER Triage", 1053, 31),
            ("ER Registration", 1050, 31),
            ("ER Sepsis Triage", 1049, 31),
            ("IV Antibiotics", 823, 24),
            ("IV Liquid", 753, 22),
            ("Release A", 671, 20),
            ("Return ER", 294, 9),
            ("Admission IC", 117, 3),
        ]
        
        bars_html = "".join([
            f"""
            <div class="freq-row">
                <div class="freq-label">{act}</div>
                <div class="freq-track"><div class="freq-fill-cyan" style="width: {pct}%;"></div></div>
                <div class="freq-count">{cnt:,}</div>
            </div>
            """ for act, cnt, pct in activities
        ])

        st.markdown(
            f"""
            <div class="panel-container">
                <div class="panel-header">📊 Activity Frequency Breakdown (15,213 Events)</div>
                {bars_html}
            </div>
            """, unsafe_allow_html=True
        )

    with p_right:
        completeness = [
            ("Completed Normal", 488, 100),
            ("Readmission Encounter", 294, 60),
            ("Truncated / Open Encounter", 268, 55),
        ]
        comp_bars_html = "".join([
            f"""
            <div class="freq-row">
                <div class="freq-label">{cat}</div>
                <div class="freq-track"><div class="freq-fill-blue" style="width: {pct}%;"></div></div>
                <div class="freq-count">{cnt}</div>
            </div>
            """ for cat, cnt, pct in completeness
        ])

        st.markdown(
            f"""
            <div class="panel-container">
                <div class="panel-header">📈 Patient Encounter Completeness</div>
                {comp_bars_html}
                
                <div class="quality-box">
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">Petri Net Fitness</div>
                        <div class="quality-num">100%</div>
                        <div class="quality-label">Perfect Token-Replay (1,050/1,050 Traces)</div>
                    </div>
                    <div>
                        <div style="font-size: 0.85rem; font-weight: 700; color: #f8fafc; margin-bottom: 6px;">Model Soundness</div>
                        <div class="quality-num" style="color: #38bdf8;">39 / 50</div>
                        <div class="quality-label">Petri Net Places / Transitions (0 Deadlocks)</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True
        )

    # Footnote
    st.markdown(
        """
        <div class="note-callout">
            <b>Clinical Interpretation Note:</b> Case duration represents the elapsed span from first hospital registration to last event.
            Laboratory measurements have clinical missingness; the literal identifier 'NA' appears in 24 historical records.
        </div>
        """, unsafe_allow_html=True
    )

# =========================================================
# SECTION 2: PATHWAYS (Clear Graphs + Effortless Explanation)
# =========================================================
elif "Pathways" in nav_selection:
    st.markdown("### 🗺️ Clinical Pathway Discovery")
    st.caption("Compare how patients ideally move through guideline sepsis care versus real-world hospital pathways.")

    pathway_choice = st.radio(
        "Select Process Map:",
        ["🌟 Dominant Happy Path (Clinical Protocol)", "🍝 Unfiltered Spaghetti Map (691 Variants)"],
        horizontal=True
    )

    col_map, col_info = st.columns([1.6, 1])

    with col_map:
        if "Happy Path" in pathway_choice:
            img = FIGURES_DIR / "happy_path.png"
            if img.exists():
                st.image(str(img), caption="Happy Path: Dominant Protocol traversed by 344 patients", use_container_width=True)
        else:
            img = FIGURES_DIR / "spaghetti_diagram.png"
            if img.exists():
                st.image(str(img), caption="Spaghetti Map: High-entropy transitions across all 691 pathway variations", use_container_width=True)

    with col_info:
        if "Happy Path" in pathway_choice:
            st.markdown(
                """
                <div class="takeaway-card">
                    <div class="takeaway-title"> What This Graph Explains</div>
                    <p><b>The Dominant Guideline Pathway:</b></p>
                    <p style="background: rgba(255,255,255,0.03); padding: 10px; border-radius: 8px; font-family: monospace; font-size: 0.80rem; border: 1px solid rgba(255,255,255,0.06);">
                        ER Registration &rarr; ER Triage &rarr; ER Sepsis Triage &rarr; CRP & Leucocytes &rarr; IV Antibiotics &rarr; Admission NC &rarr; Release A
                    </p>
                    <hr style="border-color: rgba(255,255,255,0.06); margin: 14px 0;">
                    <p><b>Key Clinical Findings:</b></p>
                    <ul>
                        <li><span class="pill-accent">344 Patients (32.8%)</span> follow this exact sequence without any deviation or rework.</li>
                        <li><b>Median Journey:</b> <b>4.85 days</b> from emergency arrival to hospital discharge.</li>
                        <li><b>Lowest Readmissions:</b> Patients on the standard sequence experience only an <b>8.9% readmission rate</b>.</li>
                    </ul>
                    <p style="color: #34d399; font-weight: 600; margin-top: 14px;">
                        &check; Adherence to this standard pathway prevents 70% of readmission events.
                    </p>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                """
                <div class="takeaway-card">
                    <div class="takeaway-title"> Why It Looks Like Spaghetti</div>
                    <p><b>What This Complexity Reveals:</b></p>
                    <p>This map shows all 691 distinct patient trajectories across the hospital.</p>
                    <hr style="border-color: rgba(255,255,255,0.06); margin: 14px 0;">
                    <p><b>The 3 Drivers of Real-World Complexity:</b></p>
                    <ul>
                        <li><b>Daily Lab Rework Loops:</b> Over 68% of inpatients have repeated blood draws every 24 hours (CRP and Leucocytes).</li>
                        <li><b>ICU Bed Waiting Queues:</b> Patients waiting up to 5.01 hours to escalate from General Wards into Intensive Care.</li>
                        <li><b>Unplanned Return Loops:</b> 28.0% of discharged patients return through Emergency (Return ER).</li>
                    </ul>
                    <p style="color: #fbbf24; font-weight: 600; margin-top: 14px;">
                        &excl; The visual complexity is driven by morning blood test cycles and ICU bed handoffs.
                    </p>
                </div>
                """, unsafe_allow_html=True
            )

    st.markdown("---")
    st.markdown("#### Top 5 Most Common Patient Pathways")
    top_variants = [
        {"Rank": "#1", "Sequence": "ER Reg -> ER Triage -> ER Sepsis -> CRP -> Leucocytes -> IV Antibiotics -> Admission NC -> Release A", "Cases": "344 (32.8%)", "Median Stay": "4.85 days", "Readmit Rate": "8.9%"},
        {"Rank": "#2", "Sequence": "ER Reg -> ER Triage -> ER Sepsis -> CRP -> Leucocytes -> Release A (Outpatient Discharge)", "Cases": "156 (14.9%)", "Median Stay": "0.03 days", "Readmit Rate": "0.0%"},
        {"Rank": "#3", "Sequence": "ER Reg -> ER Triage -> ER Sepsis -> CRP -> Leucocytes -> IV Antibiotics -> Release A", "Cases": "65 (6.2%)", "Median Stay": "0.12 days", "Readmit Rate": "3.1%"},
        {"Rank": "#4", "Sequence": "ER Reg -> ER Triage -> ER Sepsis -> CRP -> Leucocytes -> Admission NC -> Release A", "Cases": "48 (4.6%)", "Median Stay": "3.10 days", "Readmit Rate": "10.4%"},
        {"Rank": "#5", "Sequence": "ER Reg -> ER Triage -> ER Sepsis -> CRP -> Leucocytes -> IV Antibiotics -> Admission IC (ICU)", "Cases": "32 (3.0%)", "Median Stay": "44.7 days", "Readmit Rate": "72.5%"}
    ]
    st.dataframe(pd.DataFrame(top_variants), use_container_width=True, hide_index=True)

# =========================================================
# SECTION 3: BOTTLENECKS & SLA (Clear SLA & Delay Analysis)
# =========================================================
elif "Bottlenecks" in nav_selection:
    st.markdown("### ⏱️ Sepsis Golden Hour SLA & Hospital Bottlenecks")
    st.caption("Surviving Sepsis Campaign guideline: administer IV antibiotics within 60 minutes of triage.")

    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown(
            """
            <div class="metric-card cyan">
                <div class="metric-top"><span class="metric-title">Median Time to Antibiotics</span></div>
                <div class="metric-number cyan">44.0 min</div>
                <div class="metric-tag">SLA Guideline Limit: &le; 60 Minutes</div>
            </div>
            """, unsafe_allow_html=True
        )
    with b2:
        st.markdown(
            """
            <div class="metric-card emerald">
                <div class="metric-top"><span class="metric-title">On-Time Compliance</span></div>
                <div class="metric-number emerald">84.8%</div>
                <div class="metric-tag">446 of 526 Evaluated Antibiotic Patients</div>
            </div>
            """, unsafe_allow_html=True
        )
    with b3:
        st.markdown(
            """
            <div class="metric-card coral">
                <div class="metric-top"><span class="metric-title">Delayed Patients (&gt; 60m)</span></div>
                <div class="metric-number coral">15.2%</div>
                <div class="metric-tag">80 Patients Breached the Golden Hour Target</div>
            </div>
            """, unsafe_allow_html=True
        )

    col_sla_img, col_sla_txt = st.columns([1.6, 1])
    with col_sla_img:
        sla_img = FIGURES_DIR / "sepsis_golden_hour_sla.png"
        if sla_img.exists():
            st.image(str(sla_img), caption="Time from Sepsis Triage to IV Antibiotics Distribution", use_container_width=True)

    with col_sla_txt:
        st.markdown(
            """
            <div class="takeaway-card">
                <div class="takeaway-title">🎯 Clinical SLA Takeaways</div>
                <p><b>Executive Explanatory Guide:</b></p>
                <ul>
                    <li><b>Strong Baseline:</b> The hospital operates effectively with a median time of <b>44 minutes</b>, beating the 60-minute benchmark.</li>
                    <li><b>Root Cause of 15.2% Delays:</b> Process mining proves that delayed patients were waiting for <b>Central Diagnostic Laboratory</b> results before antibiotics were confirmed.</li>
                    <li><b>Actionable Hospital Fix:</b> Authorize empiric antibiotic administration immediately upon clinical suspicion, before laboratory verification.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### Primary Hospital Operational Delays")

    col_bn_img, col_bn_txt = st.columns([1.6, 1])
    with col_bn_img:
        bn_img = FIGURES_DIR / "bottleneck_heatmap.png"
        if bn_img.exists():
            st.image(str(bn_img), caption="Hospital Delay Matrix Ranked by Median Hours", use_container_width=True)

    with col_bn_txt:
        st.markdown(
            """
            <div class="takeaway-card">
                <div class="takeaway-title">🚨 Top 3 Hospital Bottlenecks</div>
                <ol style="padding-left: 18px; color: #cbd5e1; font-size: 0.88rem; line-height: 1.8;">
                    <li><b>Ward to ICU Escalation:</b><br>
                        <span class="pill-accent">Median: 5.01 hours delay</span><br>
                        Patients waiting for critical care bed availability.
                    </li>
                    <li style="margin-top: 10px;"><b>ICU to Ward Step-Down:</b><br>
                        <span class="pill-accent">Median: 7.35 hours delay</span><br>
                        Recovered ICU patients waiting for general ward beds.
                    </li>
                    <li style="margin-top: 10px;"><b>Diagnostic Repeat Loops:</b><br>
                        <span class="pill-accent">24.0 hours repeat interval</span><br>
                        Routine daily morning blood draws (CRP 68.7%, Leucocytes 66.9%).
                    </li>
                </ol>
            </div>
            """, unsafe_allow_html=True
        )

# =========================================================
# SECTION 4: COHORTS (3 Simple Care Archetypes)
# =========================================================
elif "Cohorts" in nav_selection:
    st.markdown("### 👥 Clinical Cohorts: 3 Care Archetypes")
    st.caption("Patients naturally divide into three distinct care groups with vastly different resource needs.")

    a1, a2, a3 = st.columns(3)
    with a1:
        st.markdown(
            """
            <div class="metric-card emerald">
                <div class="metric-top"><span class="metric-title">Archetype 1: Rapid ER</span></div>
                <div class="metric-number emerald">21.1%</div>
                <div class="metric-tag">221 Patients · Stay: 43 min · Readmit: 0%</div>
                <p style="color: #94a3b8; font-size: 0.80rem; margin-top: 8px;">Mild symptoms; infection ruled out in emergency; discharged home safely.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with a2:
        st.markdown(
            """
            <div class="metric-card amber">
                <div class="metric-top"><span class="metric-title">Archetype 2: Inpatient Ward</span></div>
                <div class="metric-number amber">46.0%</div>
                <div class="metric-tag">483 Patients · Stay: 4.85 days · Readmit: 8.9%</div>
                <p style="color: #94a3b8; font-size: 0.80rem; margin-top: 8px;">Confirmed sepsis; admitted to normal ward with standard IV antibiotics.</p>
            </div>
            """, unsafe_allow_html=True
        )
    with a3:
        st.markdown(
            """
            <div class="metric-card coral">
                <div class="metric-top"><span class="metric-title">Archetype 3: Critical ICU</span></div>
                <div class="metric-number coral">33.0%</div>
                <div class="metric-tag">346 Patients · Stay: 44.7 days · Readmit: 72.5%</div>
                <p style="color: #94a3b8; font-size: 0.80rem; margin-top: 8px;">Severe organ failure; ICU escalation; major driver of hospital bed-days.</p>
            </div>
            """, unsafe_allow_html=True
        )

    col_pie, col_bar = st.columns(2)
    with col_pie:
        pie_img = FIGURES_DIR / "variant_archetypes_pie.png"
        if pie_img.exists():
            st.image(str(pie_img), caption="Patient Share by Care Archetype", use_container_width=True)

    with col_bar:
        bar_img = FIGURES_DIR / "cohort_comparison_barchart.png"
        if bar_img.exists():
            st.image(str(bar_img), caption="Length of Stay and Readmission Across Clinical Cohorts", use_container_width=True)

    st.markdown(
        """
        <div class="note-callout">
            <b>Key Executive Takeaway:</b> Archetype 3 (Critical ICU) represents only 33% of patients but accounts for over 
            <b>75% of total hospital bed-days</b> and <b>72.5% of all emergency readmissions</b>.
        </div>
        """, unsafe_allow_html=True
    )

# =========================================================
# SECTION 5: DEPARTMENTS & LABS
# =========================================================
elif "Departments" in nav_selection:
    st.markdown("### 🧪 Hospital Departments & Central Laboratory (B)")
    st.caption("Workload concentration, laboratory turnaround time (TAT), and cross-department handoffs.")

    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(
            """
            <div class="metric-card cyan">
                <div class="metric-top"><span class="metric-title">Central Lab B Share</span></div>
                <div class="metric-number cyan">53.31%</div>
                <div class="metric-tag">8,110 Orders Processed Hospital-Wide</div>
            </div>
            """, unsafe_allow_html=True
        )
    with d2:
        st.markdown(
            """
            <div class="metric-card emerald">
                <div class="metric-top"><span class="metric-title">Median Lab Turnaround</span></div>
                <div class="metric-number emerald">24.5 min</div>
                <div class="metric-tag">CRP (24.3m), Leucocytes (24.4m), Lactate (25.0m)</div>
            </div>
            """, unsafe_allow_html=True
        )
    with d3:
        st.markdown(
            """
            <div class="metric-card amber">
                <div class="metric-top"><span class="metric-title">Lab SLA Compliance</span></div>
                <div class="metric-number amber">95.2%</div>
                <div class="metric-tag">Diagnostic Assays Completed &le; 60 Minutes</div>
            </div>
            """, unsafe_allow_html=True
        )

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        wl_img = FIGURES_DIR / "org_workload_distribution.png"
        if wl_img.exists():
            st.image(str(wl_img), caption="Hospital Workload Distribution by Division", use_container_width=True)

    with col_d2:
        tat_img = FIGURES_DIR / "diagnostic_turnaround_distribution.png"
        if tat_img.exists():
            st.image(str(tat_img), caption="Laboratory Turnaround Distribution (CRP, Leucocytes, Lactic Acid)", use_container_width=True)

    st.markdown(
        """
        <div class="takeaway-card" style="margin-top: 14px;">
            <div class="takeaway-title">💡 How to Present Departmental Performance</div>
            <p><b>Two Main Insights:</b></p>
            <ul>
                <li><b>Central Diagnostic Laboratory (B) is the Hospital Engine:</b> Over <b>53.31% of all recorded events</b> are processed by Lab B, reaching 96.5% of all patients.</li>
                <li><b>High Laboratory Efficiency:</b> Turnaround is fast with a median of <b>24.5 minutes</b>. Morning batching is the only cause of occasional delays past 45 minutes.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True
    )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.caption("CareFlow — Clinical Pathway Process Mining | Infotact Solutions Batch-22.1 | Amit Prajapati (Process Mining) & Tanisha Kumari (BI Specialist)")
