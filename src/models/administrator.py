from typing import Optional

from models.contact_info import ContactInfo
from models.credentials import Credentials
from models.personal_details import PersonalDetails
from models.user_base import UserBase

class Administrator(UserBase):

    def __init__(
        self,
        admin_id: Optional[int] = None,
        personal_details: Optional[PersonalDetails] = None,
        contact_info: Optional[ContactInfo] = None,
        credentials: Optional[Credentials] = None
    ):
        self.admin_id = admin_id
        super().__init__(
            personal_details=personal_details,
            contact_info=contact_info,
            credentials=credentials,
        )

    def get_role_permissions(self) -> dict:
        return {
            "can_view_grades": True,
            "can_edit_profiles": True,
            "can_delete_users": True  
        }

    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            "admin_id": self.admin_id,
        })
        return data