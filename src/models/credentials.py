from typing import Optional


class Credentials:
    """Represents user login and identity data."""
    def __init__(
            self,
            user_id: Optional[int] = None,
            username: Optional[str] = None,
            email: Optional[str] = None,
            user_type: Optional[str] = None,
            password_hash: Optional[bytes] = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.user_type = user_type
        self.password_hash = password_hash

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "user_type": self.user_type
        }