from typing import Any, Dict, List, Optional

from database.database_manager import Database


class StudentRepository:
    def __init__(self, database: Database):
        self.database = database

    def list_students(self) -> List[Dict[str, Any]]:
        return self.database.fetch_all(
            "SELECT student_id, user_id, major, can_view_grades FROM students ORDER BY student_id"
        )

    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        return self.database.fetch_one(
            "SELECT student_id, user_id, major, can_view_grades FROM students WHERE student_id = ?",
            (student_id,),
        )
