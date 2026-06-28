import os
import sqlite3

class Database:

    def __init__(self, db_name: str = "nexus.db"):
        self.db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.schema_path = os.path.join(os.path.dirname(__file__),"schema.sql")

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_database(self):

        if os.path.exists(self.db_path):
            print("Database found")
            return

        if not os.path.exists(self.schema_path):
            print("Schema fie not found")
            return

        print("Day 1 launch: Database being created")

        with open(self.schema_path, "r") as file:
            schema_script = file.read()

        conn = self.get_connection()

        try:
            conn.execute(schema_script)
            conn.commit()
            print("Database created")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            conn.close()

