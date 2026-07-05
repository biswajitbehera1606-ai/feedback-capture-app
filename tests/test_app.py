import os
import unittest

from sqlalchemy import text

from app import app, db, ensure_schema, Feedback, get_database_uri


class FeedbackAppTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Share application feedback", response.data)

    def test_submit_feedback_and_list_it(self):
        response = self.client.post(
            "/submit",
            data={
                "app_name": "NPSCSAT",
                "name": "Asha",
                "email": "asha@example.com",
                "feedback_type": "enhancement",
                "title": "Add dark mode",
                "message": "It would be helpful to have a dark theme in the mobile app.",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"saved successfully", response.data)

        list_response = self.client.get("/feedbacks")
        self.assertEqual(list_response.status_code, 200)
        self.assertIn(b"Add dark mode", list_response.data)

    def test_feedbacks_route_handles_old_schema(self):
        with self.app.app_context():
            db.session.execute(text("DROP TABLE IF EXISTS feedback"))
            db.session.execute(
                text(
                    "CREATE TABLE feedback (id INTEGER NOT NULL, name VARCHAR(120) NOT NULL, email VARCHAR(200) NOT NULL, feedback_type VARCHAR(50) NOT NULL, title VARCHAR(200) NOT NULL, message TEXT NOT NULL, status VARCHAR(20), created_at DATETIME, PRIMARY KEY (id))"
                )
            )
            db.session.commit()
            ensure_schema()

        response = self.client.get("/feedbacks")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No feedback has been captured yet for this application.", response.data)

    def test_database_uri_prefers_environment_value(self):
        original = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "postgresql://user:pass@host:5432/db"
        try:
            self.assertEqual(get_database_uri(), "postgresql://user:pass@host:5432/db")
        finally:
            if original is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = original

    def test_feedbacks_route_filters_by_app(self):
        with self.app.app_context():
            db.session.add_all(
                [
                    Feedback(
                        app_name="NPSCSAT",
                        name="Asha",
                        email="asha@example.com",
                        feedback_type="idea",
                        title="NPSCSAT title",
                        message="NPSCSAT message",
                    ),
                    Feedback(
                        app_name="CAMT",
                        name="Ravi",
                        email="ravi@example.com",
                        feedback_type="bug",
                        title="CAMT title",
                        message="CAMT message",
                    ),
                ]
            )
            db.session.commit()

        response = self.client.get("/feedbacks?app=NPSCSAT")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"NPSCSAT title", response.data)
        self.assertNotIn(b"CAMT title", response.data)


if __name__ == "__main__":
    unittest.main()
