from datetime import date

from models import User
from models import ContactInfo

class Student(User):

    def __init__(
        self,
        student_id: int = None,
        first_name: str = None,
        last_name: str = None,
        major: str = None,
        contact_info: ContactInfo = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.contact_info = contact_info if contact_info is not None else ContactInfo()

    def get_role_permissions(self) -> dict:
        return {
            "can_view_grades": True,
            "can_edit_profiles": True,  # Can edit their own contact information
            "can_delete_users": False  # Absolutely not!
        }
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update(
            {
                "student_id": self.student_id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "major": self.major,
                "contact_info": self.contact_info.to_dict() if self.contact_info else None
            }
        )
        return data