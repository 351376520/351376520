"""学生管理公开服务 API，使用本地 SQLite 保存学生记录。"""
from contextlib import contextmanager
import sqlite3


class StudentError(ValueError):
    """可向用户展示的业务错误。"""


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise StudentError(f"{label}必须是非空文本")
    return value.strip()


def _student(data):
    result = {
        "student_id": _text(data.get("student_id"), "学号"),
        "name": _text(data.get("name"), "姓名"),
        "class_name": _text(data.get("class_name"), "班级"),
        "age": data.get("age"),
    }
    if type(result["age"]) is not int or not 6 <= result["age"] <= 100:
        raise StudentError("年龄必须为6到100的整数")
    return result


class StudentService:
    def __init__(self, db):
        self.db = str(db)
        with self._connection() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                class_name TEXT NOT NULL,
                age INTEGER NOT NULL CHECK(age BETWEEN 6 AND 100)
            )""")

    @contextmanager
    def _connection(self):
        conn = sqlite3.connect(self.db)
        conn.row_factory = sqlite3.Row
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    @staticmethod
    def _get(conn, student_id):
        row = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if row is None:
            raise StudentError(f"学生不存在：{student_id}")
        return dict(row)

    def add(self, student):
        row = _student(student)
        try:
            with self._connection() as conn:
                conn.execute("INSERT INTO students (student_id, name, class_name, age) VALUES (?, ?, ?, ?)", tuple(row.values()))
        except sqlite3.IntegrityError as exc:
            raise StudentError(f"学号已存在：{row['student_id']}") from exc
        return row

    def get(self, student_id):
        student_id = _text(student_id, "学号")
        with self._connection() as conn:
            return self._get(conn, student_id)

    def list(self):
        with self._connection() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM students ORDER BY student_id")]

    def update(self, student_id, changes):
        student_id = _text(student_id, "学号")
        if "student_id" in changes:
            raise StudentError("修改时不得变更学号")
        if not changes or set(changes) - {"name", "class_name", "age"}:
            raise StudentError("请提供姓名、班级或年龄的修改值")
        with self._connection() as conn:
            current = self._get(conn, student_id)
            row = _student({**current, **changes})
            conn.execute("UPDATE students SET name = ?, class_name = ?, age = ? WHERE student_id = ?", (row["name"], row["class_name"], row["age"], student_id))
            return row

    def delete(self, student_id):
        student_id = _text(student_id, "学号")
        with self._connection() as conn:
            if conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,)).rowcount == 0:
                raise StudentError(f"学生不存在：{student_id}")
