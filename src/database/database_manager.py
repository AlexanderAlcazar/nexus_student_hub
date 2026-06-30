import os
import sqlite3


class Database:

    def __init__(self, db_name: str = "nexus.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_database(self):
        if not os.path.exists(self.schema_path):
            print("Schema file not found")
            return

        print("Day 1 launch: Database being created")

        with open(self.schema_path, "r") as file:
            schema_script = file.read()

        try:
            with self.get_connection() as conn:
                conn.executescript(schema_script)
            print("Database created")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise

    def fetch_all(self, sql_string, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql_string, params)
                return [dict(row) for row in cursor.fetchall()]
            finally:
                cursor.close()

    def fetch_one(self, sql_string, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql_string, params)
                db_row = cursor.fetchone()
                return dict(db_row) if db_row else None
            finally:
                cursor.close()

# TODO: Implement execute_write(self, sql_string, params=()) for INSERT, UPDATE, DELETE