import os
import tempfile
import unittest
from database.database_manager import Database


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(self.db_path)
        self.db.initialize_database()

    def tearDown(self):
        # Close connection held by Database instance if any exists
        if hasattr(self.db, "close"):
            self.db.close()

        # Clean up the temporary directory safely
        try:
            self.temp_dir.cleanup()
        except PermissionError:
            # Fallback for Windows file-locking quirks during test teardown
            pass

    def test_connection(self):
        # Use context manager or close conn explicitly so SQLite releases the file handle
        with self.db.get_connection() as conn:
            self.assertIsNotNone(conn)

    def test_initialize_database(self):
        # 1. Verify the database file exists on disk
        self.assertTrue(os.path.exists(self.db_path))

        # 2. Query SQLite for all table names created in the schema
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            rows = cursor.fetchall()

        # 3. Extract the table names into a simple list of strings
        table_names = [row[0] for row in rows]

        # 4. Define your expected application tables (excluding SQLite system tables)
        expected_tables = [
            "administrators",
            "contact_info",
            "personal_details",
            "students",
            "users",
        ]

        # 5. Assert that every expected table exists in the database
        for table in expected_tables:
            self.assertIn(
                table,
                table_names,
                f"Expected table '{table}' was not found in the database.",
            )



if __name__ == "__main__":
    unittest.main()