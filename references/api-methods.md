# 公开 API 与操作索引

由 `tools/collect.py --publish` 从安装的官方 CLI 静态导出，技能版本 2.0.0。

本索引逐项覆盖三份公开快照；列入索引表示已发现操作，不表示已执行或实测。参数、必填项、枚举和返回值以对应快照为准。

## TUI socket API

公开快照：[herdr-api.schema.json](../sources/herdr-api.schema.json)。协议 22；共 102 个方法。

所有方法可通过 [herdr_api.py](../scripts/herdr_api.py) 的 schema 驱动通道调用；它们不等同于 typed adapter 的便捷操作。

离线发现：`python -B scripts/herdr_api.py schema --method METHOD`。调用：`python -B scripts/herdr_api.py call METHOD --file params.json`；写调用默认仅生成 dry-run 计划，执行需 `--commit --confirm HASH`。

顺序批次使用 `batch --file requests.json`（`[{"method": "...", "params": {...}}, ...]`）；普通请求各自连接，SSH Agent 登记保留独立租约。事件订阅使用 `subscribe --file params.json`，以 timeout/max-events 限界。批量非事务，非幂等操作不自动重试。

实时通道要求真正的 TUI 上下文（`HERDR_ENV=1` 且无 `HC_TERMINAL_ID`）；Core/App 终端不能借用继承标记冒充 TUI。

- `agent.explain` → `{"$ref": "#/schemas/request/$defs/AgentTarget"}`
- `agent.focus` → `{"$ref": "#/schemas/request/$defs/AgentTarget"}`
- `agent.get` → `{"$ref": "#/schemas/request/$defs/AgentTarget"}`
- `agent.list` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `agent.prompt` → `{"$ref": "#/schemas/request/$defs/AgentPromptParams"}`
- `agent.read` → `{"$ref": "#/schemas/request/$defs/AgentReadParams"}`
- `agent.rename` → `{"$ref": "#/schemas/request/$defs/AgentRenameParams"}`
- `agent.send_keys` → `{"$ref": "#/schemas/request/$defs/AgentSendKeysParams"}`
- `agent.start` → `{"$ref": "#/schemas/request/$defs/AgentStartParams"}`
- `agent.view.clear` → `{"$ref": "#/schemas/request/$defs/AgentViewClearParams"}`
- `agent.view.set` → `{"$ref": "#/schemas/request/$defs/AgentViewSetParams"}`
- `agent.wait` → `{"$ref": "#/schemas/request/$defs/AgentWaitParams"}`
- `client.window_title.clear` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `client.window_title.set` → `{"$ref": "#/schemas/request/$defs/ClientWindowTitleSetParams"}`
- `client_shell.surface.set` → `{"$ref": "#/schemas/request/$defs/ClientShellSurfaceSetParams"}`
- `command.invoke` → `{"$ref": "#/schemas/request/$defs/CommandInvokeParams"}`
- `events.subscribe` → `{"$ref": "#/schemas/request/$defs/EventsSubscribeParams"}`
- `events.wait` → `{"$ref": "#/schemas/request/$defs/EventsWaitParams"}`
- `integration.install` → `{"$ref": "#/schemas/request/$defs/IntegrationInstallParams"}`
- `integration.list` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `integration.uninstall` → `{"$ref": "#/schemas/request/$defs/IntegrationUninstallParams"}`
- `layout.apply` → `{"$ref": "#/schemas/request/$defs/LayoutApplyParams"}`
- `layout.export` → `{"$ref": "#/schemas/request/$defs/LayoutExportParams"}`
- `layout.set_split_ratio` → `{"$ref": "#/schemas/request/$defs/LayoutSetSplitRatioParams"}`
- `notification.show` → `{"$ref": "#/schemas/request/$defs/NotificationShowParams"}`
- `pane.clear` → `{"$ref": "#/schemas/request/$defs/PaneTarget"}`
- `pane.clear_agent_authority` → `{"$ref": "#/schemas/request/$defs/PaneClearAgentAuthorityParams"}`
- `pane.close` → `{"$ref": "#/schemas/request/$defs/PaneTarget"}`
- `pane.copy_motion` → `{"$ref": "#/schemas/request/$defs/PaneCopyMotionParams"}`
- `pane.copy_search` → `{"$ref": "#/schemas/request/$defs/PaneCopySearchParams"}`
- `pane.current` → `{"$ref": "#/schemas/request/$defs/PaneCurrentParams"}`
- `pane.edges` → `{"$ref": "#/schemas/request/$defs/PaneEdgesParams"}`
- `pane.edit_scrollback` → `{"$ref": "#/schemas/request/$defs/PaneTarget"}`
- `pane.focus` → `{"$ref": "#/schemas/request/$defs/PaneTarget"}`
- `pane.focus_direction` → `{"$ref": "#/schemas/request/$defs/PaneFocusDirectionParams"}`
- `pane.get` → `{"$ref": "#/schemas/request/$defs/PaneTarget"}`
- `pane.input.set` → `{"$ref": "#/schemas/request/$defs/PaneInputSetParams"}`
- `pane.layout` → `{"$ref": "#/schemas/request/$defs/PaneLayoutParams"}`
- `pane.link.activate` → `{"$ref": "#/schemas/request/$defs/PaneLinkActivateParams"}`
- `pane.link.resolve` → `{"$ref": "#/schemas/request/$defs/PaneLinkActivateParams"}`
- `pane.list` → `{"$ref": "#/schemas/request/$defs/PaneListParams"}`
- `pane.move` → `{"$ref": "#/schemas/request/$defs/PaneMoveParams"}`
- `pane.neighbor` → `{"$ref": "#/schemas/request/$defs/PaneNeighborParams"}`
- `pane.process_info` → `{"$ref": "#/schemas/request/$defs/PaneProcessInfoParams"}`
- `pane.read` → `{"$ref": "#/schemas/request/$defs/PaneReadParams"}`
- `pane.release_agent` → `{"$ref": "#/schemas/request/$defs/PaneReleaseAgentParams"}`
- `pane.rename` → `{"$ref": "#/schemas/request/$defs/PaneRenameParams"}`
- `pane.report_agent` → `{"$ref": "#/schemas/request/$defs/PaneReportAgentParams"}`
- `pane.report_agent_session` → `{"$ref": "#/schemas/request/$defs/PaneReportAgentSessionParams"}`
- `pane.report_metadata` → `{"$ref": "#/schemas/request/$defs/PaneReportMetadataParams"}`
- `pane.resize` → `{"$ref": "#/schemas/request/$defs/PaneResizeParams"}`
- `pane.scroll` → `{"$ref": "#/schemas/request/$defs/PaneScrollParams"}`
- `pane.selection.read` → `{"$ref": "#/schemas/request/$defs/PaneSelectionReadParams"}`
- `pane.send_input` → `{"$ref": "#/schemas/request/$defs/PaneSendInputParams"}`
- `pane.send_keys` → `{"$ref": "#/schemas/request/$defs/PaneSendKeysParams"}`
- `pane.send_text` → `{"$ref": "#/schemas/request/$defs/PaneSendTextParams"}`
- `pane.split` → `{"$ref": "#/schemas/request/$defs/PaneSplitParams"}`
- `pane.swap` → `{"$ref": "#/schemas/request/$defs/PaneSwapParams"}`
- `pane.wait_for_output` → `{"$ref": "#/schemas/request/$defs/PaneWaitForOutputParams"}`
- `pane.zoom` → `{"$ref": "#/schemas/request/$defs/PaneZoomParams"}`
- `ping` → `{"$ref": "#/schemas/request/$defs/PingParams"}`
- `plugin.action.invoke` → `{"$ref": "#/schemas/request/$defs/PluginActionInvokeParams"}`
- `plugin.action.list` → `{"$ref": "#/schemas/request/$defs/PluginActionListParams"}`
- `plugin.disable` → `{"$ref": "#/schemas/request/$defs/PluginSetEnabledParams"}`
- `plugin.enable` → `{"$ref": "#/schemas/request/$defs/PluginSetEnabledParams"}`
- `plugin.link` → `{"$ref": "#/schemas/request/$defs/PluginLinkParams"}`
- `plugin.list` → `{"$ref": "#/schemas/request/$defs/PluginListParams"}`
- `plugin.log.list` → `{"$ref": "#/schemas/request/$defs/PluginLogListParams"}`
- `plugin.pane.close` → `{"$ref": "#/schemas/request/$defs/PluginPaneCloseParams"}`
- `plugin.pane.focus` → `{"$ref": "#/schemas/request/$defs/PluginPaneFocusParams"}`
- `plugin.pane.open` → `{"$ref": "#/schemas/request/$defs/PluginPaneOpenParams"}`
- `plugin.unlink` → `{"$ref": "#/schemas/request/$defs/PluginUnlinkParams"}`
- `popup.close` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `product_announcement.dismiss` → `{"$ref": "#/schemas/request/$defs/ProductAnnouncementDismissParams"}`
- `release_notes.dismiss` → `{"$ref": "#/schemas/request/$defs/ReleaseNotesDismissParams"}`
- `server.agent_manifests` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `server.live_handoff` → `{"$ref": "#/schemas/request/$defs/ServerLiveHandoffParams"}`
- `server.reload_agent_manifests` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `server.reload_config` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `server.ssh_agent.register` → `{"$ref": "#/schemas/request/$defs/ServerSshAgentRegisterParams"}`
- `server.stop` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `session.snapshot` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `tab.close` → `{"$ref": "#/schemas/request/$defs/TabTarget"}`
- `tab.create` → `{"$ref": "#/schemas/request/$defs/TabCreateParams"}`
- `tab.focus` → `{"$ref": "#/schemas/request/$defs/TabTarget"}`
- `tab.get` → `{"$ref": "#/schemas/request/$defs/TabTarget"}`
- `tab.list` → `{"$ref": "#/schemas/request/$defs/TabListParams"}`
- `tab.move` → `{"$ref": "#/schemas/request/$defs/TabMoveParams"}`
- `tab.rename` → `{"$ref": "#/schemas/request/$defs/TabRenameParams"}`
- `workspace.close` → `{"$ref": "#/schemas/request/$defs/WorkspaceCloseParams"}`
- `workspace.create` → `{"$ref": "#/schemas/request/$defs/WorkspaceCreateParams"}`
- `workspace.focus` → `{"$ref": "#/schemas/request/$defs/WorkspaceTarget"}`
- `workspace.get` → `{"$ref": "#/schemas/request/$defs/WorkspaceTarget"}`
- `workspace.list` → `{"$ref": "#/schemas/request/$defs/EmptyParams"}`
- `workspace.move` → `{"$ref": "#/schemas/request/$defs/WorkspaceMoveParams"}`
- `workspace.move_block` → `{"$ref": "#/schemas/request/$defs/WorkspaceMoveBlockParams"}`
- `workspace.rename` → `{"$ref": "#/schemas/request/$defs/WorkspaceRenameParams"}`
- `workspace.report_metadata` → `{"$ref": "#/schemas/request/$defs/WorkspaceReportMetadataParams"}`
- `worktree.create` → `{"$ref": "#/schemas/request/$defs/WorktreeCreateParams"}`
- `worktree.list` → `{"$ref": "#/schemas/request/$defs/WorktreeListParams"}`
- `worktree.open` → `{"$ref": "#/schemas/request/$defs/WorktreeOpenParams"}`
- `worktree.remove` → `{"$ref": "#/schemas/request/$defs/WorktreeRemoveParams"}`

## Core JSON-RPC API

公开快照：[core-api.schema.json](../sources/core-api.schema.json)。OpenRPC 1.3.2；共 32 个方法。

Core 与 TUI 独立；原生 `hc` 操作与 Core JSON-RPC 方法也不是一一同名。此处提供完整协议发现，不声明自动适配所有方法。

- `doc.get` → `[{"description": "Document name, using the terminal name rules.", "name": "name", "required": true, "schema": {"description": "Document name, using the terminal name rules.", "type": "string"}}, {"description": "Another machine; omitted for this core.", "name": "on", "required": false, "schema": {"description": "Another machine; omitted for this core.", "type": ["string", "null"]}}]`
- `doc.set` → `[{"name": "name", "required": true, "schema": {"type": "string"}}, {"name": "on", "required": false, "schema": {"type": ["string", "null"]}}, {"description": "Any JSON value, at most 1 MiB when serialized; null deletes it.", "name": "value", "required": true, "schema": {"description": "Any JSON value, at most 1 MiB when serialized; null deletes it."}}, {"description": "Current version from doc.get; zero for a name never written.", "name": "version", "required": true, "schema": {"description": "Current version from doc.get; zero for a name never written.", "format": "uint64", "minimum": 0, "type": "integer"}}]`
- `events.subscribe` → `[{"description": "Only children of this terminal.", "name": "children_of", "required": false, "schema": {"description": "Only children of this terminal.", "type": ["string", "null"]}}, {"description": "Only terminals carrying all of these labels (repeatable).", "name": "labels", "required": false, "schema": {"additionalProperties": {"type": "string"}, "default": {}, "description": "Only terminals carrying all of these labels (repeatable).", "type": "object"}}, {"description": "Only this terminal.", "name": "terminal", "required": false, "schema": {"description": "Only this terminal.", "type": ["string", "null"]}}]`
- `file.edit` → `[{"description": "Where a relative path starts (default: where hc runs; through the API,\nthe core's; with --on, that machine's home).", "name": "cwd", "required": false, "schema": {"description": "Where a relative path starts (default: where hc runs; through the API,\nthe core's; with --on, that machine's home).", "type": ["string", "null"]}}, {"description": "Replacements, all made or none (CLI: --old/--new pairs).", "name": "edits", "required": true, "schema": {"description": "Replacements, all made or none (CLI: --old/--new pairs).", "items": {"$ref": "#/components/schemas/Edit"}, "type": "array"}}, {"description": "On another machine (see `hc machine ls`).", "name": "on", "required": false, "schema": {"description": "On another machine (see `hc machine ls`).", "type": ["string", "null"]}}, {"description": "The file: absolute, or from `cwd`.", "name": "path", "required": true, "schema": {"description": "The file: absolute, or from `cwd`.", "type": "string"}}]`
- `file.read` → `[{"description": "Where a relative path starts (default: where hc runs; through the API,\nthe core's; with --on, that machine's home).", "name": "cwd", "required": false, "schema": {"description": "Where a relative path starts (default: where hc runs; through the API,\nthe core's; with --on, that machine's home).", "type": ["string", "null"]}}, {"description": "At most this many lines (default: all, up to 8 MB).", "name": "limit", "required": false, "schema": {"description": "At most this many lines (default: all, up to 8 MB).", "format": "uint", "minimum": 0, "type": ["integer", "null"]}}, {"description": "The first line to give, from 1.", "name": "offset", "required": false, "schema": {"description": "The first line to give, from 1.", "format": "uint", "minimum": 0, "type": ["integer", "null"]}}, {"description": "On another machine (see `hc machine ls`).", "name": "on", "required": false, "schema": {"description": "On another machine (see `hc machine ls`).", "type": ["string", "null"]}}, {"description": "The file: absolute, or from `cwd`.", "name": "path", "required": true, "schema": {"description": "The file: absolute, or from `cwd`.", "type": "string"}}]`
- `file.write` → `[{"description": "Where a relative path starts (default: where hc runs; through the API,\nthe core's; with --on, that machine's home).", "name": "cwd", "required": false, "schema": {"description": "Where a relative path starts (default: where hc runs; through the API,\nthe core's; with --on, that machine's home).", "type": ["string", "null"]}}, {"description": "Its new content, base64, at most 8 MB raw (CLI: what is piped in).", "name": "data", "required": true, "schema": {"description": "Its new content, base64, at most 8 MB raw (CLI: what is piped in).", "type": "string"}}, {"description": "On another machine (see `hc machine ls`).", "name": "on", "required": false, "schema": {"description": "On another machine (see `hc machine ls`).", "type": ["string", "null"]}}, {"description": "The file: absolute, or from `cwd`.", "name": "path", "required": true, "schema": {"description": "The file: absolute, or from `cwd`.", "type": "string"}}]`
- `hello` → `[{"description": "What that core calls this one (`rohan`), so news about `t7` reaches it as `rohan/t7`.", "name": "calls_you", "required": false, "schema": {"description": "What that core calls this one (`rohan`), so news about `t7` reaches it as `rohan/t7`.", "type": ["string", "null"]}}, {"description": "Another core dialing in: who it is. Its terminals may then be parents\nof terminals here, and hear from them.", "name": "core", "required": false, "schema": {"anyOf": [{"$ref": "#/components/schemas/CoreInfo"}, {"type": "null"}], "description": "Another core dialing in: who it is. Its terminals may then be parents\nof terminals here, and hear from them."}}, {"description": "Features supported by a core dialing in, including relaying size notifications.", "name": "features", "required": false, "schema": {"default": [], "description": "Features supported by a core dialing in, including relaying size notifications.", "items": {"type": "string"}, "type": "array"}}, {"description": "Switch this connection to framed mode after the reply.", "name": "framed", "required": false, "schema": {"default": false, "description": "Switch this connection to framed mode after the reply.", "type": "boolean"}}, {"description": "Protocol generation the caller speaks.", "name": "generation", "required": false, "schema": {"description": "Protocol generation the caller speaks.", "format": "uint32", "minimum": 0, "type": ["integer", "null"]}}]`
- `machine.add` → `[{"description": "What to call it here (default: the target's host).", "name": "name", "required": false, "schema": {"description": "What to call it here (default: the target's host).", "type": ["string", "null"]}}, {"description": "The hc session on that machine (default: its default).", "name": "session", "required": false, "schema": {"description": "The hc session on that machine (default: its default).", "type": ["string", "null"]}}, {"description": "How ssh reaches it: `vps`, `can@10.0.0.7`, `can@10.0.0.7:2222`, a Host from ~/.ssh/config.", "name": "target", "required": false, "schema": {"description": "How ssh reaches it: `vps`, `can@10.0.0.7`, `can@10.0.0.7:2222`, a Host from ~/.ssh/config.", "type": ["string", "null"]}}, {"description": "Mark it short-lived (a sandbox for a task), so clients can show it apart\nfrom machines that stay. hc treats it like any other; remove it with\n`hc machine rm`.", "name": "temporary", "required": false, "schema": {"default": false, "description": "Mark it short-lived (a sandbox for a task), so clients can show it apart\nfrom machines that stay. hc treats it like any other; remove it with\n`hc machine rm`.", "type": "boolean"}}, {"description": "Reach it with this command instead of ssh: it is given a shell line to\nrun there as its last argument, like ssh (`ssh -p 2222 -i key user@ip`,\n`fly ssh console -a app --pty=false -C`). It must pass bytes both ways\nuntouched and ask nothing. Needs --name.", "name": "via", "required": false, "schema": {"description": "Reach it with this command instead of ssh: it is given a shell line to\nrun there as its last argument, like ssh (`ssh -p 2222 -i key user@ip`,\n`fly ssh console -a app --pty=false -C`). It must pass bytes both ways\nuntouched and ask nothing. Needs --name.", "type": ["string", "null"]}}]`
- `machine.connect` → `[{"description": "The machine's name.", "name": "machine", "required": true, "schema": {"description": "The machine's name.", "type": "string"}}]`
- `machine.exec` → `[{"description": "Program and arguments, run as given (no shell).", "name": "argv", "required": false, "schema": {"description": "Program and arguments, run as given (no shell).", "items": {"type": "string"}, "type": "array"}}, {"description": "Working directory (default: where hc runs; through the API, the core's;\nwith --on, that machine's home).", "name": "cwd", "required": false, "schema": {"description": "Working directory (default: where hc runs; through the API, the core's;\nwith --on, that machine's home).", "type": ["string", "null"]}}, {"description": "Set on top of the core's environment, key=value (repeatable).", "name": "env", "required": false, "schema": {"additionalProperties": {"type": "string"}, "default": {}, "description": "Set on top of the core's environment, key=value (repeatable).", "type": "object"}}, {"description": "Bytes for its stdin, base64, at most 8 MB raw (without: stdin is closed).", "name": "input", "required": false, "schema": {"description": "Bytes for its stdin, base64, at most 8 MB raw (without: stdin is closed).", "type": ["string", "null"]}}, {"description": "A shell line instead of argv, run by that machine's shell (`sh -c`;\nWindows `%COMSPEC% /d /s /c`). The CLI sends one string with spaces or\nshell signs as a line.", "name": "line", "required": false, "schema": {"description": "A shell line instead of argv, run by that machine's shell (`sh -c`;\nWindows `%COMSPEC% /d /s /c`). The CLI sends one string with spaces or\nshell signs as a line.", "type": ["string", "null"]}}, {"description": "Run it on another machine (see `hc machine ls`).", "name": "on", "required": false, "schema": {"description": "Run it on another machine (see `hc machine ls`).", "type": ["string", "null"]}}, {"description": "Seconds before it and everything it started are ended (default 60, at most 600).", "name": "timeout", "required": false, "schema": {"description": "Seconds before it and everything it started are ended (default 60, at most 600).", "format": "double", "type": ["number", "null"]}}]`
- `machine.list` → `[]`
- `machine.rename` → `[{"description": "The machine's name now.", "name": "machine", "required": true, "schema": {"description": "The machine's name now.", "type": "string"}}, {"description": "Its new name. Addresses with the old one stop working.", "name": "new_name", "required": true, "schema": {"description": "Its new name. Addresses with the old one stop working.", "type": "string"}}]`
- `machine.rm` → `[{"description": "The machine's name.", "name": "machine", "required": true, "schema": {"description": "The machine's name.", "type": "string"}}]`
- `rpc.discover` → `[]`
- `server.restart` → `[]`
- `server.status` → `[]`
- `server.stop` → `[]`
- `templates.list` → `[]`
- `terminal.attach` → `[{"description": "Who is calling (`HC_TERMINAL_ID` inside a terminal): never itself.", "name": "caller", "required": false, "schema": {"default": null, "description": "Who is calling (`HC_TERMINAL_ID` inside a terminal): never itself.", "type": ["string", "null"]}}, {"description": "The viewer's size in cells.", "name": "cols", "required": true, "schema": {"description": "The viewer's size in cells.", "format": "uint16", "maximum": 65535, "minimum": 0, "type": "integer"}}, {"description": "The viewer's own colors and cell size, used to answer display queries.", "name": "display", "required": false, "schema": {"$ref": "#/components/schemas/Display", "default": {"bg": null, "cell": null, "cursor": null, "fg": null}, "description": "The viewer's own colors and cell size, used to answer display queries."}}, {"description": "Scrollback lines to show first (main screen only).", "name": "history", "required": false, "schema": {"default": 0, "description": "Scrollback lines to show first (main screen only).", "format": "uint", "minimum": 0, "type": "integer"}}, {"description": "Watch only: never type or resize.", "name": "observe", "required": false, "schema": {"default": false, "description": "Watch only: never type or resize.", "type": "boolean"}}, {"description": "Observer understands core-to-viewer RESIZE before replacement paints.", "name": "resize_notifications", "required": false, "schema": {"default": false, "description": "Observer understands core-to-viewer RESIZE before replacement paints.", "type": "boolean"}}, {"description": "Back after a dropped line: sets the size only once active again.", "name": "resumed", "required": false, "schema": {"default": false, "description": "Back after a dropped line: sets the size only once active again.", "type": "boolean"}}, {"name": "rows", "required": true, "schema": {"format": "uint16", "maximum": 65535, "minimum": 0, "type": "integer"}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.get` → `[{"description": "Who is calling; a parent looking at its child has seen its news.", "name": "caller", "required": false, "schema": {"description": "Who is calling; a parent looking at its child has seen its news.", "type": ["string", "null"]}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.interrupt` → `[{"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}, {"description": "Seconds to watch for an effect (default 10).", "name": "timeout", "required": false, "schema": {"description": "Seconds to watch for an effect (default 10).", "format": "double", "type": ["number", "null"]}}]`
- `terminal.keep` → `[{"description": "Keep this live terminal after loss. Existing streams end with the loss reason; reattach after `restarted`.", "name": "keep", "required": true, "schema": {"description": "Keep this live terminal after loss. Existing streams end with the loss reason; reattach after `restarted`.", "type": "boolean"}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.keys` → `[{"name": "caller", "required": false, "schema": {"type": ["string", "null"]}}, {"description": "Key names: enter, esc, tab, up, ctrl+c, alt+x, f5, a, ...", "name": "keys", "required": true, "schema": {"description": "Key names: enter, esc, tab, up, ctrl+c, alt+x, f5, a, ...", "items": {"type": "string"}, "type": "array"}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.kill` → `[{"description": "Who is calling; a parent looking at its child has seen its news.", "name": "caller", "required": false, "schema": {"description": "Who is calling; a parent looking at its child has seen its news.", "type": ["string", "null"]}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.label` → `[{"description": "Labels to set, key=value; `key=` removes one.", "name": "labels", "required": true, "schema": {"additionalProperties": {"type": "string"}, "description": "Labels to set, key=value; `key=` removes one.", "type": "object"}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.list` → `[{"description": "Include finished terminals.", "name": "all", "required": false, "schema": {"default": false, "description": "Include finished terminals.", "type": "boolean"}}, {"description": "Only terminals carrying all of these labels (repeatable).", "name": "labels", "required": false, "schema": {"additionalProperties": {"type": "string"}, "default": {}, "description": "Only terminals carrying all of these labels (repeatable).", "type": "object"}}]`
- `terminal.put` → `[{"description": "Its bytes, base64; at most 8 MB raw.", "name": "data", "required": true, "schema": {"description": "Its bytes, base64; at most 8 MB raw.", "type": "string"}}, {"description": "The file's name, kept so `.png` stays `.png` (CLI: the local file to send).", "name": "name", "required": true, "schema": {"description": "The file's name, kept so `.png` stays `.png` (CLI: the local file to send).", "type": "string"}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.read` → `[{"name": "caller", "required": false, "schema": {"type": ["string", "null"]}}, {"description": "Lines of history above the screen.", "name": "lines", "required": false, "schema": {"default": 0, "description": "Lines of history above the screen.", "format": "uint", "minimum": 0, "type": "integer"}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.rm` → `[{"description": "Who is calling; a parent looking at its child has seen its news.", "name": "caller", "required": false, "schema": {"description": "Who is calling; a parent looking at its child has seen its news.", "type": ["string", "null"]}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}]`
- `terminal.run` → `[{"description": "Program and arguments, or a template name and its task. With neither\nargv nor line: that machine's own shell.", "name": "argv", "required": false, "schema": {"default": [], "description": "Program and arguments, or a template name and its task. With neither\nargv nor line: that machine's own shell.", "items": {"type": "string"}, "type": "array"}}, {"description": "Who is calling (`HC_TERMINAL_ID` inside a terminal).", "name": "caller", "required": false, "schema": {"description": "Who is calling (`HC_TERMINAL_ID` inside a terminal).", "type": ["string", "null"]}}, {"description": "Working directory (default: where hc runs; through the API, the core's;\nwith --on, that machine's home).", "name": "cwd", "required": false, "schema": {"description": "Working directory (default: where hc runs; through the API, the core's;\nwith --on, that machine's home).", "type": ["string", "null"]}}, {"description": "Ignored: children end with their parent unless `outlive_parent`.", "name": "die_with_parent", "required": false, "schema": {"default": false, "description": "Ignored: children end with their parent unless `outlive_parent`.", "type": "boolean"}}, {"description": "The caller's colors and cell size, answering the program's display queries\nfrom its start. Omitted: Ghostty's defaults until a viewer attaches.", "name": "display", "required": false, "schema": {"anyOf": [{"$ref": "#/components/schemas/Display"}, {"type": "null"}], "description": "The caller's colors and cell size, answering the program's display queries\nfrom its start. Omitted: Ghostty's defaults until a viewer attaches."}}, {"description": "Set on top of the core's environment. Clients pass their terminal\nidentity here (TERM, TERM_PROGRAM, COLORTERM).", "name": "env", "required": false, "schema": {"additionalProperties": {"type": "string"}, "default": {}, "description": "Set on top of the core's environment. Clients pass their terminal\nidentity here (TERM, TERM_PROGRAM, COLORTERM).", "type": "object"}}, {"description": "Replace lost programs with a shell in place, never re-run the original command.", "name": "keep", "required": false, "schema": {"default": false, "description": "Replace lost programs with a shell in place, never re-run the original command.", "type": "boolean"}}, {"description": "Labels, key=value (repeatable).", "name": "labels", "required": false, "schema": {"additionalProperties": {"type": "string"}, "default": {}, "description": "Labels, key=value (repeatable).", "type": "object"}}, {"description": "A shell line instead of argv, run by that machine's shell (`sh -c`;\nWindows `%COMSPEC% /d /s /c`). The CLI sends one string with spaces or\nshell signs as a line.", "name": "line", "required": false, "schema": {"description": "A shell line instead of argv, run by that machine's shell (`sh -c`;\nWindows `%COMSPEC% /d /s /c`). The CLI sends one string with spaces or\nshell signs as a line.", "type": ["string", "null"]}}, {"description": "Name, unique among live terminals: 1-32 of a-z 0-9 - _ .", "name": "name", "required": false, "schema": {"description": "Name, unique among live terminals: 1-32 of a-z 0-9 - _ .", "type": ["string", "null"]}}, {"description": "Don't type notes about it into its parent.", "name": "no_notify", "required": false, "schema": {"default": false, "description": "Don't type notes about it into its parent.", "type": "boolean"}}, {"description": "No parent, even when started from a terminal.", "name": "no_parent", "required": false, "schema": {"default": false, "description": "No parent, even when started from a terminal.", "type": "boolean"}}, {"description": "Run it on another machine (see `hc machine ls`); its address is `machine/t7`.", "name": "on", "required": false, "schema": {"description": "Run it on another machine (see `hc machine ls`); its address is `machine/t7`.", "type": ["string", "null"]}}, {"description": "Keep it running when its parent's program ends (by default it ends too).", "name": "outlive_parent", "required": false, "schema": {"default": false, "description": "Keep it running when its parent's program ends (by default it ends too).", "type": "boolean"}}, {"description": "Parent terminal (default: the terminal it is started from).", "name": "parent", "required": false, "schema": {"description": "Parent terminal (default: the terminal it is started from).", "type": ["string", "null"]}}, {"description": "Remove it right after it exits (once a waiting parent has the exit code).", "name": "rm", "required": false, "schema": {"default": false, "description": "Remove it right after it exits (once a waiting parent has the exit code).", "type": "boolean"}}, {"description": "Initial size before the program starts. Omitted: the configured\nheadless size (default 200 columns by 120 rows). Later viewers resize normally.", "name": "size", "required": false, "schema": {"anyOf": [{"$ref": "#/components/schemas/InitialSize"}, {"type": "null"}], "description": "Initial size before the program starts. Omitted: the configured\nheadless size (default 200 columns by 120 rows). Later viewers resize normally."}}, {"description": "Seconds before a wait checks in, leaving it running (default: config\n`wait_timeout`, else 180).", "name": "timeout", "required": false, "schema": {"description": "Seconds before a wait checks in, leaving it running (default: config\n`wait_timeout`, else 180).", "format": "double", "type": ["number", "null"]}}, {"description": "Then wait until it is not working, like `terminal.wait`, and return its\noutput (the CLI waits unless --bg).", "name": "wait", "required": false, "schema": {"default": false, "description": "Then wait until it is not working, like `terminal.wait`, and return its\noutput (the CLI waits unless --bg).", "type": "boolean"}}]`
- `terminal.send` → `[{"description": "Who is sending (`HC_TERMINAL_ID`, else the calling process's parent), so a\nbare wait from the same caller waits for this send's turn.", "name": "caller", "required": false, "schema": {"description": "Who is sending (`HC_TERMINAL_ID`, else the calling process's parent), so a\nbare wait from the same caller waits for this send's turn.", "type": ["string", "null"]}}, {"description": "Type even if the program is blocked (it may answer its dialog).", "name": "force", "required": false, "schema": {"default": false, "description": "Type even if the program is blocked (it may answer its dialog).", "type": "boolean"}}, {"description": "Only type if the status is exactly this.", "name": "if", "required": false, "schema": {"anyOf": [{"$ref": "#/components/schemas/IdleOrWorking"}, {"type": "null"}], "description": "Only type if the status is exactly this."}}, {"description": "The terminal: `t7`, a name, or `machine/t7`.", "name": "terminal", "required": true, "schema": {"description": "The terminal: `t7`, a name, or `machine/t7`.", "type": "string"}}, {"description": "Pasted, then submitted with Enter.", "name": "text", "required": true, "schema": {"description": "Pasted, then submitted with Enter.", "type": "string"}}, {"description": "With wait: seconds before it checks in (default: config, else 180).", "name": "timeout", "required": false, "schema": {"description": "With wait: seconds before it checks in (default: config, else 180).", "format": "double", "type": ["number", "null"]}}, {"description": "Then wait for the turn this send started.", "name": "wait", "required": false, "schema": {"default": false, "description": "Then wait for the turn this send started.", "type": "boolean"}}]`
- `terminal.wait` → `[{"description": "See `terminal.send`.", "name": "caller", "required": false, "schema": {"description": "See `terminal.send`.", "type": ["string", "null"]}}, {"description": "Wait on children instead: all = until none is working, any = next news or a message to you.\n\n`all`: until none of the children is working (one that hasn't reported\nyet counts as working). `any`: the parent's unseen news (a turn ended, it\nblocked, it hit an error, it exited), else the next child to stop working; for the parent\nitself, also a message typed into it while it worked (reason `message`).\nA child with a sent launch task counts as working until its turn advances\npast delivery, or it reports done, blocked, error, or exits. Startup idle\ndoes not complete that task in either mode. Without a launch task, idle\nstill counts as stopped.", "name": "children", "required": false, "schema": {"anyOf": [{"$ref": "#/components/schemas/Children"}, {"type": "null"}], "description": "Wait on children instead: all = until none is working, any = next news or a message to you.\n\n`all`: until none of the children is working (one that hasn't reported\nyet counts as working). `any`: the parent's unseen news (a turn ended, it\nblocked, it hit an error, it exited), else the next child to stop working; for the parent\nitself, also a message typed into it while it worked (reason `message`).\nA child with a sent launch task counts as working until its turn advances\npast delivery, or it reports done, blocked, error, or exits. Startup idle\ndoes not complete that task in either mode. Without a launch task, idle\nstill counts as stopped."}}, {"description": "For programs, not agents: end when output printed after the wait started\ncontains this text (plain text, escape sequences stripped). Blocked,\nerror or exit end it too.", "name": "output", "required": false, "schema": {"description": "For programs, not agents: end when output printed after the wait started\ncontains this text (plain text, escape sequences stripped). Blocked,\nerror or exit end it too.", "type": ["string", "null"]}}, {"description": "The terminal; with `children`, whose children (default: the caller).", "name": "terminal", "required": false, "schema": {"description": "The terminal; with `children`, whose children (default: the caller).", "type": ["string", "null"]}}, {"description": "Seconds before it checks in (default: config `wait_timeout`, else 180).", "name": "timeout", "required": false, "schema": {"description": "Seconds before it checks in (default: config `wait_timeout`, else 180).", "format": "double", "type": ["number", "null"]}}]`

## App commands

公开快照：[app-commands.json](../sources/app-commands.json)。共 71 个公开命令。

调用方式：`herdr-app do <command> [args]`。以下参数由静态 `herdr-app commands` 导出；执行命令需单独判断影响。

- `agent.focus` → `[{"name": "terminal", "required": true}]`
- `agent.next` → `[]`
- `agent.prev` → `[]`
- `app.check_updates` → `[]`
- `app.feedback` → `[{"name": "message", "required": false}, {"name": "from", "required": false}]`
- `app.help` → `[]`
- `app.hide` → `[]`
- `app.hide_others` → `[]`
- `app.palette` → `[]`
- `app.quit` → `[]`
- `app.reset` → `[]`
- `app.settings` → `[{"name": "section", "required": false}]`
- `app.show_all` → `[]`
- `app.theme` → `[{"name": "name", "required": true}]`
- `app.update` → `[]`
- `app.update_core` → `[]`
- `app.welcome` → `[]`
- `app.whats_new` → `[]`
- `app.zoom_in` → `[]`
- `app.zoom_out` → `[]`
- `app.zoom_reset` → `[]`
- `layout.clone` → `[{"name": "name", "required": true}, {"name": "as", "required": false}]`
- `layout.hide` → `[{"name": "id", "required": true}]`
- `layout.reset` → `[{"name": "name", "required": false}]`
- `layout.resize` → `[{"name": "id", "required": true}, {"name": "px", "required": false}, {"name": "weight", "required": false}]`
- `layout.select` → `[{"name": "stack", "required": true}, {"name": "child", "required": true}]`
- `layout.set` → `[{"name": "layout", "required": true}]`
- `layout.show` → `[{"name": "id", "required": true}]`
- `layout.switch` → `[{"name": "name", "required": false}]`
- `layout.toggle` → `[{"name": "id", "required": true}]`
- `mod.clone` → `[{"name": "name", "required": true}, {"name": "as", "required": false}]`
- `mod.open` → `[{"name": "name", "required": true}]`
- `overlay.close` → `[{"name": "id", "required": false}]`
- `pane.close` → `[{"name": "pane", "required": false}]`
- `pane.focus` → `[{"name": "pane", "required": false}, {"name": "terminal", "required": false}]`
- `pane.go` → `[{"name": "direction", "required": true}]`
- `pane.split` → `[{"name": "direction", "required": true}, {"name": "pane", "required": false}, {"name": "argv", "required": false}, {"name": "mod", "required": false}, {"name": "props", "required": false}]`
- `pane.swap` → `[{"name": "direction", "required": true}]`
- `pane.zoom` → `[{"name": "pane", "required": false}]`
- `space.close` → `[{"name": "id", "required": false}, {"name": "confirmed", "required": false}]`
- `space.move` → `[{"name": "id", "required": true}, {"name": "index", "required": true}]`
- `space.new` → `[{"name": "name", "required": false}, {"name": "folder", "required": false}, {"name": "tab", "required": false}, {"name": "argv", "required": false}, {"name": "task", "required": false}, {"name": "machine", "required": false}]`
- `space.next` → `[]`
- `space.prev` → `[]`
- `space.rename` → `[{"name": "id", "required": false}, {"name": "name", "required": false}]`
- `space.select` → `[{"name": "index", "required": false}, {"name": "id", "required": false}]`
- `tab.close` → `[{"name": "id", "required": false}, {"name": "confirmed", "required": false}]`
- `tab.move` → `[{"name": "id", "required": true}, {"name": "index", "required": true}]`
- `tab.new` → `[{"name": "name", "required": false}, {"name": "space", "required": false}, {"name": "folder", "required": false}, {"name": "argv", "required": false}, {"name": "task", "required": false}, {"name": "mod", "required": false}, {"name": "props", "required": false}]`
- `tab.next` → `[]`
- `tab.prev` → `[]`
- `tab.rename` → `[{"name": "id", "required": false}, {"name": "name", "required": false}]`
- `tab.select` → `[{"name": "index", "required": false}, {"name": "id", "required": false}]`
- `tab.settle` → `[{"name": "id", "required": false}]`
- `tab.unsettle` → `[{"name": "id", "required": false}]`
- `terminal.copy` → `[]`
- `terminal.keep` → `[{"name": "terminal", "required": true}, {"name": "place", "required": false}]`
- `terminal.kill` → `[{"name": "terminal", "required": true}]`
- `terminal.open` → `[{"name": "argv", "required": false}, {"name": "folder", "required": false}, {"name": "place", "required": false}, {"name": "name", "required": false}]`
- `terminal.park` → `[{"name": "terminal", "required": true}]`
- `terminal.paste` → `[]`
- `terminal.paste_image` → `[]`
- `terminal.peek` → `[{"name": "terminal", "required": true}]`
- `terminal.pin` → `[{"name": "terminal", "required": true}, {"name": "pinned", "required": true}]`
- `terminal.right_click` → `[{"name": "to", "required": true}, {"name": "terminal", "required": false}]`
- `terminal.scroll` → `[{"name": "lines", "required": false}, {"name": "pages", "required": false}, {"name": "to", "required": false}, {"name": "terminal", "required": false}]`
- `terminal.search` → `[]`
- `terminal.show` → `[{"name": "terminal", "required": false}, {"name": "pane", "required": false}]`
- `window.close` → `[]`
- `window.maximize` → `[]`
- `window.minimize` → `[]`
