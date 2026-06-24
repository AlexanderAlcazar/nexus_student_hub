from models.credentials import Credentials
from models.personal_details import PersonalDetails
from models.contact_info import ContactInfo

class Administrator:

    def __init__(
        self,
        admin_id: int = None,
        personal_details: PersonalDetails = None,
        contact_info: ContactInfo = None,
        credentials: Credentials = None
    ):
        self.admin_id = admin_id
        self.personal_details = personal_details if personal_details is not None else PersonalDetails()
        self.contact_info = contact_info if contact_info is not None else ContactInfo()
        self.credentials = credentials if credentials is not None else Credentials()

    def get_role_permissions(self) -> dict:
        return {
            "can_view_grades": True,
            "can_edit_profiles": True,
            "can_delete_users": True  
        }

    def to_dict(self) -> dict:
        data = {
            "admin_id": self.admin_id,
        }
        data.update(self.personal_details.to_dict())
        data.update(self.contact_info.to_dict())
        data.update(self.credentials.to_dict())
        return data