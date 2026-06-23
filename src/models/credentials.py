class Credentials:
    """Handles core network authentication, account identifiers, and system access levels."""
    def __init__(
            self,
            user_id: int = None,
            username: str = None,
            email: str = None,
            user_type: str = None,
            password_hash: str = None
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