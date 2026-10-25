"""CareFlow Heuristic Process Mining & Dependency Net Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_process_event_log(db_path=DB_PATH):
    """Load and format event data for heuristic mining with PM4Py."""
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

def compute_causal_dependency_matrix(event_log):
    """Compute formal heuristic dependency scores between all clinical activity pairs."""
    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
    activities = sorted(list(pm4py.get_event_attribute_values(event_log, "concept:name").keys()))

    dep_records = []
    for a in activities:
        for b in activities:
            ab_count = dfg.get((a, b), 0)
            ba_count = dfg.get((b, a), 0)

            if a == b:
                # Self-loop dependency measure
                dep_score = ab_count / (ab_count + 1.0)
            else:
                # Causal dependency measure between distinct activities
                total = ab_count + ba_count
                dep_score = (ab_count - ba_count) / (total + 1.0) if total > 0 else 0.0

            if ab_count > 0:
                dep_records.append({
                    "activity_from": a,
                    "activity_to": b,
                    "frequency_a_to_b": ab_count,
                    "frequency_b_to_a": ba_count,
                    "dependency_score": round(float(dep_score), 4),
                    "is_self_loop": (a == b),
                })

    dep_df = pd.DataFrame(dep_records).sort_values("dependency_score", ascending=False).reset_index(drop=True)
    return dep_df, dfg, start_activities, end_activities

def export_dependency_matrix(dep_df):
    """Export the causal dependency scores to CSV."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = REPORTS_DIR / "heuristic_dependency_matrix.csv"
    dep_df.to_csv(out_csv, index=False)
    print(f"Exported causal dependency matrix: {out_csv}")

def render_heuristic_net_topology(dep_df, min_dependency=0.5, min_frequency=50):
    """Filter out noise and render the statistically significant Causal Heuristic Net."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    G = nx.DiGraph()

    # Filter for significant causal dependencies
    filtered_edges = dep_df[
        (dep_df["dependency_score"] >= min_dependency)
        & (dep_df["frequency_a_to_b"] >= min_frequency)
    ].copy()

    for _, row in filtered_edges.iterrows():
        u = row["activity_from"]
        v = row["activity_to"]
        score = row["dependency_score"]
        freq = row["frequency_a_to_b"]
        G.add_edge(u, v, weight=score, freq=freq)

    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, k=1.8, seed=42)

    # Node coloring
    node_colors = []
    for node in G.nodes():
        if node == "ER Registration":
            node_colors.append("#2ecc71")
        elif "Release" in node:
            node_colors.append("#e74c3c")
        elif node == "Return ER":
            node_colors.append("#e67e22")
        else:
            node_colors.append("#3498db")

    weights = [G[u][v]["weight"] for u, v in G.edges()]
    edge_widths = [1.5 + (w * 3.5) for w in weights]

    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3200, edgecolors="black", linewidths=1.5)
    nx.draw_networkx_labels(G, pos, font_size=8.5, font_weight="bold")
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color="#2c3e50", arrowsize=18, connectionstyle="arc3,rad=0.1")

    # Edge labels showing dependency score and transition frequency
    edge_labels = {
        (u, v): f"d={G[u][v]['weight']:.2f}\n(n={G[u][v]['freq']})"
        for u, v in G.edges()
    }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=7.5, font_color="#1a1a1a")

    plt.title(
        f"CareFlow Heuristic Causal Net (Dependency Threshold >= {min_dependency}, Freq >= {min_frequency})\n"
        "[Green: Intake | Blue: Clinical Care | Red: Release | Orange: Readmission]",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    plt.axis("off")
    plt.tight_layout()

    out_img = OUTPUT_DIR / "heuristic_net_topology.png"
    plt.savefig(out_img, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Created Heuristic Net visualization: {out_img}")

def main():
    print("Loading event log for Heuristic Mining...")
    log = load_process_event_log()
    print(f"Loaded {log['case:concept:name'].nunique()} patient cases, {len(log)} events.")

    print("\nComputing Causal Dependency Matrix...")
    dep_df, dfg, start_acts, end_acts = compute_causal_dependency_matrix(log)
    export_dependency_matrix(dep_df)

    print("\nRendering Heuristic Net topology diagram...")
    render_heuristic_net_topology(dep_df, min_dependency=0.5, min_frequency=50)

    print("\nTop Strong Causal Dependencies (Dependency Score >= 0.7):")
    strong = dep_df[dep_df["dependency_score"] >= 0.7]
    print(strong[["activity_from", "activity_to", "frequency_a_to_b", "dependency_score"]].head(8).to_string(index=False))
    print("\nHeuristic mining completed successfully.")

if __name__ == "__main__":
    main()
