# 集成、状态上报与插件

## 内置集成

```text
herdr integration status [--outdated-only]
herdr integration install KIND
herdr integration uninstall KIND
```

集成=Agent 原生状态/会话钩子，Skill=Agent 操作说明，plugin=Herdr 加载的工作流扩展；三者不能互相替代。安装集成会改 Agent 配置，先检查已有集成和任务范围。不要安装 CLI 已不支持的平台集成。
Windows 官方支持集合比可识别 kind 少：Pi、OMP、Claude、Codex、Copilot、Devin、OpenCode、Kilo、Droid、Kimi、Qoder、Antigravity。实际集合以当前 `herdr integration` 和平台返回为准。
原生恢复需要集成上报 agent_session；单纯“识别到进程”不能保证重启后恢复对话。安装后验收 integration status 以及新 Agent 的 get/list 中 agent_session。

## 检测清单

```text
herdr server agent-manifests [--json]
herdr server update-agent-manifests [--json]
herdr server reload-agent-manifests
herdr agent explain TARGET --json
herdr agent explain --file PATH --agent LABEL --json
```

先用 explain 读取匹配区域、来源、版本、warnings；本地覆盖后 reload，远程清单更新用 update。更新操作修改检测缓存，不是普通查询。CLI 更新不代表运行中 server 已支持 explain 等新方法。

## 自定义上报

report-agent 上报语义 idle/working/blocked/unknown，会影响等待、通知和聚合；release-agent 在进程结束时释放本来源生命周期权威。report-agent-session 只更新原生会话身份，不上报工作状态。恢复命令参数放 -- 后，命令必须是 PATH 上普通命令名，参数不得含撇号。

仅展示标题/进度/费用用 report-metadata，避免抢占官方状态来源。参数语法见 cli-reference.md。
source/applies-to-source <=80 字符，只允许 ASCII 字母数字及冒号、点、下划线、连字符。seq 用单调递增序号；过期上报可能 API 接受但不应用。
ttl-ms 范围 1..86400000；未指定则保持直到替换/清除/对象关闭。metadata 值规范化并截断到 80 字符。未提到的 token 保留，clear-token 删除；空白值规范化后也清除。
每个 pane/workspace 生命周期最多 32 个带序号 token 来源，清除或过期不释放名额，长期钩子复用稳定 source。

```text
herdr pane report-metadata PANE --source custom:progress --token progress=3/8 --ttl-ms 60000
herdr workspace report-metadata WORKSPACE --source custom:build --token build=passing --ttl-ms 60000
```

token 为展示数据，可能显示到 UI，不在其中写密码。agent/applies-to-source 只守卫 title/display-agent/state-label，不守卫 token patch。

## 插件完整命令

```text
herdr plugin install OWNER/REPO[/SUBDIR] [--ref REF] [--yes]
herdr plugin update [PLUGIN_ID|OWNER/REPO[/SUBDIR]...] [--yes]
herdr plugin uninstall PLUGIN_ID|OWNER/REPO[/SUBDIR]
herdr plugin link PATH [--disabled]
herdr plugin unlink PLUGIN_ID
herdr plugin list [--plugin ID] [--json]
herdr plugin enable ID
herdr plugin disable ID
herdr plugin config-dir ID
herdr plugin action list [--plugin ID]
herdr plugin action invoke ACTION_ID [--plugin ID]
herdr plugin log list [--plugin ID] [--limit N]
herdr plugin pane open --plugin ID --entrypoint ID [--placement overlay|popup|split|tab|zoomed] [--width SIZE] [--height SIZE] [--workspace ID] [--target-pane PANE] [--direction right|down] [--cwd PATH] [--env KEY=VALUE] [--focus|--no-focus]
herdr plugin pane focus PANE
herdr plugin pane close PANE
```

先审查来源 ref/commit、herdr-plugin.toml、build/actions/events/panes/link_handlers 的实际 argv、平台及依赖，再在用户授权安装范围内执行。--yes 是非交互安装开关，不能用来绕过未经审查的构建命令。
install 只接受 GitHub 简写，不接受任意 URL。无目标 update 更新全部托管插件，平时明确指定目标。
link 可指向目录或清单文件，要求 min_herdr_version 不高于运行版本。检查 link/list 的 warnings；未知事件名可以链接成功但不会按预期触发。
config-dir 可能创建目录或初始化旧配置，不属于纯只读命令。unlink/uninstall 注销并保留文件，不能承诺立即删除所有托管目录。
动作返回的日志仅证明进程启动，应继续检查 log list 与实际产物。相同 action id 用 plugin.id.action 消歧。禁用插件返回 plugin_disabled，平台不支持返回 platform_unsupported。

Windows 插件属于预览，清单声明 platforms，argv 需支持 Windows，不假设存在 sh。先在测试对象验证。popup 是会话级模态终端，通常没有 pane_id，也不参与 pane/agent API；关闭需对应 popup.close API。后台操作优先 split/tab 和 --no-focus，避免抢占用户模态界面。

插件持久登记在会话旁 plugins.json，进程外执行声明命令；插件配置/状态目录由插件自己管理，Herdr 不提供通用插件存储 API。环境提供 HERDR_BIN_PATH、HERDR_SOCKET_PATH、HERDR_PLUGIN_ROOT、HERDR_PLUGIN_CONFIG_DIR、HERDR_PLUGIN_STATE_DIR、HERDR_PLUGIN_CONTEXT_JSON 及可用 pane 上下文，调用时优先官方 binary。
