from models.credentials import Credentials
from models.personal_details import PersonalDetails
from models.contact_info import ContactInfo

class Student():

    def __init__(
        self,
        student_id: int = None,
        major: str = None,
        personal_details: PersonalDetails = None,
        contact_info: ContactInfo = None,
        credentials: Credentials = None

    ):
        self.student_id = student_id
        self.major = major
        self.personal_details = personal_details if personal_details is not None else PersonalDetails()
        self.contact_info = contact_info if contact_info is not None else ContactInfo()
        self.credentials = credentials if credentials is not None else Credentials()

    def get_role_permissions(self) -> dict:
        return {
            "can_view_grades": True,
            "can_edit_profiles": True,  # Can edit their own contact information
            "can_delete_users": False  # Absolutely not!
        }
    def to_dict(self) -> dict:
        data = {
            "student_id": self.student_id,
            "major": self.major
        }
        data.update(self.personal_details.to_dict())
        data.update(self.contact_info.to_dict())
        data.update(self.credentials.to_dict())
        return data