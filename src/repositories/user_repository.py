from datetime import datetime, timezone
from typing import Any, Dict, Optional

from database.database_manager import Database


class UserRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_user(self, username: str, email: str, password_hash: bytes, user_type: str) -> Dict[str, Any]:
        with self.database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, user_type)
                    VALUES (%s, %s, %s, %s)
                    RETURNING user_id
                    """,
                    (username, email, password_hash, user_type),
                )
                created_user_id = cursor.fetchone()[0]
            conn.commit()
        created_user = self.get_user_by_id(created_user_id)
        if created_user is None:
            raise RuntimeError("User creation succeeded but the new user could not be loaded.")
        return created_user

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, username, email, password_hash, user_type, created_at
            FROM users
            WHERE user_id = %s
            """,
            (user_id,),
        )

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, username, email, password_hash, user_type, created_at
            FROM users
            WHERE username = %s
            """,
            (username,),
        )

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, username, email, password_hash, user_type, created_at
            FROM users
            WHERE email = %s
            """,
            (email,),
        )

    def get_personal_details(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, first_name, last_name
            FROM personal_details
            WHERE user_id = %s
            """,
            (user_id,),
        )

    def save_personal_details(self, user_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        with self.database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO personal_details (user_id, first_name, last_name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name
                    """,
                    (user_id, first_name, last_name),
                )
            conn.commit()

        stored = self.get_personal_details(user_id)
        if stored is None:
            raise RuntimeError("Personal details could not be saved for the provided user.")
        return stored

    def get_contact_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, phone_number, street_address, city, state, zip_code
            FROM contact_info
            WHERE user_id = %s
            """,
            (user_id,),
        )

    def save_contact_info(
        self,
        user_id: int,
        phone_number: Optional[str] = None,
        street_address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        zip_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        with self.database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO contact_info (user_id, phone_number, street_address, city, state, zip_code)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET phone_number = EXCLUDED.phone_number,
                        street_address = EXCLUDED.street_address,
                        city = EXCLUDED.city,
                        state = EXCLUDED.state,
                        zip_code = EXCLUDED.zip_code
                    """,
                    (user_id, phone_number, street_address, city, state, zip_code),
                )
            conn.commit()

        stored = self.get_contact_info(user_id)
        if stored is None:
            raise RuntimeError("Contact information could not be saved for the provided user.")
        return stored

    def get_student_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, student_id, major
            FROM students
            WHERE user_id = %s
            """,
            (user_id,),
        )

    def save_student_profile(self, user_id: int, major: Optional[str] = None) -> Dict[str, Any]:
        with self.database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO students (user_id, major)
                    VALUES (%s, %s)
                    ON CONFLICT (user_id) DO UPDATE
                    SET major = EXCLUDED.major
                    """,
                    (user_id, major),
                )
            conn.commit()

        stored = self.get_student_profile(user_id)
        if stored is None:
            raise RuntimeError("Student profile could not be saved for the provided user.")
        return stored

    def get_profile_by_user_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_id(user_id)
        if user is None:
            return None

        profile = dict(user)
        personal_details = self.get_personal_details(user_id) or {}
        contact_info = self.get_contact_info(user_id) or {}
        student_profile = self.get_student_profile(user_id)

        for key in ("user_id",):
            personal_details.pop(key, None)
            contact_info.pop(key, None)

        profile.update(personal_details)
        profile.update(contact_info)

        if student_profile is not None:
            profile["major"] = student_profile.get("major")

        return profile

    def create_auth_session(self, user_id: int, refresh_token_hash: str, expires_at: datetime) -> Dict[str, Any]:
        with self.database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO auth_sessions (user_id, refresh_token_hash, expires_at)
                    VALUES (%s, %s, %s)
                    RETURNING session_id
                    """,
                    (user_id, refresh_token_hash, expires_at),
                )
                session_id = cursor.fetchone()[0]
            conn.commit()
        created = self.get_auth_session_by_id(session_id)
        if created is None:
            raise RuntimeError("Auth session creation succeeded but the session could not be loaded.")
        return created

    def get_auth_session_by_id(self, session_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT session_id, user_id, refresh_token_hash, expires_at, revoked_at, replaced_by_session_id, created_at
            FROM auth_sessions
            WHERE session_id = %s
            """,
            (session_id,),
        )

    def find_active_auth_session_by_hash(self, refresh_token_hash: str) -> Optional[Dict[str, Any]]:
        session = self.database.fetch_one(
            """
            SELECT session_id, user_id, refresh_token_hash, expires_at, revoked_at, replaced_by_session_id, created_at
            FROM auth_sessions
            WHERE refresh_token_hash = %s
            """,
            (refresh_token_hash,),
        )
        if session is None:
            return None
        if session["revoked_at"] is not None:
            return None

        expires_value = session["expires_at"]
        if isinstance(expires_value, str):
            expires_at = datetime.fromisoformat(expires_value)
        else:
            expires_at = expires_value
        if expires_at <= datetime.now(timezone.utc):
            return None
        return session

    def revoke_auth_session(
        self,
        session_id: int,
        revoked_at: datetime,
        replaced_by_session_id: Optional[int] = None,
    ) -> bool:
        with self.database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE auth_sessions
                    SET revoked_at = %s, replaced_by_session_id = %s
                    WHERE session_id = %s AND revoked_at IS NULL
                    """,
                    (revoked_at, replaced_by_session_id, session_id),
                )
                affected_rows = cursor.rowcount
            conn.commit()
            return affected_rows > 0
