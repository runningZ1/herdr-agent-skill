# Herdr Agent Skill 2.0.0

统一操作 Herdr TUI、Herdr Core 和桌面 App 的 Agent Skill，使用官方 `herdr`、`hc`、`herdr-app` 作为后端。包含 TUI 常用安全适配、全量 Socket API 客户端、Core/App 完整操作目录与官方 Skill 快照。

独立维护的社区项目。官方应用和 Agent 自身需要另外安装；加载本技能不会安装服务、集成、插件或模型。

## 快速开始

将整个目录放进宿主支持的技能目录，让 Agent 加载 [SKILL.md](SKILL.md)。脚本运行使用技能实际路径，不依赖当前工作区或固定用户名。在本仓库根目录可执行：

```powershell
python -B scripts/herdr_agent.py version
python -B scripts/herdr_agent.py schema
python -B scripts/herdr_api.py schema
herdr --version
hc --version
herdr-app --version
```

运行脚本要求 Python 3.10+；`tools/` 维护工具要求 Python 3.11+（使用标准库 TOML 解析）。均无第三方 Python 依赖。本轮基线为 Windows x86_64 / Python 3.12、TUI 0.9.5 / protocol 22、Core 0.1.18、App 0.1.13；其他平台的运行验证单独报告。

## 三个操作面

| 产品 | 入口与覆盖 | 资料 |
|---|---|---|
| TUI `herdr` | 26 项精选适配；102 项 Socket 方法均有通用通道；其他本地管理用官方 CLI | [适配契约](references/agent-cli-contract.md)、[Socket](references/socket-api.md)、[TUI CLI](references/cli-reference.md) |
| Core `hc` | 32 项 API 的原生 CLI / connect 路由；持久终端、Agent、远程文件和命令、模板、事件 | [Core 指南](references/core.md)、[官方 Skill](references/official-core-skill.md) |
| App `herdr-app` | 71 条内置 commands；空间、tab、pane、布局、主题、按键和 mod | [App 指南](references/app.md)、[官方 Skill](references/official-app-skill.md) |

数量来自发布快照，是能力发现与调用路由的范围，不是逐项实测数量。完整来源在 [方法目录](references/api-methods.md) 和 [覆盖矩阵](references/coverage-matrix.md)。

`HERDR_ENV=1` 只用于真实 TUI 窗格；Core/App 不受此门槛。`HC_TERMINAL_ID` 优先表明 Core 上下文，TUI 适配器会拒绝带该变量的调用。若 App/Core 子进程继承了 TUI 的 `HERDR_*`，只清理将启动的子进程环境；不使用 `allow_nested` 绕过，不重启现有服务。

`hc server status` 不启动 Core，而机器列表等查询可能按需启动。App 静态 `commands/--skill` 不需要窗口；`ls/status/shot` 需要已有窗口。不运行裸二进制探测。

## TUI 安全适配与全量 API

真实 TUI 受管窗格内执行：

```powershell
python -B scripts/herdr_agent.py doctor
python -B scripts/herdr_agent.py workspace list --limit 10 --fields workspace_id,label
python -B scripts/herdr_api.py call ping
python -B scripts/herdr_api.py schema --method layout.apply
```

精选适配器检查实时目标、业务参数及后置状态。写操作默认预演，核对后使用同一输入 `--commit --confirm PLAN_HASH` 提交。计划 hash 是一致性检查，不是用户授权，也不提供幂等和回滚。

全量 API 客户端支持 `call`、逐请求连接的 `batch`、有界 `subscribe`，并为连接作用域的 SSH Agent 登记保留独立租约。它与精选适配器的保护程度不同：预演只检查方法和 JSON 对象形状，不查询业务目标；服务器执行时验证完整参数。所有非只读方法默认预演。原始 API 的完整 schema 随包分发，不需要自己猜参数或 Windows pipe 名称。具体示例、超时、连接作用域及未知写入恢复见 [Socket 操作指南](references/socket-api.md)。

复杂 JSON 使用 `--file PATH` 或有限 stdin `--file -`。两个脚本与原生 CLI 的参数/输出不能混用。成功仅表示相应调用完成，输入入队、启动成功或 Agent done 都不能替代业务验收。

## 对话窗口自动命名

可选 TUI 插件随源码和 ZIP 一起提供：

```powershell
herdr plugin link ./plugins/auto-name
herdr plugin action invoke local.auto-name.sync
herdr plugin disable local.auto-name
```

保留人工名称，仅命名空/数字标签和插件自身仍拥有的名称。优先采用 Agent 标题；Claude 通用标题会从确切本机会话的有限片段读取首条用户消息；无主题时使用 Agent 与目录。该插件不适用 Core/App。

2.0.0 修复空 `cwd` 崩溃，并在每次 rename 前原子保存待确认状态；后续查询或其他标签失败不会丢失已完成的归属。未知结果仍显示旧名时保持待确认，不盲目重发。Herdr 没有条件 rename，最后一次查询与写入之间仍有并发窗口。

常见秘密在进入名称前尽力脱敏；无法识别任意形式敏感文本，首句其余内容仍会展示到标签。状态保存名称指纹，日志不输出标题明文。禁用只停止后续命名，保留已有名称。

## 验证与分发

```powershell
python -B tests/test_adapter.py
python -B tests/test_socket_api.py
python -B tests/test_auto_name.py
python -B tests/test_tools.py
python -B tools/validate.py
python -B tools/validate.py --live
python -B tools/build.py --verify
```

默认测试使用隔离状态和模拟后端，不启动付费模型，不操作真实标签。`--live` 只核对 TUI 官方 Skill、doctor 和有界工作区列表，不自动启动 Core/App。真实变更场景可按 [E2E 脚本](tests/e2e.py) 使用 `--run`；仅额外指定 `--agent` 时启动模型。

分发包为 `dist/herdr.zip` 与 SHA256 校验文件；包含源码、三份公开 schema、官方 Skill、插件 Python 入口及 TOML 清单。排除本机证据、历史目录、用户会话、日志、临时采集和缓存。`--verify` 解包后执行包内回归和静态完整性检查。

## 维护官方能力基线

```powershell
python -B tools/collect.py
# 审阅差异后发布公开快照：
python -B tools/collect.py --publish
```

默认只将静态资料写入被忽略的 `sources/current/` 并报告与发布快照的差异；`--publish` 更新公开 schema、官方 Skill、帮助和 API 目录。采集器直接调用静态官方命令，不沿用业务适配器精确版本拒绝策略。它不会采集用户对话或机器配置。

升级后重新核对协议、路由、平台限制与测试；采集成功不代表兼容性或业务验收通过。来源和历史验证见 [sources-validation.md](references/sources-validation.md)。

## 2.0.0 变更

- 从 TUI 技能扩展为 TUI/Core/App 统一路由，保留产品权限、ID 和机器配置隔离。
- 新增全部 TUI 方法的真实 Unix socket / Windows named-pipe 通道、顺序批次、SSH Agent 租约与有界事件采集。
- 修复自动命名的空值与不确定写入恢复，降低状态/日志中的主题暴露。
- 修复插件、TOML 和 schema 分发遗漏，更新采集、目录一致性与 CI 检查。
- 修正订阅字段、个人默认远端、过时集成列表及过强覆盖声明。

## 协议与归属

原创代码与文档采用 [MIT](LICENSE)。官方资料保留各自上游归属，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；技能不重新许可官方应用。本项目与 Herdr 官方无隶属关系。
