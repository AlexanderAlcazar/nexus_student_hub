import os
import tempfile
import unittest

from container import AppSettings, build_container


class TestContainer(unittest.TestCase):
    def test_builds_database_from_settings(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = AppSettings(database_name="container.db", data_dir=temp_dir)
            container = build_container(settings)

            self.assertEqual(container.database.db_path, os.path.join(temp_dir, "container.db"))
            self.assertTrue(container.database.schema_path.endswith("schema.sql"))
            container.database.initialize_database()
            self.assertEqual(container.student_repository.list_students(), [])


if __name__ == "__main__":
    unittest.main()
