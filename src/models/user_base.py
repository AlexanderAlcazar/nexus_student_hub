from typing import Any, Dict, Optional

from models.contact_info import ContactInfo
from models.credentials import Credentials
from models.personal_details import PersonalDetails


class UserBase:
    def __init__(
        self,
        personal_details: Optional[PersonalDetails] = None,
        contact_info: Optional[ContactInfo] = None,
        credentials: Optional[Credentials] = None,
    ):
        self.personal_details = personal_details if personal_details is not None else PersonalDetails()
        self.contact_info = contact_info if contact_info is not None else ContactInfo()
        self.credentials = credentials if credentials is not None else Credentials()

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        data.update(self.personal_details.to_dict())
        data.update(self.contact_info.to_dict())
        data.update(self.credentials.to_dict())
        return data
