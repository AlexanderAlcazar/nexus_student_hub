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

    def complete_profile(self, user_id: int, profile_data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        user = self.user_repository.get_user_by_id(user_id)
        if user is None:
            raise ValueError("User not found.")

        normalized = self._normalize_profile_data(profile_data, kwargs)
        if not normalized:
            raise ValueError("At least one profile field must be provided.")

        personal_details = normalized.get("personal_details") or {}
        contact_info = normalized.get("contact_info") or {}

        if "first_name" in normalized or "last_name" in normalized:
            self.user_repository.save_personal_details(
                user_id,
                first_name=normalized.get("first_name", personal_details.get("first_name")),
                last_name=normalized.get("last_name", personal_details.get("last_name")),
            )
        elif personal_details:
            self.user_repository.save_personal_details(
                user_id,
                first_name=personal_details.get("first_name"),
                last_name=personal_details.get("last_name"),
            )

        if (
            "phone_number" in normalized
            or "street_address" in normalized
            or "city" in normalized
            or "state" in normalized
            or "zip_code" in normalized
        ):
            self.user_repository.save_contact_info(
                user_id,
                phone_number=normalized.get("phone_number", contact_info.get("phone_number")),
                street_address=normalized.get("street_address", contact_info.get("street_address")),
                city=normalized.get("city", contact_info.get("city")),
                state=normalized.get("state", contact_info.get("state")),
                zip_code=normalized.get("zip_code", contact_info.get("zip_code")),
            )
        elif contact_info:
            self.user_repository.save_contact_info(
                user_id,
                phone_number=contact_info.get("phone_number"),
                street_address=contact_info.get("street_address"),
                city=contact_info.get("city"),
                state=contact_info.get("state"),
                zip_code=contact_info.get("zip_code"),
            )

        if user["user_type"] == "student" and "major" in normalized:
            self.user_repository.save_student_profile(user_id, normalized["major"])

        profile = self.user_repository.get_profile_by_user_id(user_id)
        if profile is None:
            raise RuntimeError("Profile completion succeeded but the profile could not be loaded.")
        return self._public_user(profile)

    @staticmethod
    def _normalize_profile_data(profile_data: Optional[Dict[str, Any]], kwargs: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}

        if profile_data:
            normalized.update(profile_data)

        if kwargs:
            normalized.update(kwargs)

        if "personal_details" in normalized and isinstance(normalized["personal_details"], dict):
            normalized.update(normalized["personal_details"])

        if "contact_info" in normalized and isinstance(normalized["contact_info"], dict):
            normalized.update(normalized["contact_info"])

        return normalized

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
