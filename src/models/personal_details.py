from typing import Optional


class PersonalDetails:
    """Handles real-world human identity metrics."""
    def __init__(self, first_name: Optional[str] = None, last_name: Optional[str] = None):
        self.first_name = first_name
        self.last_name = last_name

    def to_dict(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name
        }