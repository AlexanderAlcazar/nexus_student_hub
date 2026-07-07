import unittest
from models.credentials import Credentials


class TestCredentials(unittest.TestCase):
    def test_credentials_default(self):
        credentials = Credentials()
        self.assertIsNone(credentials.user_id)
        self.assertIsNone(credentials.username)
        self.assertIsNone(credentials.email)
        self.assertIsNone(credentials.user_type)
        self.assertIsNone(credentials.password_hash)
        print("Default Credentials test passed.")

    def test_credentials_with_arguments(self):
        user_id  = 1000
        username = "testuser"
        emai = "testuser@email.com"
        user_type = "admin"
        password_hash = "hashed_password"
        credentials = Credentials(
            user_id=user_id,
            username=username,
            email=emai,
            user_type=user_type,
            password_hash=password_hash
        )
        self.assertEqual(credentials.user_id, user_id)
        self.assertEqual(credentials.username, username)
        self.assertEqual(credentials.email, emai)
        self.assertEqual(credentials.user_type, user_type)
        self.assertEqual(credentials.password_hash, password_hash)
        print("Credentials with arguments test passed.")

    def test_to_dict(self):
        user_id = 1000
        username = "testuser"
        emai = "testuser@email.com"
        user_type = "admin"
        password_hash = "hashed_password"
        credentials = Credentials(
            user_id=user_id,
            username=username,
            email=emai,
            user_type=user_type,
            password_hash=password_hash
        )
        expected_dict = {
            "user_id": user_id,
            "username": username,
            "email": emai,
            "user_type": user_type
        }
        self.assertEqual(credentials.to_dict(), expected_dict)
        print("Credentials to_dict test passed.")





