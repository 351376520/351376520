# 范围与任务

已确认的MVP：Python标准库CLI与SQLite本地持久化，学号、姓名、班级、年龄，新增、按学号查询、列表、修改、删除。规则和测试边界见 README.md 与 CODEBUDDY.md。本案例不包含Web页面、登录、网络服务或真实学生数据。

1. 隔离：从远端 main 克隆到独立目录，创建 feature/student-management-harness；所有新增文件仅在本案例目录，保留根 README 字节不变。已完成。
2. 公开接缝测试与最小stub。Blocked by: 1。11例有效红灯，已完成。
3. 服务、CLI最小实现及完整测试。Blocked by: 2。11例绿灯，已完成。
4. 必要文档、数据库/缓存忽略、差异检查与交接。Blocked by: 3。已完成。
5. 独立只读评审。Blocked by: 4。待主理人安排；实施者不验收自己的工作。
6. 评审通过后，按主理人通知提交并推送新分支。Blocked by: 5。尚未执行；不强制推送、不自动合并main。
