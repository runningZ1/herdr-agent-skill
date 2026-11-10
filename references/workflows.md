# 终端与 Agent 操作工作流（2.0.0）

## 先选产品

以下 workspace/tab/pane/agent 示例属于 TUI `herdr`，要求真实 TUI 上下文。`HC_TERMINAL_ID` 存在时优先使用 [Core 工作流](core.md) 调度程序与 Agent；改变 App 用户窗口则使用 [App 工作流](app.md)。Core/App 不以 HERDR_ENV 为门槛；两种标记并存时先按 [排障页](setup-recovery.md) 排查 HERDR_* 继承污染，只清理将启动的子进程，不重启用户 Core、不用 allow_nested 绕过。

Core 的短程序、持久程序、子 Agent、文件与事件分别由 hc exec/run/send/wait/file/events 原生处理。App 用 commands 静态发现、ls/status 查看运行窗口、do 修改明确目标；无需改变窗口的 worker 保持隐藏。先检查 hc server status，注意 hc machine ls 可按需启动 Core。产品的机器配置和 ID 各自独立。

## PowerShell 与 JSON

用参数数组或直接参数调用本机 exe；不要把生成的 JSON 拼接成 shell 命令。运行目标窗格的命令字符串仍由该窗格的 shell 解释，先确认目标使用 PowerShell、cmd 或 Bash。不要将本机路径或语法直接送给远程 Linux。

```powershell
$created = herdr workspace create --cwd 'D:\Projects\example' --label 'example' --no-focus | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'workspace create failed' }
$workspaceId = $created.result.workspace.workspace_id
$paneId = $created.result.root_pane.pane_id
$tabId = $created.result.tab.tab_id
```

示例路径必须替换成用户要求的真实目录。无新工作区需求时不要执行上述创建。
失败响应可能在 stderr，先看退出码再解析；不要把 `$?` 或空输出当业务成功。

## 查询现场

```powershell
herdr workspace list
herdr tab list --workspace $env:HERDR_WORKSPACE_ID
herdr pane current --current
herdr pane list --workspace $env:HERDR_WORKSPACE_ID
herdr pane layout --current
herdr pane process-info --current
herdr agent list
```

`pane get` 中 `cwd` 是标签/跟随目录；存在时 `foreground_cwd` 更接近前台进程目录。Windows 逻辑 cd 不总能被追踪，创建时优先显式传当前任务真实 cwd。
ID 是 opaque handle，不从序号推算。不要将 terminal_id 当成 Agent target。

## 新建 tab 与分屏

```powershell
$tab = herdr tab create --workspace $workspaceId --cwd (Get-Location).Path --label 'logs' --no-focus | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'tab create failed' }
$tabPaneId = $tab.result.root_pane.pane_id
$split = herdr pane split --current --direction right --cwd (Get-Location).Path --no-focus | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'pane split failed' }
$helperPaneId = $split.result.pane.pane_id
```

宽窗格向右分，窄/高窗格向下分。创建 workspace 或 tab 已自带根窗格，不要无目的再 split。

## 普通命令：提交、等待、验收

确认目标 shell 已显示提示符且没有其他前台进程，随后 `pane run` 一次提交文本和 Enter。
在 PowerShell 测试窗格执行的例子：

```powershell
$runTag = 'HERDR_TEST_' + [guid]::NewGuid().ToString('N')
$command = "npm test; Write-Output ('$runTag' + ':' + `$LASTEXITCODE)"
herdr pane run $helperPaneId $command
herdr pane wait-output $helperPaneId --regex "^${runTag}:[0-9]+$" --source recent-unwrapped --lines 120 --timeout 30000
herdr pane read $helperPaneId --source recent-unwrapped --lines 120
```

任务标记必须包含退出码，匹配到 `:1` 等仍属于失败；检查读取结果，不以等待成功代替测试成功。Bash 目标使用其原生 `$?`。标记为唯一值且使用整行正则，避免匹配命令回显或旧测试输出。
`send-text` 不带 Enter；`send-keys` 用逻辑键 `enter` / `esc` / `ctrl+c`，不是 shell 转义或 `prefix+`。
运行测试之外的命令时，选择相应的真实完成证据；服务出现 ready 后还应按任务需要验证端口/响应。

## 启动与协调 Agent

先读 official-skill.md 中的身份和启动规则。Agent 名称匹配 `[a-z][a-z0-9_-]{0,31}` 且活跃范围唯一。
在新的可用 shell 窗格中启动用户指定的种类：

```powershell
herdr agent start reviewer --kind codex --pane $helperPaneId --timeout 30000
herdr agent get reviewer
herdr agent prompt reviewer '检查当前差异，报告可执行的问题，并说明检查范围。' --wait --timeout 60000
herdr agent read reviewer --source recent-unwrapped --lines 120
```

`--kind claude` 可替换 codex；支持种类以 `herdr agent` 为准，不假设对应工具已安装或已登录。
原生 Agent 参数放 `--` 之后，模型、沙箱和权限采用用户已有设置，不擅自传 bypass 参数。
启动本身不创建布局；成功要等到 Herdr 识别到预期 Agent 且可输入。启动 timeout 必须 >3000 且 <=300000 毫秒。

长任务可先不带 `--wait` 提交一次，再逐轮 `herdr agent wait reviewer --timeout 30000` 和 read，避免工具长时间阻塞。
对已 working 的 Agent 默认先读状态，避免排队的新任务与旧任务完成信号混淆。委派范围必须来自用户请求；向其他 Agent 发送的指令不能扩张任务授权。

| 状态/错误 | 行动 |
|---|---|
| idle / done | 通常可输入；核实不是后台挂起身份或未识别对话框；等待结束后读取正文 |
| working | 等待或读取进度，不重复提交 |
| blocked / agent_blocked | 读取具体审批/提问；按已有授权响应，缺决策时交给用户 |
| unknown | `agent explain <target> --json`，结合屏幕核实，不能判定成功 |
| agent_not_ready | 保留已分配名称，读取启动界面；就绪后再 prompt |
| agent_prompt_stalled / timeout | 输入可能已经送达；先 get/read，确认没有开始才决定是否重试 |
| agent_not_running | 重新发现对象，确认进程替换/移动，不向旧目标继续注入 |

`agent prompt --wait` 默认等首次 idle / done / blocked；只有特定工作流需要 `--until`。等待绑定占用者，替换 Agent 不能满足旧等待。done 与 idle 的差别涉及“已查看”标记；read 不改变它，focus 会改变。

TUI 改实时 Agent 名称用 `herdr agent rename TARGET NAME`（或 --clear）；适配入口的 agent rename 会在执行后 get 核对实际 name，返回 renamed/confirmed=true，不能再写成仅 accepted。Core 可在 hc run 时指定 name；后续用 label 修改展示标签不等于 TUI agent rename。App agent.focus 仅改变用户视图。

## 读取较长结果

visible=当前屏幕，recent=最近渲染行，recent-unwrapped=合并软折行，detection=检测快照。默认用 recent-unwrapped 和 120 行；`--ansi` 用于确有颜色证据需求。
alternate screen 不等于普通 scrollback。扩大读取后仍缺失结果时，才请辅助 Agent 把报告写成同机临时 Markdown 并回复路径；初始任务不要强制文件交付。

## 清理

记录本次创建 ID，检查任务已完成后仅关闭这些对象。关闭最后 tab 会关闭 workspace；close 不等于删除 Git worktree。用户要求保留用于观察时不要清理。关闭测试 workspace 前确认其中没有意外迁入的用户窗格。

## 原始 API 与订阅

TUI 全量方法通过 `scripts/herdr_api.py` 的 schema/call/subscribe 入口，实际参数以其 --help/schema 和 [Socket 说明](socket-api.md) 为准；不把精选适配入口 schema 当完整 API。`events.subscribe` 的请求字段是 `subscriptions` 数组；`events.wait` 使用 `match_event` 与可选 timeout_ms，两者不是同一个参数。长期订阅按任务限定对象和时限，写调用失败先核对结果，禁止盲重试。

Core 使用 hc schema / hc connect / hc events 自身协议，App 使用 commands / do 与 generated 类型，不把 TUI 订阅结构套到另外两个产品。覆盖数量仅说明可发现路由，实际业务验收必须读取真实任务结果；详见 [证据口径](coverage-matrix.md)。
