import sqlite3
import unittest

from database.database_manager import Database
from repositories.user_repository import UserRepository
from services.auth_service import AuthService


class _PersistentConnection:
    """Wraps a sqlite3.Connection so that close() is a no-op.

    The Database class uses ``contextlib.closing`` around every connection it
    opens, which would destroy the single in-memory database after the first
    call.  Suppressing close() keeps the in-memory schema and data alive for
    the entire test.
    """

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def __getattr__(self, name: str):
        return getattr(self._conn, name)

    def close(self) -> None:  # intentional no-op
        pass


def _build_auth_service() -> AuthService:
    """Return an AuthService wired to a fresh in-memory database."""
    shared_conn = sqlite3.connect(":memory:", check_same_thread=False)
    shared_conn.row_factory = sqlite3.Row
    shared_conn.execute("PRAGMA foreign_keys = ON;")

    wrapper = _PersistentConnection(shared_conn)

    db = Database(
        db_name=":memory:",
        connection_factory=lambda _: wrapper,
    )
    db.initialize_database()
    repo = UserRepository(db)
    return AuthService(repo)


class TestAuthService(unittest.TestCase):

    def setUp(self):
        self.service = _build_auth_service()

    # ------------------------------------------------------------------
    # register_user
    # ------------------------------------------------------------------

    def test_register_returns_public_user(self):
        user = self.service.register_user("alice", "alice@example.com", "secret", "student")
        self.assertEqual(user["username"], "alice")
        self.assertEqual(user["email"], "alice@example.com")
        self.assertEqual(user["user_type"], "student")
        self.assertIn("user_id", user)
        self.assertNotIn("password_hash", user)
        print("register_user returns public user dict test passed.")

    def test_register_duplicate_username_raises(self):
        self.service.register_user("bob", "bob@example.com", "pass1", "student")
        with self.assertRaises(Exception):
            self.service.register_user("bob", "other@example.com", "pass2", "student")
        print("register_user duplicate username raises exception test passed.")

    def test_register_stores_different_hashes_for_same_password(self):
        """Salt must be random — two users with the same password get different hashes."""
        self.service.register_user("u1", "u1@example.com", "samepassword", "student")
        self.service.register_user("u2", "u2@example.com", "samepassword", "student")

        repo = self.service.user_repository
        h1 = repo.find_by_username("u1")["password_hash"]
        h2 = repo.find_by_username("u2")["password_hash"]
        self.assertNotEqual(h1, h2)
        print("register_user stores different hashes for same password test passed.")

    # ------------------------------------------------------------------
    # authenticate
    # ------------------------------------------------------------------

    def test_authenticate_correct_password_returns_user(self):
        self.service.register_user("carol", "carol@example.com", "mypassword", "student")
        result = self.service.authenticate("carol", "mypassword")
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "carol")
        self.assertNotIn("password_hash", result)
        print("authenticate with correct password returns user test passed.")

    def test_authenticate_wrong_password_returns_none(self):
        self.service.register_user("dave", "dave@example.com", "rightpass", "student")
        result = self.service.authenticate("dave", "wrongpass")
        self.assertIsNone(result)
        print("authenticate with wrong password returns None test passed.")

    def test_authenticate_unknown_user_returns_none(self):
        result = self.service.authenticate("nobody", "anypassword")
        self.assertIsNone(result)
        print("authenticate unknown user returns None test passed.")

    def test_authenticate_administrator_role(self):
        self.service.register_user("admin1", "admin1@example.com", "adminpass", "administrator")
        result = self.service.authenticate("admin1", "adminpass")
        self.assertIsNotNone(result)
        self.assertEqual(result["user_type"], "administrator")
        print("authenticate administrator role test passed.")

    def test_authenticate_does_not_expose_password_hash(self):
        self.service.register_user("eve", "eve@example.com", "secret", "student")
        result = self.service.authenticate("eve", "secret")
        self.assertNotIn("password_hash", result)
        print("authenticate does not expose password_hash test passed.")
