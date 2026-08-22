from contextlib import closing
from typing import Any, Dict, Optional

from database.database_manager import Database


class UserRepository:
    def __init__(self, database: Database):
        self.database = database

    def create_user(self, username: str, email: str, password_hash: bytes, user_type: str) -> Dict[str, Any]:
        with closing(self.database.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, user_type)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, password_hash, user_type),
            )
            conn.commit()

        created_user_id = cursor.lastrowid
        created_user = self.get_user_by_id(created_user_id)
        if created_user is None:
            raise RuntimeError("User creation succeeded but the new user could not be loaded.")
        return created_user

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, username, email, password_hash, user_type, created_at
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        )

    def find_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, username, email, password_hash, user_type, created_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        )

    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            """
            SELECT user_id, username, email, password_hash, user_type, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        )
