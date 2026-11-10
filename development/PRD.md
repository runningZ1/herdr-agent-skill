# Herdr Skill 2.0.0 产品需求

## 目标与范围

面向需要操作 Herdr TUI、Core 和 App 的 Agent，提供明确产品判定、可执行接口与证据边界。复用安装的官方 herdr、hc、herdr-app，不增加后台服务、凭据库或第三方 Python 依赖，不占用官方命令名。技能版本统一 2.0.0；协议 schema_version 与产品二进制版本分别维护，不能机械同步。

## 功能契约

| 能力 | 交付 |
|---|---|
| 产品选择 | HC_TERMINAL_ID 优先识别 Core；HERDR_ENV 仅 TUI，不阻止 Core/App |
| TUI 精选操作 | scripts/herdr_agent.py；结构化结果、有界输出、写入预演与计划核对 |
| TUI 全量 API | scripts/herdr_api.py 提供 schema/call/subscribe，参数与原生 schema 对齐 |
| Core | 32 API 方法逐项列出原生 CLI/connect 路由，不新增 wrapper |
| App | 71 commands 参数/行为目录、静态发现与窗口执行边界 |
| App 定制 | home 发现、generated AGENTS.md/herdr.d.ts/gpui-kit.d.ts、个人副本与 mod 生命周期维护 |
| 远程 | TUI/Core 独立机器配置，无个人默认服务器；目标前缀贯穿实际操作 |
| 集成 | 当前 18 integration TARGET 与 agent kind/平台/状态支持分离 |
| 维护 | 静态采集、构建分发与验证分别报告；来源与上游许可保留 |

## 上下文与非目标

HERDR_* 继承污染可使 App/Core 终端误识别为 TUI。只对待启动子进程清理继承变量，保留 Core 身份，不修改持久环境、不重启用户 Core，不用 allow_nested 绕过。hc server status 不启动服务；hc machine ls 可能启动 Core。裸 herdr-app 会打开窗口，不用于发现。

不停止或重启用户服务，不安装无关 Agent 集成，不读取真实会话正文或凭据来补文档，不对缺少验证的原生能力宣称实测。Core update 计划重启保留终端，不代表 server stop/TUI stop 同样保留进程。Codex --no-daemon 来自当前 hc Skill，仅用于 Core 启动与模板。

## 验收口径

路由与运行分开：TUI 102 / Core 32 / App 71 是静态目录，不是逐项业务验证。现有 TUI 历史测试说明特定版本下的部分闭环，不能替代 2.0.0 新增功能验证。具体脚本用其 --help/schema；订阅字段是 events.subscribe 的 subscriptions 与 events.wait 的 match_event。改名成功需二次查询确认，不能仅把 accepted 当已验证。

维护验收由主线程在全部修改落地后执行；只运行任务授权检查。文档工作不运行测试、不启动 App/用户任务、不重启服务。真实运行、远程、恢复、升级和视觉效果仅在实际执行并有证据时记为通过。
