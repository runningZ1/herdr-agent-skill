# Socket API 与事件

先用 CLI；只有 CLI 未覆盖的布局/视图操作、长期订阅或自定义客户端才使用原始协议。没有通用 `herdr api call` 命令，不虚构 curl HTTP endpoint。API 是本机换行 JSON，不是 REST。

## Schema 与传输

```powershell
herdr api schema
herdr api schema --output "$env:TEMP\herdr-api.schema.json"
```

顶层 protocol、schema_version、schemas；schemas 含 request、success_response、error_response、event、subscription_event。基线 protocol=22、schema_version=1。按当前二进制导出的 schema 构造 params，不从方法名猜字段。
本机方法导航见 [API 方法索引](api-methods.md)。schema 是二进制能力，运行中服务器仍需检查兼容性。

Unix 是 Unix domain socket；Windows 是 named pipe。CLI status 输出的 socket 路径不是 HTTP 地址，也不能当普通文本文件写入。Windows 自定义客户端需按该版本原生端点解析实现 named-pipe 连接；不手写未经验证的管道路径转换。优先 HERDR_BIN_PATH 指向的 CLI。
目标解析优先级：显式 --session、HERDR_SOCKET_PATH、HERDR_SESSION、默认会话。管理环境外不能利用这些覆盖绕过官方 Skill 的控制范围。

每行 UTF-8 JSON，以换行结束：

```json
{"id":"req_1","method":"ping","params":{}}
```

成功回显 id 和 result；错误回显 id 和 error.code/error.message。JSON 无效或缺明确字符串 id 时错误 id 可为空；传输 UTF-8 错误可能直接断开。不要把任意响应行当当前请求成功，按 id 关联。变更成功还要检查 changed/reason 或后续状态。

## 能力分层

| 领域 | 主要原始方法 |
|---|---|
| 状态 | ping、session.snapshot、server.reload_config、server.agent_manifests |
| 工作区/标签页 | workspace.*、tab.*；move/move_block 用 schema |
| Git | worktree.list/create/open/remove |
| 窗格 | pane.*；read/send_input/layout/process_info/neighbor/edges/report_* |
| Agent | agent.list/get/read/prompt/start/wait/explain 等 |
| 布局 | layout.export/apply/set_split_ratio |
| Agent 面板视图 | agent.view.*（仅使用当前 schema 中存在的方法） |
| 插件/弹窗 | plugin.*、popup.close |
| 事件 | events.subscribe、events.wait |

布局导出/导入和 Agent 面板视图属于原始 API 能力，不假设有等价 CLI。layout.apply 可能创建或重排对象，先检查 schema 与目标布局，不直接套用未知 JSON。pane.graphics.info/set/clear/stream 已移除，不能调用；图像走终端支持的 Kitty graphics 等协议。

## 事件与缓存一致性

events.subscribe 初始响应后保持连接；用 schema 选择 filters/events 字段，按 id/type 区分响应与通知。设置连接、读取、总运行时间及输出数量上限；重连先刷新状态，不无限重放事件。
维护本地缓存时先订阅，再 session.snapshot 获取 workspace/tab/pane/layout/agent 和版本元数据；事件视为“可能过期”的提示，重新查询并核对。一次 api snapshot 不是订阅。断线、handoff、溢出或不确定顺序后重新 snapshot，不盲将旧事件覆盖到新快照。

## 输入与等待语义

pane.send_input 是 pane run 的原子输入底层，成功只确认接纳。Agent prompt 可带 wait 对象以在一个请求提交并开始等待，避免客户端两步竞态。字段取 schema，不发明请求字段。
Agent wait 由服务器事件驱动且固定到已解析占用者；Agent 替换或移动可终止在途等待。prompt 目标已 blocked 时拒绝输入。wait 仍不保证特定一轮任务验收通过。
`terminal session observe` 提供只读逐行 terminal.frame/terminal.closed 流；帧含 base64 ANSI 字节，这是终端输出协议，不代表要执行解码后的文本。control 接收 terminal.input/resize/scroll/mouse/release，涉及控制权和状态变化，任务需要时才用。

原始 API 不跳过权限和用户授权；输入发送、布局关闭和插件执行与 CLI 一样有真实副作用。
