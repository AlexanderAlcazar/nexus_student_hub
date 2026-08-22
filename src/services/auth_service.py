import hashlib
import hmac
import os
from typing import Any, Dict, Optional

from repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, user_repository: UserRepository, iterations: int = 120000, salt_size: int = 16):
        self.user_repository = user_repository
        self.iterations = iterations
        self.salt_size = salt_size

    def register_user(self, username: str, email: str, password: str, user_type: str) -> Dict[str, Any]:
        salt = os.urandom(self.salt_size)
        password_hash = self._hash_password(password, salt)
        user = self.user_repository.create_user(username, email, password_hash, user_type)
        return self._public_user(user)

    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.user_repository.find_by_username(username)
        if user is None:
            return None

        if not self._verify_password(password, user["password_hash"]):
            return None

        return self._public_user(user)

    def _hash_password(self, password: str, salt: bytes) -> bytes:
        password_bytes = password.encode("utf-8")
        digest = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, self.iterations)
        return salt + digest

    def _verify_password(self, password: str, stored_hash: bytes) -> bool:
        salt = stored_hash[: self.salt_size]
        expected_hash = stored_hash[self.salt_size :]
        actual_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.iterations,
        )
        return hmac.compare_digest(actual_hash, expected_hash)

    @staticmethod
    def _public_user(user: Dict[str, Any]) -> Dict[str, Any]:
        return {key: value for key, value in user.items() if key != "password_hash"}
