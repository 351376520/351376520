# 学生管理 Harness 协作规则

在 CodeBuddy 中打开本案例目录 `examples/student-management-harness/`。

- 使用 Python 3.12+、标准库 sqlite3/unittest，不需要安装依赖。默认数据库位于案例目录，示例仅使用虚构学生。
- 仅在本案例目录内工作；不读取凭据、私钥、token 或其他项目，不改全局 Git，不覆盖仓库根 README.md。
- 先确认需求、输入输出及测试边界再增加测试。本次已确认：StudentService 公开 API 使用临时 SQLite；CLI 使用真实子进程和独立临时数据库。
- 学号唯一且不可空；姓名班级去空白后非空；年龄为6到100整数，拒绝布尔值；修改保持学号，不修改输入。
- 红绿流程：先运行能因预期业务行为失败的测试，再最小实现；不削弱测试。0个测试不算通过。
- 从本目录运行 `python3 -m unittest discover -s tests -v`；本机已验证解释器为 `/Users/lq/harness-lab/.venv/bin/python`，可替换命令中的 python3。
- 未批准不得 commit、push、发布或执行破坏性操作；不得强制推送。本次用户已授权在独立评审通过后提交并推送 `feature/student-management-harness` 新分支，实施阶段须等待主理人通知，不合并 main。
- 交接报告文件、实际命令与原始结果、未跑检查、问题与下一步。独立角色评审后才能验收。
