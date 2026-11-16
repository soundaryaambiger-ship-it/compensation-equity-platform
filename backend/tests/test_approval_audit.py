import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import decision
from app.db.base import Base
from app.models.entities import AdjustmentProposal, AuditEvent


class ApprovalAuditTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.proposal_id = "ADJ-2026-000001"
        self.session.add(AdjustmentProposal(
            id=self.proposal_id,
            employee_id="EMP-000001",
            proposed_amount_inr=1000,
            reason="Test proposal",
            evidence_json="{}",
            status="PENDING",
        ))
        self.session.add(AuditEvent(
            id=f"EVT-{self.proposal_id}-CREATED",
            entity_type="AdjustmentProposal",
            entity_id=self.proposal_id,
            event_type="CREATED",
            actor="analysis-orchestrator",
            details="Created for test",
        ))
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_decision_keeps_creation_and_decision_events(self):
        result = decision(self.proposal_id, "APPROVED", "test-reviewer", self.session)
        events = self.session.query(AuditEvent).filter_by(entity_id=self.proposal_id).all()

        self.assertEqual(result["status"], "APPROVED")
        self.assertEqual(len(events), 2)
        self.assertEqual(len({event.id for event in events}), 2)


if __name__ == "__main__":
    unittest.main()
