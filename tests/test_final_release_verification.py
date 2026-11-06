"""
CareFlow: Clinical Pathway Process Mining
Unit Test Suite: Final Release End-to-End Regression & Verification
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: Infotact Solutions Batch-22.1 Data Analytics Final Review
"""

import json
import os
import unittest
import pandas as pd


class TestFinalReleaseVerification(unittest.TestCase):
    """
    Comprehensive regression suite validating all clinical metrics, data warehouse
    integrity, Petri Net soundness, and reporting artifacts for final institutional release.
    """

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cls.reports_dir = os.path.join(cls.base_dir, "reports")
        cls.figures_dir = os.path.join(cls.reports_dir, "figures", "process_maps")
        cls.models_dir = os.path.join(cls.reports_dir, "models")
        cls.star_schema_dir = os.path.join(cls.reports_dir, "star_schema")

    def test_01_event_log_scale_and_completeness(self):
        """Verify ground-truth cohort scale: 1,050 cases, 15,213 events, 16 activities."""
        trace_csv = os.path.join(self.reports_dir, "trace_level_metrics.csv")
        self.assertTrue(os.path.exists(trace_csv), f"Missing trace metrics: {trace_csv}")

        df_traces = pd.read_csv(trace_csv)
        self.assertEqual(len(df_traces), 1050, f"Expected 1050 cases, got {len(df_traces)}")
        self.assertEqual(df_traces["event_count"].sum(), 15213, "Expected 15,213 total clinical events")
        self.assertGreater(df_traces["duration_days"].median(), 4.0, "Median duration should exceed 4 days")

    def test_02_sepsis_golden_hour_compliance(self):
        """Verify Sepsis Golden Hour SLA: 84.8% compliance within 60 min and 3-hour bundle."""
        master_json = os.path.join(self.reports_dir, "careflow_process_mining_master_summary.json")
        self.assertTrue(os.path.exists(master_json), f"Missing master summary: {master_json}")

        with open(master_json, "r", encoding="utf-8") as f:
            master_data = json.load(f)

        kpis = master_data["executive_kpis"]
        self.assertAlmostEqual(kpis["sepsis_antibiotics_golden_hour_compliance_pct"], 84.8, places=1)
        self.assertAlmostEqual(kpis["sepsis_antibiotics_three_hour_bundle_compliance_pct"], 96.5, places=1)

    def test_03_diagnostic_lab_throughput_and_tat(self):
        """Verify Central Diagnostic Lab B throughput share (53.31%) and turnaround metrics."""
        tat_json = os.path.join(self.reports_dir, "diagnostic_turnaround_summary.json")
        self.assertTrue(os.path.exists(tat_json), f"Missing TAT report: {tat_json}")

        with open(tat_json, "r", encoding="utf-8") as f:
            tat_data = json.load(f)

        self.assertEqual(tat_data["total_cohort_cases"], 1050)
        self.assertEqual(tat_data["total_laboratory_events"], 8110)
        self.assertAlmostEqual(tat_data["laboratory_share_of_all_events_pct"], 53.31, places=2)

    def test_04_formal_petri_net_soundness(self):
        """Verify formal inductive Petri Net WF-Net XML model exists and has correct topology."""
        pnml_path = os.path.join(self.models_dir, "sepsis_petri_net.pnml")
        self.assertTrue(os.path.exists(pnml_path), f"Missing PNML model: {pnml_path}")
        self.assertGreater(os.path.getsize(pnml_path), 5000, "PNML model file is suspiciously small")

        # Verify token replay summary
        token_json = os.path.join(self.reports_dir, "token_replay_summary.json")
        self.assertTrue(os.path.exists(token_json), f"Missing token replay summary: {token_json}")
        with open(token_json, "r", encoding="utf-8") as f:
            token_data = json.load(f)
        self.assertEqual(token_data["mean_trace_fitness"], 1.0, "Expected 100% token replay fitness")
        self.assertEqual(token_data["total_missing_tokens"], 0, "Expected 0 missing tokens")

    def test_05_readmission_risk_factors(self):
        """Verify 28.0% baseline readmission rate and primary risk factors."""
        risk_json = os.path.join(self.reports_dir, "readmission_risk_summary.json")
        self.assertTrue(os.path.exists(risk_json), f"Missing readmission risk summary: {risk_json}")

        with open(risk_json, "r", encoding="utf-8") as f:
            risk_data = json.load(f)

        self.assertAlmostEqual(risk_data["baseline_readmission_rate_pct"], 28.0, places=1)
        self.assertEqual(risk_data["total_readmission_cases"], 294)
        self.assertGreater(risk_data["primary_odds_ratio"], 10.0, "Primary odds ratio should exceed 10x")

    def test_06_star_schema_data_warehouse_integrity(self):
        """Verify all 5 Star-Schema tables exist with zero orphan foreign keys."""
        fact_path = os.path.join(self.star_schema_dir, "fact_clinical_events.csv")
        dim_pt_path = os.path.join(self.star_schema_dir, "dim_patient_cohort.csv")
        dim_act_path = os.path.join(self.star_schema_dir, "dim_activity.csv")
        dim_dept_path = os.path.join(self.star_schema_dir, "dim_department.csv")
        dim_time_path = os.path.join(self.star_schema_dir, "dim_time_bucket.csv")

        for p in [fact_path, dim_pt_path, dim_act_path, dim_dept_path, dim_time_path]:
            self.assertTrue(os.path.exists(p), f"Missing Star Schema table: {p}")

        df_fact = pd.read_csv(fact_path)
        df_pt = pd.read_csv(dim_pt_path)
        df_act = pd.read_csv(dim_act_path)
        df_dept = pd.read_csv(dim_dept_path)
        df_time = pd.read_csv(dim_time_path)

        self.assertEqual(len(df_fact), 15213, "Fact table row count mismatch")
        self.assertEqual(len(df_pt), 1050, "Patient dimension row count mismatch")
        self.assertEqual(len(df_act), 16, "Activity dimension row count mismatch")
        self.assertEqual(len(df_dept), 26, "Department dimension row count mismatch")
        self.assertEqual(len(df_time), 5, "Time bucket dimension row count mismatch")

        # Referential integrity check
        self.assertTrue(set(df_fact["patient_cohort_key"]).issubset(set(df_pt["patient_cohort_key"])))
        self.assertTrue(set(df_fact["activity_key"]).issubset(set(df_act["activity_key"])))
        self.assertTrue(set(df_fact["department_key"]).issubset(set(df_dept["department_key"])))
        self.assertTrue(set(df_fact["time_bucket_key"]).issubset(set(df_time["time_bucket_key"])))

    def test_07_clinical_decision_support_stratification(self):
        """Verify CDSS SPES risk triage identifies 543 high-risk cohort patients."""
        cdss_json = os.path.join(self.reports_dir, "clinical_decision_rules.json")
        cdss_csv = os.path.join(self.reports_dir, "clinical_decision_recommendations.csv")
        self.assertTrue(os.path.exists(cdss_json), f"Missing CDSS rules JSON: {cdss_json}")
        self.assertTrue(os.path.exists(cdss_csv), f"Missing CDSS recommendations CSV: {cdss_csv}")

        with open(cdss_json, "r", encoding="utf-8") as f:
            cdss_data = json.load(f)

        self.assertEqual(cdss_data["high_risk_escalation_cases"], 543)
        self.assertAlmostEqual(cdss_data["high_risk_escalation_pct"], 51.71, places=1)
        self.assertEqual(cdss_data["total_evaluated_patients"], 1050)

    def test_08_presentation_guide_and_master_bundle(self):
        """Verify executive presentation defense guide and master summary JSON are populated."""
        master_json = os.path.join(self.reports_dir, "careflow_process_mining_master_summary.json")
        defense_json = os.path.join(self.reports_dir, "final_defense_slide_kpis.json")
        defense_guide = os.path.join(self.reports_dir, "final_defense_presentation_guide.md")
        whitepaper = os.path.join(self.reports_dir, "executive_process_mining_whitepaper.md")

        self.assertTrue(os.path.exists(master_json), "Missing master summary bundle")
        self.assertTrue(os.path.exists(defense_json), "Missing defense slide KPIs JSON")
        self.assertTrue(os.path.exists(defense_guide), "Missing defense presentation guide")
        self.assertTrue(os.path.exists(whitepaper), "Missing executive whitepaper")

        with open(master_json, "r", encoding="utf-8") as f:
            master_data = json.load(f)

        self.assertIn("project", master_data)
        self.assertIn("executive_kpis", master_data)
        self.assertIn("clinical_decision_support_system", master_data)
        self.assertEqual(master_data["executive_kpis"]["total_patient_cases"], 1050)

    def test_09_process_maps_and_figures_completeness(self):
        """Verify all critical process maps and visual artifacts are generated in reports/figures/."""
        critical_figures = [
            "happy_path.png",
            "spaghetti_diagram.png",
            "sepsis_golden_hour_sla.png",
            "token_fitness_distribution.png",
            "readmission_risk_factors.png",
            "star_schema_entity_relationship.png",
            "clinical_decision_support_matrix.png",
            "careflow_executive_milestone_roadmap.png",
            "trace_duration_vs_events.png",
            "inter_ward_transfer_delays.png",
            "diagnostic_turnaround_distribution.png"
        ]
        for fig_name in critical_figures:
            fig_path = os.path.join(self.figures_dir, fig_name)
            self.assertTrue(os.path.exists(fig_path), f"Missing figure: {fig_path}")
            self.assertGreater(os.path.getsize(fig_path), 5000, f"Figure file size too small: {fig_name}")


if __name__ == "__main__":
    unittest.main()
