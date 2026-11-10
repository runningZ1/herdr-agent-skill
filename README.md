# Herdr Agent Skill

让 AI Agent 统一操作 **Herdr TUI、Herdr Core 和桌面 App**：管理终端与 Agent、工作区与布局、远程机器与文件，以及插件和自定义界面。

当前版本 **2.0.0**。使用官方 `herdr`、`hc`、`herdr-app` 作为后端，提供 TUI 安全适配与全量 Socket 客户端，并附带三个产品的操作指南、官方 Skill 和公开 API 快照。独立维护的社区项目，与 Herdr 官方无隶属关系。

## 安装与快速开始

运行脚本需要 **Python 3.10+**，无第三方 Python 依赖。只需安装准备使用的官方产品；Core、App 和 TUI 不要求同时安装。

```powershell
git clone https://github.com/runningZ1/herdr-agent-skill.git herdr
Set-Location herdr

# 静态发现，不访问运行中的会话。
python -B scripts/herdr_agent.py version
python -B scripts/herdr_agent.py schema
python -B scripts/herdr_api.py schema
```

作为 Agent Skill 使用时，将整个 `herdr` 目录放入宿主支持的技能目录，并让 Agent 加载 [SKILL.md](SKILL.md)。保留 `scripts/`、`references/`、`sources/` 等相对路径；Agent 执行脚本应使用技能的实际绝对路径。

加载技能不会安装官方应用、模型、状态集成或插件。官方安装与更新入口见 [TUI 文档](https://herdr.dev/llms.txt)、[Core 官网](https://herdr.dev/core/) 和 [App 操作指南](references/app.md)。

## 选择正确入口

| 需要做什么 | 使用入口 | 详细说明 |
|---|---|---|
| TUI 工作区、标签页、窗格及常用 Agent 操作 | `scripts/herdr_agent.py`：26 项精选操作，带目标检查、写入预演和后置确认 | [适配器契约](references/agent-cli-contract.md) |
| TUI 完整 API、布局导入导出、事件或批次 | `scripts/herdr_api.py`：102 个方法的通用调用通道 | [Socket API](references/socket-api.md)、[TUI CLI](references/cli-reference.md) |
| 持久终端、Agent 编排、远程文件/命令、模板 | 官方 `hc`：32 项 Core API 的 CLI / connect 路由 | [Core 指南](references/core.md)、[官方 Skill](references/official-core-skill.md) |
| 桌面空间、标签页、布局、主题、快捷键和 mod | 官方 `herdr-app`：71 条内置命令及界面定制流程 | [App 指南](references/app.md)、[官方 Skill](references/official-app-skill.md) |

这些数量来自发布快照，表示可发现能力与操作路由，**不表示每项功能均已端到端实测**。全部方法与参数来源见 [API 目录](references/api-methods.md)，证据层级见 [覆盖矩阵](references/coverage-matrix.md)。

| 组件 | 当前基线 | 运行与验证范围 |
|---|---|---|
| Skill | 2.0.0 | 运行脚本 Python 3.10+；维护工具 Python 3.11+ |
| TUI | 0.9.5 / protocol 22 | Windows x86_64 / Python 3.12，包含真实会话与 named-pipe 验证 |
| Core | 0.1.18 | 官方 Skill、CLI 与 32 项 schema 路由已核对 |
| App | 0.1.13 | 官方 Skill、71 条 commands 与生成指南已核对；未进行本轮视觉验收 |

其他平台和版本需要单独验证。版本升级后的 schema 采集不能代替兼容性或业务验收。

## 基本使用

以下命令在技能根目录执行。选择对应产品，不要将 TUI 的 workspace/pane ID、Core 终端地址和 App 界面 ID 混用。

### TUI

运行控制要求真实 TUI 受管窗格及 `HERDR_ENV=1`。未进入受管环境时，使用安装、帮助和静态发现；不要伪造变量或猜其他会话地址。

```powershell
python -B scripts/herdr_agent.py doctor
python -B scripts/herdr_agent.py workspace list --limit 10 --fields workspace_id,label
python -B scripts/herdr_api.py call ping
python -B scripts/herdr_api.py schema --method layout.apply
```

精选适配器检查业务参数、实时目标和后置状态。原始 API 客户端支持 `call`、逐请求连接的 `batch`、有界 `subscribe`，以及独立的 SSH Agent 租约连接；预演只检查方法和 JSON 对象形状，完整参数由服务器验证。

两个入口的写操作均默认预演。核对目标和 effect 后，用同一输入加 `--commit --confirm PLAN_HASH` 提交。hash 是参数与上下文一致性检查，不是用户授权、幂等键或事务。复杂 JSON 使用 `--file PATH` 或有限 stdin `--file -`；具体例子见 [Socket 操作流程](references/socket-api.md)。

### Core 与 App

静态发现不需要打开窗口：

```powershell
hc --version
hc --skill
hc schema
herdr-app --version
herdr-app commands
```

Core 负责启动、读取、消息、等待与清理终端；App 负责用户看到的空间、标签页、窗格和 UI。App 定制先读取其 home 下生成的 `AGENTS.md`、`herdr.d.ts` 和 `gpui-kit.d.ts`，官方 layout/mod 先 clone 再修改。

`hc server status` 不启动 Core；机器列表等查询可能按需启动 Core。App 的 `ls/status/shot` 需要已有窗口。不要运行裸 `herdr`、`hc` 或 `herdr-app` 探测，它们可能附加会话或打开界面。

### 上下文与结果判断

- `HERDR_ENV` 规则只适用于 TUI；Core/App 不受此门槛。`HC_TERMINAL_ID` 优先表明 Core 上下文，TUI 适配器会拒绝带该变量的调用。
- App/Core 子进程若继承 TUI 的 `HERDR_*` 标记，按 [排障指南](references/setup-recovery.md) 处理；只清理将启动的子进程，不用 `allow_nested` 绕过，不重启用户已有服务。
- 输入入队、启动成功、Agent done 或等待结束都不等于业务完成。读取实际结果，并核对文件、测试或其他产物。
- 写入超时或结果未知时先核对现场，不盲目重发。只清理本次任务创建的对象，保持产品、机器和会话目标一致。

## 可选：TUI 对话窗口自动命名

插件随源码与分发包提供，需要单独启用：

```powershell
herdr plugin link ./plugins/auto-name
herdr plugin action invoke local.auto-name.sync
```

仅处理空名称、数字标签及插件仍拥有的名称，保留人工改名。优先采用 Agent 标题；Claude 使用通用标题时，会读取确切本机会话的有限片段，从首条用户消息提取主题；无主题时使用 Agent 与目录。该插件仅适用于 TUI。

2.0.0 修复了空 `cwd` 崩溃和部分成功后归属丢失。每次 rename 前先原子保存待确认状态，结果未知时保留 pending，不盲目重发。Herdr 没有条件 rename，最后一次查询与写入之间仍存在并发窗口。

名称会尽力清理常见秘密，状态仅存名称指纹，日志不输出标题明文；无法识别任意形式的敏感文字，提取后的其余主题仍会出现在标签中。

```powershell
# 停止后续自动命名，保留已有名称。
herdr plugin disable local.auto-name
```

## 项目结构

```text
herdr/
├── SKILL.md                    # Agent 加载的统一入口
├── README.md                   # 安装、使用与维护说明
├── scripts/                    # 精选适配器、全量 API 客户端、兼容诊断
├── references/                 # 产品指南、能力目录与官方资料快照
├── sources/                    # 三份随包分发的公开 API / commands JSON
│   └── current/                # 临时采集结果；不提交、不分发
├── plugins/auto-name/          # 可选 TUI 自动命名插件与 TOML 清单
├── tests/                      # 离线回归与显式启动的真实 E2E
├── tools/                      # 采集、完整性验证与构建工具
├── development/                # PRD、技术设计和审查记录
│   ├── evidence/               # 本机验证证据；不提交、不分发
│   └── history/                # 本机历史副本；不提交、不分发
├── .github/workflows/          # Windows CI
├── LICENSES/                   # 上游许可副本
├── LICENSE
├── THIRD_PARTY_NOTICES.md
└── dist/                       # 本地 ZIP 与 SHA256；不提交
```

Git 跟踪公开源码、文档和三份 schema；临时采集、历史、本机证据、缓存、环境文件和日志保持隔离。运行所需资源留在技能目录中，安装时无需依赖外部开发工作区。

## 验证与构建

维护工具要求 **Python 3.11+**，使用标准库 `tomllib`。在仓库根目录执行：

```powershell
# 完整离线回归：适配器、Socket、插件和维护工具。
python -B -m unittest discover -s tests -p "test_*.py"

# 文件、文档链接、插件入口、版本与公开快照一致性。
python -B tools/validate.py

# 生成分发包，解包后执行完整离线回归。
python -B tools/build.py --verify
```

默认回归使用隔离状态和模拟后端，不启动付费模型或操作用户真实标签。需要真实 TUI 只读检查时，在受管窗格内执行 `python -B tools/validate.py --live`；它不会自动启动 Core/App。

真实变更测试见 [tests/e2e.py](tests/e2e.py)，必须显式指定 `--run`；只有额外指定 `--agent` 才启动模型。验证边界与历史证据见 [来源与验证](references/sources-validation.md)。

构建生成 `dist/herdr.zip` 和 `dist/SHA256SUMS.txt`。包内包含脚本、指南、官方 Skill、公开 schema、插件 Python/TOML 及测试维护源码；不包含用户会话、秘密、日志、本机证据或临时采集。ZIP 是本地构建产物，GitHub 仓库保留可重建的源码。

## 更新官方资料

```powershell
# 仅采集静态资料到 sources/current/，并报告发布快照差异。
python -B tools/collect.py

# 审阅差异后，更新公开快照、帮助和方法索引。
python -B tools/collect.py --publish
```

采集器分别读取三个官方二进制的静态帮助、Skill 和 schema/commands，不沿用业务适配器的精确版本拒绝策略，不采集会话正文或机器配置。发布后重新核对产品指南与平台限制，再执行验证和构建。

## 2.0.0 主要变更

- 从 TUI 技能扩展为 TUI/Core/App 统一操作路由。
- 新增全部 TUI 方法的真实 socket/pipe 通道、顺序批次、SSH Agent 租约与有界订阅。
- 修复自动命名空值、不确定写入恢复和标题日志暴露。
- 补齐插件、TOML、schema 分发，并增加跨产品目录一致性检查与 CI 回归。
- 修正订阅字段、个人默认远端、集成列表及覆盖/实测声明。

## 许可与归属

原创代码和文档采用 [MIT](LICENSE)。官方资料保留各自上游归属，见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；本项目的许可不重新许可官方应用。
