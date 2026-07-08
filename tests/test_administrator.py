import unittest

from models import administrator
from models.administrator import Administrator, Credentials, PersonalDetails, ContactInfo


class TestAdministrator(unittest.TestCase):
    def test_administrator_default(self):
        admin = Administrator()
        self.assertIsNone(admin.admin_id)

        self.assertIsInstance(admin.personal_details, PersonalDetails)
        self.assertIsNone(admin.personal_details.first_name)
        self.assertIsNone(admin.personal_details.last_name)

        self.assertIsInstance(admin.contact_info, ContactInfo)
        self.assertIsNone(admin.contact_info.phone_number)
        self.assertIsNone(admin.contact_info.street_address)
        self.assertIsNone(admin.contact_info.city)
        self.assertIsNone(admin.contact_info.state)
        self.assertIsNone(admin.contact_info.zip_code)

        self.assertIsInstance(admin.credentials, Credentials)
        self.assertIsNone(admin.credentials.user_id)
        self.assertIsNone(admin.credentials.username)
        self.assertIsNone(admin.credentials.email)
        self.assertIsNone(admin.credentials.user_type)
        self.assertIsNone(admin.credentials.password_hash)

        print("Default Administrator test passed.")

    def test_administrator_with_arguments(self):
        admin_id = 1
        personal_details = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        contact_info = {
            "phone_number": "0987654321",
            "street_address": "456 Elm St",
            "city": "Othertown",
            "state": "NY",
            "zip_code": "54321"
        }
        credentials = {
            "user_id": 1,
            "username": "johndoe",
            "email": "testuser@email.com",
            "user_type": "administrator",
            "password_hash": "hashed_password"
        }
        administrator = Administrator(
            admin_id=admin_id,
            personal_details=PersonalDetails(**personal_details),
            contact_info=ContactInfo(**contact_info),
            credentials=Credentials(**credentials)
        )
        self.assertEqual(administrator.admin_id, admin_id)
        self.assertEqual(administrator.personal_details.first_name, personal_details["first_name"])
        self.assertEqual(administrator.personal_details.last_name, personal_details["last_name"])
        self.assertEqual(administrator.contact_info.phone_number, contact_info["phone_number"])
        self.assertEqual(administrator.contact_info.street_address, contact_info["street_address"])
        self.assertEqual(administrator.contact_info.city, contact_info["city"])
        self.assertEqual(administrator.contact_info.state, contact_info["state"])
        self.assertEqual(administrator.contact_info.zip_code, contact_info["zip_code"])
        self.assertEqual(administrator.credentials.user_id, credentials["user_id"])
        self.assertEqual(administrator.credentials.username, credentials["username"])
        self.assertEqual(administrator.credentials.email, credentials["email"])
        self.assertEqual(administrator.credentials.user_type, credentials["user_type"])
        self.assertEqual(administrator.credentials.password_hash, credentials["password_hash"])
        print("Administrator with arguments test passed.")

    def test_get_role_permissions(self):
        administrator = Administrator()
        permissions = administrator.get_role_permissions()
        self.assertTrue(permissions["can_view_grades"])
        self.assertTrue(permissions["can_edit_profiles"])
        self.assertTrue(permissions["can_delete_users"])
        print("Administrator get_role_permissions test passed.")

    def test_to_dict(self):
        admin_id = 1
        personal_details = {
            "first_name": "Jane",
            "last_name": "Smith"
        }
        contact_info = {
            "phone_number": "0987654321",
            "street_address": "456 Elm St",
            "city": "Othertown",
            "state": "NY",
            "zip_code": "54321"
        }
        credentials = {
            "user_id": 1,
            "username": "johndoe",
            "email": "testuser@email.com",
            "user_type": "administrator",
            "password_hash": "hashed_password"
        }
        administrator = Administrator(
            admin_id=admin_id,
            personal_details=PersonalDetails(**personal_details),
            contact_info=ContactInfo(**contact_info),
            credentials=Credentials(**credentials)
        )
        expected_dict = {
            "admin_id": admin_id,
            "first_name": personal_details["first_name"],
            "last_name": personal_details["last_name"],
            "phone_number": contact_info["phone_number"],
            "street_address": contact_info["street_address"],
            "city": contact_info["city"],
            "state": contact_info["state"],
            "zip_code": contact_info["zip_code"],
            "user_id": credentials["user_id"],
            "username": credentials["username"],
            "email": credentials["email"],
            "user_type": credentials["user_type"]
        }
        self.assertEqual(administrator.to_dict(), expected_dict)
        print("Administrator to_dict test passed.")
