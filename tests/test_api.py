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
        payload = login_response.json()
        self.assertEqual(payload["user"]["username"], "api_user")
        self.assertIn("access_token", payload)
        self.assertIn("refresh_token", payload)
        self.assertEqual(payload["token_type"], "bearer")
        self.assertGreater(payload["expires_in"], 0)

    def test_refresh_token_rotates_and_old_token_is_rejected(self):
        self.client.post(
            "/register",
            json={
                "username": "refresh_user",
                "email": "refresh_user@example.com",
                "password": "supersecret",
                "user_type": "student",
            },
        )
        login_response = self.client.post(
            "/login",
            json={"username": "refresh_user", "password": "supersecret"},
        )
        self.assertEqual(login_response.status_code, 200)
        refresh_token = login_response.json()["refresh_token"]

        refresh_response = self.client.post("/token/refresh", json={"refresh_token": refresh_token})
        self.assertEqual(refresh_response.status_code, 200)
        refreshed_payload = refresh_response.json()
        self.assertIn("access_token", refreshed_payload)
        self.assertIn("refresh_token", refreshed_payload)
        self.assertNotEqual(refreshed_payload["refresh_token"], refresh_token)

        old_refresh_reuse = self.client.post("/token/refresh", json={"refresh_token": refresh_token})
        self.assertEqual(old_refresh_reuse.status_code, 401)
        self.assertEqual(old_refresh_reuse.json()["detail"], "Invalid or expired refresh token.")

    def test_logout_revokes_refresh_token(self):
        self.client.post(
            "/register",
            json={
                "username": "logout_user",
                "email": "logout_user@example.com",
                "password": "supersecret",
                "user_type": "student",
            },
        )
        login_response = self.client.post(
            "/login",
            json={"username": "logout_user", "password": "supersecret"},
        )
        self.assertEqual(login_response.status_code, 200)
        refresh_token = login_response.json()["refresh_token"]

        logout_response = self.client.post("/logout", json={"refresh_token": refresh_token})
        self.assertEqual(logout_response.status_code, 200)
        self.assertEqual(logout_response.json()["status"], "logged_out")

        refresh_after_logout = self.client.post("/token/refresh", json={"refresh_token": refresh_token})
        self.assertEqual(refresh_after_logout.status_code, 401)
        self.assertEqual(refresh_after_logout.json()["detail"], "Invalid or expired refresh token.")

    def test_auth_me_returns_user_with_valid_access_token(self):
        self.client.post(
            "/register",
            json={
                "username": "me_user",
                "email": "me_user@example.com",
                "password": "supersecret",
                "user_type": "student",
            },
        )
        login_response = self.client.post(
            "/login",
            json={"username": "me_user", "password": "supersecret"},
        )
        self.assertEqual(login_response.status_code, 200)
        access_token = login_response.json()["access_token"]

        me_response = self.client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        self.assertEqual(me_response.status_code, 200)
        payload = me_response.json()
        self.assertEqual(payload["username"], "me_user")
        self.assertNotIn("password_hash", payload)

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

    def test_get_user_endpoint(self):
        register_response = self.client.post(
            "/register",
            json={
                "username": "lookup_user",
                "email": "lookup_user@example.com",
                "password": "supersecret",
                "user_type": "student",
            },
        )
        self.assertEqual(register_response.status_code, 200)
        user_id = register_response.json()["user_id"]

        response = self.client.get(f"/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["user_id"], user_id)
        self.assertEqual(payload["username"], "lookup_user")
        self.assertEqual(payload["email"], "lookup_user@example.com")
        self.assertNotIn("password_hash", payload)

    def test_get_user_endpoint_not_found(self):
        response = self.client.get("/users/999999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "User not found.")


if __name__ == "__main__":
    unittest.main()
