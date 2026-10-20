"""CareFlow Clinical Pathway Process Mining Module
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
import networkx as nx
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_process_event_log(db_path=DB_PATH):
    """Load and format event data for process mining analysis with PM4Py."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, leucocytes, crp, lactic_acid
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

def get_process_summary(event_log):
    """Compute foundational process mining metrics."""
    cases = pm4py.get_event_attribute_values(event_log, "case:concept:name")
    activities = pm4py.get_event_attribute_values(event_log, "concept:name")
    start_activities = pm4py.get_start_activities(event_log)
    end_activities = pm4py.get_end_activities(event_log)
    variants = pm4py.get_variants(event_log)

    summary = {
        "total_cases": len(cases),
        "total_events": len(event_log),
        "unique_activities": len(activities),
        "unique_variants": len(variants),
        "start_activities": {k: int(v) for k, v in start_activities.items()},
        "end_activities": {k: int(v) for k, v in end_activities.items()},
    }
    return summary

def extract_variants_table(event_log, top_n=15):
    """Extract frequent patient trace variants and export metrics."""
    variants = pm4py.get_variants(event_log)
    variant_list = []
    total_cases = event_log["case:concept:name"].nunique()

    # Sort variants by case count descending
    sorted_variants = sorted(
        variants.items(),
        key=lambda item: item[1] if isinstance(item[1], int) else len(item[1]),
        reverse=True,
    )

    cum_cases = 0
    for rank, (var_tuple, cases) in enumerate(sorted_variants, start=1):
        case_count = cases if isinstance(cases, int) else len(cases)
        cum_cases += case_count
        variant_str = " -> ".join(var_tuple)
        variant_list.append({
            "rank": rank,
            "pathway": variant_str,
            "length": len(var_tuple),
            "case_count": case_count,
            "percentage": round((case_count / total_cases) * 100, 2),
            "cumulative_percentage": round((cum_cases / total_cases) * 100, 2),
        })

    variant_df = pd.DataFrame(variant_list)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    variant_df.to_csv(REPORTS_DIR / "variant_analysis.csv", index=False)
    print(f"Exported variant analysis to: {REPORTS_DIR / 'variant_analysis.csv'}")
    return variant_df

def plot_variant_pareto(variant_df, top_n=12):
    """Generate Pareto chart of top pathway variants."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    subset = variant_df.head(top_n).copy()

    fig, ax1 = plt.subplots(figsize=(12, 6))

    color = "#1f77b4"
    bars = ax1.bar(
        [f"Var {r}" for r in subset["rank"]],
        subset["case_count"],
        color=color,
        alpha=0.85,
        edgecolor="black",
    )
    ax1.set_xlabel("Pathway Variant Rank", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Patient Cases", color=color, fontsize=11, fontweight="bold")
    ax1.tick_params(axis="y", labelcolor=color)

    # Annotate bar counts
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(
            f"{int(h)}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    ax2 = ax1.twinx()
    color2 = "#d62728"
    ax2.plot(
        [f"Var {r}" for r in subset["rank"]],
        subset["cumulative_percentage"],
        color=color2,
        marker="o",
        linewidth=2,
    )
    ax2.set_ylabel(
        "Cumulative Case Coverage (%)",
        color=color2,
        fontsize=11,
        fontweight="bold",
    )
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(0, 105)

    plt.title(
        f"Top {top_n} Clinical Pathway Variants Coverage (Pareto Distribution)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    fig.tight_layout()
    chart_path = OUTPUT_DIR / "variant_distribution.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created variant Pareto chart: {chart_path}")

def render_dfg_networkx(dfg, start_activities, end_activities, output_path, title="Directly-Follows Graph (DFG) Frequency"):
    """Render directly-follows graph with NetworkX and Matplotlib."""
    G = nx.DiGraph()

    for (u, v), weight in dfg.items():
        G.add_edge(u, v, weight=weight)

    plt.figure(figsize=(15, 10))
    pos = nx.spring_layout(G, k=1.8, seed=42)

    # Node coloring: start = green, end = red, normal = light blue
    node_colors = []
    for node in G.nodes():
        if node in start_activities and node in end_activities:
            node_colors.append("#ffbb78")
        elif node in start_activities:
            node_colors.append("#2ca02c")
        elif node in end_activities:
            node_colors.append("#d62728")
        else:
            node_colors.append("#aec7e8")

    weights = [G[u][v]["weight"] for u, v in G.edges()]
    max_w = max(weights) if weights else 1
    edge_widths = [1.0 + (w / max_w) * 5.0 for w in weights]

    nx.draw_networkx_nodes(
        G, pos, node_color=node_colors, node_size=3200, edgecolors="black"
    )
    nx.draw_networkx_labels(
        G, pos, font_size=8.5, font_weight="bold", font_family="sans-serif"
    )
    nx.draw_networkx_edges(
        G, pos, width=edge_widths, edge_color="#333333", arrowsize=18, connectionstyle="arc3,rad=0.1"
    )

    # Draw edge weight labels for significant transitions
    edge_labels = {
        (u, v): f"{w}" for (u, v), w in dfg.items() if w >= np.percentile(weights, 60)
    }
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=edge_labels, font_size=7.5, font_color="#1f1f1f"
    )

    plt.title(f"{title}\n(Node Colors: Green=Start, Red=End, Blue=Clinical Activity)", fontsize=13, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Created DFG graph: {output_path}")

def discover_and_save_dfg(event_log):
    """Mine Directly-Follows Graph and export visual diagram."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)

    # Save visualization using NetworkX
    output_png = OUTPUT_DIR / "dfg_frequency.png"
    render_dfg_networkx(
        dfg, start_activities, end_activities, output_png, title="Directly-Follows Process Map (Activity Frequencies)"
    )

    # Save summary json
    summary_path = REPORTS_DIR / "process_mining_summary.json"
    summary = get_process_summary(event_log)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved process summary JSON: {summary_path}")
    return dfg, start_activities, end_activities

def main():
    print("Loading event log...")
    log = load_process_event_log()
    summary = get_process_summary(log)
    print(f"Loaded {summary['total_cases']} cases, {summary['total_events']} events, {summary['unique_variants']} variants.")

    print("\nExtracting trace variants...")
    variant_df = extract_variants_table(log)
    plot_variant_pareto(variant_df)

    print("\nMining Directly-Follows Graph (DFG)...")
    discover_and_save_dfg(log)
    print("\nProcess mining discovery completed successfully.")

if __name__ == "__main__":
    main()
