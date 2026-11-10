# Herdr App 2.0.0 操作与定制

App 负责 spaces/tabs/panes、焦点、布局、主题与 mods，Core（`hc`）运行终端和 Agent。先读 [官方 App Skill](official-app-skill.md)；调度和远程执行用 [Core 指南](core.md)。`HC_TERMINAL_ID` 是 Core 终端地址，不是 App pane ID；Core/App 不要求 `HERDR_ENV=1`。混有 `HERDR_*` 时按 [排障页](setup-recovery.md) 处理继承污染，不能据此把 App 终端认作 TUI。

## 发现与执行边界

`herdr-app --help`、`--skill`、`commands` 可静态读取，不需打开窗口。裸 `herdr-app` 会打开或抬起窗口，不能用于探测。`ls`、`status` 和 `shot` 连接运行中的窗口；`do` 修改用户看到的内容，仅按已授权意图执行。没有窗口不自动启动，不能为了维护停止/重启用户 App/Core。


```sh
herdr-app ls
herdr-app status
herdr-app commands
herdr-app do pane.split '{"direction":"right","pane":"p12"}'
```

先查实际 ID，再执行目标动作。do 支持 `--key value` 或一个 JSON object，数组/对象用 JSON；未知键拒绝。id/pane/space/terminal 必须是字符串；null 保留省略语义，不能用数字触发默认目标。Agent 调用不会弹缺参对话框，必须给出当前操作所需参数，即使静态目录把交互参数标为可选。检查返回 ID/error 和 exit code，再通过 ls/status 确认；启动成功只证明创建终端，不能证明程序或任务成功。

新建 space/tab 会立刻显示，必须有用户需求且显式命名。远程 `space.new --machine <name> --folder /srv/app` 的路径属于那台机器；脚本省略 machine 默认本机，`--machine ''` 显式本机；键盘/点击新建会跟随当前 space 的机器。Core 后台 worker 默认隐藏；仅需要显示时使用 App 命令或任务要求的 `herdr.space` / `herdr.tab` 标签。

`terminal.park` 取走 pane 并关闭 keep，程序继续；`terminal.keep` 是把已有后台终端放到窗口，与 `hc keep` 的丢失恢复语义不同。pane/tab/space close 和 terminal.kill 会结束关联程序，不能混同 window.close 的窗口关闭。terminal.search 操作当前终端的查找栏；焦点回到程序后 Escape 发给程序，查找栏仍可保留。

## 全部 71 项内置 commands

本表来自本机静态 `herdr-app commands`，与 [原始命令快照](../sources/app-commands.json) 一致。参数 `*` 为目录 required；未标记仍可能需要显式值以避免缺参交互。about 保留官方英文语义，平台限制按描述处理。内置命令数量不包含 mod 的 `<mod>.<command>`，且不代表这些写操作已执行或实测。

| Command | 参数（* 必填） | 官方行为 |
|---|---|---|
| `space.new` | `name`, `folder`, `tab`, `argv`, `task`, `machine` | Make a space: its name (default: none, so it's called after where its first terminal is), the folder its terminals start in (default: the focused terminal's), its first tab's name (default: none, so it's called by its number), optionally an agent (argv) and its first message (task), and the machine it lives on (`hc machine ls`; default the focused space's machine for keys and clicks, this computer for scripts; empty string: this computer; its terminals start in that machine's home unless folder). |
| `space.close` | `id`, `confirmed` | Close a space and end its terminals (asks first unless confirmed). |
| `space.rename` | `id`, `name` | Rename a space (asks the person when no name; an empty name: called after where its first terminal is again). |
| `space.move` | `id*`, `index*` | Move a space to a position (1 = first). |
| `tab.new` | `name`, `space`, `folder`, `argv`, `task`, `mod`, `props` | Make a tab in a space (default: the selected one; name default: none, so it's called by its number) with a terminal in folder (default: the focused terminal's), optionally an agent (argv) and its first message (task); or with a mod as its only pane (`mod`, its `props`: a file, a board). With no space open, a person's new tab starts a space (as space.new). |
| `tab.close` | `id`, `confirmed` | Close a tab and end its terminals. |
| `tab.rename` | `id`, `name` | Rename a tab (asks the person when no name; an empty name: called by its number again). |
| `tab.move` | `id*`, `index*` | Move a tab to a position in its space (1 = first). |
| `pane.split` | `direction*`, `pane`, `argv`, `mod`, `props` | Split a pane (default: the focused one) "right" or "down" with a new terminal, or with a mod (`mod`, its `props`) beside it. |
| `pane.close` | `pane` | Close a pane and end its terminal. |
| `terminal.open` | `argv`, `folder`, `place`, `name` | Start a terminal: as a new tab (place "tab", default), or "right"/"down" of the focused pane. |
| `terminal.keep` | `terminal*`, `place` | Give a running terminal without a pane (a sub-agent) a pane: a new tab, or "right"/"down". |
| `terminal.park` | `terminal*` | Take a terminal's pane away and disable core keep; it keeps running (a sub-agent shows under its parent again). |
| `terminal.right_click` | `to*`, `terminal` | Where right-clicks in a terminal (default: the focused one) go when its program takes the mouse: "program" or "menu" (Herdr's, the default). Shift+right-click is always the menu. |
| `terminal.pin` | `terminal*`, `pinned*` | Pin an agent to the top of the agent lists (pinned true) or unpin it (false). Pins are kept with the terminal, so every Herdr client shows them, and end with it. |
| `terminal.kill` | `terminal*` | End a terminal and its sub-agents. |
| `space.select` | `index`, `id` | Show a space (by position or id). |
| `space.next` | 无 | Show the next space. |
| `space.prev` | 无 | Show the previous space. |
| `tab.select` | `index`, `id` | Show a tab (by position in the space, or id). |
| `tab.settle` | `id` | Put a tab away on this screen (default: the shown one): out of the lists, still running. It comes back when shown or when an agent in it needs you. |
| `tab.unsettle` | `id` | Bring a settled tab back to the lists. |
| `tab.next` | 无 | Show the next tab. |
| `tab.prev` | 无 | Show the previous tab. |
| `pane.zoom` | `pane` | Show only this pane of its tab, or all again. |
| `pane.focus` | `pane`, `terminal` | Focus a pane (or the pane showing a terminal). |
| `pane.go` | `direction*` | Focus the pane or focusable mod to the "left", "right", "up" or "down". |
| `pane.swap` | `direction*` | Swap the focused pane with its neighbor in a direction. |
| `terminal.peek` | `terminal*` | Peek at a running terminal over the tab, with keep-as-tab and close controls. |
| `terminal.show` | `terminal`, `pane` | Show a terminal in a pane for now, in place of its own (no terminal: back). |
| `terminal.copy` | 无 | Copy the focused terminal's selection. With nothing selected, that key goes to the program. |
| `terminal.scroll` | `lines`, `pages`, `to`, `terminal` | Scroll a terminal's view of its history (default: the focused one). Give exactly one of: lines (a whole number; negative goes up, toward history), pages (a number, fractions allowed; one page is the terminal's rows), to: "top" (oldest history) or "bottom" (the live screen). This scrolls Herdr's view, not the program. |
| `terminal.paste` | 无 | Paste into the focused terminal (copied files as if dropped; an image alone as terminal.paste_image pastes it). |
| `terminal.paste_image` | 无 | Ctrl+V: the clipboard's image as a file on the focused terminal's machine, when that's another one; on Windows, paste clipboard text; otherwise Ctrl+V goes to the terminal. |
| `terminal.search` | 无 | Search the focused terminal's screen and scrollback; the find bar and query stay with that terminal. |
| `agent.focus` | `terminal*` | Show an agent (sub-agents too). |
| `agent.next` | 无 | Show the next agent, in the order the agents list shows them. |
| `agent.prev` | 无 | Show the previous agent. |
| `layout.switch` | `name` | Show a layout (layouts/<name>.json), or the next one. |
| `layout.clone` | `name*`, `as` | Duplicate a layout as <name>-copy (or as), then show it. |
| `mod.clone` | `name*`, `as` | Duplicate a mod as <name>-copy (or as). |
| `layout.set` | `layout*` | Replace a personal layout tree; shipped layouts accept only click/look fields (not structure). |
| `layout.toggle` | `id*` | Hide or show a layout node. |
| `layout.show` | `id*` | Show a layout node. |
| `layout.hide` | `id*` | Hide a layout node. |
| `layout.resize` | `id*`, `px`, `weight` | Size a layout node. |
| `layout.select` | `stack*`, `child*` | Show one child of a stack. |
| `layout.reset` | `name` | Reset a shipped layout and its clicks (the old file is kept aside). |
| `mod.open` | `name*` | Toggle a mod as the overlay its mod.json describes; calling again closes it. |
| `overlay.close` | `id` | Close an overlay (default: the top dialog or popup). |
| `app.help` | 无 | Toggle the keys dialog. |
| `app.welcome` | 无 | Show the welcome again. |
| `app.whats_new` | 无 | Show what this release brought (it opens once by itself after an update). |
| `app.feedback` | `message`, `from` | Draft feedback for the person to review and send (from: person or agent). |
| `app.palette` | 无 | Toggle the command palette: every command by name, with its key; calling again closes it. |
| `app.settings` | `section` | Open the settings (section: look, alerts, updates). |
| `app.check_updates` | 无 | Look for a newer Herdr and herdr-core now. |
| `app.update_core` | 无 | Update herdr-core to its latest release of this generation; terminals keep running. |
| `app.reset` | 无 | The escape hatch: set the shown layout and keys aside, back to the default screen. |
| `app.theme` | `name*` | Use a theme (a preset or themes/<name>.json). |
| `app.zoom_in` | 无 | Make everything bigger. |
| `app.zoom_out` | 无 | Make everything smaller. |
| `app.zoom_reset` | 无 | Back to normal size. |
| `app.update` | 无 | Restart into the update Herdr downloaded (your terminals keep running). |
| `app.quit` | 无 | Quit (macOS). |
| `app.hide` | 无 | Hide the app (macOS). |
| `app.hide_others` | 无 | Hide other apps (macOS). |
| `app.show_all` | 无 | Show all apps (macOS). |
| `window.close` | 无 | Close the window (on Linux, quits). |
| `window.minimize` | 无 | Minimize the window. |
| `window.maximize` | 无 | Maximize the window, or back. |

## generated AGENTS.md 与类型发现

先解析 `HERDR_APP_HOME`，未设置时用 `~/.config/herdr-app`（Windows 也用该 home，而非推断为 APPDATA）。目录中的 `AGENTS.md`、`herdr.d.ts`、`gpui-kit.d.ts` 是当前安装生成的权威说明与完整类型；App 每次启动重写，禁止编辑。先读 AGENTS 对应章节，再查 herdr.d.ts 的数据、命令、状态/overlay/shared API，以及 gpui-kit.d.ts 的元素、View、事件和生命周期。文件不存在时先确认 home 与安装状态，不为生成文件启动用户 App；把缺失报告为当前维护前提。

用户可维护的文件包括 layouts/*.json、keys.json、settings.json、programs.json 和 mods/<name>/；frame/ 和生成类型不是用户源码。App mods 使用原生 GPUI JavaScript，不是 DOM/HTML/CSS、Node 或 webview。沿用已安装示例与类型，不凭旧版 API 猜接口。

## mod 与布局维护流程

1. 根据任务定位单个 mod/layout，备份实际用户文件。内置资源先用 `mod.clone --name <name> --as <copy>` 或 `layout.clone` 创建个人副本，再编辑副本。仅修改任务需要的文件。mod 是可信代码，可运行命令和访问网络；审查其执行路径与外部依赖后再加载。
2. mod 目录至少有 `main.js`，按需含 `mod.json` 与相对模块/资源。main.js 默认导出继承 View 的类；init 初始化，render 描述 UI，实时数据变化触发重绘。按安装类型实现，不引入无用轮询；慢工作使用 exec/fetch 和 cx.spawn。
3. 每个回调只使用自己的 cx，不能保存后跨回调复用；无 setTimeout/setInterval 或 top-level await，定时器用 cx.timer。用主题色和原生动画。根元素 on_size_change 报告布局后逻辑像素尺寸。`focusable:true` 的 mod 需从 nextCommand 收到 focus 后聚焦自身键盘 handle。
4. 保存会热重载所有副本；坏保存保留旧版并在 status 报错，因此画面还能用不证明新版本成功。避免模块顶层全局副作用；隐藏副本仍活着，不能以隐藏作为清理时点。可选 async close(cx) 内直接开始并 await 清理，总预算 250 ms（退出时副本共享），未完成会取消，不能依赖先前启动的任务。
5. 每次改动后执行 `herdr-app check <mod-folder>`，检查 status，再 `herdr-app shot <file.png>` 并实际查看图片。check 只覆盖初次描述和 eager native elements，不运行 deferred rows、后续异步状态或完整布局；需要在运行窗口按要求验证交互和视觉。未做的步骤必须明示，不宣称验收通过。当前技能文档升级没有修改用户 mod，也没有执行这组检查。

布局保存与 keys/settings/programs 保存同样会热加载，出现 layout.error/keys.error/settings.error/programs.error 时读具体错误后修正。重置会把用户文件移开，不能把 app.reset 当普通排障。退出清理可按安装指南使用 exec 与 terminal.kill 发送已授权清理，其他排队命令在退出时可能无法执行。

## 更新与报告

app.check_updates 是联网检查，成功后才有“已是最新”；app.update_core / hc update 是 Core 更新，计划重启保留终端；app.update 会重启窗口进入已下载版本。按用户授权执行，不用升级解决未定位的环境污染。反馈命令仅草拟供用户审核，不能擅自提交。shot 是最后一帧，需已有已绘制窗口；图片可能包含任务内容，限制保存/分发范围。

本页记录命令与生成指南的静态阅读。71 项路由存在性、mod 维护指导和真实 UI/远程/升级验收是不同证据，见 [覆盖矩阵](coverage-matrix.md)。
