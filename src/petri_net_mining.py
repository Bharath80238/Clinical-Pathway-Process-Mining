"""Formal Petri Net Discovery Module using Inductive Miner
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
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

    return net, initial_marking, final_marking, metrics

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

if __name__ == "__main__":
    main()
