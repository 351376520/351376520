"""学生管理命令行入口；只使用 Python 标准库。"""
import argparse
import json
from pathlib import Path
import sqlite3
import sys

from students import StudentError, StudentService

DEFAULT_DB = Path(__file__).resolve().parent / "students.sqlite3"


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"错误：命令参数不正确（{message}）\n")


def parser():
    result = Parser(description="学生管理练习：新增、查询、列表、修改和删除虚构学生")
    result.add_argument("--db", type=Path, default=DEFAULT_DB, help="SQLite数据库路径（默认：案例目录/students.sqlite3）；放在子命令前")
    commands = result.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="新增学生：学号 姓名 班级 年龄")
    add.add_argument("student_id", help="唯一学号")
    add.add_argument("name", help="姓名")
    add.add_argument("class_name", help="班级")
    add.add_argument("age", type=int, help="6到100的整数")
    for command, help_text in (("get", "按学号查询"), ("delete", "按学号删除")):
        child = commands.add_parser(command, help=help_text)
        child.add_argument("student_id", help="学号")
    commands.add_parser("list", help="按学号升序列出学生")
    update = commands.add_parser("update", help="按学号修改，至少提供一个字段；学号保持不变")
    update.add_argument("student_id", help="学号")
    update.add_argument("--name", help="新姓名")
    update.add_argument("--class-name", help="新班级")
    update.add_argument("--age", type=int, help="新年龄，6到100的整数")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        service = StudentService(args.db)
        if args.command == "add":
            output = service.add({key: getattr(args, key) for key in ("student_id", "name", "class_name", "age")})
        elif args.command == "get":
            output = service.get(args.student_id)
        elif args.command == "list":
            output = service.list()
        elif args.command == "update":
            changes = {key: getattr(args, key) for key in ("name", "class_name", "age") if getattr(args, key) is not None}
            output = service.update(args.student_id, changes)
        else:
            service.delete(args.student_id)
            output = {"message": "删除成功", "student_id": args.student_id.strip()}
    except (StudentError, sqlite3.Error, OSError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
