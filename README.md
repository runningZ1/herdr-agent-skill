# Herdr Agent Skill

面向 AI Agent 的 Herdr TUI 操作技能与无交互 CLI 适配器。通过官方 `herdr` 管理工作区、标签页、窗格与 Codex/Claude 生命周期，提供稳定 JSON、能力发现、有界读取和写操作预演。

这是独立维护的社区项目。官方 Herdr TUI 需要另外安装；Herdr App / `hc` 不适用。

## 快速开始

要求 Python 3.10+，无第三方运行依赖。当前验证环境为 Windows x86_64、Python 3.12、Herdr TUI 0.9.5 / protocol 22；其他平台尚未验证。

```powershell
git clone https://github.com/runningZ1/herdr-agent-skill.git herdr
cd herdr
python -B scripts/herdr_agent.py version
python -B scripts/herdr_agent.py schema
python -B scripts/herdr_agent.py errors
```

上述命令不访问运行中的会话。运行控制必须从 Herdr 管理的窗格内执行，且 `HERDR_ENV=1`；不要在外部伪造环境变量绕过限制。

```powershell
python -B scripts/herdr_agent.py doctor
python -B scripts/herdr_agent.py workspace list --limit 10 --fields workspace_id,label
python -B scripts/herdr_agent.py workspace create --help
```

若作为 Agent Skill 安装，将整个目录放入宿主支持的技能目录，保持目录名 `herdr`，并让 Agent 加载 [SKILL.md](SKILL.md)。执行脚本时使用该 Skill 的实际路径，不依赖特定用户名或项目目录。

## 能力与执行规则

| 能力 | 行为 |
|---|---|
| 工作区、标签页、窗格 | 查询、创建、布局与有界读取；具体操作以 schema 为准 |
| Agent 生命周期与消息 | 启动、查询、发送提示、等待、读取结果 |
| 机器协议 | JSON / JSONL；统一 `ok`、`data` / `error`、请求 ID 和退出码 |
| 写操作 | 默认预演，核对目标后以 `--commit --confirm PLAN_HASH` 提交 |
| 输入与读取 | JSON 文件或 stdin；列表分页、字段投影、超时与截断标记 |
| 高级官方功能 | worktree、SSH、插件、集成等通过专题参考路由到官方命令 |

复杂 JSON 优先使用 `--file PATH` 或 `--file -`，避免 shell 引号损坏。stdout 中 `ok=true` 仅代表该命令声明的成功：提示入队、Agent 空闲或等待结束都不能代替业务结果验收。

写入失败且 `outcome=committed` 或 `unknown` 时，先核对现场，不盲目重发。计划摘要是参数一致性检查，不是用户授权，也不提供 exactly-once 或事务回滚。

详细说明：[适配契约](references/agent-cli-contract.md) · [覆盖矩阵](references/coverage-matrix.md) · [操作工作流](references/workflows.md) · [来源与验证边界](references/sources-validation.md)。

## 对话窗口自动命名（Herdr TUI）

可选插件 `plugins/auto-name/` 使用官方事件钩子命名默认序号标签页，不启动额外常驻服务。要求 Python 3.10+ 和 Herdr TUI 0.9.5；已在 Windows 验证。

```powershell
herdr plugin link ./plugins/auto-name
herdr plugin action invoke local.auto-name.sync
```

插件在会话启动、新建标签页/窗格、Agent 检测/状态变化和窗格聚焦时自动处理。优先采用 Agent 上报的对话标题，去掉 OMP 状态旋转符和标题前缀；Claude 只有通用标题时，从本机对应会话的首段读取第一条用户消息。没有对话主题时先用“Agent · 项目目录”，得到主题后更新。标题最多 36 字符，读取和命名均不调用外部模型。

只修改空名称、纯数字名称，以及插件自己生成且未被手动修改的名称。已有自定义名称保持不变；手动改名后停止跟随，改回纯数字可恢复自动命名。多窗格标签页优先用首个 Agent 的主题。插件状态保存在 Herdr 提供的插件状态目录，并按会话 socket 隔离；不直接修改 `session.json`。命名前会重新核对标签，API 查询与重命名之间仍存在极短的并发窗口。

```powershell
python -B tests/test_auto_name.py
herdr plugin log list --plugin local.auto-name --limit 10
herdr plugin disable local.auto-name
```

禁用只停止后续自动命名，已经设置的名称保留。本插件不适用于 Herdr App / `hc`。

## 测试与构建

在仓库根目录执行：

```powershell
python -B tests/test_adapter.py
python -B tools/validate.py
python -B tools/build.py --verify
```

默认测试使用隔离后端，不连接真实会话、不启动模型。构建结果位于 `dist/herdr.zip`，同时生成 SHA256 校验文件；解包验证会再次运行契约测试。

真实验证必须在受管窗格内显式启动：

```powershell
python -B tools/validate.py --live
python -B tests/e2e.py --run
```

E2E 会创建并清理标记的测试对象。只有额外指定 `--agent claude` 或 `--agent codex` 才测试模型交互并使用已有额度。请先阅读 [测试脚本](tests/e2e.py) 的帮助与清理边界。

## 源码与维护

| 目录 | 用途 |
|---|---|
| `scripts/` | 适配器与兼容诊断入口 |
| `tests/` | 契约测试、显式真实 E2E |
| `tools/` | 验证、构建、官方资料采集 |
| `references/` | 上游资料、命令参考与操作契约 |
| `development/` | 设计和审查文档；本机证据与历史脚本被 Git 忽略 |

`python -B tools/collect.py` 将本机官方资料导出到被忽略的 `sources/current/`，不覆盖维护中的参考文档。不要提交会话文件、终端原始输出、凭据或本机验收 JSON。

## 协议与归属

本项目原创代码与文档采用 [MIT License](LICENSE)。随附的 Herdr 官方资料保留 Apache-2.0，参见 [第三方声明](THIRD_PARTY_NOTICES.md) 和 [上游协议副本](LICENSES/Apache-2.0.txt)。本项目与 Herdr 官方不存在隶属关系。
