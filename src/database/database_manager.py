import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import psycopg
from psycopg.rows import dict_row


class Database:
    def __init__(
        self,
        db_name: str = "nexus_student_hub",
        data_dir: Optional[str] = None,
        schema_path: Optional[str] = None,
        dsn: Optional[str] = None,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "postgres",
        connection_factory: Optional[Callable[[str], psycopg.Connection]] = None,
        schema_loader: Optional[Callable[[str], str]] = None,
    ):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.schema_path = schema_path or os.path.join(base_dir, "schema.sql")
        self._schema_loader = schema_loader or self._read_schema

        if dsn is None:
            env_dsn = os.getenv("DATABASE_URL")
            if env_dsn:
                dsn = env_dsn
            else:
                dsn = f"host={host} port={port} dbname={db_name} user={user} password={password}"

        self.dsn = dsn
        self.db_path = dsn  # compatibility with existing test attribute checks
        self._connection_factory = connection_factory or self._default_connection_factory

    @staticmethod
    def _default_connection_factory(dsn: str) -> psycopg.Connection:
        return psycopg.connect(dsn)

    @staticmethod
    def _read_schema(schema_path: str) -> str:
        with open(schema_path, "r", encoding="utf-8") as file:
            return file.read()

    def get_connection(self) -> psycopg.Connection:
        return self._connection_factory(self.dsn)

    def initialize_database(self) -> None:
        if not os.path.exists(self.schema_path):
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        print("Database being created")

        try:
            schema_script = self._schema_loader(self.schema_path)
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(schema_script)
                conn.commit()
            print("Database created")
        except psycopg.Error as exc:
            print(f"Database error: {exc}")
            raise

    def fetch_all(self, sql_string: str, params: Tuple[Any, ...] = ()) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(sql_string, params)
                return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, sql_string: str, params: Tuple[Any, ...] = ()) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(sql_string, params)
                db_row = cursor.fetchone()
                return dict(db_row) if db_row else None

    def execute_write(self, sql_string: str, params: Tuple[Any, ...] = ()) -> bool:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_string, params)
            conn.commit()
        return True
