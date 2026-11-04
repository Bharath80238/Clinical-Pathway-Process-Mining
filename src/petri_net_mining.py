"""Formal Petri Net Discovery Module using Inductive Miner
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
MODELS_DIR = PROJECT_ROOT / "reports" / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_process_event_log(db_path=DB_PATH):
    """Load events from SQLite and format for PM4Py Petri Net discovery."""
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

def discover_inductive_petri_net(event_log):
    """Mine formal Petri Net (Places, Transitions, Markings) via Inductive Miner."""
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(event_log)

    places = list(net.places)
    transitions = list(net.transitions)
    arcs = list(net.arcs)

    labeled_transitions = [t for t in transitions if t.label is not None]
    silent_transitions = [t for t in transitions if t.label is None]

    metrics = {
        "mining_algorithm": "Inductive Miner (IM)",
        "total_places": len(places),
        "total_transitions": len(transitions),
        "labeled_clinical_transitions": len(labeled_transitions),
        "silent_routing_transitions_tau": len(silent_transitions),
        "total_directed_arcs": len(arcs),
        "initial_marking": [p.name for p in initial_marking],
        "final_marking": [p.name for p in final_marking],
        "clinical_labels": sorted(list({t.label for t in labeled_transitions})),
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = REPORTS_DIR / "petri_net_metrics.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"Exported Petri net metrics JSON: {summary_path}")

    # Export PNML model file
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    pnml_path = MODELS_DIR / "sepsis_petri_net.pnml"
    pm4py.write_pnml(net, initial_marking, final_marking, str(pnml_path))
    print(f"Exported formal Petri Net model (PNML): {pnml_path}")

    return net, initial_marking, final_marking, metrics

def render_petri_net_visualization(net, initial_marking, final_marking):
    """Render formal bipartite Petri Net graph (Places vs Transitions) using NetworkX."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    G = nx.DiGraph()

    # Add places
    for p in net.places:
        G.add_node(p.name, node_type="place", label=p.name)

    # Add transitions
    for t in net.transitions:
        is_silent = (t.label is None)
        lbl = "tau" if is_silent else t.label
        G.add_node(t.name, node_type="transition", is_silent=is_silent, label=lbl)

    # Add directed arcs
    for a in net.arcs:
        G.add_edge(a.source.name, a.target.name)

    plt.figure(figsize=(16, 10))
    pos = nx.spring_layout(G, k=1.5, seed=42)

    place_nodes = [n for n, attr in G.nodes(data=True) if attr["node_type"] == "place"]
    clinical_trans = [n for n, attr in G.nodes(data=True) if attr["node_type"] == "transition" and not attr["is_silent"]]
    silent_trans = [n for n, attr in G.nodes(data=True) if attr["node_type"] == "transition" and attr["is_silent"]]

    # Draw places as circles
    nx.draw_networkx_nodes(G, pos, nodelist=place_nodes, node_color="#ecf0f1", node_size=1200, edgecolors="#2c3e50", linewidths=1.5)
    
    # Draw clinical transitions as blue boxes
    nx.draw_networkx_nodes(G, pos, nodelist=clinical_trans, node_color="#3498db", node_shape="s", node_size=1800, edgecolors="black", linewidths=1.5)
    
    # Draw silent transitions as dark gray small boxes
    nx.draw_networkx_nodes(G, pos, nodelist=silent_trans, node_color="#7f8c8d", node_shape="s", node_size=600, edgecolors="black", linewidths=1)

    # Draw directed arcs
    nx.draw_networkx_edges(G, pos, edge_color="#34495e", arrowsize=14, width=1.0, connectionstyle="arc3,rad=0.08")

    # Labels
    labels = {n: attr["label"] for n, attr in G.nodes(data=True) if not attr.get("is_silent", False)}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=7.5, font_weight="bold")

    plt.title("CareFlow Formal Petri Net Model (Inductive Miner)\n[Circles: Places | Blue Boxes: Clinical Transitions | Gray Boxes: Silent Routing (tau)]", fontsize=12, fontweight="bold")
    plt.axis("off")
    plt.tight_layout()

    out_img = OUTPUT_DIR / "petri_net_topology.png"
    plt.savefig(out_img, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Created Petri net visualization: {out_img}")

def main():
    print("Loading event log for formal Petri Net discovery...")
    log = load_process_event_log()
    print(f"Loaded {log['case:concept:name'].nunique()} cases, {len(log)} events.")

    print("\nExecuting Inductive Miner...")
    net, im, fm, metrics = discover_inductive_petri_net(log)
    print(f"  Discovered Places: {metrics['total_places']}")
    print(f"  Discovered Transitions: {metrics['total_transitions']} ({metrics['labeled_clinical_transitions']} clinical, {metrics['silent_routing_transitions_tau']} silent tau)")
    print(f"  Total Directed Arcs: {metrics['total_directed_arcs']}")
    print(f"  Initial Marking: {metrics['initial_marking']}")
    print(f"  Final Marking: {metrics['final_marking']}")

    print("\nRendering Petri Net graph topology...")
    render_petri_net_visualization(net, im, fm)
    print("Petri net mining completed successfully.")

if __name__ == "__main__":
    main()
