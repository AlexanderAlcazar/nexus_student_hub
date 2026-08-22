from typing import Optional

from models.contact_info import ContactInfo
from models.credentials import Credentials
from models.personal_details import PersonalDetails
from models.user_base import UserBase

class Student(UserBase):

    def __init__(
        self,
        student_id: Optional[int] = None,
        major: Optional[str] = None,
        personal_details: Optional[PersonalDetails] = None,
        contact_info: Optional[ContactInfo] = None,
        credentials: Optional[Credentials] = None

    ):
        self.student_id = student_id
        self.major = major
        super().__init__(
            personal_details=personal_details,
            contact_info=contact_info,
            credentials=credentials,
        )

    def get_role_permissions(self) -> dict:
        return {
            "can_view_grades": True,
            "can_edit_profiles": True,  # Can edit their own contact information
            "can_delete_users": False  # Absolutely not!
        }
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "student_id": self.student_id,
            "major": self.major,
        })
        return data