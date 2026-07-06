import unittest
from models.contact_info import ContactInfo


class TestContactInfo(unittest.TestCase):

    def test_contact_default(self):
        contact_info = ContactInfo()
        self.assertIsNone(contact_info.phone_number)
        self.assertIsNone(contact_info.street_address)
        self.assertIsNone(contact_info.city)
        self.assertIsNone(contact_info.state)
        self.assertIsNone(contact_info.zip_code)

    def test_contact_with_arguments(self):
        phone_number = "80555221629"
        street_address = "123 Main St"
        city = "Los Angeles"
        state = "CA"
        zip_code = "90001"
        contact_info = ContactInfo(
            phone_number=phone_number,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code
        )
        self.assertEqual(contact_info.phone_number, phone_number)
        self.assertEqual(contact_info.street_address, street_address)
        self.assertEqual(contact_info.city, city)
        self.assertEqual(contact_info.state, state)
        self.assertEqual(contact_info.zip_code, zip_code)

    def test_to_dict(self):
        phone_number = "80555221629"
        street_address = "123 Main St"
        city = "Los Angeles"
        state = "CA"
        zip_code = "90001"
        contact_info = ContactInfo(
            phone_number=phone_number,
            street_address=street_address,
            city=city,
            state=state,
            zip_code=zip_code
        )
        expected_dict = {
            "phone_number": phone_number,
            "street_address": street_address,
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
        self.assertEqual(contact_info.to_dict(), expected_dict)

