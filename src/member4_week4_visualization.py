
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load conformance report
file_path = Path("reports/week4/conformance_summary.csv")
df = pd.read_csv(file_path)

# Count patient statuses
counts = df["Conformance_Status"].value_counts()

# Create bar chart
plt.figure(figsize=(8, 5))
counts.reindex(["Conformant", "Non-compliant"], fill_value=0).plot(
    kind="bar"
)

plt.title("Week 4 - Patient Conformance Analysis")
plt.xlabel("Conformance Status")
plt.ylabel("Number of Patients")
plt.xticks(rotation=0)
plt.tight_layout()

# Save chart
output_path = Path("reports/week4/conformance_chart.png")
plt.savefig(output_path, dpi=300)
plt.show()

print("Chart saved:", output_path)
