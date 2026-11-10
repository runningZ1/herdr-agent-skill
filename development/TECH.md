# Herdr Skill 2.0.0 架构与机器契约

## 产品与接口

herdr 是 TUI；hc 是持久终端 Core；herdr-app 是用户窗口。共享技能入口按任务与上下文路由，不复用产品的 socket、ID、机器配置或生命周期协议。HC_TERMINAL_ID 优先判断 Core，HERDR_ENV 仅约束 TUI；并存时检查污染。清理只作用于将启动的子进程继承环境，不修改用户/系统环境、不停止既有 Core。

| 层 | 实现与约束 |
|---|---|
| TUI 精选适配 | scripts/herdr_agent.py，标准库 Python；同一 registry 生成 help/schema/argv |
| TUI 完整 API | scripts/herdr_api.py，schema/call/subscribe；以实际脚本帮助和 sources/herdr-api.schema.json 为契约 |
| Core | hc 原生 CLI；hc schema 发现 32 方法，hc connect 路由 hello/doc 等无专用命令的 API |
| App | herdr-app commands 发现 71 内置命令，do 调用；generated 类型定义 mod API |
| 采集与发布 | tools/collect.py、validate.py、build.py；官方快照与本地增强文档区分，排除会话和凭据 |

## 精选适配入口

RESOURCE ACTION 接受显式 --input JSON / --file PATH，- 为显式 stdin；最大 64 KiB、拒绝未知字段和无效值。输出为单个版本化 JSON/JSONL 终结 envelope；stdout 不混诊断。list 默认 20 最大 100，本地 offset/投影非服务器分页；read 有行数与字节/字符边界。timeout 有界，不构造任意 shell/raw argv 入口。

读直接执行，写默认预演。提交要求相同 plan_hash，绑定参数、binary/hash、actor、cwd、环境摘要、socket/session、目标快照与有效窗口。hash 是一致性检查，不是权限凭证或服务器事务；已获授权任务可自动核对提交。不得自动重试写入；dispatch 后超时、取消、输出超限为 outcome unknown，后置校验失败为 committed/unknown，提供核对建议。

布局 create/split 使用 no-focus 并 get 确认对象；close 用 list 确认消失且保护当前调用者对象。agent rename 后 get 验证实际名称并返回 confirmed=true。prompt 的 submitted 与 wait 的 settled 不等于任务完成；必须读取真实结果。tool_version 为 2.0.0，schema_version 独立演进。完整精选字段/输出/错误详见 references/agent-cli-contract.md。

## 原生协议与订阅

TUI request schema 当前含 102 方法。events.subscribe 请求 subscriptions 数组，events.wait 请求 match_event 与可选 timeout_ms，不能编造 filters/events 参数。完整 API 的具体命令语法由 herdr_api.py --help/schema 提供，不在开发文档再建立不同契约。

Core schema 为 OpenRPC 文档，含参数/结果/错误。hc connect 提供官方 JSON-RPC 连接，hello 协商，terminal.attach 需 framed 传输。doc.set 按版本条件写，冲突不自动覆盖。events.subscribe 使用 Core 自己的过滤字段，快照/heartbeat/missed 重同步与 TUI 分开。文件/短程序/持久程序按原生 CLI；无需自制 Core wrapper。

App do 接受 key/value 或 JSON object，目标 ID 必须是字符串，未知参数失败。commands 可离线读取，ls/status/shot 需要运行窗口，裸启动会打开窗口。Core 后台任务默认隐藏；App 新建对象会改变用户视图。

## mod 维护

解析 HERDR_APP_HOME（默认 ~/.config/herdr-app），读取生成的 AGENTS.md、herdr.d.ts、gpui-kit.d.ts，不编辑这些文件。内置 mod/layout 先 clone。View 回调各自使用 cx，使用主题色、原生动画与 cx.spawn/timer；保存热重载，错误时保留旧版，需检查 status。close 清理预算 250 ms，不能在隐藏时误做销毁。

修改 mod 后 check、status、shot 并查看图像；check 不覆盖延后渲染/全部交互。当前文档升级不修改或验证用户 mod，不声称视觉通过。

## 证据与兼容

静态发现只证明目录；运行时查询、fixture、实际业务和视觉验证分别记录。hc server status 不启动 Core，hc machine ls 可按需启动。Core update 计划重启保留终端；stop 可能结束所有程序。TUI 的服务停止、恢复、配置与 Core/App 不互换。当前维护不读取用户会话正文、凭据或运行任意真实任务。
