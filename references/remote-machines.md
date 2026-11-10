# SSH 机器与目标隔离（2.0.0）

先确认产品：TUI 用 `herdr machine` / `--machine`，Core/App 用 `hc machine` / `--on`。两套机器配置独立，TUI 已保存的机器不会自动出现在 App 侧栏。OpenSSH 别名也不自动成为任何产品的已保存机器。

## TUI 机器

```text
herdr machine list [--json]
herdr machine status [LABEL_OR_ID] [--json]
herdr machine reconnect LABEL_OR_ID
herdr machine add SSH_ALIAS [--label TEXT] [--remote-session NAME]
herdr machine rename PROFILE_ID --label TEXT
herdr machine enable PROFILE_ID
herdr machine disable PROFILE_ID
herdr machine remove PROFILE_ID
herdr --remote SSH_ALIAS [--session NAME] [--remote-keybindings local|server]
```

只在用户要求时添加/禁用/删除机器。machine add 可能安装/更新远端并启动会话，不是只读的“保存地址”；交互模式会检查正在运行的会话，非交互默认 default，最好明确 remote-session。安装或替换不兼容服务器可能要求交互确认，不能把它当只读探测，更不能替用户默认同意关闭现有服务器。

目标必须来自用户当前任务、当前仓库约定或已确认的机器列表；本技能没有个人服务器默认值。若仓库 AGENTS.md 要求其他远程技能，按其解析 SSH 别名。已有别名后复用原生 SSH 工具，不另建密码登录实现、不保存凭据。

机器 profile 已保存且启用后，在当前 Herdr 受管环境中执行：

```powershell
$machine = 'Build machine' # 替换成 machine list 的实际唯一标签或 profile id
herdr --machine $machine agent list
herdr --machine $machine pane list
herdr --machine $machine agent get reviewer
herdr --machine $machine agent prompt reviewer '报告当前任务进度。' --wait --timeout 30000
```

同一目标前缀贯穿发现、写入、等待、读结果；不同机器可能都有 w1:p1 或 reviewer。TUI 选中的机器不会改变当前 shell CLI 的目标。
--machine 必须是已启用的 profile id 或唯一且区分大小写的标签，不能直接给 SSH 主机名；不能与 --session / --remote 混用。

转发支持 workspace/worktree/tab/pane/notification/agent（不含 attach、本地 explain --file）、api snapshot、status server、server stop/reload-config/agent-manifests/reload-agent-manifests 及基于 API 的 plugin link/unlink/enable/disable/list/action/log/pane。
本地安装、配置、plugin install、session 管理、交互附加不转发。不要假设 update-agent-manifests 等额外命令也受支持，先查当前帮助。

远端必须已有运行中兼容服务器，转发不会自动安装/启动/重启，也不会失败后回退 Local。连接失败不保证写入没发生，先读远端状态再决定重试。
远程 worktree cwd/path 用绝对路径、~ 或 ~/ 前缀；plugin link 用绝对路径。显式指定远端 ID，--current 不能引用调用者本地窗格。

reachable 只说明本次 machine status 检查成功，不代表 TUI 正连接。reconnect 需要用户在其终端完成 SSH 认证，Agent 不代输入密码。remove/disable 断开客户端连接，远端会话继续存在。

## Core / App 机器

为 App 侧栏添加服务器时使用 Core 原生命令，先静态查看 `hc machine --help` 和 `hc machine add --help`。`hc server status` 不启动 Core；`hc machine ls` 会连接并可能按需启动 Core。不要从带 TUI `HERDR_*` 污染的进程首次启动 Core，按 [排障页](setup-recovery.md) 只清理当前子进程继承环境。

```text
hc machine add SSH_ALIAS --name NAME --install
hc machine ls
hc machine login NAME
hc machine update NAME
hc machine rename NAME NEW_NAME
hc machine rm NAME
```

仅在用户授权添加和远程安装时带 `--install`；它可复制当前 hc 到未安装或过旧的远端，不是查询。`--via COMMAND` 使用可双向传原始字节且无需交互的传输命令，必须配 `--name`；`--session` 指定远端 Core session，`--temp` 仅标记短期机器，仍需后续明确 rm。不要把 TUI 的 --label/--remote-session 参数套到 hc。

配置列表不等于连接或业务执行成功；在用户授权的真实任务中，用 `hc exec --on NAME --cwd /absolute/path <cmd>` 或 `hc run --on NAME ...` 核对实际机器，再用返回的 `NAME/t7` 全程定位。文件使用 `hc file read|write|edit --on NAME`，本机 harness 文件工具不会自动指向远端。App 展示远程 space 使用 `herdr-app do space.new --name NAME --machine MACHINE --folder /absolute/path`；只在用户要求显示时创建。

`hc machine rm` 只忘记本机连接，远端终端继续。`hc machine update` 会复制并计划重启远端 Core，现有终端保留；TUI 安装替换/停服的进程影响不同，不能互相套用。本轮仅静态阅读帮助，不把机器接入、远程任务或升级当成已实测。
