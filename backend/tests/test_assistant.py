import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.routes import assistant_chat
from app.db.base import Base
from app.models.entities import Employee
from app.schemas.assistant import AssistantChatRequest
from app.services.assistant import answer_question


class LocalAssistantTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.session.add_all([
            Employee(
                id="EMP-000001",
                name="Synthetic Employee 00001",
                role_id="ROLE-01",
                level_id="L01",
                location_id="LOC-BLR",
                hire_date=date(2020, 1, 1),
                employment_status="ACTIVE",
                fte=1.0,
            ),
            Employee(
                id="EMP-000002",
                name="Synthetic Employee 00002",
                role_id="ROLE-01",
                level_id="L01",
                location_id="LOC-BLR",
                hire_date=date(2020, 1, 1),
                employment_status="ACTIVE",
                fte=1.0,
            ),
        ])
        self.session.commit()

    def tearDown(self):
        self.session.close()
        self.engine.dispose()

    def test_employee_id_lookup_uses_local_employee_record(self):
        answer = answer_question(
            "What is the employee ID of Synthetic Employee 00001?",
            self.session,
        )

        self.assertIn("EMP-000001", answer)

    def test_ambiguous_employee_id_question_asks_for_a_name(self):
        answer = answer_question("I want to know the employee ID", self.session)

        self.assertIn("Which synthetic employee", answer)

    def test_employee_count_comes_from_local_database(self):
        result = assistant_chat(
            AssistantChatRequest(question="How many employees are there?"),
            self.session,
        )

        self.assertEqual(result["answer"], "There are 2 employees in the local database.")


if __name__ == "__main__":
    unittest.main()
