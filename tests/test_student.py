import unittest
from models.student import Student, Credentials, PersonalDetails, ContactInfo

class TestStudent(unittest.TestCase):
    def test_student_default(self):
        student = Student()
        self.assertIsNone(student.student_id)
        self.assertIsNone(student.major)

        self.assertIsInstance(student.personal_details, PersonalDetails)
        self.assertIsNone(student.personal_details.first_name)
        self.assertIsNone(student.personal_details.last_name)

        self.assertIsInstance(student.contact_info, ContactInfo)
        self.assertIsNone(student.contact_info.phone_number)
        self.assertIsNone(student.contact_info.street_address)
        self.assertIsNone(student.contact_info.city)
        self.assertIsNone(student.contact_info.state)
        self.assertIsNone(student.contact_info.zip_code)

        self.assertIsInstance(student.credentials, Credentials)
        self.assertIsNone(student.credentials.user_id)
        self.assertIsNone(student.credentials.username)
        self.assertIsNone(student.credentials.email)
        self.assertIsNone(student.credentials.user_type)
        self.assertIsNone(student.credentials.password_hash)


        print("Default Student test passed.")

    def test_student_with_arguments(self):
        student_id = 1
        major = "Computer Science"
        personal_details = {
            "first_name": "John",
            "last_name": "Doe"
        }
        contact_info = {
            "phone_number": "1234567890",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345"
        }
        credentials = {
            "user_id": 1,
            "username": "johndoe",
            "email": "testuser@email.com",
            "user_type": "student",
            "password_hash": "hashed_password"
        }
        student = Student(
            student_id=student_id,
            major=major,
            personal_details=PersonalDetails(**personal_details),
            contact_info=ContactInfo(**contact_info),
            credentials=Credentials(**credentials)
        )
        self.assertEqual(student.student_id, student_id)
        self.assertEqual(student.major, major)
        self.assertEqual(student.personal_details.first_name, personal_details["first_name"])
        self.assertEqual(student.personal_details.last_name, personal_details["last_name"])
        self.assertEqual(student.contact_info.phone_number, contact_info["phone_number"])
        self.assertEqual(student.contact_info.street_address, contact_info["street_address"])
        self.assertEqual(student.contact_info.city, contact_info["city"])
        self.assertEqual(student.contact_info.state, contact_info["state"])
        self.assertEqual(student.contact_info.zip_code, contact_info["zip_code"])
        self.assertEqual(student.credentials.user_id, credentials["user_id"])
        self.assertEqual(student.credentials.username, credentials["username"])
        self.assertEqual(student.credentials.email, credentials["email"])
        self.assertEqual(student.credentials.user_type, credentials["user_type"])
        self.assertEqual(student.credentials.password_hash, credentials["password_hash"])
        print("Student with arguments test passed.")

    def test_get_role_permissions(self):
        student = Student()
        expected_permissions = {
            "can_view_grades": True,
            "can_edit_profiles": True,
            "can_delete_users": False
        }
        self.assertEqual(student.get_role_permissions(), expected_permissions)
        print("Student get_role_permissions test passed.")

    def test_to_dict(self):
        student_id = 1
        major = "Computer Science"
        personal_details = {
            "first_name": "John",
            "last_name": "Doe"
        }
        contact_info = {
            "phone_number": "1234567890",
            "street_address": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "zip_code": "12345"
        }
        credentials = {
            "user_id": 1,
            "username": "johndoe",
            "email": "testuser@email.com",
            "user_type": "student",
            "password_hash": "hashed_password"
        }

        student = Student(
            student_id=student_id,
            major=major,
            personal_details=PersonalDetails(**personal_details),
            contact_info=ContactInfo(**contact_info),
            credentials=Credentials(**credentials)
        )
        expected_dict = {
            "student_id": student_id,
            "major": major,
            **personal_details,
            **contact_info,
            **{k: v for k, v in credentials.items() if k != "password_hash"}  # Exclude password_hash from the expected dict
        }
        self.assertEqual(student.to_dict(), expected_dict)
        print("Student to_dict test passed.")



