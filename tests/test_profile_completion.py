import tempfile
import unittest

from container import AppSettings, build_container


class TestProfileCompletion(unittest.TestCase):
    def test_student_profile_completion_persists_profile_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = AppSettings(database_name="profile.db", data_dir=temp_dir)
            container = build_container(settings)
            container.database.initialize_database()

            created_user = container.auth_service.register_user(
                username="student1",
                email="student1@example.com",
                password="secret123",
                user_type="student",
            )

            profile = container.profile_service.complete_profile(
                created_user["user_id"],
                profile_data={
                    "personal_details": {
                        "first_name": "Ada",
                        "last_name": "Lovelace",
                    },
                    "contact_info": {
                        "phone_number": "555-0101",
                        "street_address": "1 London Rd",
                        "city": "London",
                        "state": "ENG",
                        "zip_code": "SW1A",
                    },
                    "major": "Computer Science",
                },
            )

            self.assertEqual(profile["first_name"], "Ada")
            self.assertEqual(profile["last_name"], "Lovelace")
            self.assertEqual(profile["major"], "Computer Science")
            self.assertEqual(profile["city"], "London")

            stored_profile = container.user_repository.get_profile_by_user_id(created_user["user_id"])
            self.assertEqual(stored_profile["first_name"], "Ada")
            self.assertEqual(stored_profile["major"], "Computer Science")

    def test_complete_profile_raises_for_missing_user(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = AppSettings(database_name="profile_missing.db", data_dir=temp_dir)
            container = build_container(settings)
            container.database.initialize_database()

            with self.assertRaises(ValueError):
                container.profile_service.complete_profile(
                    999,
                    profile_data={"first_name": "Ghost"},
                )


if __name__ == "__main__":
    unittest.main()
