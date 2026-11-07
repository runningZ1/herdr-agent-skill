# Herdr Agent 工具重设计

## 目标与边界

用户：在 Windows Herdr TUI 内运行的 AI Agent，兼顾人工诊断。复用官方 herdr.exe 0.9.5 / protocol 22，本地受管进程通过官方 CLI 访问本地会话；不替代 Herdr TUI、不混用 Herdr App/hc、不实现新的凭据库或后台服务器。

交付一套技能：中文自然语言入口、官方 Skill 原文、官方功能全景、可执行轻量适配 CLI、机器契约、操作预演、测试与分发。适配层采用本机已有 Python 3.10+ 标准库，避免新增第三方依赖；本次仅声明 Windows 实测。入口为技能内 scripts/herdr_agent.py，不修改系统 PATH、不抢占官方 herdr 命令。

## 业务来源

https://herdr.dev/zh-cn/tui/docs/cli-reference/ 与 agent-automation/：workspace/tab 创建返回实际 ID；agent start 需要已有空闲 shell；prompt 成功不保证完成；read 获取文本。其余领域见技能 references 中的官方专题来源。以本机 CLI 帮助/schema 为语法基线。

## 首批闭环

1. 列出 workspace、限定返回数量和投影；成功证据为结构化记录及分页元数据。
2. workspace/tab 创建预演→计划哈希提交→get 验证；关闭仅明确目标并核对关闭后不存在。
3. 在指定 pane 启动 Codex/Claude→向就绪 Agent 发送不同提示→有界 wait/read；分别区分启动就绪、输入已提交、生命周期稳定、实际回复。

历史真实验证：w6 的创建/关闭，以及 w7 内两种 Agent 的消息/回答。重设计后须单独验证新适配入口，不能用旧测试替代。

## 交付契约

| 项目 | 决策 |
|---|---|
| 后端 | 固定解析的绝对 herdr.exe；argv 数组、shell=False |
| 认证 | 继承官方受管会话上下文，不读取 SSH/Agent 凭据 |
| 作用域 | 适配入口只操作继承的本地 socket；跨机器与其他会话使用官方 Skill 专页，不在 v1 混入隐式目标 |
| 副作用 | 查询、布局创建/改名/关闭、Agent 启动/提示；无任意 shell/plugin 执行入口 |
| 输入 | 显式 JSON --input 或 UTF-8 --file（- 为 stdin），冲突拒绝，未知字段拒绝 |
| 输出 | stdout 恰好一个版本化 JSON/JSONL 终结 envelope；诊断不混入 |
| 数据规模 | list 默认 20 最大 100，offset 本地分页、标明非服务器分页；read 默认 80 最大 500 行/受字节上限约束 |
| 长任务 | wait 最大 60 秒；prompt 提交后返回 get/read 下一步，不承诺逐轮完成 |
| 写入 | 默认 dry-run；显式 --commit --confirm PLAN_HASH；绑定参数、binary、actor、socket、cwd、环境摘要和目标快照 |
| 重试 | 不自动重试任何写入；超时返回 outcome unknown 与查询建议 |
| 兼容 | 官方命令/输出不改动；新入口单独 schema_version=1.0 / tool_version=1.0.0 |
| 执行风险 | 目标文本由固定 argv 传递；拒绝选项注入、控制符；不支持 pane run、send-keys、权限旁路参数 |

## 全功能覆盖策略

不是把 102 个 socket 方法标成 102 个已实现命令。技能文档覆盖全部官方领域；适配 CLI 精选 workspace/tab/pane/agent 和版本/诊断/发现。远程、worktree、插件、集成、配置、恢复、原始订阅均路由到官方接口，按实际授权操作并在覆盖矩阵注明 native/未实测。

## 验收

发现性、机器输出纯净、参数类型/来源、界限分页、投影、退出码、受管环境门槛、预演零变更、计划变更拒绝、真实 create/get/close、错误与超时/输出洪泛测试。对适配程序失败路径使用受控假后端测试，对业务闭环使用真实 herdr。测试不能停止当前 Herdr server 或改用户现存工作区。保留已有 w7，另建本轮专用对象并清理。
