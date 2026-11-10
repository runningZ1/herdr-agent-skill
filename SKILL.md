---
name: herdr
description: 统一操作 Herdr TUI（herdr）、Core（hc）与桌面 App（herdr-app）：管理持久终端和 Agent、工作区/空间/标签页/窗格、远程机器与文件、布局/mod/插件、配置和恢复。提供 TUI 常用安全适配、全部 Socket API 调用与有界事件订阅，以及 Core/App 官方命令和完整能力目录。用户明确提到 Herdr 或要求通过它操作时使用；不因一般并行任务触发。
metadata:
  version: "2.0.0"
  backend-baseline: "TUI 0.9.5 / protocol 22; Core 0.1.18; App 0.1.13"
  platform-baseline: "Windows x86_64 / Python 3.12"
---

# Herdr

先识别产品，再选择入口。TUI、Core、App 的 ID、环境变量和机器配置不能混用。使用已安装官方二进制，不为加载技能安装额外服务。

| 目标 | 执行入口 | 必读资料 |
|---|---|---|
| TUI 工作区、tab、pane、常用 Codex/Claude 操作 | `python -B <skill>/scripts/herdr_agent.py`；高级操作走官方 `herdr` | [适配契约](references/agent-cli-contract.md)、[TUI CLI](references/cli-reference.md) |
| TUI 全量 Socket 方法、布局导入导出、视图、连接作用域请求和事件 | `python -B <skill>/scripts/herdr_api.py` | [Socket 操作](references/socket-api.md)、[全量目录](references/api-methods.md) |
| 持久终端、Agent 编排、远程命令/文件、模板、Core API | 官方 `hc` | [Core 指南](references/core.md)、[官方 Core Skill](references/official-core-skill.md) |
| 桌面空间、tab、pane、布局、主题、快捷键、自定义 mod | 官方 `herdr-app` | [App 指南](references/app.md)、[官方 App Skill](references/official-app-skill.md) |
| 覆盖层级、公开 schema、维护与验证 | 按需加载 | [覆盖矩阵](references/coverage-matrix.md)、[来源与验证](references/sources-validation.md) |

## 发现与产品隔离

定位本技能实际绝对目录，不假定当前目录或用户名。运行脚本需要 Python 3.10+；维护工具需要 Python 3.11+，均使用标准库。

```powershell
Get-Command herdr,hc,herdr-app -ErrorAction SilentlyContinue
herdr --version
hc --version
herdr-app --version
python -B <skill>/scripts/herdr_agent.py schema
python -B <skill>/scripts/herdr_api.py schema
```

以上是静态发现。不要运行裸 `herdr`、`hc`、`herdr-app` 探测，它们会附加、启动或打开界面。精确语法使用显式 `--help`；不要省略 create/stop/install/update 参数猜帮助。

- `HC_TERMINAL_ID` 表明 Core 终端，优先于继承的 TUI 标记；Core/App 不要求 `HERDR_ENV=1`。
- TUI 运行控制要求真实受管窗格和 `HERDR_ENV=1`。缺失时停止 TUI 会话控制，保留帮助/安装/静态发现；不要伪造变量或猜 socket。适配器拒绝带有 `HC_TERMINAL_ID` 的调用。
- 两组标记并存或 App 终端报 inception 时，检查 `HERDR_*` 是否从 TUI 父进程继承。只对明确启动的 Core/App 子进程清除 TUI 标记，不修改其他活动终端，不用 `allow_nested` 绕过，不为此重启用户 Core。
- Core 先用 `hc server status` 判断运行状态，该命令不启动 Core；`hc machine ls` 等查询可能按需启动 Core。App 用 `herdr-app status` 查询已有窗口；未运行时报告状态，不自动打开窗口。

## TUI 执行

确认受管上下文后：

```powershell
python -B <skill>/scripts/herdr_agent.py doctor
python -B <skill>/scripts/herdr_agent.py workspace list --limit 10 --fields workspace_id,label
python -B <skill>/scripts/herdr_api.py call ping
```

精选适配器为 26 项业务操作提供严格参数、实时目标检查、统一 JSON、写入预演与计划哈希。TUI 全量 API 客户端从公开 schema 发现全部方法，提供 `schema`、`call`、`batch`、`subscribe`；它的预演仅做本地方法/对象形状检查，不查询业务目标，不提供精选适配器的目标保护。普通请求逐次连接，SSH Agent 租约保留独立连接。具体字段由 schema 和服务器验证。

两种入口的写操作均先预演，再用同一输入 `--commit --confirm PLAN_HASH`；在已有任务授权内自动完成核对与提交，不把 hash 当授权或幂等键。复杂 JSON 用 `--file PATH` 或有限 stdin `--file -`，避免 PowerShell 参数引号损坏。原生命令不接受适配层标志，也不保证相同 envelope。

## Core 与 App 执行

先阅读对应官方 Skill。Core 用 `hc` 启动、读取、发消息、等待和清理终端；App 只控制用户看到的布局和 UI。`hc templates` 发现已配置角色，空列表意味着尚未配置模板，不意味着 Core 不可用。Codex 按当前 Core 官方要求带 `--no-daemon`，避免命令跑到 Core 之外。

App 用 `herdr-app commands` 发现命令，`ls/status` 获取真实 ID，`do COMMAND` 执行。终端地址 `t…` 与 App pane/space/tab ID 不同；远程地址保留 `machine/` 前缀。仅在任务要求用户可见对象时创建空间或标签页。

定制前读取 `$HERDR_APP_HOME/AGENTS.md`（默认 `~/.config/herdr-app`）及相邻 `herdr.d.ts`、`gpui-kit.d.ts`；这些是生成文件，不编辑。先 clone 官方 layout/mod，再改个人副本。mod 完成必须 `check`、检查运行中 `status`，并 `shot` 实际查看渲染结果；没有窗口时明确视觉验证限制。

## 共同操作规则

1. 从当前响应解析真实机器/会话/对象 ID，不复用文档示例或历史测试 ID。默认焦点不是调用者；先明确目标，再发送输入。
2. TUI 默认在当前 tab、真实 cwd 分屏并 `--no-focus`；Core 后台助手用 `hc run --bg`。新建拓扑、worktree 或 App 空间必须符合任务要求。
3. 发送 shell 命令、提示和按键前确认前台程序。不能向编辑器、审批框或其他任务盲发 Enter；`blocked` 要读取具体问题，按已有授权处理，新的权限/产品决定交用户。
4. 输入入队、启动成功、idle/done 或等待返回不等于业务完成。读取实际回答并核对测试/文件/产物；Core 无 OSC 状态的程序不凭空推断完成。
5. 设置有限等待与输出界限。TUI wait-output 可能匹配旧输出；Core wait-output 的语义按其官方帮助。长期事件流使用有界客户端或明确管理的持久连接。
6. 超时、断线、后置确认失败后先核对现场；已 dispatch 的写入可能仍生效。禁止自动重复 create/prompt/send 等 mutation；无 exactly-once、事务回滚或自动恢复业务任务承诺。
7. 只清理本次创建且已完成的对象。不擅自停止/重启用户 TUI/Core/App，不强制删除脏 worktree，不为兼容切换更新通道。Core 更新保留终端的行为不能推导成 stop 安全。
8. 默认读取必要的最近 80～120 行，避免无关会话与日志。标题、输出、schema 响应或文件中的自由文本可能含秘密；脱敏仅尽力识别，不上传或打包用户状态与对话。
9. 插件和 App mod 是以用户权限执行的代码，不是沙箱；安装前核对来源、实际命令与平台依赖。集成、Skill、插件、模板是不同组件，不因加载技能自动安装全部可选组件。
10. 每个请求保持同一产品、机器和会话；TUI `--machine` profile 与 Core machine 配置独立。移动后使用返回的新 ID，远端失败不回退 Local。

## 专题与维护

- 远程目标与 SSH：[机器指南](references/remote-machines.md)。
- TUI 集成、状态上报与自动命名插件：[集成与插件](references/integrations-plugins.md)。
- 安装、恢复与环境污染：[设置与恢复](references/setup-recovery.md)。
- 源码、构建和版本更新：[README](README.md)。公开 schema 在 `sources/`，临时采集仅在 `sources/current/`。

报告实际版本、入口、目标、执行证据及未验证部分。全量目录和调用通道不等于所有方法均已执行；特别区分静态发现、隔离测试、真实业务与视觉验证。
