import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import _dashboard_compensation_summary
from app.db.base import Base
from app.models.entities import (
    AuditEvent,
    CompensationBand,
    Employee,
    Level,
    Location,
    Role,
    SalaryRecord,
)


class DashboardSummaryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.session.add_all([
            Role(id="ROLE-01", name="Engineer", family="Engineering"),
            Level(id="L01", name="Level 1", rank=1),
            Location(id="LOC-01", name="Test City", country="IN", currency="INR", fx_to_inr=1),
        ])
        self.session.add(CompensationBand(
            id="BAND-01",
            role_id="ROLE-01",
            level_id="L01",
            location_id="LOC-01",
            currency="INR",
            minimum=100,
            midpoint=150,
            maximum=200,
            effective_from=date(2025, 1, 1),
            effective_to=None,
        ))
        self.session.add_all([
            Employee(
                id="EMP-000001",
                name="Synthetic Employee 00001",
                role_id="ROLE-01",
                level_id="L01",
                location_id="LOC-01",
                hire_date=date(2020, 1, 1),
            ),
            Employee(
                id="EMP-000002",
                name="Synthetic Employee 00002",
                role_id="ROLE-01",
                level_id="L01",
                location_id="LOC-01",
                hire_date=date(2020, 1, 1),
            ),
        ])
        self.session.flush()
        self.session.add_all([
            SalaryRecord(
                id="SAL-1",
                employee_id="EMP-000001",
                effective_date=date(2026, 1, 1),
                base_salary=150,
                currency="INR",
                fte=1,
                annualized_inr=150,
                band_id="BAND-01",
                change_reason="ANNUAL_REVIEW",
            ),
            SalaryRecord(
                id="SAL-2",
                employee_id="EMP-000002",
                effective_date=date(2026, 1, 1),
                base_salary=250,
                currency="INR",
                fte=1,
                annualized_inr=250,
                band_id="BAND-01",
                change_reason="ANNUAL_REVIEW",
            ),
        ])
        self.session.add(AuditEvent(
            id="EVT-1",
            entity_type="AdjustmentProposal",
            entity_id="ADJ-2026-000001",
            event_type="CREATED",
            actor="analysis-orchestrator",
            details="Created from analysis",
        ))
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_summary_is_calculated_from_latest_salary_and_real_events(self):
        summary = _dashboard_compensation_summary(self.session)

        self.assertEqual(summary["latest_salary_distribution"]["within"], 1)
        self.assertEqual(summary["latest_salary_distribution"]["above"], 1)
        self.assertEqual(summary["latest_salary_distribution"]["total"], 2)
        self.assertEqual(summary["compensation_by_role_family"][0]["average_salary_inr"], 200)
        self.assertEqual(summary["recent_activity"][0]["entity_id"], "ADJ-2026-000001")
        self.assertEqual(summary["salary_history_end"], "2026-01-01")


if __name__ == "__main__":
    unittest.main()
