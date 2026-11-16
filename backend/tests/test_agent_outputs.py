import unittest

from app.api.routes import _agent_outputs


class AgentOutputTests(unittest.TestCase):
    def test_builds_data_derived_summaries_and_samples_for_each_agent(self):
        result = {
            "quality_issues": [{"employee_id": "EMP-000002", "issue": "INVALID_FTE"}],
            "normalized_records": [
                {
                    "employee_id": "EMP-000001",
                    "date": "2026-01-01",
                    "normalized_salary_inr": 1200000,
                },
                {
                    "employee_id": "EMP-000002",
                    "date": "2026-01-01",
                    "normalized_salary_inr": None,
                },
            ],
            "band_findings": [{"employee_id": "EMP-000001", "compa_ratio": 1.0, "band_position": 0.5}],
            "comparable_groups": {
                ("ROLE-01", "L01", "LOC-01", "2026"): [{"employee_id": "EMP-000001"}],
            },
            "disparity_findings": [{"employee_id": "EMP-000002", "gap_pct": 20.0}],
            "review_proposals": [{"employee_id": "EMP-000002", "proposed_amount_inr": 100000}],
        }

        outputs = _agent_outputs(result)
        by_agent = {output["agent"]: output for output in outputs}

        self.assertEqual(len(outputs), 6)
        self.assertEqual(by_agent["normalization"]["output_count"], 2)
        self.assertIn("1 lack a normalized INR value", by_agent["normalization"]["summary"])
        self.assertEqual(by_agent["comparability"]["sample"][0]["record_count"], 1)
        self.assertEqual(by_agent["recommendation"]["sample"][0]["employee_id"], "EMP-000002")


if __name__ == "__main__":
    unittest.main()
