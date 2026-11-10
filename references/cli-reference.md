# CLI 功能索引（2.0.0）

本页 TUI 部分按 0.9.5 官方文档与本机帮助整理；Core / App 原生入口见页尾及各专页。`<>` 是待替换参数，`[]` 表可选，不能原样粘贴。以下路由索引不代表每项已经实测。
先确认产品与上下文：HC_TERMINAL_ID 优先表明 Core 终端，HERDR_ENV 仅用于 TUI，不能阻止 Core/App。TUI 查当前 `herdr <group>`；server 等有裸命令副作用的组改用 `--help`。
多数 TUI API 控制命令直接返回 JSON；不要给所有产品/命令机械添加 `--json`。Core/App 的机器、ID、协议与配置独立，不能把 TUI 前缀传给 hc。

## 启动、版本、服务器、会话

```text
herdr --version
herdr --help
herdr --skill
herdr --default-config
herdr status [server|client]
herdr api snapshot
herdr api schema [--json] [--output PATH]
herdr                         # 交互式启动/附加，非探测
herdr --session NAME           # 命名会话
herdr server                  # 无界面服务器，前台长期进程
herdr server stop
herdr server reload-config
herdr server agent-manifests [--json]
herdr server update-agent-manifests [--json]
herdr server reload-agent-manifests
herdr session list [--json]
herdr session attach NAME
herdr session stop NAME [--json]
herdr session delete NAME [--json]
herdr update [--handoff]
herdr channel show
herdr channel set stable|preview
herdr completion zsh|bash|fish|powershell|elvish
herdr config check
herdr config reset-keys
```

stop/delete 会影响进程或持久状态；先明确目标会话与用户意图。默认会话名是 default。update 可能导致客户端/服务器版本不同；查看 status。`--handoff` 实验性，不能承诺无损。config reset-keys 会备份并移除自定义键位，不作为常规检查。

## 工作区 workspace

```text
herdr workspace list
herdr workspace create [--cwd PATH] [--label TEXT] [--env KEY=VALUE] [--focus|--no-focus]
herdr workspace get ID
herdr workspace focus ID
herdr workspace rename ID LABEL
herdr workspace report-metadata ID --source SOURCE [--token NAME=VALUE] [--clear-token NAME] [--seq N] [--ttl-ms N]
herdr workspace close ID [--group]
```

env 可重复。创建会产生第一个 tab 和 root pane。关闭有 linked worktree 的父 workspace 可能返回 workspace_group_close_required；先检查组，不能直接补 --group。

## Git worktree

```text
herdr worktree list [--workspace ID|--cwd PATH] [--trust-repository]
herdr worktree create [--workspace ID|--cwd PATH] [--branch NAME] [--base REF] [--path PATH] [--label TEXT] [--focus|--no-focus] [--trust-repository]
herdr worktree open [--workspace ID|--cwd PATH] (--path PATH|--branch NAME) [--label TEXT] [--focus|--no-focus] [--trust-repository]
herdr worktree remove --workspace ID [--force] [--trust-repository]
```

create 使用已有本地分支，或由 base/HEAD 新建分支。默认检出路径取 worktrees.directory 配置。close 只关 Herdr 状态；remove 执行 git worktree remove，不删分支。脏检出拒绝后先报告，不能自动 force。操作前检查仓库归属、分支和工作区实际目录。

## 标签页 tab

```text
herdr tab list [--workspace ID]
herdr tab create [--workspace ID] [--cwd PATH] [--label TEXT] [--env KEY=VALUE] [--focus|--no-focus]
herdr tab get ID
herdr tab focus ID
herdr tab rename ID LABEL
herdr tab close ID
```

显式 workspace 避免依赖用户当前焦点。关闭最后 tab 也关闭 workspace；涉及 worktree 组时可能 confirmation_required。CLI/API 普通关闭不继承 TUI 的所有确认保护。

## 窗格 pane：布局和进程

```text
herdr pane list [--workspace ID]
herdr pane current [--pane ID|--current]
herdr pane get ID
herdr pane layout [--pane ID|--current]
herdr pane process-info [--pane ID|--current]
herdr pane neighbor --direction left|right|up|down [--pane ID|--current]
herdr pane edges [--pane ID|--current]
herdr pane focus --direction left|right|up|down [--pane ID|--current]
herdr pane resize --direction left|right|up|down [--amount FLOAT] [--pane ID|--current]
herdr pane zoom [ID|--pane ID|--current] [--toggle|--on|--off]
herdr pane rename ID LABEL|--clear
herdr pane input [ID|--pane ID|--current] --right-click herdr|pane
herdr pane split [ID|--pane ID|--current] --direction right|down [--ratio FLOAT] [--cwd PATH] [--env KEY=VALUE] [--right-click herdr|pane] [--focus|--no-focus]
herdr pane swap --direction left|right|up|down [--pane ID|--current]
herdr pane swap --source-pane ID --target-pane ID
herdr pane move ID --tab TAB --split right|down [--target-pane ID] [--ratio FLOAT] [--focus|--no-focus]
herdr pane move ID --new-tab [--workspace ID] [--label TEXT] [--focus|--no-focus]
herdr pane move ID --new-workspace [--label TEXT] [--tab-label TEXT] [--focus|--no-focus]
herdr pane close ID
```

swap 仅同一 tab；move 跨 workspace 后改用新 pane_id。读取响应 changed/reason，不能把成功返回一律理解为布局已改变。远程不能借本地 --current 定位。

## 窗格 pane：读写、等待、上报

```text
herdr pane read ID [--source visible|recent|recent-unwrapped|detection] [--lines N] [--format text|ansi] [--ansi] [--raw]
herdr pane send-text ID TEXT
herdr pane send-keys ID KEY [KEY...]
herdr pane run ID COMMAND
herdr pane wait-output ID (--match TEXT|--regex PATTERN) [--source visible|recent|recent-unwrapped] [--lines N] [--timeout MS] [--raw]
herdr pane report-agent ID --source SOURCE --agent LABEL --state idle|working|blocked|unknown [--message TEXT] [--seq N] [--agent-session-id ID] [--agent-session-path PATH] [-- RESUME_COMMAND...]
herdr pane report-agent-session ID --source SOURCE --agent LABEL [--seq N] [--agent-session-id ID] [--agent-session-path PATH] [--session-start-source SOURCE] [-- RESUME_COMMAND...]
herdr pane release-agent ID --source SOURCE --agent LABEL [--seq N]
herdr pane report-metadata ID --source SOURCE [--agent LABEL] [--applies-to-source SOURCE] [--title TEXT|--clear-title] [--display-agent TEXT|--clear-display-agent] [--state-label STATUS=TEXT] [--clear-state-labels] [--token NAME=VALUE] [--clear-token NAME] [--seq N] [--ttl-ms N]
```

`pane read` 帮助与官网参数枚举可能不完全一致，遇语法问题以实时命令和 schema 为准。recent 读取默认 80 行；visible/detection 未指定 lines 时取完整快照。等待 regex 为 Rust 语法，逐行匹配；match 为字面子串。上报细节见 integrations-plugins.md。

## 智能体 agent

```text
herdr agent list
herdr agent get TARGET
herdr agent read TARGET [--source visible|recent|recent-unwrapped|detection] [--lines N] [--format text|ansi] [--ansi]
herdr agent send-keys TARGET KEY [KEY...]
herdr agent prompt TARGET TEXT [--wait] [--until STATUS]... [--timeout MS]
herdr agent rename TARGET NAME|--clear
herdr agent focus TARGET
herdr agent wait TARGET [--until STATUS]... [--timeout MS]
herdr agent attach TARGET [--takeover]
herdr agent start NAME --kind KIND --pane ID [--timeout MS] [-- AGENT_ARGS...]
herdr agent explain TARGET [--json|--verbose]
herdr agent explain --file PATH --agent LABEL [--json|--verbose]
```

TARGET=实时唯一名称或当前承载 Agent 的 pane_id。KIND 本机 0.9.5：pi、claude、codex、gemini、cursor、devin、agy、cline、omp、mastracode、opencode、copilot、kimi、kiro、droid、amp、grok、hermes、kilo、qodercli、qwen、letta、maki、muse。支持识别不代表已安装/授权，平台可用集成范围也不同。

上述是 agent start kind；当前 integration install 的 18 个 TARGET 见 [集成页](integrations-plugins.md)，两种枚举不同。TUI 原生 rename 可设置 NAME 或 --clear；精选适配入口的 rename 会二次 get 验证并返回 confirmed=true。

## 直接终端、通知

```text
herdr terminal attach TERMINAL_ID [--takeover]
herdr terminal session control TARGET [--takeover] [--cols N] [--rows N]
herdr terminal session observe TARGET [--cols N] [--rows N]
herdr terminal title set TITLE
herdr terminal title clear
herdr notification show TITLE [--body TEXT] [--position top-left|top-right|bottom-left|bottom-right] [--sound none|done|request]
```

attach 是交互式，不在普通脚本中阻塞运行；ctrl+b q 分离，ctrl+b ctrl+b 发送字面组合键。observe 是长期只读 JSON 帧流，control 获得唯一写控制权；takeover 会接管其他控制方，需要任务明确要求。

TUI 机器、集成、插件详见各专页。完整 API 的 schema/call/subscribe 由 `scripts/herdr_api.py` 提供；以脚本 --help 与 [Socket 文档](socket-api.md) 为参数契约，不把精选 herdr_agent.py 的 schema 当作 102 方法全集。events.subscribe 请求使用 subscriptions，events.wait 请求使用 match_event，不能以猜测的 filters/events 代替。

## Core 原生 CLI 与全部 API

```text
hc --help
hc --skill
hc schema
hc server status
hc run|ls|get|attach|read|kill|rm|label|keep
hc send|keys|interrupt|wait|put
hc exec
hc file read|write|edit
hc templates
hc events
hc machine add|ls|login|update|rename|rm
hc connect
hc update
hc server start|stop|restart
```

以上 `|` 为入口索引而非可粘贴语法。所有 32 API 方法及原生 CLI / connect 路由、API 必填参数见 [Core 指南](core.md) 和 [Core schema](../sources/core-api.schema.json)，包括没有专用子命令的 hello/doc.get/doc.set。schema 是静态发现；connect 和一般 Core 查询可按需启动 Core，server status 不会。更新会计划重启并保留终端；server stop 影响所有程序，不能擅自执行。

## App 原生 CLI 与 71 commands

```text
herdr-app --help
herdr-app --skill
herdr-app commands
herdr-app ls
herdr-app status
herdr-app do COMMAND [--key VALUE|JSON_OBJECT]
herdr-app check MOD_FOLDER
herdr-app shot [FILE.png]
```

静态 commands 无需窗口；其余窗口操作依赖当前运行 App，不运行裸命令启动窗口来探测。全部 71 个内置 command、参数和行为在 [App 指南](app.md) 与 [命令快照](../sources/app-commands.json)。布局/按键/mod 定制先发现 HERDR_APP_HOME 下 generated AGENTS.md、herdr.d.ts、gpui-kit.d.ts，不修改这些生成文件；mod 修改需 check/status/shot 并区分静态检查和实际视觉验收。
