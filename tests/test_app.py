import unittest

from app import app, db


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


if __name__ == "__main__":
    unittest.main()
