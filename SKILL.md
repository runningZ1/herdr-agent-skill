---
name: herdr
description: 使用 Herdr TUI 官方 CLI 与本地 Agent 适配入口管理工作区、标签页、窗格、Codex/Claude 消息和生命周期；提供 schema、统一 JSON、写入预演、计划校验、有界读取与错误恢复，并指导官方 worktree、SSH、插件、集成、配置恢复操作。用户明确提到 Herdr TUI 或要求通过 Herdr 操作时使用；不因一般并行任务触发。运行控制要求 HERDR_ENV=1；Herdr App/hc 不适用。
metadata:
  version: "1.0.1"
  tested-backend: "Herdr TUI 0.9.5 / protocol 22"
  tested-platform: "Windows x86_64 / Python 3.12"
---

# Herdr TUI

使用官方 `herdr` 作为唯一执行后端，不安装同名第三方工具或新后台服务。
官方内置 Skill 原文保存在 [official-skill.md](references/official-skill.md)，来自 `herdr --skill`。
优先用本技能的 `scripts/herdr_agent.py` 执行常用确定性操作；未覆盖领域用官方原生命令。
先读 [适配入口契约](references/agent-cli-contract.md)，用 [覆盖矩阵](references/coverage-matrix.md) 区分已实现、官方路由、已实测。
以已安装二进制和实时响应为准，静态基线为 TUI 0.9.5 / API protocol 22。

## 开始操作

定位本技能绝对目录后使用入口（Python 3.10+，不需要安装依赖或改 PATH）：

```powershell
$cli = (Resolve-Path './scripts/herdr_agent.py').Path # 在本 Skill 根目录执行
python $cli version
python $cli schema
Get-Command herdr
$env:HERDR_ENV
```

若 `HERDR_ENV` 不等于 `1`，仅提供安装、帮助、静态配置说明，说明当前 Agent 未运行在 Herdr 窗格内，停止运行中会话检查与控制。不要伪造变量或猜 socket 绕过限制；在 Herdr 窗格内重新启动 Agent 后操作。

确认在受管窗格后：

```powershell
python $cli doctor
python $cli workspace list --limit 10 --fields workspace_id,label
```

`version/schema/errors` 是静态发现，可在受管环境外运行；`doctor` 和业务操作检查受管环境。
旧 `scripts/doctor.py` 保持兼容，仅用于原有脚本，不套用新 envelope。
明确目标元组：机器、会话、工作区、窗格或实时 Agent 名称。默认继承当前 socket；使用 `--current` 指向调用者。跨机器在发现和后续每条命令中保持同一 `--machine` 前缀。

## 按任务加载参考

| 用户请求 | 加载与执行 |
|---|---|
| 常用业务命令的 schema、JSON、预演/提交、错误 | [适配入口契约](references/agent-cli-contract.md)，再 `python $cli RESOURCE ACTION --help` |
| 查看布局、分屏、运行 shell、读取日志 | [操作工作流](references/workflows.md)、[CLI 索引](references/cli-reference.md) |
| 启动 Claude/Codex、委派、等待结果 | 先读 [官方 Skill](references/official-skill.md)，再读 [工作流](references/workflows.md) |
| 新建工作区/标签页、worktree、移动窗格 | [CLI 索引](references/cli-reference.md) |
| SSH 机器、远程操作 | [远程机器](references/remote-machines.md) |
| 集成、状态钩子、插件 | [集成与插件](references/integrations-plugins.md) |
| 安装、配置、恢复、Windows 问题 | [设置与恢复](references/setup-recovery.md) |
| API、事件订阅、布局导入导出、Agent 视图 | [Socket API](references/socket-api.md)，再导出本机 schema |
| 精确命令语法 | `herdr <group>` 或 `herdr <group> --help`；[帮助快照](references/installed-cli-help.md) 供离线参考 |
| 来源、测试边界、维护 | [来源与验证](references/sources-validation.md) |

不要运行裸 `herdr` 探测，它会打开 TUI。不要通过省略参数探测嵌套 `create` / `stop` / `install` / `update` 命令，默认参数可能直接生效。`herdr server` 也会启动服务器，查帮助用 `herdr server --help`。

## 共同规则

先区分两种输出：适配入口为 stdout 上的 schema_version/ok/data/error；官方命令保留其原始 result/text/stderr。不能把适配标志添加到官方命令，或反过来套用。

适配写入：同一个 JSON 输入先 `--dry-run`，检查真实目标、effect、cwd，再 `--commit --confirm PLAN_HASH`；已有任务授权内自动完成这两步。计划过期或目标改变时重新预演。不能通过改参数复用 hash，不把确认哈希当用户授权。
复杂 JSON 使用 `--file PATH` 或 `--file -` stdin，避免 PowerShell 原生参数引号丢失。stdin 最大64KiB。默认 list limit20/max100，本地 offset 分页；read 默认80/max500行，64K字符上限；截断要看 metadata。这些适配参数不代表官方 CLI 同名功能。

1. 从 JSON 解析真实 ID，不套用示例值。创建 workspace 返回 `result.workspace`、`result.tab`、`result.root_pane`；创建 tab 返回 `result.tab`、`result.root_pane`；split 返回 `result.pane`。
2. 默认在当前 tab、当前实际目录创建兄弟窗格，用 `--no-focus`；按几何形状选择 right 或 down。只有任务要求不同拓扑或位置时创建 workspace、tab、worktree。
3. 普通命令用 `pane run`，Agent 提示用 `agent prompt`。先确认前台是目标 shell 或 Agent，不能向不明编辑器、审批框或其他任务注入命令。
4. 显式限制等待时间，交互工具单次建议不超过 60000 毫秒，长任务分轮检查。`pane wait-output` 会匹配旧输出，使用本次独有标记。
5. `pane run` 成功只表示输入入队，`agent prompt` 成功也不等于任务完成。等待后读取结果，验证文件、测试或产物。`idle` / `done` 不证明业务验收通过，`unknown` 不证明成功。
6. 超时、连接断开或 `agent_prompt_stalled` 后先检查现场，不能直接重发 mutation。适配层 outcome=committed/unknown 时禁止自动重试；PLAN_MISMATCH 且 not_started 可重新预演。没有 exactly-once 或事务回滚保证。Agent 等待是生命周期等待，已 working 的 Agent 完成旧轮次也可能满足等待。
7. `blocked` 时读取具体问题，按已有明确授权处理常规选项；需要新权限或产品决定时交给用户，不盲发 Enter，不自动取消限制。
8. 只清理本次创建且已完成的对象。关闭现有对象、停止服务器、强制删除脏 worktree、切更新通道等必须属于用户授权。`workspace close --group` 会连带关闭关联 worktree，不能作为通用重试。
9. 不为修复兼容性擅自停止主服务器；停止会结束窗格进程。`--trust-repository` 仅用于已独立验证的仓库。
10. 默认只读最近 80～120 行，需要时扩大；避免无关窗格和完整敏感日志。凭据不写入 Skill 或报告。
11. 移动窗格后改用 `result.move_result.pane.pane_id`；旧 ID 不能作为通用目标继续使用。

## 完成与反馈

完整源码、测试与构建工具都在本技能目录内，参见 [维护入口](README.md)。`tests/test_adapter.py` 默认使用隔离假后端；真实布局验证用 `tests/e2e.py --run`，只有显式加 `--agent` 才启动模型。不要依赖server-manager中的旧任务路径或历史ID。

报告目标机器/会话、实际对象、执行证据和未验证部分。对长任务报告 working / blocked 状态，不把“已提交”报告成“已完成”。升级后先检查 `herdr status`、命令帮助与 schema，再按来源说明刷新文档。
