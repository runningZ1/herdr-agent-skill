# 来源、验证与维护

## 封装原则

保留 `references/official-skill.md` 的官方正文，来源是本机 `herdr --skill`（TUI 0.9.5），不改动官方执行后端。SKILL.md 和中文参考为本地增强。根据 agent-cli-creator 2.1.0 新增 scripts/herdr_agent.py 统一适配入口，Python 标准库即可运行；旧 doctor.py 保持兼容。
本项目新增代码和文档采用 MIT，见根目录 LICENSE。上游资料采用 Apache-2.0，原协议保留在 LICENSES/Apache-2.0.txt，具体归属见 THIRD_PARTY_NOTICES.md；上游仓库为 herdrdev/herdr，官方 Skill 路径 skills/herdr/SKILL.md。本地新增说明不代表上游官方发布。

## 已阅读的官方资料

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

官网中文说明可能由 LLM 翻译，遇歧义以已安装 CLI、schema、对应版本原文为准。
Herdr App / herdr-core 的 `hc` 与 TUI `herdr` 不共享 Agent，不能混用操作示例。

## 本机验证基线

验证日期：2026-11-06（工作区本地日期）。Herdr client/server 均为 0.9.5，stable，protocol 22，端点兼容。当前环境 HERDR_ENV=1。

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

## 第三轮：适配 CLI 验证

新增入口提供统一 envelope、结构化发现、有限列表与投影、JSON 文件/stdin、目标校验、写入预演/计划哈希提交及分层错误。契约测试包括输出纯净、未知参数、精确 ID、文件来源、受管环境、红队输入、脱敏、超时/洪泛、错误映射与计划过期；异常注入测试不等于真实网络/认证故障验证。

真实新入口验收：workspace create dry-run 前后总数一致；修改 label 后复用 hash 被拒绝且 outcome=not_started；创建 w9 和 tab，启动 Claude、发送无工具算术提示，读取实际 `ADAPTER_REPLY: 63`；关闭 w9 后 list 核对消失。首次 shell 初始化时 cwd 更新导致预演 hash 失效，重新查询/预演后提交成功，没有重发已执行的写操作。早期失败的 w8 同样已清理；保留第二轮 w7。

测试源码、工具、设计及原始证据现已全部迁入本技能目录，参见根目录README.md。分发包包含tests/tools源码，development内的本机证据与历史源码不分发。server-manager仅保留progress.md任务记录。新适配入口仅测试Windows/Python3.12/herdr0.9.5。现有Agent的任意业务开发、远程和高级原生功能仍按上方未验证范围报告。

## 内容检查

完整源码审查已升级至适配入口1.0.1，7个活跃Python源码与维护方式见根README和development/源码审查.md。当前默认契约测试28项通过，真实字母ID工作区wB的创建/tab/split/改名/关闭通过，分发包解压后的28项测试通过。本轮没有重新启动付费模型。

已通读导出的官方 Skill，保留其 HERDR_ENV 与目标限定规则；无安装执行器、无自动凭据读取、无上传数据逻辑。doctor 只调用 --version、status、config check、pane current --current，且在受管环境外只调用 --version。安装内容不含服务器账号、SSH key、Herdr session.json 或测试对话。
插件、远程设置与配置修改属于能力说明，不会因加载 Skill 自动执行。

## 更新维护

1. 运行 herdr --version 和 status，确认本机与服务器实际版本/兼容性。
2. 在临时目录导出 herdr --skill，与 official-skill.md 比较；更新原文前保留已有副本。
3. 重新采集相关命令组 --help 和 api schema；按 schema 更新 api-methods.md。
4. 核对中文工作流、平台差异、错误码和官方文档路径，不用全局 skills add 覆盖本地增强。
5. 运行 doctor 和轻量验收；仅有授权时新建明确标记的测试对象，验证后清理。
6. 检查所有参考链接和 ZIP 内容，排除日志、会话数据、凭据和 __pycache__。

官方 Skill 原文 SHA-256（UTF-8、LF）：`fbd9d502767f7dff29c211505a0bd9ba34e980ed4cc456247e2adc1642883984`。
