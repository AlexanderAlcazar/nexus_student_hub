import os
import tempfile
import unittest
from database.database_manager import Database


class TestDatabaseManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.db = Database(db_name="test.db", data_dir=self.temp_dir.name)
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
        self.assertEqual(self.db.db_path, self.db_path)

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

    def test_schema_uses_normalized_role_tables(self):
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(students);")
            student_columns = [row[1] for row in cursor.fetchall()]
            self.assertEqual(student_columns, ["student_id", "user_id", "major"])

            cursor.execute("PRAGMA table_info(administrators);")
            admin_columns = [row[1] for row in cursor.fetchall()]
            self.assertEqual(admin_columns, ["admin_id", "user_id"])

            cursor.execute("PRAGMA index_list(students);")
            student_indexes = cursor.fetchall()
            self.assertTrue(any(row[2] for row in student_indexes), "students.user_id should be unique")

            cursor.execute("PRAGMA index_list(administrators);")
            admin_indexes = cursor.fetchall()
            self.assertTrue(any(row[2] for row in admin_indexes), "administrators.user_id should be unique")



if __name__ == "__main__":
    unittest.main()