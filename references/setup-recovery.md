# 安装、配置、恢复与排障（2.0.0）

## 先判定 TUI / Core / App

`HC_TERMINAL_ID` 存在时优先判定为 Core 终端；App 内的终端也由 Core 管理。`HERDR_ENV=1` 仅是 TUI 受管上下文标记，不能作为 Core/App 操作门槛。若两者同时存在，先怀疑从 TUI 启动 Core/App 时继承了 `HERDR_*`，不要仅凭 HERDR_ENV 启用 TUI 操作或启动嵌套 TUI。

先使用静态 `hc --help` / `--skill` / `schema` 与 `herdr-app --help` / `--skill` / `commands`。`hc server status` 不会启动 Core；`hc machine ls` 等看似只读的 Core 查询可能按需启动 Core。裸 herdr-app 会打开窗口，不用于探测。没有运行中的产品时，报告状态并按任务授权决定是否启动，不能因诊断擅自启动或重启。

遇到 App 终端内 “inception detected” 等错误，只核对变量是否存在，不导出全部环境。为接下来明确要启动的子进程清除继承的 `HERDR_*`；保留 Core 自身 `HC_TERMINAL_ID` 上下文，不修改用户/系统持久环境，不重启用户 Core，不用 `allow_nested` 掩盖错误识别。PowerShell 7 的子进程局部示例（仅运行不启动 Core 的 status）：

```powershell
$child = [System.Diagnostics.ProcessStartInfo]::new()
$child.FileName = (Get-Command hc -CommandType Application).Source
$child.UseShellExecute = $false
$child.ArgumentList.Add('server')
$child.ArgumentList.Add('status')
foreach ($key in @($child.Environment.Keys)) {
  if ($key -like 'HERDR_*') { [void]$child.Environment.Remove($key) }
}
$process = [System.Diagnostics.Process]::Start($child)
$process.WaitForExit()
```

更换为任务已授权的实际命令/argv 时仍只改这个子进程环境。已有 Core/终端的继承环境不会被上述操作追溯修改；不要宣称清理一个子进程即可修复全部现有终端。若需后续维护运行中的 Core，先查看现有终端并取得相应停服授权；当前技能升级不包含该操作。

## 安装与版本

本机已有产品直接复用：TUI 检查 `Get-Command herdr`、`herdr --version`；Core/App 分别检查 hc / herdr-app 的版本和帮助。官方 TUI Windows 安装入口 https://herdr.dev/install.ps1；按对应产品安装文档检查脚本后运行，不混用产品安装器。Core/App 的说明见 [Core](core.md) 和 [App](app.md)。
官方 Skill 可通过 `herdr --skill` 导出，或 `npx skills add herdrdev/herdr --skill herdr -g` 安装。本目录已经安装增强版，不要再用全局 npx 安装制造重复副本或覆盖增强入口。

0.9.5 Windows 发布目录常见 `%USERPROFILE%\.herdr\packages\standalone\releases`；实际命令用 PATH 解析，不锁定某个版本号路径。
更新先看 status/channel；仅用户要求升级时执行 update。不要擅切 preview 或开启 handoff；客户端和服务器可版本不同，以协议兼容和 status 为准。

## 配置

用 `herdr --help` 确认真实 Config/Logs 路径，HERDR_CONFIG_PATH 可覆盖。Windows 默认 `%APPDATA%\herdr\config.toml`，Unix 默认 `~/.config/herdr/config.toml`。
先 `herdr config check`，仅按需加载配置相关小节；默认值用 `herdr --default-config` 查看，不直接覆盖用户文件。编辑前备份，编辑后 check，再按需 server reload-config。不能重载的设置需要下次服务器启动生效，避免为此自动重启当前任务。
配置范围包含 terminal/cwd、UI/主题/侧栏/通知、键位、worktrees、session/恢复、experimental、agent manifests 等，以版本对应 config-reference 为准，不猜 TOML 键。

```toml
[experimental]
pane_history = true

[session]
resume_agents_on_restore = false
```

上例仅用于明确要求对应行为时，不自动启用。pane_history 默认关闭，保存屏幕内容可能含敏感信息；resume_agents_on_restore 默认开启，设 false 会关闭原生 Agent 恢复。

## 持久化与恢复

| 情况 | 实际保留 |
|---|---|
| 客户端分离/关窗，服务器继续运行 | 原窗格进程和对话继续；重新 attach 回来 |
| TUI 服务器停止/系统重启 | 原窗格进程结束；恢复布局/cwd，不等于继续执行 |
| 启用 pane_history 后重启 | 可回放匹配布局的屏幕，不恢复原进程 |
| 支持且上报有效 agent_session | 可用原生 resume 命令重建受支持 Agent 的对话 |
| 实验 handoff | 尽力转移活进程；等待/订阅/连接仍可能断开，不保证无损 |

普通分离 ctrl+b q，然后重新运行 herdr。不要以 server stop 代替分离。
session.json 包含私密布局和会话引用；旁有 session-snapshots 布局历史，加载失败备份在 session-backups；屏幕历史在 session-history.json。不要把这些文件打包进技能。
手动恢复只在用户明确要求恢复时：session list --json 找实际目录，先保存当前文件；明确停目标服务器的影响后停止，复制选定布局快照到 session.json，再重启。不能在活服务器写入期间直接替换持久文件。快照不包含活进程或屏幕历史。

## Windows 差异

原生 ConPTY，传输为 Windows named pipe，不使用 Unix AF_UNIX/socat 示例。PATH 上 agent exe 或 shim 必须可由 Windows 启动。
逻辑 cd 跟踪部分支持，显式传真实 --cwd，必要时修复 shell/OSC7 集成。Agent 进程树识别不等同 Unix 前台进程组。
普通客户端连接管理员服务器默认受限。`server.allow_unelevated_clients` 或 server --allow-unelevated-clients 会扩大同账号普通进程对管理员窗格的控制能力，不能作为通用报错修复；必须用户明确需要该共享。reload 不会改变运行中访问策略。

## 按现象排障

| 现象 | 检查顺序 |
|---|---|
| 找不到 herdr | Get-Command、当前 PATH、官方安装路径；不重复安装多个版本 |
| 不在 TUI Herdr | 仅对 TUI 不伪造 HERDR_ENV；Core/App 使用自身上下文，不套 TUI 门槛 |
| 连接失败 | status、session list、目标 socket/会话；不扫描无关会话，不自动 stop/start |
| 方法不存在/协议不兼容 | 对比客户端与运行中服务器，查看 status/schema；升级安装不等于服务器已换新 |
| Agent 未识别/unknown | agent get/read/explain、integration status、server agent-manifests；核对平台 |
| Agent blocked | read 当前 UI，明确问题再决定；不用盲 Enter 修复 |
| wait 超时/stalled | 先 read/get；确认实际状态，避免重复提示或命令 |
| 窗格输出不完整 | recent-unwrapped，增大有界 lines；最后才请求同机 Markdown 文件 |
| 保存目录不存在 | 恢复真实目录/shell；不要擅改成 HOME 掩盖失败 |
| 插件无效 | list warnings、min version、platforms、action list、log list --limit 20 |

CLI API/server 错误通常 stderr JSON、退出 1；语法错误退出 2。报告保留 code/message 和命令，不泄露敏感屏幕、路径中的密钥或完整日志。

## Core / App 更新与恢复差异

Core 的 `hc update`、`hc machine update` 与 server.restart 是计划重启，保留程序并重新接管终端，连接/流仍可能中断；`hc server stop` 会停止程序，kept 终端待下次启动后恢复 shell。`hc keep` 在丢失后仅恢复 shell，不自动重放任务。App 关窗通常不杀 Core 终端；显式 pane/tab/space close 或 terminal.kill 可结束关联程序，不能把两者混淆。

TUI 的 herdr server stop 及持久布局恢复规则不能照搬到 Core；TUI 与 Core 的机器、会话和配置各自独立。Core shell 配置在下一次启动新程序时生效，无需为了配置改动重启已有用户任务。当前 Core Skill 的 Codex `--no-daemon` 要求适用于 hc 启动与模板，不能外推为 TUI 统一启动参数。
