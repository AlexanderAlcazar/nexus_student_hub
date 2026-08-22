import unittest

from models.contact_info import ContactInfo
from models.credentials import Credentials
from models.personal_details import PersonalDetails
from models.user_base import UserBase


class TestUserBase(unittest.TestCase):
    def test_defaults(self):
        user = UserBase()
        self.assertIsInstance(user.personal_details, PersonalDetails)
        self.assertIsInstance(user.contact_info, ContactInfo)
        self.assertIsInstance(user.credentials, Credentials)

    def test_to_dict(self):
        user = UserBase(
            personal_details=PersonalDetails(first_name="John", last_name="Doe"),
            contact_info=ContactInfo(phone_number="123", city="Anytown"),
            credentials=Credentials(user_id=1, username="jdoe", email="jdoe@example.com", user_type="student"),
        )

        self.assertEqual(
            user.to_dict(),
            {
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "123",
                "street_address": None,
                "city": "Anytown",
                "state": None,
                "zip_code": None,
                "user_id": 1,
                "username": "jdoe",
                "email": "jdoe@example.com",
                "user_type": "student",
            },
        )


if __name__ == "__main__":
    unittest.main()
