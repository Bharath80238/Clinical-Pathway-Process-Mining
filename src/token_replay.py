"""CareFlow Token-Based Replay Simulation & Trace Fitness Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
PNML_PATH = PROJECT_ROOT / "reports" / "models" / "sepsis_petri_net.pnml"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_process_event_log(db_path=DB_PATH):
    """Load and format events for token-based replay."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)

    event_log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="event_time",
    )
    return event_log

def load_petri_net_model(pnml_path=PNML_PATH):
    """Load formal Petri Net model or mine if missing."""
    if Path(pnml_path).exists():
        net, initial_marking, final_marking = pm4py.read_pnml(str(pnml_path))
        print(f"Loaded Petri net model from PNML: {pnml_path}")
    else:
        print("PNML file not found, discovering Inductive Petri Net dynamically...")
        log = load_process_event_log()
        net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log)
    return net, initial_marking, final_marking

def execute_token_based_replay(event_log, net, initial_marking, final_marking):
    """Execute token-based replay simulation across all patient traces."""
    print("Executing token-based replay simulation across event log...")
    replay_results = pm4py.conformance_diagnostics_token_based_replay(
        event_log, net, initial_marking, final_marking
    )

    case_ids = list(event_log.groupby("case:concept:name").groups.keys())
    
    trace_records = []
    for cid, res in zip(case_ids, replay_results):
        trace_records.append({
            "case_id": cid,
            "trace_is_fit": bool(res.get("trace_is_fit", False)),
            "trace_fitness": round(float(res.get("trace_fitness", 0.0)), 4),
            "produced_tokens": int(res.get("produced_tokens", 0)),
            "consumed_tokens": int(res.get("consumed_tokens", 0)),
            "missing_tokens": int(res.get("missing_tokens", 0)),
            "remaining_tokens": int(res.get("remaining_tokens", 0)),
        })

    trace_df = pd.DataFrame(trace_records)

    # Global log fitness
    mean_fitness = round(float(trace_df["trace_fitness"].mean()), 4)
    median_fitness = round(float(trace_df["trace_fitness"].median()), 4)
    perfectly_fit_cases = int(trace_df["trace_is_fit"].sum())
    fit_share_pct = round((perfectly_fit_cases / len(trace_df)) * 100, 2)

    summary = {
        "total_evaluated_traces": len(trace_df),
        "mean_trace_fitness": mean_fitness,
        "median_trace_fitness": median_fitness,
        "perfectly_fit_traces": perfectly_fit_cases,
        "perfectly_fit_share_pct": fit_share_pct,
        "total_produced_tokens": int(trace_df["produced_tokens"].sum()),
        "total_consumed_tokens": int(trace_df["consumed_tokens"].sum()),
        "total_missing_tokens": int(trace_df["missing_tokens"].sum()),
        "total_remaining_tokens": int(trace_df["remaining_tokens"].sum()),
    }

    # Export CSV and JSON reports
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "token_replay_case_fitness.csv"
    trace_df.to_csv(csv_path, index=False)
    print(f"Exported case fitness CSV: {csv_path}")

    json_path = REPORTS_DIR / "token_replay_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported token replay summary JSON: {json_path}")

    return trace_df, summary

def plot_token_replay_diagnostics(trace_df, summary):
    """Plot token fitness distribution and token accounting charts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Panel 1: Trace fitness distribution
    fitness_vals = trace_df["trace_fitness"]
    ax1.hist(fitness_vals, bins=15, color="#16a085", edgecolor="black", alpha=0.85)
    ax1.axvline(fitness_vals.mean(), color="#e74c3c", linestyle="--", linewidth=2, label=f"Mean Fitness ({summary['mean_trace_fitness']:.3f})")
    ax1.set_title("Trace Replay Fitness Distribution (Petri Net Model)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Token Fitness Score (0.0 to 1.0)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Patient Cases", fontsize=10, fontweight="bold")
    ax1.legend(frameon=True, facecolor="white")

    # Panel 2: Token Accounting Breakdown
    token_labels = ["Produced Tokens\n(p)", "Consumed Tokens\n(c)", "Missing Tokens\n(m)", "Remaining Tokens\n(r)"]
    token_counts = [
        summary["total_produced_tokens"],
        summary["total_consumed_tokens"],
        summary["total_missing_tokens"],
        summary["total_remaining_tokens"],
    ]
    colors = ["#2980b9", "#27ae60", "#e74c3c", "#f39c12"]

    bars = ax2.bar(token_labels, token_counts, color=colors, edgecolor="black", alpha=0.85)
    ax2.set_title("Global Token Accounting Across 1,050 Patient Traces", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Total Tokens", fontsize=10, fontweight="bold")

    for bar in bars:
        h = bar.get_height()
        ax2.annotate(
            f"{int(h):,}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "token_fitness_distribution.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created token fitness chart: {chart_path}")

def main():
    print("Loading event log...")
    log = load_process_event_log()
    net, im, fm = load_petri_net_model()
    trace_df, summary = execute_token_based_replay(log, net, im, fm)
    plot_token_replay_diagnostics(trace_df, summary)

    print("\n--- Token-Based Replay Global Conformance Metrics ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("\nToken-based replay simulation completed successfully.")

if __name__ == "__main__":
    main()
