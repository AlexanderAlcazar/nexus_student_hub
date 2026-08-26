import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from repositories.user_repository import UserRepository


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        iterations: int = 120000,
        salt_size: int = 16,
        jwt_secret: str = "dev-only-change-me-at-least-32-bytes-long",
        access_ttl_seconds: int = 900,
        refresh_ttl_seconds: int = 2592000,
    ):
        self.user_repository = user_repository
        self.iterations = iterations
        self.salt_size = salt_size
        self.jwt_secret = jwt_secret
        self.access_ttl_seconds = access_ttl_seconds
        self.refresh_ttl_seconds = refresh_ttl_seconds
        self.jwt_algorithm = "HS256"

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

    def login_with_session(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.user_repository.find_by_username(username)
        if user is None:
            return None

        if not self._verify_password(password, user["password_hash"]):
            return None

        session_bundle = self._issue_token_bundle(user)
        return {
            "user": self._public_user(user),
            **session_bundle,
        }

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

    @staticmethod
    def _hash_refresh_token(refresh_token: str) -> str:
        return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()

    def _create_access_token(self, user: Dict[str, Any]) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user["user_id"]),
            "username": user["username"],
            "user_type": user["user_type"],
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=self.access_ttl_seconds)).timestamp()),
            "token_type": "access",
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def _issue_token_bundle(self, user: Dict[str, Any]) -> Dict[str, Any]:
        access_token = self._create_access_token(user)
        refresh_token = secrets.token_urlsafe(48)
        refresh_expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.refresh_ttl_seconds)
        refresh_hash = self._hash_refresh_token(refresh_token)
        session = self.user_repository.create_auth_session(
            user_id=user["user_id"],
            refresh_token_hash=refresh_hash,
            expires_at=refresh_expires_at,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_ttl_seconds,
            "refresh_session_id": session["session_id"],
        }

    def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        refresh_hash = self._hash_refresh_token(refresh_token)
        existing = self.user_repository.find_active_auth_session_by_hash(refresh_hash)
        if existing is None:
            raise ValueError("Invalid or expired refresh token.")

        user = self.user_repository.get_user_by_id(existing["user_id"])
        if user is None:
            raise ValueError("User not found for refresh token.")

        rotated = self._issue_token_bundle(user)
        revoked = self.user_repository.revoke_auth_session(
            session_id=existing["session_id"],
            revoked_at=datetime.now(timezone.utc),
            replaced_by_session_id=rotated["refresh_session_id"],
        )
        if not revoked:
            raise RuntimeError("Refresh token rotation failed.")

        return {
            "access_token": rotated["access_token"],
            "refresh_token": rotated["refresh_token"],
            "token_type": rotated["token_type"],
            "expires_in": rotated["expires_in"],
        }

    def revoke_refresh_session(self, refresh_token: str) -> bool:
        refresh_hash = self._hash_refresh_token(refresh_token)
        existing = self.user_repository.find_active_auth_session_by_hash(refresh_hash)
        if existing is None:
            return False
        return self.user_repository.revoke_auth_session(
            session_id=existing["session_id"],
            revoked_at=datetime.now(timezone.utc),
        )

    def decode_access_token(self, access_token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(access_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
        except jwt.PyJWTError as exc:
            raise ValueError("Invalid or expired access token.") from exc
        if payload.get("token_type") != "access":
            raise ValueError("Invalid access token type.")
        return payload
