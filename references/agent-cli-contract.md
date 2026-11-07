# Herdr Agent 适配入口 1.0.1

## 入口与定位

`python scripts/herdr_agent.py RESOURCE ACTION [OPTIONS]`（先定位到本 Skill 的绝对目录）。要求 Python 3.10+、官方 Herdr TUI 0.9.5；运行中业务操作要求 HERDR_ENV=1。只声明 Windows 原生实测。

入口复用官方 CLI，不需要安装另一个 Herdr 服务、配置新账号或改 PATH。与原生 `herdr` 区分命名。完整官方能力仍使用其对应参考页；不能把适配层 schema 当作完整 Herdr socket schema。

```powershell
$cli = (Resolve-Path './scripts/herdr_agent.py').Path # 在本 Skill 根目录执行
python $cli version
python $cli schema
python $cli errors
python $cli doctor
python $cli workspace list --limit 10 --fields workspace_id,label
python $cli workspace create --help
```

version/schema/errors 是本地静态发现，不连接会话。doctor 是本机会话诊断，不读取账号密钥。不要把 --json、--machine 等官方参数直接附在适配命令后面。

## 输入与目标

业务字段使用 `--input JSON` 或 `--file UTF-8路径`，`--file -` 显式读取 stdin。两者互斥；未知字段报错；最大 64 KiB。PowerShell 传复杂 JSON 时优先文件或 stdin，避免原生命令参数引号被 shell 移除。

```powershell
@{ target = '实际Agent名称'; lines = 80 } | ConvertTo-Json | python $cli agent read --file -
```

适配层不允许 --machine/--session/socket 覆盖，始终使用调用者继承的本地受管会话；跨机器按 remote-machines.md 使用官方 CLI。JSON 中以 - 开头的 operand、ANSI/双向控制符、无效 ID 均拒绝，不能用 -- 使非法业务字段变合法。CLI -- 终止选项解析，但业务 operands 仍在 JSON 中。
无任意 shell、raw argv、pane run、按键注入或 Agent 原生权限参数入口；需要这些官方能力时按原生操作页，不能把 shell 脚本塞到适配层冒充普通提示。

## 写入预演与提交

写命令默认 dry-run。预演执行参数验证和实际目标查询，只跳过变更；检查通过才返回 plan_hash。提交重新执行同一规划路径，绑定完整参数、绝对 binary/文件 hash、actor、cwd、环境摘要、socket/session、目标身份、timeout 和有效期窗口。
有效期到当前 5 分钟窗口结束，临近边界可能短于 5 分钟；过期需重新预演。hash 是一致性校验，不是身份令牌或 OS 沙箱。

```powershell
$request = Join-Path $env:TEMP 'herdr-workspace-request.json'
@{ cwd = (Get-Location).Path; label = '我的测试工作区' } |
  ConvertTo-Json | Set-Content -LiteralPath $request -Encoding UTF8
$plan = python $cli workspace create --file $request --dry-run | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw $plan.error.message }
# 在已有任务授权内核对 plan.target、effect、cwd 和有效期，再执行：
python $cli workspace create --file $request --commit --confirm $plan.data.plan_hash
```

已获得用户授权的 Agent 可自动执行“预演→核对→提交”，无需对每个可逆操作再问用户。--commit 不代表业务授权，可用范围仍由用户原任务限定。
不提供服务器幂等键、不记录 prompt 明文、不自动重试；重复提交 create/prompt 可重复生效。超时或 committed/unknown 错误先查询，不复用旧计划重发。适配入口拒绝关闭其继承的调用者 workspace/tab/pane；关闭这些对象需另走明确授权的官方流程。前置查询与写入之间不是服务器事务，执行后仍需核对。

## 业务接口

| 操作 | 必填 JSON 字段 | 可选字段 | 效果与验收 |
|---|---|---|---|
| workspace list/get | get: id | 无 | 只读列表/精确对象 |
| workspace create | cwd, label | 无 | 创建并 get 核对 ID |
| workspace rename/close | id, label（rename） | 无 | 改名/关闭，close 后 list 确认消失 |
| tab list/get | get: id | list: workspace | 查询 |
| tab create | workspace, cwd, label | 无 | 创建并 get 核对 ID |
| tab rename/close | id, label（rename） | 无 | 改名/关闭；最后 tab 可能关闭 workspace |
| pane list/get/current/layout/process-info | get/layout/process-info: id | list: workspace | current 固定调用者 --current |
| pane split | id, direction, cwd | 无 | direction=right/down，返回新 ID 后 get |
| pane rename/close | id, label（rename） | 无 | 明确目标修改/关闭 |
| pane read | target（pane_id） | source, lines | 有界文本快照 |
| agent list/get | get: target | 无 | 目标是 live name/pane_id |
| agent start | name, kind, pane | 无 | kind=codex/claude；验证预期种类和交互就绪 |
| agent rename | target, name | 无 | 设置实时名称，accepted 不等于二次验证 |
| agent prompt | target, text | 无 | 仅闲置且可输入 Agent；返回 submitted/task_complete=false |
| agent wait | target | 无 | 有界生命周期等待，不能解释为任务成功 |
| agent read | target | source, lines | 读实际回答，必须区分提示回显和 Agent 回复 |

完整字段类型/枚举/约束由 `schema` 中同一执行注册表生成。source=visible/recent/recent-unwrapped/detection；lines 默认 80、最大 500。所有布局 create/split 使用 --no-focus。rename 后get核对实际名称，成功返回renamed/confirmed=true。公开ID是句柄，实际可包含字母（如wA、wA:p1），不能只按十进制数字校验。

## 机器输出与分页

默认 stdout 恰好一个 JSON；--output jsonl 仍是一行终结 envelope，没有流式片段或进度。--quiet 保留终结结果，--no-input/--no-color 总是强制生效。帮助是明确请求时的普通文本。
成功 `{schema_version:"1.0",ok:true,type:"result",data,meta}`，错误 `ok:false,type:"error",error:{code,message,retryable,outcome,details,next_actions},meta`。next_actions 中 argv 是可执行的查询/发现建议，不会自动运行。

list 默认 limit=20、最大100，offset>=0；pagination 返回 total、returned、truncated、next_offset。后端取完整列表再本地切片，不是服务器分页；列表变化时不保证跨调用的 snapshot 一致性。每个后端 stdout/stderr 最大1MiB，超限失败，不把截断 JSON 当结果。
--fields 为已返回对象的顶层字段，始终保留已有的 workspace_id/tab_id/pane_id/name，不能按任意 jq 执行代码。空列表无法推断动态字段集合，schema 声明字段发现机制；非空列表无效字段报错。
read 最多保留 64000 字符，truncated=true 明确标注；不截断序列化 JSON。终端 ANSI/控制符和常见 secret 模式脱敏；任意自由文本中的未知秘密无法保证识别，读屏仍需按任务缩小范围。

## 错误与恢复

| Exit | 常见 code | 行动 |
|---|---|---|
| 0 | result | 检查 verification，不仅看 exit |
| 2 | INVALID_INPUT | schema/help 修正字段/类型/范围 |
| 3 | OUTSIDE_HERDR / DEPENDENCY_MISSING / INCOMPATIBLE_VERSION / RESOURCE_NOT_FOUND | 修复受管环境/安装/版本/目标；不自动重启服务器 |
| 4 | TIMEOUT / BACKEND_UNAVAILABLE | 查询实际状态，再决定后续 |
| 5 | STATE_CONFLICT / PLAN_MISMATCH | 读取现场或重新预演 |
| 1 | BACKEND_ERROR / BACKEND_PROTOCOL / OUTPUT_LIMIT / INTERNAL | 停止盲重试，查看结构化详情 |
| 130 | INTERRUPTED | 停止并核对可能已经提交的写操作 |

已 dispatch 写入的 timeout、取消或输出超限标 outcome=unknown、retryable=false；后置验证失败标 committed/unknown。官方未识别 error.code 保留 backend_code 和归类 BACKEND_ERROR，不通过本地化 message 猜“可重试”。BACKEND_UNAVAILABLE 保留给可明确识别连接故障，未识别故障不会伪造分类。
没有 OAuth/login 命令；Agent 自身鉴权、首次信任或审批界面通过 Herdr read 查看，需要人工决策时停止。不自动代登录或自动批准。无效业务参数在连接后端前拒绝；stdin交互终端拒绝、未结束的重定向管道受timeout限制。

## 限制

不新增沙箱；既有 Herdr/Agent 保持其自身权限、网络和文件访问。超时仅终止本次 CLI 子进程，已启动的 Agent 或命令可能继续。无远端适配、长期订阅、独立二进制、后台 job store、事务回滚、exactly-once 保证。其他官方领域由 Skill 原生路由完整覆盖，不将其标成适配层已实现。
