# Herdr Core（hc）2.0.0 操作指南

Core 负责持久终端、程序、Agent、远程机器和文件；App 负责窗口布局。TUI 的 `herdr` 是另一套运行时。先读 [官方 Core Skill](official-core-skill.md)，再用当前 `hc <command> --help` 确认参数。这里的 32 项是本机 `hc schema` 静态发现的 API 路由数量，不代表 32 项端到端实测；完整参数、类型、结果与错误见 [Core schema](../sources/core-api.schema.json)。

## 上下文与启动副作用

`HC_TERMINAL_ID` 存在时优先判定为 Core 终端，地址可以是 `t7`、名称或 `machine/t7`，不是 App pane ID。Core/App 不以 `HERDR_ENV=1` 为操作门槛。若同时出现 `HERDR_*`，应检查来自 TUI 父进程的污染，按 [排障页](setup-recovery.md) 只清理将启动的子进程环境；不伪造身份、不重启用户 Core、不用 `allow_nested` 绕过。

`hc --help`、`hc --skill`、`hc schema` 是静态发现；`hc server status` 不会启动 Core。`hc machine ls`、其他连接 Core 的查询以及 `hc connect` 可能按需启动 Core，不能当作完全无副作用的首次探测。先查 status；需要启动时从正确且无 TUI 污染的产品环境启动，已有活跃 Core 不为诊断重启。

## 原生 CLI 工作流

先查看 `hc templates` 是否已有合适角色；只在已授权任务内启动交互式 Agent。用 `--bg` 保持调用方可接收消息，不使用一次性 print 模式。首条任务放在 `run` 中，检查返回的 `first_message.sent`；false 表示未发出，先确认就绪后再发送。没有合适模板时按当前 Skill 启动用户指定的命令。Codex 的 `--no-daemon` 要求来自当前 `hc --skill`（包括模板），防止它的命令跑到 hc 之外；此要求不外推为 TUI 参数。


```sh
hc run --bg --name review --cwd /path/to/repo reviewer "Review src/x.rs only; no subagents."
hc get review
hc wait review
hc read review --lines 100
```

上例只在相应模板已存在时使用；路径必须是真实任务目录。普通程序用 `hc run --bg --name build <cmd>`，短命令用 `hc exec`。状态由程序 OSC 7501 上报，普通程序可以没有 status。`wait` 返回状态不等于任务成功，读取实际结果；`reason:message` 先处理消息，`reason:timeout` 是检查点，`not_started` 或发送失败先读取，禁止盲目重发。run 超时可能仍保留运行中的终端，使用返回地址继续 wait/read，不能重复启动。

`hc ls` 包含用户的其他任务；只操作任务授权范围。`interrupt` 停当前轮而不杀进程，`kill` 结束程序，`rm` 只移除已结束终端。blocked 时读具体审批并按用户授权处理，不用 `send --force` 绕过决策。子终端默认随父终端结束；只有确需独立存活时用 `--outlive-parent`。后台 worker 默认不加 App 标签，避免改变用户窗口。

## 32 项 API / CLI 路由

API 参数中的 `*` 表示 schema required；其余为可选。CLI flag 不必与 API 字段同名，按原生命令帮助转换。没有专用子命令的 API 使用官方 `hc connect` 协议，不另造 wrapper。

| API method | 原生入口 | API 参数 |
|---|---|---|
| `hello` | `hc connect` 连接握手（API） | `calls_you`, `core`, `features`, `framed`, `generation` |
| `server.status` | `hc server status` | 无 |
| `server.stop` | `hc server stop` | 无 |
| `server.restart` | `hc server restart` | 无 |
| `terminal.run` | `hc run` | `argv`, `caller`, `cwd`, `die_with_parent`, `display`, `env`, `keep`, `labels`, `line`, `name`, `no_notify`, `no_parent`, `on`, `outlive_parent`, `parent`, `rm`, `size`, `timeout`, `wait` |
| `templates.list` | `hc templates` | 无 |
| `terminal.list` | `hc ls` | `all`, `labels` |
| `terminal.get` | `hc get <t>` | `caller`, `terminal*` |
| `terminal.kill` | `hc kill <t>` | `caller`, `terminal*` |
| `terminal.rm` | `hc rm <t>` | `caller`, `terminal*` |
| `terminal.keep` | `hc keep <t> [--off]` | `keep*`, `terminal*` |
| `terminal.label` | `hc label <t> k=v...` | `labels*`, `terminal*` |
| `terminal.read` | `hc read <t>` | `caller`, `lines`, `terminal*` |
| `terminal.attach` | `hc attach <t>`；framed API 可 observe | `caller`, `cols*`, `display`, `history`, `observe`, `resize_notifications`, `resumed`, `rows*`, `terminal*` |
| `terminal.send` | `hc send <t> <text>` | `caller`, `force`, `if`, `terminal*`, `text*`, `timeout`, `wait` |
| `terminal.wait` | `hc wait <t>` / `hc wait --children all\|any` | `caller`, `children`, `output`, `terminal`, `timeout` |
| `terminal.keys` | `hc keys <t> <keys...>` | `caller`, `keys*`, `terminal*` |
| `terminal.interrupt` | `hc interrupt <t>` | `terminal*`, `timeout` |
| `terminal.put` | `hc put <t> <file>` | `data*`, `name*`, `terminal*` |
| `machine.exec` | `hc exec [--on m] <cmd>` | `argv`, `cwd`, `env`, `input`, `line`, `on`, `timeout` |
| `file.read` | `hc file read [--on m] <path>` | `cwd`, `limit`, `offset`, `on`, `path*` |
| `file.write` | `hc file write [--on m] <path>` | `cwd`, `data*`, `on`, `path*` |
| `file.edit` | `hc file edit [--on m] <path>` | `cwd`, `edits*`, `on`, `path*` |
| `doc.get` | `hc connect` JSON-RPC（API，无专用子命令） | `name*`, `on` |
| `doc.set` | `hc connect` JSON-RPC（API，无专用子命令） | `name*`, `on`, `value*`, `version*` |
| `events.subscribe` | `hc events` | `children_of`, `labels`, `terminal` |
| `machine.add` | `hc machine add` | `name`, `session`, `target`, `temporary`, `via` |
| `machine.list` | `hc machine ls` | 无 |
| `machine.connect` | `hc machine login`（CLI 重连工作流）；API `machine.connect` | `machine*` |
| `machine.rename` | `hc machine rename` | `machine*`, `new_name*` |
| `machine.rm` | `hc machine rm` | `machine*` |
| `rpc.discover` | `hc schema` | 无 |

## 没有专用子命令的 API

`hc connect` 将官方协议接到 stdin/stdout（远端也可 `ssh box hc connect`），会连接或启动 Core。按 `hc schema` 的 JSON-RPC 2.0 结构发送请求，使用独立 request id 并检查 error；例如先发握手，再读取一个非敏感的应用自有文档：

```json
{"jsonrpc":"2.0","id":1,"method":"hello","params":{}}
{"jsonrpc":"2.0","id":2,"method":"doc.get","params":{"name":"my-tool-state"}}
```

`doc.set` 要求 name/value/version，使用 `doc.get` 返回的当前 version 进行条件更新；null 删除值但保留版本，最大 1 MiB。版本冲突重新读取并由业务决定，不覆盖用户的 `herdr-app` 布局文档。上述是协议示例，不代表本轮执行过请求。

`terminal.attach` 需要先 `hello {framed:true}` 协商二进制帧传输，不能把流当逐行 JSON。`hello` 提供 generation/features/methods；以实际协商结果为准。`events.subscribe` 返回匹配终端快照后顺序通知变化、每 15 秒 heartbeat；落后时可能出现 missed 与新快照，需要重建状态。CLI 直接用 `hc events --terminal <t>`、`--children-of <t>` 或可重复 `--label k=v`。不要套用 TUI 的 subscriptions/match_event 契约。

## 机器、文件与恢复

机器配置独立于 TUI；完整接入见 [远程机器](remote-machines.md)。远端返回 `machine/t7` 后全程保留前缀。文件使用 `hc file read|write|edit --on <machine>`；write 替换整文件，edit 要求每个 old 精确匹配一次、修改全部成功或全部失败。短命令 `hc exec` 无持久终端，退出、超时或调用方消失会结束其启动的进程；非零和超时是结果，仍检查实际 exit code。

`keep` 在进程丢失后恢复为 shell，不重放任务；普通正常退出和显式 kill 不恢复。流在丢失后结束，恢复后重新 attach。`hc update` / `hc machine update` 的计划重启保留终端，但会影响连接；这与 TUI `herdr server stop` 结束窗格进程不同。`hc server stop` 会停程序，kept 终端到下次启动才变为 shell；不可把它当普通更新。

本页仅记录静态帮助、Skill 与 schema。当前任务不启动 Core、不读取会话正文、不运行程序、不停止或重启用户服务。运行时错误为 stderr `{error:{kind,message,hint}}`；保留原 kind，按结果核对，不能套用 TUI 的错误 envelope。
