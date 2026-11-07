# 功能覆盖与证据层级

## 判定口径

“覆盖”分为适配 CLI 实现、官方原生操作指导、真实业务验证，不能互换。Socket schema 的102项方法是可发现目录，不是本地新增102个封装或102项实测。

| 领域 | 适配入口 | 官方原生路由 | 实际证据 |
|---|---|---|---|
| 版本/发现/诊断 | version/schema/errors/doctor | --version/status/api schema | 本机版本、配置与受管 pane |
| workspace | list/get/create/rename/close | focus/report-metadata/group close | 真实创建、get、删除；dry-run 零变更、错误 hash 拒绝 |
| tab | list/get/create/rename/close | focus/env/完整创建参数 | 创建和根 pane；随测试 workspace 清理 |
| pane | list/get/current/layout/process-info/split/rename/close/read | swap/move/resize/zoom/run/send-keys/report/wait-output 等 | 真实读取；布局高阶改动仅文档 |
| Agent | list/get/start/prompt/wait/read/rename | explain/focus/attach/其他 kind | 官方 Codex+Claude 对话；新适配层以验收报告为准 |
| Git worktree | 原生 | cli-reference.md | 未做 Git 变更实测 |
| SSH 机器/远端转发 | 原生 | remote-machines.md | 未连接/变更远端实测 |
| 集成/检测钩子 | 原生 | integrations-plugins.md | 帮助/schema；安装未实测 |
| 插件/动作/插件窗格 | 原生 | integrations-plugins.md | 帮助/schema；安装/执行未实测 |
| 通知/标题/直接终端 | 原生 | cli-reference.md | 文档和帮助，无通知/接管测试 |
| 配置/更新/会话恢复 | 原生 | setup-recovery.md | config check 真实通过；停止/升级/恢复未执行 |
| Socket布局/视图/订阅 | 原生 API | socket-api.md/api-methods.md | 本机schema提取；没有自定义 pipe 客户端或订阅实测 |

## 避免误用

机器输出、默认 limit、--commit/--confirm、错误 code、plan_hash 是本地适配入口协议，不是官方 herdr 参数。官方大多数控制命令是 JSON，但 read/status 等返回文本，错误多在 stderr；不能套用适配层 stdout envelope。

官方优先级：运行中服务器兼容性→本机CLI帮助/schema→对应版本官方文档→本地说明。遇未覆盖参数转用相应原生参考页，不猜适配层支持。具体命令与断言保存在任务目录测试报告，不把测试对话和私密会话数据放入分发包。
