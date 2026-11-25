import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from students import StudentError, StudentService

ROOT = Path(__file__).resolve().parents[1]


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "students.sqlite3"
        self.service = StudentService(self.db)
        self.student = {"student_id": "S001", "name": "虚构小明", "class_name": "一班", "age": 12}

    def test_crud_and_persistence(self):
        self.assertEqual(self.service.list(), [])
        self.assertEqual(self.service.add(self.student), self.student)
        self.assertEqual(StudentService(self.db).get("S001"), self.student)
        changed = self.service.update("S001", {"name": "虚构小红", "age": 13})
        self.assertEqual(changed["name"], "虚构小红")
        self.assertEqual(changed["student_id"], "S001")
        self.assertEqual(self.service.list(), [changed])
        self.service.delete("S001")
        self.assertEqual(self.service.list(), [])

    def test_strip_and_do_not_mutate_inputs(self):
        data = {**self.student, "student_id": " S001 ", "name": " 虚构小明 ", "class_name": " 一班 "}
        original = copy.deepcopy(data)
        self.assertEqual(self.service.add(data), self.student)
        self.assertEqual(data, original)
        changes = {"name": " 虚构小红 "}
        self.service.update(" S001 ", changes)
        self.assertEqual(changes, {"name": " 虚构小红 "})

    def test_duplicate_id(self):
        self.service.add(self.student)
        with self.assertRaisesRegex(StudentError, "学号已存在"):
            self.service.add(self.student)
        self.assertEqual(len(self.service.list()), 1)

    def test_required_fields(self):
        for field in ("student_id", "name", "class_name"):
            for value in ("", "  ", None, 123):
                with self.subTest(field=field, value=value):
                    with self.assertRaises(StudentError):
                        self.service.add({**self.student, field: value})
        with self.assertRaises(StudentError):
            self.service.add({})
        self.assertEqual(self.service.list(), [])

    def test_age_boundaries_and_types(self):
        for age in (5, 101, True, False, 12.0, "12", None):
            with self.subTest(age=age):
                with self.assertRaises(StudentError):
                    self.service.add({**self.student, "age": age})
        for age in (6, 100):
            row = {**self.student, "student_id": str(age), "age": age}
            self.assertEqual(self.service.add(row), row)

    def test_update_validation_and_identity(self):
        self.service.add(self.student)
        for changes in ({"student_id": "S002"}, {"age": True}, {"name": " "}, {"class_name": " "}, {"unknown": 1}):
            with self.subTest(changes=changes):
                with self.assertRaises(StudentError):
                    self.service.update("S001", changes)
                self.assertEqual(self.service.get("S001"), self.student)

    def test_missing_student(self):
        for action in (lambda: self.service.get("missing"), lambda: self.service.update("missing", {"age": 12}), lambda: self.service.delete("missing")):
            with self.assertRaisesRegex(StudentError, "学生不存在"):
                action()

    def test_parameterized_sql_and_list_order(self):
        for student_id in ("z", "x'; DROP TABLE students; --", "a"):
            self.service.add({**self.student, "student_id": student_id})
        self.assertEqual([row["student_id"] for row in self.service.list()], ["a", "x'; DROP TABLE students; --", "z"])


class CliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "cli.sqlite3"

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT / "cli.py"), "--db", str(self.db), *args], capture_output=True, text=True, cwd=self.temp.name)

    def test_cli_crud_across_processes(self):
        args = ("add", "S001", "虚构小明", "一班", "12")
        self.assertEqual(self.run_cli(*args).returncode, 0)
        result = self.run_cli("get", "S001")
        self.assertEqual(result.returncode, 0)
        self.assertIn("虚构小明", result.stdout)
        self.assertEqual(self.run_cli("update", "S001", "--name", "虚构小红", "--age", "13").returncode, 0)
        self.assertIn("虚构小红", self.run_cli("list").stdout)
        self.assertEqual(self.run_cli("delete", "S001").returncode, 0)
        self.assertEqual(self.run_cli("list").stdout.strip(), "[]")

    def test_cli_business_errors(self):
        for args, message in ((("get", "missing"), "学生不存在"), (("add", "S001", " ", "一班", "12"), "姓名"), (("add", "S001", "虚构小明", "一班", "101"), "年龄")):
            result = self.run_cli(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(message, result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_cli_usage_and_help(self):
        help_result = self.run_cli("--help")
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--db", help_result.stdout)
        for args in (("add", "S001", "虚构小明", "一班", "twelve"), ("update", "S001"), ("unknown",)):
            result = self.run_cli(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("错误", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
