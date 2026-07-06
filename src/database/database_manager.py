import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


class Database:

    def __init__(self, db_name: str = "nexus.db"):
        # Use the repository-level data directory (relative to process CWD)
        data_dir = os.path.abspath("data")
        os.makedirs(data_dir, exist_ok=True)
        if os.path.isabs(db_name):
            self.db_path = db_name
        else:
            self.db_path = os.path.join(data_dir, db_name)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.schema_path = os.path.join(base_dir, "schema.sql")

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_database(self) -> None:
        if not os.path.exists(self.schema_path):
            print("Schema file not found")
            return

        print("Day 1 launch: Database being created")

        with open(self.schema_path, "r", encoding="utf-8") as file:
            schema_script = file.read()

        try:
            with self.get_connection() as conn:
                conn.executescript(schema_script)
                conn.commit()
            print("Database created")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise

    def fetch_all(self, sql_string: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_string, params)
            return [dict(row) for row in cursor.fetchall()]  # Connection context manager closes everything safely

    def fetch_one(self, sql_string: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql_string, params)
            db_row = cursor.fetchone()
            return dict(db_row) if db_row else None

    def execute_write(self, sql_string: str, params: Tuple[Any, ...] = ()) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql_string, params)
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Write error: {e}")
            return False