import os
import sqlite3
from contextlib import closing
from typing import Any, Callable, Dict, List, Optional, Tuple


class Database:

    def __init__(
        self,
        db_name: str = "nexus.db",
        data_dir: Optional[str] = None,
        schema_path: Optional[str] = None,
        connection_factory: Callable[[str], sqlite3.Connection] = sqlite3.connect,
        schema_loader: Optional[Callable[[str], str]] = None,
    ):
        if data_dir is None:
            data_dir = os.path.abspath("data")

        os.makedirs(data_dir, exist_ok=True)

        if os.path.isabs(db_name):
            self.db_path = db_name
        else:
            self.db_path = os.path.join(data_dir, db_name)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.schema_path = schema_path or os.path.join(base_dir, "schema.sql")
        self._connection_factory = connection_factory
        self._schema_loader = schema_loader or self._read_schema

    @staticmethod
    def _read_schema(schema_path: str) -> str:
        with open(schema_path, "r", encoding="utf-8") as file:
            return file.read()

    def get_connection(self) -> sqlite3.Connection:
        conn = self._connection_factory(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def initialize_database(self) -> None:
        if not os.path.exists(self.schema_path):
            print("Schema file not found")
            return

        print("Day 1 launch: Database being created")

        try:
            schema_script = self._schema_loader(self.schema_path)
            with closing(self.get_connection()) as conn:
                conn.executescript(schema_script)
                conn.commit()
            print("Database created")
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise

    def fetch_all(self, sql_string: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        with closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_string, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, sql_string: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        with closing(self.get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_string, params)
            db_row = cursor.fetchone()
            return dict(db_row) if db_row else None

    def execute_write(self, sql_string: str, params: Tuple[Any, ...] = ()) -> bool:
        try:
            with closing(self.get_connection()) as conn:
                cursor = conn.cursor()
                cursor.execute(sql_string, params)
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Write error: {e}")
            return False