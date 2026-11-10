# TUI Socket API 与事件（2.0.0）

优先使用官方 CLI 和精选适配器；需要其未覆盖的方法、顺序批次、SSH Agent 租约或事件时，使用随包的 `scripts/herdr_api.py`。它提供真实 Unix domain socket / Windows named-pipe 传输，不是 HTTP 或 REST，也不虚构 `herdr api call`。

## 发现完整参数

```powershell
python -B scripts/herdr_api.py schema
python -B scripts/herdr_api.py schema --method layout.apply
herdr api schema --json
```

完整公开 schema 为 `sources/herdr-api.schema.json`，包含 request、success_response、error_response、event、subscription_event。当前 protocol=22、schema_version=1、102 个方法；索引见 [api-methods.md](api-methods.md)。`schema --method` 返回选定请求及其引用定义，字段意义和默认值以 schema 为准。

普通 `herdr api schema` 只输出摘要，不是完整 JSON。升级时先刷新快照和审阅兼容性；不能因为有新方法名称就猜参数。

## 单次调用与预演

脚本路径以实际技能目录为准，下面在技能根目录执行：

```powershell
python -B scripts/herdr_api.py call ping
@{ pane_id = $env:HERDR_PANE_ID } | ConvertTo-Json |
  python -B scripts/herdr_api.py call pane.get --file -
```

运行操作要求真实 TUI 管理上下文、HERDR_ENV=1 和继承的 HERDR_SOCKET_PATH。带有 HC_TERMINAL_ID 时拒绝操作，避免把 Core 中继承的 TUI 标记当成真实目标。客户端不提供任意端点/会话/机器覆盖，不猜其他会话。远程 TUI 可在目标机器的真实 TUI 窗格执行同一脚本；官方支持的远程命令按 [机器指南](remote-machines.md) 使用 `herdr --machine`。

只读方法直接执行；其他所有 schema 方法均保守按写入处理，默认仅输出预演。写请求：

```powershell
$request = Join-Path $env:TEMP 'herdr-rename-request.json'
# tab_id 必须来自本次发现，不复用示例 ID。
@{ tab_id = $actualTabId; label = '构建结果' } |
  ConvertTo-Json | Set-Content -LiteralPath $request -Encoding UTF8
$plan = python -B scripts/herdr_api.py call tab.rename --file $request | ConvertFrom-Json
if (-not $plan.ok) { throw $plan.error.message }
# 在已有任务授权内核对 endpoint、requests 和 effect。
python -B scripts/herdr_api.py call tab.rename --file $request --commit --confirm $plan.data.plan_hash
```

预演只核对方法名、params 对象与输入大小；**不连接服务器、不解析业务目标、不执行完整 JSON Schema 验证**。服务器在执行时检查具体参数。若需要实时目标校验和调用者关闭保护，优先使用精选 `herdr_agent.py`；不要将其保证套到原始客户端。

hash 绑定完整请求序列、继承端点、调用者上下文、脚本与 schema 指纹、timeout/max-events 和当前 5 分钟窗口。输入或窗口改变须重新预演。它不是授权、幂等键或事务；同一个计划重复提交仍可能重复生效。

实际连接先发送 ping 核对服务器协议，再发送请求；按 id 关联成功/错误，不将通知误当响应。Windows 按 Herdr v0.9.5 `src/ipc.rs` 的 GenericNamespaced 规则在实际继承地址前添加 `\\.\pipe\`，不读写 `.sock` 标记文件。阻塞连接/读写在独立子进程中执行，父进程落实整个传输期限。

## 顺序批次与连接租约

`batch --file PATH` 读取 1～32 项请求数组，每项仅含 method 和 params；按官方服务器的一连接一请求模型逐项新建连接、发送并确认，第一项服务器错误即停止后续请求。只要有写方法，整组默认预演并需要 hash 提交。

```json
[
  {"method":"ping","params":{}},
  {"method":"layout.export","params":{"pane_id":"从本次发现取得的真实pane_id"}}
]
```

```powershell
python -B scripts/herdr_api.py batch --file ./requests.json --timeout 15
```

`server.ssh_agent.register` 只在 Unix 且服务器支持相应能力时可用；登记持续到它的专用连接关闭。batch 保留该连接，同时让后续请求各自使用新连接，不向租约连接发送第二个请求。包含登记且没有订阅的批次在所有请求确认后保留租约到本次 timeout；若需要事件采集，把 events.subscribe 放在最后，此时租约随事件上限/期限释放。单次 call 登记也只保留到本次 timeout，不能报告为后台永久登记。超过 60 秒的租约交给官方 SSH 工作流或经明确管理的原生客户端，不能靠重复登记伪造连续性。

订阅仅允许作为 batch 最后一项；服务器在订阅连接上只推送通知，不继续处理普通请求。client-shell 等能力仍须有效客户端上下文，按 schema 查询其作用域；新连接不能制造客户端投影或不存在的命令 ID。

批次不是事务：前项已成功时，后项失败不会回滚。结束、超时或失败后连接都会关闭。失败结果保留已收到的 responses、events 与 dispatched 方法，核对现场后再决定下一步。

## 有界订阅与等待

订阅参数实际是 **subscriptions 数组**，不是 filters/events；等待事件使用 **match_event**。

```json
{"subscriptions":[{"type":"pane.created"}]}
```

```powershell
python -B scripts/herdr_api.py subscribe --file ./subscriptions.json --timeout 10 --max-events 10
```

上面的 type 须存在于当前 schema 的 Subscription 变体；先查 `schema --method events.subscribe`。`subscribe` 默认最多 20 条事件、15 秒；每次新调用都是新连接，关闭后服务端订阅结束。调用 `call events.subscribe` 默认只取得初始确认；需要采集事件时使用 subscribe 或显式 `--max-events`。

原始事件信封为 `{event,data}`，不是 `{type:"event"}`。订阅确认后达到事件数或期限即返回，reason=event_limit/deadline；期限到达但请求尚未确认则返回 TIMEOUT。客户端按 id 确认初始响应，再单独处理该连接的通知，不向订阅连接发送后续普通请求。客户端不自动重连或重放。

`events.wait` 的 match_event 结构与 Subscription 不同；按 schema 构造：

```powershell
python -B scripts/herdr_api.py schema --method events.wait
python -B scripts/herdr_api.py call events.wait --file ./wait.json --timeout 30
```

维护缓存时先订阅，再以 session.snapshot 或对象 get 获取权威状态。事件是失效提示，不能无条件覆盖快照；断线、handoff、溢出后重新读取快照。一次 api snapshot 不是订阅。

## 有界输出与失败语义

输入最大 64 KiB（UTF-8 文件或有限 stdin）；单帧最大 1 MiB、总 wire 输出 4 MiB、事件最多 100 条，传输 timeout 为 1～60 秒。不执行外部 shell，不启动后台服务，不自动重试。

stdout 为一个 `{schema_version,ok,data/error}` JSON。data 含原始 responses/events，经通用秘密和控制符清理；自由文本脱敏不能保证识别未知秘密。读屏和快照仍应缩小业务范围。

写入 dispatch 后超时、断线、输出超限或后置失败可能标记 outcome=unknown，retryable=false；已成功响应的写入可报告 committed，但不证明目标业务已经完成。中断时也先核对现场。服务器 error 会保留 backend_error 与已收到的证据，不能用退出码猜是否可以重发。

## 较少使用的方法与约束

所有方法均可经 call/session 构造真实请求；这不消除服务器能力、对象状态或客户端连接要求：

| 能力 | 方法与调用前提 |
|---|---|
| 布局导出、重建、比例 | layout.export/apply/set_split_ratio；apply 可能重建终端并关闭旧 tab，不保留活 PTY/进程 |
| Agent 面板 | agent.view.set/clear；依当前 schema 的视图数据 |
| 终端复制、选择、链接 | pane.copy_motion/copy_search/selection.read/link.activate/link.resolve；核对坐标和 content_revision，旧屏幕坐标可能失效 |
| 滚动、清屏、历史编辑 | pane.scroll/clear/edit_scrollback；清除或编辑历史按写入处理 |
| 聚焦、输入策略 | pane.focus/focus_direction/input.set；不要误用当前焦点代替调用者 |
| 生命周期权威 | pane.clear_agent_authority 与 pane.release_agent 是不同方法，按来源和 schema 执行 |
| 客户端命令 | command.invoke 的 command_id 来自 endpoint client-shell projection，不编造命令 ID |
| 客户端显示、公告 | client_shell.surface.set、client.window_title.*、product_announcement.dismiss、release_notes.dismiss；依有效客户端与当前公告状态 |
| SSH 登记、handoff | server.ssh_agent.register 连接作用域；server.live_handoff 涉及现有会话，需任务授权与兼容支持 |

Agent prompt 成功只证明接纳；wait 绑定占用者也不保证本轮任务验收。pane.graphics.* 已移除，不能调用。交互终端 observe/control 使用独立 terminal 协议和官方 CLI，不属于此 newline JSON API 的假扩展。
