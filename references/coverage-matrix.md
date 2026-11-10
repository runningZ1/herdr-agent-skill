# 功能覆盖与证据层级（2.0.0）

“覆盖”必须区分可发现目录、可调用路由、操作指导和真实业务验证。TUI 102 个 schema request 方法、Core 32 个 API 方法、App 71 个内置 commands 是当前静态快照的目录数量，不是 205 项实测，也不保证未来版本数量不变。

| 产品 / 领域 | 可调用入口 | 指导与机器来源 | 证据口径 |
|---|---|---|---|
| TUI 精选布局与 Agent | scripts/herdr_agent.py | [机器契约](agent-cli-contract.md)；自身 schema | 历史 fixture、布局和部分模型闭环；不推定 2.0.0 已重跑 |
| TUI 102 API 方法 | scripts/herdr_api.py schema/call/batch/subscribe；官方 herdr 原生 CLI | [Socket](socket-api.md)、[方法目录](api-methods.md)、sources/herdr-api.schema.json | 全量方法可发现/路由；本轮真实 Windows pipe 的 ping、专用工作区 create/rename/get/close、batch/layout.export 通过；未逐项执行全部方法 |
| TUI 工作区/tab/pane/Agent/终端 | herdr workspace/tab/pane/agent/terminal | [CLI](cli-reference.md)、[工作流](workflows.md) | 历史布局与有限对话证据见来源页，不覆盖所有 kind/等待场景 |
| TUI worktree/远程/配置/恢复 | 对应原生命令或 API | [机器](remote-machines.md)、[恢复](setup-recovery.md) | 操作指导；本轮未创建 worktree、安装远端或重启服务器 |
| TUI 集成/插件/metadata | herdr integration/plugin/pane/workspace | [集成与插件](integrations-plugins.md) | 18 TARGET 是当前 CLI 枚举；识别、可安装与状态上报分别判断 |
| TUI 事件 | events.subscribe / events.wait | subscriptions 数组 / match_event，见 Socket schema | 本轮订阅初始确认与有界 deadline 返回通过；未以无事件超时证明真实事件投递或掉线恢复 |
| Core 全部 32 API | hc 原生 CLI；无专用子命令时 hc connect | [Core](core.md)、[官方 Skill](official-core-skill.md)、sources/core-api.schema.json | 本轮 --help/--skill/schema 静态读取，未调用 32 项业务操作 |
| Core 程序/Agent/文件/机器/事件/doc | hc run/send/wait/file/machine/events/connect | 32 方法表逐项给入口与 API 参数 | Core/App 独立上下文；未用 HERDR_ENV 设置门槛，不声称远程/升级/所有 Agent 已验证 |
| App 全部 71 commands | herdr-app do COMMAND | [App 全表](app.md)、[官方 Skill](official-app-skill.md)、sources/app-commands.json | commands 可离线发现，不证明窗口与命令执行成功 |
| App 布局/按键/mod | do / home 中用户文件 | generated AGENTS.md、herdr.d.ts、gpui-kit.d.ts | 本轮发现并阅读生成指南相关章节，未修改用户 mod、运行 check 或进行视觉验收 |
| App 运行窗口 | ls/status/shot | [App 操作与定制](app.md) | 本轮不启动窗口、不截图、不控制真实显示 |

## 产品隔离

HC_TERMINAL_ID 优先识别 Core 终端，HERDR_ENV 仅表示 TUI。两者并存需排查 HERDR_* 污染，只清理将启动的子进程，不重启用户 Core、不使用 allow_nested。TUI/Core 机器配置与标识独立；App 使用 Core 机器。

hc server status 不启动 Core，hc machine ls 等查询可按需启动。Core 更新的计划重启保留终端；TUI 停服与 Core server.stop 均可能终止程序，不能用升级行为推断停服安全。保持静态采集、运行时只读、受控 fixture、真实业务、视觉验收分别报告。

## 验收记录规则

每项记录版本/平台、实际命令、是否连接运行时、退出/结构化结果、业务证据和清理结果；不读取不相关真实会话正文或凭据。历史证据只支持当时版本与对象，当前新增脚本/文档必须以实际执行记录报告。测试未跑就明确“未运行”，不能沿用旧 28 项通过数字作为 2.0.0 验证结果。
