import sqlite3
import unittest

from database.database_manager import Database
from repositories.user_repository import UserRepository


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


def _in_memory_db() -> Database:
    """Return a Database backed by an in-memory SQLite connection."""
    shared_conn = sqlite3.connect(":memory:", check_same_thread=False)
    shared_conn.row_factory = sqlite3.Row
    shared_conn.execute("PRAGMA foreign_keys = ON;")

    wrapper = _PersistentConnection(shared_conn)

    db = Database(
        db_name=":memory:",
        connection_factory=lambda _: wrapper,
    )
    db.initialize_database()
    return db


class TestUserRepository(unittest.TestCase):

    def setUp(self):
        self.db = _in_memory_db()
        self.repo = UserRepository(self.db)
        self.password_hash = b"\x00" * 32

    # ------------------------------------------------------------------
    # create_user
    # ------------------------------------------------------------------

    def test_create_user_returns_user_dict(self):
        user = self.repo.create_user("alice", "alice@example.com", self.password_hash, "student")
        self.assertEqual(user["username"], "alice")
        self.assertEqual(user["email"], "alice@example.com")
        self.assertEqual(user["user_type"], "student")
        self.assertIn("user_id", user)
        print("create_user returns user dict test passed.")

    def test_create_user_assigns_auto_id(self):
        user1 = self.repo.create_user("u1", "u1@example.com", self.password_hash, "student")
        user2 = self.repo.create_user("u2", "u2@example.com", self.password_hash, "administrator")
        self.assertNotEqual(user1["user_id"], user2["user_id"])
        print("create_user assigns auto-increment IDs test passed.")

    def test_create_user_stores_password_hash(self):
        user_row = self.repo.create_user("bob", "bob@example.com", self.password_hash, "student")
        fetched = self.repo.get_user_by_id(user_row["user_id"])
        self.assertEqual(fetched["password_hash"], self.password_hash)
        print("create_user stores password hash test passed.")

    def test_create_user_duplicate_username_raises(self):
        self.repo.create_user("dup", "dup@example.com", self.password_hash, "student")
        with self.assertRaises(Exception):
            self.repo.create_user("dup", "other@example.com", self.password_hash, "student")
        print("create_user duplicate username raises exception test passed.")

    # ------------------------------------------------------------------
    # get_user_by_id
    # ------------------------------------------------------------------

    def test_get_user_by_id_returns_user(self):
        created = self.repo.create_user("carol", "carol@example.com", self.password_hash, "student")
        fetched = self.repo.get_user_by_id(created["user_id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["username"], "carol")
        print("get_user_by_id returns user test passed.")

    def test_get_user_by_id_missing_returns_none(self):
        result = self.repo.get_user_by_id(99999)
        self.assertIsNone(result)
        print("get_user_by_id missing returns None test passed.")

    # ------------------------------------------------------------------
    # find_by_username
    # ------------------------------------------------------------------

    def test_find_by_username_returns_user(self):
        self.repo.create_user("dave", "dave@example.com", self.password_hash, "student")
        found = self.repo.find_by_username("dave")
        self.assertIsNotNone(found)
        self.assertEqual(found["email"], "dave@example.com")
        print("find_by_username returns user test passed.")

    def test_find_by_username_missing_returns_none(self):
        result = self.repo.find_by_username("nobody")
        self.assertIsNone(result)
        print("find_by_username missing returns None test passed.")

    # ------------------------------------------------------------------
    # find_by_email
    # ------------------------------------------------------------------

    def test_find_by_email_returns_user(self):
        self.repo.create_user("eve", "eve@example.com", self.password_hash, "administrator")
        found = self.repo.find_by_email("eve@example.com")
        self.assertIsNotNone(found)
        self.assertEqual(found["username"], "eve")
        print("find_by_email returns user test passed.")

    def test_find_by_email_missing_returns_none(self):
        result = self.repo.find_by_email("ghost@example.com")
        self.assertIsNone(result)
        print("find_by_email missing returns None test passed.")
