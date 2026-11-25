# 学生管理 Harness 练习

使用 Python 3.12+ 标准库实现命令行学生管理，数据保存到本地 SQLite。无需安装依赖、网页登录或网络服务。请仅使用虚构学生数据。

在 CodeBuddy 中打开本目录。以下命令均在本目录执行；先确认 `python3 --version` 为3.12及以上。本机也可用 `/Users/lq/harness-lab/.venv/bin/python` 替换 `python3`，无需复制虚拟环境。

```bash
python3 cli.py --help
python3 cli.py add S001 虚构小明 一班 12
python3 cli.py get S001
python3 cli.py list
python3 cli.py update S001 --name 虚构小红 --class-name 二班 --age 13
python3 cli.py delete S001
python3 -m unittest discover -s tests -v
```

默认数据库是本案例目录中的 `students.sqlite3`，不受启动命令时的当前目录影响，已由本目录 `.gitignore` 忽略。指定独立数据库时，将全局参数放在子命令前，父目录需要已存在：

```bash
python3 cli.py --db /tmp/fictional-students.sqlite3 list
```

成功时输出中文可读 JSON，退出码0；业务或存储错误写入标准错误并退出1，参数错误退出2。`--help` 不创建数据库。CLI错误不打印 Python 调用栈。

公开 API 是 `students.StudentService(db_path)` 的 `add(mapping)`、`get(student_id)`、`list()`、`update(student_id, changes)` 和 `delete(student_id)`。记录字段为 `student_id/name/class_name/age`，查询与写入返回新字典，列表按学号文本升序排列，删除返回 None；无效业务输入抛出 `StudentError`。传入文件数据库路径，连接在每次操作后关闭，不支持 `:memory:` 临时连接模式。测试使用临时文件数据库。

学号、姓名、班级必须是去除首尾空白后非空的文本；学号唯一，修改时不可变更。年龄只接受6到100的整数，API拒绝布尔值、浮点数和数字字符串。修改至少提供姓名、班级、年龄中的一个字段，不接收其他字段。找不到学生、重复学号均有明确错误，输入字典不会被修改。

测试覆盖服务公开行为、SQLite跨实例持久化、非法输入、唯一性、SQL参数化，以及CLI真实子进程跨命令增删改查。测试数据库全部位于自动清理的临时目录；没有测试或发现0个测试不算成功。

文件职责：`students.py` 保存业务规则与SQLite操作，`cli.py` 提供参数及输出，`tests/test_students.py` 验证公开行为，`TASKS.md` 记录范围和依赖，`HANDOFF.md` 保存本次红绿证据与交接状态。
