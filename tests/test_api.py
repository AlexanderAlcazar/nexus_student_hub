import tempfile
import unittest

from fastapi.testclient import TestClient

from container import AppSettings
from server.app import create_app


class TestApi(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        settings = AppSettings(database_name="api_test.db", data_dir=self.temp_dir.name)
        self.app = create_app(settings)
        self.client = TestClient(self.app)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_health_endpoint(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_register_and_login(self):
        register_response = self.client.post(
            "/register",
            json={
                "username": "api_user",
                "email": "api_user@example.com",
                "password": "supersecret",
                "user_type": "student",
            },
        )
        self.assertEqual(register_response.status_code, 200)
        user = register_response.json()
        self.assertEqual(user["username"], "api_user")
        self.assertNotIn("password_hash", user)

        login_response = self.client.post(
            "/login",
            json={"username": "api_user", "password": "supersecret"},
        )
        self.assertEqual(login_response.status_code, 200)
        self.assertEqual(login_response.json()["username"], "api_user")

    def test_profile_completion_endpoint(self):
        register_response = self.client.post(
            "/register",
            json={
                "username": "profile_user",
                "email": "profile_user@example.com",
                "password": "supersecret",
                "user_type": "student",
            },
        )
        user_id = register_response.json()["user_id"]

        response = self.client.post(
            "/profile/complete",
            json={
                "user_id": user_id,
                "personal_details": {"first_name": "Test", "last_name": "User"},
                "contact_info": {"city": "Seattle", "state": "WA"},
                "major": "Computer Science",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["first_name"], "Test")
        self.assertEqual(payload["city"], "Seattle")
        self.assertEqual(payload["major"], "Computer Science")


if __name__ == "__main__":
    unittest.main()
