# SSH 机器与目标隔离

先分清 OpenSSH 别名和 Herdr 已保存机器 ID/标签。SSH 别名不自动等于可供 --machine 使用的 profile。

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

在 server-manager 工作区接入服务器时，按 AGENTS.md 使用 remote-server-ops 解析 SSH 别名；默认目标仅在用户未指定其他服务器时才是 server-198。已有别名后只用原生 ssh/scp/rsync/sftp，不另建密码登录实现。Herdr 不保存 SSH 密钥/密码，不把凭据写入技能。

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
