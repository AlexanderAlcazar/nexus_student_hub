import unittest
from models.personal_details import PersonalDetails

class TestPersonalDetails(unittest.TestCase):

    def test_personal_default(self):
        personal_details = PersonalDetails()
        self.assertIsNone(personal_details.first_name)
        self.assertIsNone(personal_details.last_name)

    def test_personal_with_arguments(self):
        first_name = "John"
        last_name = "Doe"
        personal_details = PersonalDetails(
            first_name=first_name,
            last_name=last_name
        )
        self.assertEqual(personal_details.first_name, first_name)
        self.assertEqual(personal_details.last_name, last_name)

    def test_to_dict(self):
        first_name = "John"
        last_name = "Doe"
        personal_details = PersonalDetails(
            first_name=first_name,
            last_name=last_name
        )
        expected_dict = {
            "first_name": first_name,
            "last_name": last_name
        }
        self.assertEqual(personal_details.to_dict(), expected_dict)

