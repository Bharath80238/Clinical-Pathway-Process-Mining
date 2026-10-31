
import pandas as pd
from pathlib import Path

print("Starting Week 4 Conformance Checking...")

# File paths
input_file = Path("reports/week3/cleaned_event_log.csv")
output_folder = Path("reports/week4")
output_folder.mkdir(parents=True, exist_ok=True)

# Load dataset
df = pd.read_csv(input_file)

df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
df = df.sort_values(["Case_ID", "Timestamp"])

print("Dataset loaded successfully.")
print("Total records:", len(df))

# Actual activity names in the dataset
required_initial_activities = [
    "ER Registration",
    "ER Triage",
    "ER Sepsis Triage"
]

clinical_activities = [
    "Leucocytes",
    "CRP",
    "LacticAcid"
]

treatment_activities = [
    "IV Liquid",
    "IV Antibiotics"
]

results = []

# Check each patient journey
for case_id, group in df.groupby("Case_ID", sort=False):

    activities = group["Activity_Name"].dropna().tolist()
    activity_set = set(activities)

    issues = []

    # Check initial registration and triage sequence
    for activity in required_initial_activities:
        if activity not in activity_set:
            issues.append(f"Missing {activity}")

    positions = {}
    for activity in required_initial_activities:
        if activity in activities:
            positions[activity] = activities.index(activity)

    if len(positions) == 3:
        if not (
            positions["ER Registration"]
            < positions["ER Triage"]
            < positions["ER Sepsis Triage"]
        ):
            issues.append("Incorrect registration/triage order")

    # Check whether at least one diagnostic activity exists
    if not any(activity in activity_set for activity in clinical_activities):
        issues.append("No recorded diagnostic activity")

    # Check whether at least one treatment activity exists
    if not any(activity in activity_set for activity in treatment_activities):
        issues.append("No recorded treatment activity")

    # Check return to ER
    if "Return ER" in activity_set:
        issues.append("Patient returned to ER")

    status = "Conformant" if len(issues) == 0 else "Non-compliant"

    results.append({
        "Case_ID": case_id,
        "Observed_Activities": " -> ".join(activities),
        "Conformance_Status": status,
        "Issue": "; ".join(issues) if issues else "No rule violation detected"
    })

# Create report
summary = pd.DataFrame(results)

summary.to_csv(
    output_folder / "conformance_summary.csv",
    index=False
)

# Save non-compliant patients separately
non_compliant = summary[
    summary["Conformance_Status"] == "Non-compliant"
]

non_compliant.to_csv(
    output_folder / "non_compliant_cases.csv",
    index=False
)

# Summary statistics
total = len(summary)
conformant = (summary["Conformance_Status"] == "Conformant").sum()
non_conformant = total - conformant

print("\nWeek 4 Conformance Checking Completed!")
print("Total patients:", total)
print("Conformant patients:", conformant)
print("Non-compliant patients:", non_conformant)

print("\nReports saved in:", output_folder)
