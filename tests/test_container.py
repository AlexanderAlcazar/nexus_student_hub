import os
import tempfile
import unittest

from container import AppSettings, build_container


class TestContainer(unittest.TestCase):
    def test_builds_database_from_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = AppSettings(database_name="container.db", data_dir=temp_dir)
            container = build_container(settings)

            self.assertEqual(container.database.db_path, os.path.join(temp_dir, "container.db"))
            self.assertTrue(container.database.schema_path.endswith("schema.sql"))
            container.database.initialize_database()
            created_user = container.auth_service.register_user(
                username="jdoe",
                email="jdoe@example.com",
                password="secret123",
                user_type="student",
            )
            self.assertEqual(created_user["username"], "jdoe")
            self.assertIsNone(container.auth_service.authenticate("jdoe", "wrong"))
            authenticated_user = container.auth_service.authenticate("jdoe", "secret123")
            self.assertIsNotNone(authenticated_user)
            self.assertNotIn("password_hash", authenticated_user)


if __name__ == "__main__":
    unittest.main()
