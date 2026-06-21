from abc import ABC, abstractmethod


class User(ABC):

    def __init__(
            self,
            user_id: int = None,
            username: str = None,
            email: str = None,
            password_hash: str = None,
            user_type: str = None
    ):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.user_type = user_type

    def verify_password(self, password_input: str) -> bool:
        """
        Verifies a plain-text password input against the stored secure hash.
        """
        # TODO: Replace this temporary plain-text check with a secure
        # cryptographic comparison using hashlib or bcrypt once the database layer is implemented.
        return self.password_hash == password_input

    @abstractmethod
    def get_role_permissions(self) -> dict:
        """
        Must be overridden to return specific domain access rights.
        """
        # TODO: Implement this in subclasses (Student/Admin) to return role-based
        # permissions matrices for UI rendering and server-side request verification.
        pass

   
    def to_dict(self) -> dict:
       return{
           "user_id": self.user_id,
           "username": self.username,
           "email": self.email,
           "user_type": self.user_type

       }
