# 来源、验证与维护（2.0.0）

## 封装原则

官方快照按产品分开：`references/official-skill.md` 来自 TUI `herdr --skill`，`references/official-core-skill.md` 来自 `hc --skill`，`references/official-app-skill.md` 来自 `herdr-app --skill`，不把本地增强改写成官方正文。精选 TUI 适配为 scripts/herdr_agent.py，全量 TUI API 为 scripts/herdr_api.py；Core 与 App 使用原生 CLI，不新增 wrapper。Python 辅助工具使用标准库，版本 2.0.0。
本项目新增代码和文档采用 MIT，见根目录 LICENSE。TUI/Core 上游公开项目采用 Apache-2.0，原协议保留在 LICENSES/Apache-2.0.txt；App CLI 资料保留上游归属，不推定采用相同许可。具体文件来源见 THIRD_PARTY_NOTICES.md。本地新增说明不代表上游官方发布。

## 官方资料与事实优先级

- [CLI 参考](https://herdr.dev/zh-cn/tui/docs/cli-reference/)
- [官方 Skill 与安装](https://herdr.dev/zh-cn/tui/docs/agent-skill/)
- [版本对应上游 Skill](https://github.com/herdrdev/herdr/blob/v0.9.5/skills/herdr/SKILL.md)
- [Socket API](https://herdr.dev/zh-cn/tui/docs/socket-api/)
- [Agent 自动化](https://herdr.dev/zh-cn/tui/docs/agent-automation/)
- [Windows 支持](https://herdr.dev/zh-cn/tui/docs/windows-beta/)
- [插件](https://herdr.dev/zh-cn/tui/docs/plugins/)
- [配置参考](https://herdr.dev/zh-cn/tui/docs/config-reference/)
- [会话状态与恢复](https://herdr.dev/zh-cn/tui/docs/session-state/)
- [故障排除](https://herdr.dev/zh-cn/tui/docs/troubleshooting/)

官网中文说明可能由 LLM 翻译；遇歧义先确认具体产品、当前 CLI/生成类型/schema 及版本对应原文。TUI `herdr` 与 Core `hc` 不共享机器或 Agent；App 是 Core 的窗口客户端。HC_TERMINAL_ID 优先表明 Core；HERDR_ENV 仅是 TUI 上下文，污染时只清理将启动的子进程，不以此阻止 Core/App，不重启用户 Core。

2.0.0 静态来源包括 `hc --help` / `--skill` / `schema`，`herdr-app --help` / `--skill` / `commands`，以及当前 TUI integration install / agent rename 帮助。Core schema 有 32 方法，App commands 有 71 内置命令，TUI integration install 有 18 TARGET；数量是快照而非实测数。原始结构见 sources/core-api.schema.json、sources/app-commands.json、sources/herdr-api.schema.json。

App 维护先发现 `$HERDR_APP_HOME`（默认 ~/.config/herdr-app）中的 generated AGENTS.md、herdr.d.ts、gpui-kit.d.ts；本轮阅读生成指南相关章节与 API 注释，不修改这些文件。完整定制步骤见 [App 指南](app.md)。本轮文档分工没有启动 App/Core、运行用户任务、读取会话正文或凭据，也没有运行测试/构建/视觉检查。

## 历史 TUI 验证基线（非 2.0.0 复跑）

以下为 2026-11-06 工作区记录，反映当时 Herdr client/server 0.9.5、stable、protocol 22 和 HERDR_ENV=1，不代表当前现场状态。

只读校验：版本、status、config check、当前 pane、命令组帮助、完整 API schema 导出；schema 自动提取 102 个 request 方法。doctor 在受管环境返回成功，并检查非受管环境跳过运行中会话访问。

用户授权的三个实际测试：

| 测试 | 返回与验收 |
|---|---|
| 新建工作区 | 创建中文标签“Herdr Skill 验证”，返回 w6；workspace get 确认存在 |
| 新建标签页 | 在 w6 新建“Agent 启动验证”，返回 w6:t2、根窗格 w6:p2；tab get 确认 |
| 启动智能体 | 在 w6:p2 使用 agent start 启动 codex，实际 get 返回 idle、interactive_ready=true |

测试使用 --no-focus，没有给测试 Agent 提交开发任务。测试对象在验证后关闭，操作记录只保存在任务目录，不随技能分发。
这些 ID 是本次证据，不能在以后操作时复用。

第二轮实际测试：再次 list 确认旧工作区 w6 已删除，新建工作区 w7，分别在 w7:p1 和 w7:p2 启动 Codex 与 Claude。分别发送无工具、无文件操作的算术与翻译问题，读取实际回答 `CODEX_REPLY: 42` 和 `CLAUDE_REPLY: Test successful`。Claude 使用 prompt --wait 等到 done 后读到回答；Codex 使用不带 wait 的 prompt，再重复读取直到观察到真实回答，证明即时 settled 状态不能代替消息完成验收。Claude 首次启动要求确认导入本次用户提供的项目 AGENTS.md，确认后就绪。本轮工作区保留供用户查看。

未实测：辅助 Agent 的实际开发任务、远程 SSH 设置/转发、worktree 创建/强制删除、集成安装、插件安装/构建、原始 socket 客户端、长期事件订阅、服务器停止/升级/恢复。对应说明来源于官方文档和本机帮助，不宣称全部端到端验证。

## 历史第三轮：精选适配 CLI 验证

新增入口提供统一 envelope、结构化发现、有限列表与投影、JSON 文件/stdin、目标校验、写入预演/计划哈希提交及分层错误。契约测试包括输出纯净、未知参数、精确 ID、文件来源、受管环境、红队输入、脱敏、超时/洪泛、错误映射与计划过期；异常注入测试不等于真实网络/认证故障验证。

真实新入口验收：workspace create dry-run 前后总数一致；修改 label 后复用 hash 被拒绝且 outcome=not_started；创建 w9 和 tab，启动 Claude、发送无工具算术提示，读取实际 `ADAPTER_REPLY: 63`；关闭 w9 后 list 核对消失。首次 shell 初始化时 cwd 更新导致预演 hash 失效，重新查询/预演后提交成功，没有重发已执行的写操作。早期失败的 w8 同样已清理；保留第二轮 w7。

测试源码、工具、设计及原始证据现已全部迁入本技能目录，参见根目录README.md。分发包包含tests/tools源码，development内的本机证据与历史源码不分发。server-manager仅保留progress.md任务记录。新适配入口仅测试Windows/Python3.12/herdr0.9.5。现有Agent的任意业务开发、远程和高级原生功能仍按上方未验证范围报告。

## 历史源码审查与当前边界

旧审查记录适配入口 1.0.1、28 项默认契约测试、真实字母 ID 工作区与旧分发包验证，详见 development/源码审查.md。这些数字是历史结果，2.0.0 新脚本、原生路由和分发包需要由主线程按实际运行结果单独报告。

HERDR_ENV 规则仅用于 TUI；Core/App 的静态发现与原生操作不受该门槛。hc server status 不启动 Core，但 hc machine ls 等查询可能按需启动；不要在污染的 TUI 父进程下将其当作首次无副作用探测。清理继承环境只作用于当前子进程，不使用 allow_nested，不重启用户服务。

安装技能或加载本说明不会自动执行插件、远程安装、配置或 mod 修改。维护快照不采集 session.json、window/view/shared 状态、对话、日志、机器凭据或遥测文件；generated 指南/类型仅按必要章节阅读，不打包用户 home。

## 更新维护

1. 分别读取 herdr / hc / herdr-app 版本及静态帮助；需要运行状态时 TUI 用 status，Core 先 server status，App 有运行窗口才 ls/status，不为采集启动或重启用户产品。
2. 分别导出三个 --skill，比较后更新对应 official 快照，保持官方正文；版本、来源、上游许可和本地增强边界一起维护。
3. 采集 TUI api schema、Core schema、App commands，与中文目录和覆盖矩阵逐项核对；TUI subscriptions 与 match_event 分别归属 events.subscribe / events.wait，不编造通用过滤参数。
4. 对照当前 integration install 帮助更新 TARGET，区分 agent kind/平台可安装性。App 定制阅读 home 下生成说明与类型，绝不编辑生成文件；mod 复制与 check/status/shot 流程见 app.md。
5. 修改全部落地后由主线程执行任务要求的检查，分别记录 fixture、静态采集、真实业务与视觉结果。只有实际授权和执行后才记为通过；维护不扩大到停服、集成安装、真实模型任务。
6. 构建前检查分发白名单、链接、官方快照与 schema；排除用户日志、会话数据、凭据、缓存与本机测试证据，不能把 sources/current 中用户数据一起打包。

旧 TUI 官方正文曾记录 UTF-8 LF SHA-256 `fbd9d502767f7dff29c211505a0bd9ba34e980ed4cc456247e2adc1642883984`；它仅是历史快照指纹，不能作为三个产品新快照的一致性证明。

## 2.0.0 本轮执行证据

本轮在 Windows / Python 3.12 实际执行 TUI 只读 validate：官方 Skill 匹配、doctor、配置与有界工作区列表通过，公开目录核对为 TUI 102 / Core 32 / App 71。Core/App 新增路由以静态官方资料和生成指南为证，没有逐项执行或 App 视觉验收。

新原始客户端已通过真实 Windows named pipe 调用 ping；在专用无焦点测试工作区执行预演/hash 提交、create/rename/get、顺序 batch 和 layout.export，随后 close 并 list 确认消失。订阅初始确认后按 2 秒期限正常返回，未将无事件的 timeout 冒充事件投递证明。一次性验收脚本已删除；未启动付费 Agent、停止服务器或操作用户原有工作区。

官方 TUI 0.9.5 服务端每个连接只处理一个请求，源码依据为 src/api/server.rs 的 handle_connection_with_stop。客户端因此逐请求建立连接，Unix SSH Agent 登记单独保留租约；不提供不受服务器支持的同连接普通请求序列。Windows 现场能力明确 ssh_agent_registration=false，未宣称在 Windows 实测 Unix 租约。

自动命名的空 cwd、部分成功、rename/确认查询超时、人工改名、敏感状态、总期限与持久化失败使用隔离回归，不改用户标签。发布构建使用 tools/build.py --verify 执行解包后的全部离线 test_*.py；完整通过与包指纹以本次构建输出为准，不能将历史测试数字套到新版本。
