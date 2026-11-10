# 已安装 CLI 静态帮助

由 `tools/collect.py` 静态采集。所有帮助请求都显式使用 `--help`；不查询运行时，不启动 Core 或 App。

版本：`herdr 0.9.5`；`hc 0.1.18`；`herdr-app 0.1.13`。

## herdr --help

```text
herdr — terminal workspace manager for AI coding agents

Usage: herdr [options]
       herdr --session <name> [options]
       herdr --machine <label-or-id> <command>
       herdr --remote <ssh-target> [--session <name>]
       herdr session attach <name>
       herdr completion zsh
       herdr update [--handoff]
       herdr channel set <stable|preview>
       herdr machine <subcommand> ...
       herdr server stop
       herdr server reload-config
       herdr api <subcommand> ...
       herdr completion <shell>
       herdr config <subcommand> ...
       herdr channel <subcommand> ...
       herdr workspace <subcommand> ...
       herdr worktree <subcommand> ...
       herdr tab <subcommand> ...
       herdr notification <subcommand> ...
       herdr agent <subcommand> ...
       herdr pane <subcommand> ...
       herdr session <subcommand> ...
       herdr integration <subcommand> ...

Common commands:
  herdr                            Launch or attach to the persistent session
  herdr status [server|client]     Show local client and running server status
  herdr update                     Download and install the latest version
  herdr completion zsh             Generate shell completions for zsh
  herdr server stop                Stop the running server via the API socket
  herdr channel set <stable|preview> Choose the stable or preview update channel
  herdr server reload-config       Reload config.toml in the running server
  herdr config reset-keys          Back up config.toml and remove custom keybindings
  herdr channel <subcommand>       Manage the stable or preview update channel
  herdr machine <subcommand>       Manage saved SSH machines
  herdr api <subcommand>           Inspect socket API metadata and live runtime state
  herdr workspace <subcommand>     Workspace helpers over the socket API
  herdr worktree <subcommand>      Git worktree helpers over the socket API
  herdr tab <subcommand>           Tab helpers over the socket API
  herdr notification <subcommand>  Notification helpers over the socket API
  herdr agent <subcommand>         Agent/terminal helpers over the socket API
  herdr pane <subcommand>          Pane control helpers over the socket API
  herdr session <subcommand>       Manage named persistent sessions
  herdr integration <subcommand>   Manage built-in agent integrations

Advanced commands:
  herdr server                     Run as headless server

Options:
  --session <name>    Use or create a named persistent session
  --machine <label-or-id>  Run an API command on a saved SSH machine
  --remote <target>   Attach through SSH to a remote Herdr server
  --remote-keybindings <local|server>
                      Keybindings for --remote app attach (default: local)
  --handoff           Opt into live handoff for update or remote attach
  --default-config    Print default configuration and exit
  --skill             Print the agent skill file and exit
  --version, -V       Print version and exit
  --help, -h          Show this help

Config: C:\Users\zijie\AppData\Roaming\herdr\config.toml
Logs:   C:\Users\zijie\AppData\Roaming\herdr\herdr.log (plus herdr-client.log, herdr-server.log)
Env:    HERDR_CONFIG_PATH overrides config file path
Home:   https://herdr.dev

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr plugin --help

```text
Install and run workflow plugins

Usage: herdr plugin [COMMAND]

Commands:
  install     Install a plugin from GitHub
  uninstall   Uninstall a plugin
  update      Update GitHub-installed plugins
  link        Link a local plugin
  unlink      Unlink a local plugin
  enable      Enable a plugin
  disable     Disable a plugin
  list        List installed plugins
  config-dir  Print a plugin config directory
  action      List or invoke plugin actions
  log         Inspect plugin command logs [alias: logs]
  pane        Manage plugin-owned panes

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr terminal --help

```text
Attach to or observe raw terminal streams

Usage: herdr terminal [COMMAND]

Commands:
  attach   Attach directly to a terminal stream
  session  Work with terminal sessions
  title    Manage the outer terminal title

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr agent --help

```text
Control and inspect agent panes

Usage: herdr agent [COMMAND]

Commands:
  list       List agents
  get        Show an agent
  read       Read agent terminal output
  send-keys  Send key presses to an agent
  prompt     Submit a prompt to an agent
  rename     Rename an agent
  focus      Focus an agent
  wait       Wait until an agent reaches one of the requested states
  attach     Attach directly to an agent terminal
  start      Start a supported interactive agent in an existing pane
  explain    Explain agent detection state

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr api --help

```text
Inspect socket API metadata and live runtime state

Usage: herdr api [COMMAND]

Commands:
  snapshot  Print the live session snapshot
  schema    Print or write the bundled API schema

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr channel --help

```text
Manage stable and preview update channels

Usage: herdr channel [COMMAND]

Commands:
  show  Print the configured update channel
  set   Choose the update channel

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr completion --help

```text
Generate shell completion scripts

Usage: herdr completion <SHELL>

Arguments:
  <SHELL>
          Shell to generate completions for
          
          [possible values: bash, elvish, fish, powershell, zsh]
```

## herdr config --help

```text
Manage local configuration

Usage: herdr config [COMMAND]

Commands:
  check       Validate config.toml and print diagnostics
  reset-keys  Reset custom keybindings

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr integration --help

```text
Manage built-in agent integrations

Usage: herdr integration [COMMAND]

Commands:
  install    Install an integration
  uninstall  Uninstall an integration
  status     Show integration status

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr machine --help

```text
Manage saved SSH machines

Usage: herdr machine [COMMAND]

Commands:
  list       List saved SSH machines
  status     Check saved machines without prompting for authentication
  reconnect  Authenticate a saved machine in this terminal and verify connectivity
  add        Prepare the remote Herdr server and save an SSH machine
  rename     Rename a saved SSH machine
  remove     Remove a saved SSH machine
  enable     Enable a saved SSH machine
  disable    Disable a saved SSH machine

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr notification --help

```text
Show Herdr notifications

Usage: herdr notification [COMMAND]

Commands:
  show  Show a notification

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr pane --help

```text
Control terminal panes

Usage: herdr pane [COMMAND]

Commands:
  list                  List panes
  current               Show the current pane
  get                   Show a pane
  layout                Show pane layout information
  process-info          Show pane process information
  neighbor              Find a pane neighbor
  edges                 Show pane edge information
  focus                 Focus a neighboring pane
  resize                Resize a pane split
  zoom                  Toggle or set pane zoom
  read                  Read pane terminal output
  rename                Rename a pane
  input                 Set pane input routing
  split                 Split a pane
  swap                  Swap panes
  move                  Move a pane
  close                 Close a pane
  send-text             Send literal text to a pane
  send-keys             Send key presses to a pane
  wait-output           Wait for matching pane output
  run                   Run a command in a pane
  report-agent          Report pane agent lifecycle state
  report-agent-session  Report pane agent session identity
  release-agent         Release pane agent lifecycle authority
  report-metadata       Report display-only pane metadata

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr server --help

```text
Run or control the headless server

Usage: herdr server [OPTIONS] [COMMAND]

Commands:
  stop                    Stop the running server
  reload-config           Reload config in the running server
  agent-manifests         Show active agent detection manifests
  update-agent-manifests  Fetch and reload agent detection manifests
  reload-agent-manifests  Reload local agent detection manifest overrides

Options:
      --allow-unelevated-clients
          Allow ordinary same-account clients to control this elevated server

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr session --help

```text
Manage named persistent sessions

Usage: herdr session [COMMAND]

Commands:
  list    List sessions
  attach  Attach to a session
  stop    Stop a session
  delete  Delete a stopped session

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr status --help

```text
Show local client and running server status

Usage: herdr status [OPTIONS] [COMMAND]

Commands:
  server  Show running server status
  client  Show local client status

Options:
      --json
          

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr tab --help

```text
Manage tabs over the socket API

Usage: herdr tab [COMMAND]

Commands:
  list    List tabs
  create  Create a tab
  get     Show a tab
  focus   Focus a tab
  rename  Rename a tab
  close   Close a tab

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr update --help

```text
Download and install the latest version

Usage: herdr update [OPTIONS]

Options:
      --handoff
          Try live handoff after installing
```

## herdr workspace --help

```text
Manage workspaces over the socket API

Usage: herdr workspace [COMMAND]

Commands:
  list             List workspaces
  create           Create a workspace
  get              Show a workspace
  focus            Focus a workspace
  rename           Rename a workspace
  report-metadata  Report display-only workspace metadata
  close            Close a workspace

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr worktree --help

```text
Manage Git worktree-backed workspaces

Usage: herdr worktree [COMMAND]

Commands:
  list    List worktree workspaces
  create  Create and open a Git worktree
  open    Open an existing Git worktree
  remove  Remove a worktree checkout

Are you an AI? Use these resources ONLY IF your task specifically asks you to:
  Help a human understand or set up Herdr for the first time:
    https://herdr.dev/agent-guide.md
  Debug or investigate a problem with Herdr:
    https://herdr.dev/llms.txt
  Control Herdr panes, agents, or workspaces:
    SKIP if a Herdr skill is already in your context. Otherwise run: herdr --skill
```

## herdr plugin action --help

```text
List or invoke plugin actions

Usage: herdr plugin action [COMMAND]

Commands:
  list    List plugin actions
  invoke  Invoke a plugin action
```

## herdr plugin config-dir --help

```text
Print a plugin config directory

Usage: herdr plugin config-dir <PLUGIN_ID>

Arguments:
  <PLUGIN_ID>
```

## herdr plugin disable --help

```text
Disable a plugin

Usage: herdr plugin disable <PLUGIN_ID>

Arguments:
  <PLUGIN_ID>
```

## herdr plugin enable --help

```text
Enable a plugin

Usage: herdr plugin enable <PLUGIN_ID>

Arguments:
  <PLUGIN_ID>
```

## herdr plugin install --help

```text
Install a plugin from GitHub

Usage: herdr plugin install [OPTIONS] <OWNER/REPO[/SUBDIR]>

Arguments:
  <OWNER/REPO[/SUBDIR]>
          

Options:
      --ref <REF>
          

  -y, --yes
```

## herdr plugin link --help

```text
Link a local plugin

Usage: herdr plugin link [OPTIONS] <PATH>

Arguments:
  <PATH>
          

Options:
      --disabled
          

      --enabled
```

## herdr plugin list --help

```text
List installed plugins

Usage: herdr plugin list [OPTIONS]

Options:
      --plugin <ID>
          

      --json
```

## herdr plugin log --help

```text
Inspect plugin command logs

Usage: herdr plugin log [COMMAND]

Commands:
  list  List plugin command logs
```

## herdr plugin pane --help

```text
Manage plugin-owned panes

Usage: herdr plugin pane [COMMAND]

Commands:
  open   Open a plugin pane
  focus  Focus a plugin pane
  close  Close a plugin pane
```

## herdr plugin uninstall --help

```text
Uninstall a plugin

Usage: herdr plugin uninstall <PLUGIN>

Arguments:
  <PLUGIN>
```

## herdr plugin unlink --help

```text
Unlink a local plugin

Usage: herdr plugin unlink <PLUGIN_ID>

Arguments:
  <PLUGIN_ID>
```

## herdr plugin update --help

```text
Update GitHub-installed plugins

Usage: herdr plugin update [OPTIONS] [PLUGIN]...

Arguments:
  [PLUGIN]...
          

Options:
  -y, --yes
```

## herdr terminal attach --help

```text
Attach directly to a terminal stream

Usage: herdr terminal attach [OPTIONS] <TERMINAL_ID>

Arguments:
  <TERMINAL_ID>
          

Options:
      --takeover
```

## herdr terminal session --help

```text
Work with terminal sessions

Usage: herdr terminal session [COMMAND]

Commands:
  control  Control a terminal stream
  observe  Observe a terminal stream
```

## herdr terminal title --help

```text
Manage the outer terminal title

Usage: herdr terminal title [COMMAND]

Commands:
  set    Set the outer terminal title
  clear  Clear the outer terminal title
```

## herdr agent attach --help

```text
Attach directly to an agent terminal

Usage: herdr agent attach <TARGET> [OPTIONS]

Arguments:
  <TARGET>
          

Options:
      --takeover
```

## herdr agent explain --help

```text
Explain agent detection state

Usage: herdr agent explain [OPTIONS] [TARGET]

Arguments:
  [TARGET]
          

Options:
      --file <PATH>
          

      --agent <LABEL>
          

      --json
          

      --format <FORMAT>
          [possible values: text, json]

  -v, --verbose
```

## herdr agent focus --help

```text
Focus an agent

Usage: herdr agent focus <target>

Arguments:
  <target>
```

## herdr agent get --help

```text
Show an agent

Usage: herdr agent get <target>

Arguments:
  <target>
```

## herdr agent list --help

```text
List agents

Usage: herdr agent list
```

## herdr agent prompt --help

```text
Submit a prompt to an agent

Usage: herdr agent prompt <TARGET> <TEXT> [OPTIONS]

Arguments:
  <TARGET>
          

  <TEXT>
          

Options:
      --wait
          Wait for the first matching state observed after submission

      --until <STATUS>
          State to match after --wait; repeat for more than one state
          
          [possible values: idle, working, blocked, done, unknown]

      --timeout <MS>
          Fail after this many milliseconds

If the agent is already blocked, submission is rejected with agent_blocked before any input is sent. When an accepted submission starts from another non-working state, --wait requires an observed working or blocked state within 5000ms; otherwise it returns agent_prompt_stalled. A caller timeout that expires first returns timeout. It then matches idle, done, or blocked by default, or any exact --until state. It does not track turns: if the agent is already working, that active turn's completion may match.
```

## herdr agent read --help

```text
Read agent terminal output

Usage: herdr agent read <TARGET> [OPTIONS]

Arguments:
  <TARGET>
          

Options:
      --source <SOURCE>
          Terminal snapshot source (default: recent)
          
          [possible values: visible, recent, recent-unwrapped, detection]

      --lines <N>
          

      --format <FORMAT>
          [possible values: text, ansi]

      --ansi
```

## herdr agent rename --help

```text
Rename an agent

Usage: herdr agent rename <TARGET> <NAME>|--clear

Arguments:
  <TARGET>
          

  [NAME]
          

Options:
      --clear
```

## herdr agent send-keys --help

```text
Send key presses to an agent

Usage: herdr agent send-keys <TARGET> <KEY>...

Arguments:
  <TARGET>
          

  <KEY>...
          

Use esc as the canonical Escape key name; escape is also accepted.
```

## herdr agent start --help

```text
Start a supported interactive agent in an existing pane

Usage: herdr agent start <NAME> --kind <KIND> --pane <ID> [OPTIONS] [-- [AGENT_ARG]...]

Arguments:
  <NAME>
          

  [AGENT_ARG]...
          

Options:
      --kind <KIND>
          Supported agent kind and canonical executable
          
          [possible values: pi, claude, codex, gemini, cursor, devin, agy, cline, omp, mastracode, opencode, copilot, kimi, kiro, droid, amp, grok, hermes, kilo, qodercli, qwen, letta, maki, muse]

      --pane <ID>
          Existing pane at an interactive shell prompt

      --timeout <MS>
          Wait for interactive readiness (default: 30000; max: 300000)

The pane must be at its interactive shell prompt. Success means the expected agent was detected in the same terminal and is ready for input.

next: herdr agent prompt <TARGET> <TEXT> --wait
```

## herdr agent wait --help

```text
Wait until an agent reaches one of the requested states

Usage: herdr agent wait <TARGET> [OPTIONS]

Arguments:
  <TARGET>
          

Options:
      --until <STATUS>
          State to match; repeat for more than one state
          
          [possible values: idle, working, blocked, done, unknown]

      --timeout <MS>
          Fail after this many milliseconds

Without --until, matches idle, done, or blocked. Use --until unknown explicitly when needed. Without --timeout, waits indefinitely.
```

## herdr api schema --help

```text
Print or write the bundled API schema

Usage: herdr api schema [OPTIONS]

Options:
      --json
          

      --output <PATH>
```

## herdr api snapshot --help

```text
Print the live session snapshot

Usage: herdr api snapshot
```

## herdr channel set --help

```text
Choose the update channel

Usage: herdr channel set <CHANNEL>

Arguments:
  <CHANNEL>
          [possible values: stable, preview]
```

## herdr channel show --help

```text
Print the configured update channel

Usage: herdr channel show
```

## herdr config check --help

```text
Validate config.toml and print diagnostics

Usage: herdr config check
```

## herdr config reset-keys --help

```text
Reset custom keybindings

Usage: herdr config reset-keys
```

## herdr integration install --help

```text
Install an integration

Usage: herdr integration install <TARGET>

Arguments:
  <TARGET>
          [possible values: pi, omp, claude, codex, copilot, devin, droid, kimi, opencode, kilo, hermes, qodercli, qwen, cursor, mastracode, antigravity-cli, grok, letta]
```

## herdr integration status --help

```text
Show integration status

Usage: herdr integration status [OPTIONS]

Options:
      --outdated-only
```

## herdr integration uninstall --help

```text
Uninstall an integration

Usage: herdr integration uninstall <TARGET>

Arguments:
  <TARGET>
          [possible values: pi, omp, claude, codex, copilot, devin, droid, kimi, opencode, kilo, hermes, qodercli, qwen, cursor, mastracode, antigravity-cli, grok, letta]
```

## herdr machine add --help

```text
Prepare the remote Herdr server and save an SSH machine

Usage: herdr machine add [OPTIONS] <SSH_TARGET>

Arguments:
  <SSH_TARGET>
          

Options:
      --label <LABEL>
          Set the machine label shown in the sidebar (defaults to the SSH host, or host/session)

      --remote-session <NAME>
          Select a session explicitly (default without an interactive terminal)
```

## herdr machine disable --help

```text
Disable a saved SSH machine

Usage: herdr machine disable <PROFILE_ID>

Arguments:
  <PROFILE_ID>
```

## herdr machine enable --help

```text
Enable a saved SSH machine

Usage: herdr machine enable <PROFILE_ID>

Arguments:
  <PROFILE_ID>
```

## herdr machine list --help

```text
List saved SSH machines

Usage: herdr machine list [OPTIONS]

Options:
      --json
```

## herdr machine reconnect --help

```text
Authenticate a saved machine in this terminal and verify connectivity

Usage: herdr machine reconnect <LABEL_OR_ID>

Arguments:
  <LABEL_OR_ID>
```

## herdr machine remove --help

```text
Remove a saved SSH machine

Usage: herdr machine remove <PROFILE_ID>

Arguments:
  <PROFILE_ID>
```

## herdr machine rename --help

```text
Rename a saved SSH machine

Usage: herdr machine rename --label <LABEL> <PROFILE_ID>

Arguments:
  <PROFILE_ID>
          

Options:
      --label <LABEL>
          Set the machine label shown in the sidebar
```

## herdr machine status --help

```text
Check saved machines without prompting for authentication

Usage: herdr machine status [OPTIONS] [LABEL_OR_ID]

Arguments:
  [LABEL_OR_ID]
          

Options:
      --json
```

## herdr notification show --help

```text
Show a notification

Usage: herdr notification show [OPTIONS] <TITLE>

Arguments:
  <TITLE>
          

Options:
      --body <TEXT>
          

      --position <POSITION>
          [possible values: top-left, top-right, bottom-left, bottom-right]

      --sound <SOUND>
          [possible values: none, done, request]
```

## herdr pane close --help

```text
Close a pane

Usage: herdr pane close <pane_id>

Arguments:
  <pane_id>
```

## herdr pane current --help

```text
Show the current pane

Usage: herdr pane current [OPTIONS]

Options:
      --pane <ID>
          

      --current
```

## herdr pane edges --help

```text
Show pane edge information

Usage: herdr pane edges [OPTIONS]

Options:
      --pane <ID>
          

      --current
```

## herdr pane focus --help

```text
Focus a neighboring pane

Usage: herdr pane focus [OPTIONS] --direction <DIRECTION>

Options:
      --direction <DIRECTION>
          [possible values: left, right, up, down]

      --pane <ID>
          

      --current
```

## herdr pane get --help

```text
Show a pane

Usage: herdr pane get <pane_id>

Arguments:
  <pane_id>
```

## herdr pane input --help

```text
Set pane input routing

Usage: herdr pane input [OPTIONS] --right-click <TARGET> [PANE_ID]

Arguments:
  [PANE_ID]
          

Options:
      --pane <ID>
          

      --current
          

      --right-click <TARGET>
          [possible values: herdr, pane]
```

## herdr pane layout --help

```text
Show pane layout information

Usage: herdr pane layout [OPTIONS]

Options:
      --pane <ID>
          

      --current
```

## herdr pane list --help

```text
List panes

Usage: herdr pane list [OPTIONS]

Options:
      --workspace <WORKSPACE_ID>
```

## herdr pane move --help

```text
Move a pane

Usage: herdr pane move [OPTIONS] <PANE_ID>

Arguments:
  <PANE_ID>
          

Options:
      --tab <TAB_ID>
          

      --split <DIRECTION>
          [possible values: right, down]

      --target-pane <ID>
          

      --ratio <FLOAT>
          

      --new-tab
          

      --workspace <ID>
          

      --new-workspace
          

      --label <TEXT>
          

      --tab-label <TEXT>
          

      --focus
          

      --no-focus
```

## herdr pane neighbor --help

```text
Find a pane neighbor

Usage: herdr pane neighbor [OPTIONS] --direction <DIRECTION>

Options:
      --direction <DIRECTION>
          [possible values: left, right, up, down]

      --pane <ID>
          

      --current
```

## herdr pane process-info --help

```text
Show pane process information

Usage: herdr pane process-info [OPTIONS]

Options:
      --pane <ID>
          

      --current
```

## herdr pane read --help

```text
Read pane terminal output

Usage: herdr pane read [OPTIONS] <PANE_ID>

Arguments:
  <PANE_ID>
          

Options:
      --source <SOURCE>
          Terminal snapshot source (default: recent)
          
          [possible values: visible, recent, recent-unwrapped, detection]

      --lines <N>
          

      --format <FORMAT>
          [possible values: text, ansi]

      --ansi
          

      --raw
```

## herdr pane release-agent --help

```text
Release pane agent lifecycle authority

Usage: herdr pane release-agent [OPTIONS] --source <ID> --agent <LABEL> <PANE_ID>

Arguments:
  <PANE_ID>
          

Options:
      --source <ID>
          

      --agent <LABEL>
          

      --seq <N>
```

## herdr pane rename --help

```text
Rename a pane

Usage: herdr pane rename [OPTIONS] <PANE_ID> [LABEL]...

Arguments:
  <PANE_ID>
          

  [LABEL]...
          

Options:
      --clear
```

## herdr pane report-agent --help

```text
Report pane agent lifecycle state

Usage: herdr pane report-agent [OPTIONS] --source <ID> --agent <LABEL> --state <STATUS> <PANE_ID> [-- [RESUME_ARG]...]

Arguments:
  <PANE_ID>
          

  [RESUME_ARG]...
          Command that resumes this session after a Herdr restart; starts with a plain command name

Options:
      --source <ID>
          

      --agent <LABEL>
          

      --state <STATUS>
          [possible values: idle, working, blocked, unknown]

      --message <TEXT>
          

      --seq <N>
          

      --agent-session-id <ID>
          

      --agent-session-path <PATH>
```

## herdr pane report-agent-session --help

```text
Report pane agent session identity

Usage: herdr pane report-agent-session [OPTIONS] --source <ID> --agent <LABEL> <PANE_ID> [-- [RESUME_ARG]...]

Arguments:
  <PANE_ID>
          

  [RESUME_ARG]...
          Command that resumes this session after a Herdr restart; starts with a plain command name

Options:
      --source <ID>
          

      --agent <LABEL>
          

      --seq <N>
          

      --agent-session-id <ID>
          

      --agent-session-path <PATH>
          

      --session-start-source <SOURCE>
```

## herdr pane report-metadata --help

```text
Report display-only pane metadata

Usage: herdr pane report-metadata [OPTIONS] --source <ID> <PANE_ID>

Arguments:
  <PANE_ID>
          

Options:
      --source <ID>
          

      --agent <LABEL>
          

      --applies-to-source <ID>
          

      --title <TEXT>
          

      --clear-title
          

      --display-agent <TEXT>
          

      --clear-display-agent
          

      --state-label <STATUS=TEXT>
          

      --clear-state-labels
          

      --token <NAME=VALUE>
          

      --clear-token <NAME>
          

      --seq <N>
          

      --ttl-ms <N>
```

## herdr pane resize --help

```text
Resize a pane split

Usage: herdr pane resize [OPTIONS] --direction <DIRECTION>

Options:
      --direction <DIRECTION>
          [possible values: left, right, up, down]

      --amount <FLOAT>
          

      --pane <ID>
          

      --current
```

## herdr pane run --help

```text
Run a command in a pane

Usage: herdr pane run <PANE_ID> <COMMAND>...

Arguments:
  <PANE_ID>
          

  <COMMAND>...
```

## herdr pane send-keys --help

```text
Send key presses to a pane

Usage: herdr pane send-keys <PANE_ID> <KEY>...

Arguments:
  <PANE_ID>
          

  <KEY>...
          

Use esc as the canonical Escape key name; escape is also accepted.
```

## herdr pane send-text --help

```text
Send literal text to a pane

Usage: herdr pane send-text <PANE_ID> <TEXT>

Arguments:
  <PANE_ID>
          

  <TEXT>
          

next: herdr pane run <PANE_ID> <COMMAND> sends text and Enter in one call
```

## herdr pane split --help

```text
Split a pane

Usage: herdr pane split [OPTIONS] [PANE_ID]

Arguments:
  [PANE_ID]
          

Options:
      --pane <ID>
          

      --current
          

      --direction <DIRECTION>
          [possible values: right, down]

      --ratio <FLOAT>
          

      --cwd <PATH>
          

      --env <KEY=VALUE>
          Set an environment variable for the launched process

      --right-click <TARGET>
          [possible values: herdr, pane]

      --focus
          

      --no-focus
```

## herdr pane swap --help

```text
Swap panes

Usage: herdr pane swap [OPTIONS]

Options:
      --direction <DIRECTION>
          [possible values: left, right, up, down]

      --pane <ID>
          

      --current
          

      --source-pane <ID>
          

      --target-pane <ID>
```

## herdr pane wait-output --help

```text
Wait for matching pane output

Usage: herdr pane wait-output [OPTIONS] <--match <TEXT>|--regex <PATTERN>> <PANE_ID>

Arguments:
  <PANE_ID>
          

Options:
      --match <TEXT>
          Match a literal substring

      --regex <PATTERN>
          Match a Rust regular expression

      --source <SOURCE>
          Terminal snapshot source (default: recent)
          
          [possible values: visible, recent, recent-unwrapped]

      --lines <N>
          Restrict the searched snapshot to N lines

      --timeout <MS>
          Fail after this many milliseconds

      --raw
          Keep ANSI escape sequences while matching

The selected snapshot is searched immediately, including existing output, then polled. Without --timeout, this waits indefinitely.
```

## herdr pane zoom --help

```text
Toggle or set pane zoom

Usage: herdr pane zoom [OPTIONS] [PANE_ID]

Arguments:
  [PANE_ID]
          

Options:
      --pane <ID>
          

      --current
          

      --toggle
          

      --on
          

      --off
```

## herdr server agent-manifests --help

```text
Show active agent detection manifests

Usage: herdr server agent-manifests [OPTIONS]

Options:
      --json
```

## herdr server reload-agent-manifests --help

```text
Reload local agent detection manifest overrides

Usage: herdr server reload-agent-manifests
```

## herdr server reload-config --help

```text
Reload config in the running server

Usage: herdr server reload-config
```

## herdr server stop --help

```text
Stop the running server

Usage: herdr server stop
```

## herdr server update-agent-manifests --help

```text
Fetch and reload agent detection manifests

Usage: herdr server update-agent-manifests [OPTIONS]

Options:
      --json
```

## herdr session attach --help

```text
Attach to a session

Usage: herdr session attach <NAME>

Arguments:
  <NAME>
```

## herdr session delete --help

```text
Delete a stopped session

Usage: herdr session delete [OPTIONS] <NAME>

Arguments:
  <NAME>
          

Options:
      --json
```

## herdr session list --help

```text
List sessions

Usage: herdr session list [OPTIONS]

Options:
      --json
```

## herdr session stop --help

```text
Stop a session

Usage: herdr session stop [OPTIONS] <NAME>

Arguments:
  <NAME>
          

Options:
      --json
```

## herdr status client --help

```text
Show local client status

Usage: herdr status client [OPTIONS]

Options:
      --json
```

## herdr status server --help

```text
Show running server status

Usage: herdr status server [OPTIONS]

Options:
      --json
```

## herdr tab close --help

```text
Close a tab

Usage: herdr tab close <tab_id>

Arguments:
  <tab_id>
```

## herdr tab create --help

```text
Create a tab

Usage: herdr tab create [OPTIONS]

Options:
      --workspace <WORKSPACE_ID>
          

      --cwd <PATH>
          

      --label <TEXT>
          

      --env <KEY=VALUE>
          Set an environment variable for the launched process

      --focus
          

      --no-focus
```

## herdr tab focus --help

```text
Focus a tab

Usage: herdr tab focus <tab_id>

Arguments:
  <tab_id>
```

## herdr tab get --help

```text
Show a tab

Usage: herdr tab get <tab_id>

Arguments:
  <tab_id>
```

## herdr tab list --help

```text
List tabs

Usage: herdr tab list [OPTIONS]

Options:
      --workspace <WORKSPACE_ID>
```

## herdr tab rename --help

```text
Rename a tab

Usage: herdr tab rename <TAB_ID> <LABEL>...

Arguments:
  <TAB_ID>
          

  <LABEL>...
```

## herdr workspace close --help

```text
Close a workspace

Usage: herdr workspace close <workspace_id>

Arguments:
  <workspace_id>
```

## herdr workspace create --help

```text
Create a workspace

Usage: herdr workspace create [OPTIONS]

Options:
      --cwd <PATH>
          

      --label <TEXT>
          

      --env <KEY=VALUE>
          Set an environment variable for the launched process

      --focus
          

      --no-focus
```

## herdr workspace focus --help

```text
Focus a workspace

Usage: herdr workspace focus <workspace_id>

Arguments:
  <workspace_id>
```

## herdr workspace get --help

```text
Show a workspace

Usage: herdr workspace get <workspace_id>

Arguments:
  <workspace_id>
```

## herdr workspace list --help

```text
List workspaces

Usage: herdr workspace list
```

## herdr workspace rename --help

```text
Rename a workspace

Usage: herdr workspace rename <WORKSPACE_ID> <LABEL>...

Arguments:
  <WORKSPACE_ID>
          

  <LABEL>...
```

## herdr workspace report-metadata --help

```text
Report display-only workspace metadata

Usage: herdr workspace report-metadata [OPTIONS] --source <ID> <WORKSPACE_ID>

Arguments:
  <WORKSPACE_ID>
          

Options:
      --source <ID>
          

      --token <NAME=VALUE>
          

      --clear-token <NAME>
          

      --seq <N>
          

      --ttl-ms <N>
```

## herdr worktree create --help

```text
Create and open a Git worktree

Usage: herdr worktree create [OPTIONS]

Options:
      --workspace <ID>
          

      --cwd <PATH>
          

      --branch <NAME>
          

      --base <REF>
          

      --path <PATH>
          

      --label <TEXT>
          

      --focus
          

      --no-focus
          

      --trust-repository
```

## herdr worktree list --help

```text
List worktree workspaces

Usage: herdr worktree list [OPTIONS]

Options:
      --workspace <ID>
          

      --cwd <PATH>
          

      --trust-repository
```

## herdr worktree open --help

```text
Open an existing Git worktree

Usage: herdr worktree open [OPTIONS]

Options:
      --workspace <ID>
          

      --cwd <PATH>
          

      --path <PATH>
          

      --branch <NAME>
          

      --label <TEXT>
          

      --focus
          

      --no-focus
          

      --trust-repository
```

## herdr worktree remove --help

```text
Remove a worktree checkout

Usage: herdr worktree remove [OPTIONS]

Options:
      --workspace <ID>
          

      --force
          

      --trust-repository
```

## herdr plugin action invoke --help

```text
Invoke a plugin action

Usage: herdr plugin action invoke [OPTIONS] <ACTION_ID>

Arguments:
  <ACTION_ID>
          

Options:
      --plugin <ID>
```

## herdr plugin action list --help

```text
List plugin actions

Usage: herdr plugin action list [OPTIONS]

Options:
      --plugin <ID>
```

## herdr plugin log list --help

```text
List plugin command logs

Usage: herdr plugin log list [OPTIONS]

Options:
      --plugin <ID>
          

      --limit <N>
```

## herdr plugin pane close --help

```text
Close a plugin pane

Usage: herdr plugin pane close <PANE_ID>

Arguments:
  <PANE_ID>
```

## herdr plugin pane focus --help

```text
Focus a plugin pane

Usage: herdr plugin pane focus <PANE_ID>

Arguments:
  <PANE_ID>
```

## herdr plugin pane open --help

```text
Open a plugin pane

Usage: herdr plugin pane open [OPTIONS]

Options:
      --plugin <ID>
          

      --entrypoint <ID>
          

      --placement <PLACEMENT>
          [possible values: overlay, split, tab, zoomed]

      --workspace <ID>
          

      --target-pane <PANE>
          

      --direction <DIRECTION>
          [possible values: right, down]

      --cwd <PATH>
          

      --env <KEY=VALUE>
          Set an environment variable for the launched process

      --focus
          

      --no-focus
```

## herdr terminal session control --help

```text
Control a terminal stream

Usage: herdr terminal session control [OPTIONS] <TARGET>

Arguments:
  <TARGET>
          

Options:
      --takeover
          

      --cols <N>
          

      --rows <N>
```

## herdr terminal session observe --help

```text
Observe a terminal stream

Usage: herdr terminal session observe [OPTIONS] <TARGET>

Arguments:
  <TARGET>
          

Options:
      --cols <N>
          

      --rows <N>
```

## herdr terminal title clear --help

```text
Clear the outer terminal title

Usage: herdr terminal title clear
```

## herdr terminal title set --help

```text
Set the outer terminal title

Usage: herdr terminal title set <TITLE>

Arguments:
  <TITLE>
```

## hc --help

```text
hc - run programs and coding agents in terminals that stay alive

Usage: hc <command> [options]
       hc               pick a terminal and attach (new… on top)

Terminals
  run <cmd|template> [task]   run it and wait like a shell (--bg: don't wait)
  ls                          list live terminals (--all: finished too)
  get <t>                     show one terminal
  attach [t]                  put this terminal on it (ctrl+\ detaches)
  read <t>                    print its screen and history
  kill <t>                    end its program
  rm <t>                      remove a finished terminal
  label <t> k=v...            set labels
  keep <t> [--off]            replace lost programs with a shell (also run --keep)
                              signal death recovers too; streams end on loss, reattach

Talk to programs
  send <t> <text>             paste text and press enter
  keys <t> <keys...>          press keys: enter, esc, up, ctrl+c
  interrupt <t>               press the stop key, report what happened
  wait <t>                    wait until it stops working (--output X: until it prints X,
                              --children: your helpers). Use it instead of sleep.
  put <t> <file>              send a file beside it, print where it landed

No terminal
  exec [--on m] <cmd>         run it, print exactly what it wrote, exit with its code
                              (-i: feed it what is piped in)
  file read|write|edit [--on m] <path>
                              a file here or there: print it, write what is piped
                              in, or replace exact text (--old X --new Y)

More
  templates                   list templates
  events                      follow changes live
  server start|stop|status|restart
                              stop parks kept terminals; next core start gives them shells
  update [--version X|--from <file>]   latest release, at least X, or a build
  machine add|ls|login|update|rename|rm   other machines, over ssh or a command
                              (--via 'fly ssh console -a x --pty=false -C')
  connect                     the API over stdin/stdout (ssh box hc connect)
  schema                      the API as JSON Schema, for app builders

<t> is an address like t7 or t1b, or a name. In a terminal, attach, read, get,
kill, rm, wait and interrupt pick one when it's left out.
Options: --json (default when piped; run and read print text), -V --version,
--licenses (what hc includes, and their licenses).
Per command: hc <command> --help
Settings: ~/.config/herdr-core/config.toml. notes = false: hc types nothing
on its own (no notes to parent agents, no <hc> tags on messages).
shell = ["nu"] overrides the shell for new terminals and keep recovery.

Examples
  hc run --on vps "cd app && npm test"     like ssh, in a terminal that stays
  hc run --bg claude                       Claude Code in a new terminal
  hc attach t3                             take it over
  hc run reviewer "review src/x.rs"        a template with a task

Agent? Run: hc --skill
```

## hc attach --help

```text
Put this terminal on a core terminal (detach: ctrl+\)

Usage: hc.EXE attach [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json               JSON output even in a terminal
      --observe            Watch only: never type or resize
      --history <HISTORY>  Scrollback lines to show first (main screen only) [default: 0]
  -h, --help               Print help
```

## hc connect --help

```text
Speak the protocol over stdin/stdout (`ssh box hc connect`)

Usage: hc.EXE connect [OPTIONS]

Options:
      --json               JSON output even in a terminal
      --session <SESSION>  The hc session to reach, like HC_SESSION (one command that reads the same in sh, cmd and PowerShell)
  -h, --help               Print help
```

## hc events --help

```text
Follow fact changes as they happen (one JSON line each when piped)

Usage: hc.EXE events [OPTIONS]

Options:
      --json                       JSON output even in a terminal
      --terminal <TERMINAL>        Only this terminal
      --children-of <CHILDREN_OF>  Only children of this terminal
      --label <K=V>                Only terminals carrying all of these labels (repeatable)
  -h, --help                       Print help
```

## hc exec --help

```text
Run one program without a terminal, here or on a machine: exactly what it wrote, and its exit code

Usage: hc.EXE exec [OPTIONS] <ARGV>...

Arguments:
  <ARGV>...  Program and arguments, run as given (no shell)

Options:
      --json               JSON output even in a terminal
      --on <MACHINE>       Run it on another machine (see `hc machine ls`)
      --cwd <CWD>          Working directory (default: where hc runs; through the API, the core's; with --on, that machine's home)
      --env <K=V>          Set on top of the core's environment, key=value (repeatable)
      --timeout <TIMEOUT>  Seconds before it and everything it started are ended (default 60, at most 600)
  -i, --stdin              Feed what is piped into hc to its stdin
  -h, --help               Print help
```

## hc file --help

```text
Read, write or edit a file here or on a machine: an agent's hands there

Usage: hc.EXE file [OPTIONS] <COMMAND>

Commands:
  read   Print a text file, or lines of it (--offset, --limit)
  write  Write what is piped in as the file, making missing folders
  edit   Replace exact text found once (--old X --new Y, repeatable); all or none
  help   Print this message or the help of the given subcommand(s)

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc get --help

```text
Show one terminal

Usage: hc.EXE get [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc interrupt --help

```text
Press the stop key and report what happened

Usage: hc.EXE interrupt [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json               JSON output even in a terminal
      --timeout <TIMEOUT>  Seconds to watch for an effect (default 10)
  -h, --help               Print help
```

## hc keep --help

```text
Keep a live terminal after loss (--off disables)

Usage: hc.EXE keep [OPTIONS] <TERMINAL>

Arguments:
  <TERMINAL>  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json  JSON output even in a terminal
      --off   Keep this live terminal after loss. Existing streams end with the loss reason; reattach after `restarted`
  -h, --help  Print help
```

## hc keys --help

```text
Press named keys (enter, esc, up, ctrl+c, alt+x, f5, a...)

Usage: hc.EXE keys [OPTIONS] <TERMINAL> <KEYS>...

Arguments:
  <TERMINAL>  The terminal: `t7`, a name, or `machine/t7`
  <KEYS>...   Key names: enter, esc, tab, up, ctrl+c, alt+x, f5, a, ...

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc kill --help

```text
End a terminal's program (hangup, then escalate)

Usage: hc.EXE kill [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc label --help

```text
Set labels (key=value; key= removes)

Usage: hc.EXE label [OPTIONS] <TERMINAL> <K=V>...

Arguments:
  <TERMINAL>  The terminal: `t7`, a name, or `machine/t7`
  <K=V>...    Labels to set, key=value; `key=` removes one

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc ls --help

```text
List live terminals

Usage: hc.EXE ls [OPTIONS]

Options:
      --all          Include finished terminals
      --json         JSON output even in a terminal
      --label <K=V>  Only terminals carrying all of these labels (repeatable)
  -h, --help         Print help
```

## hc machine --help

```text
Other machines, reached over ssh

Usage: hc.EXE machine [OPTIONS] <COMMAND>

Commands:
  add     Add a machine you reach with ssh: hc machine add vps
  ls      List the machines added here
  login   Log in again (a password or code) after the machine says it needs one. On Windows: reconnect once its SSH keys work
  update  Copy this hc there and restart hc there (its terminals keep running)
  rename  Give a machine a new name here
  rm      Forget a machine (its terminals keep running there)
  help    Print this message or the help of the given subcommand(s)

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc put --help

```text
Send a local file beside a terminal (on its machine); prints where it landed

Usage: hc.EXE put [OPTIONS] <TERMINAL> <FILE>

Arguments:
  <TERMINAL>  The terminal: `t7`, a name, or `machine/t7`
  <FILE>      The file's name, kept so `.png` stays `.png` (CLI: the local file to send)

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc read --help

```text
Print a terminal's screen and history

Usage: hc.EXE read [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json           JSON output even in a terminal
      --lines <LINES>  Lines of history above the screen [default: 0]
  -h, --help           Print help
```

## hc rm --help

```text
Remove a finished terminal

Usage: hc.EXE rm [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]  The terminal: `t7`, a name, or `machine/t7`

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc run --help

```text
Start a program, or a template by name with its task: hc run reviewer "review src/x.rs"

Usage: hc.EXE run [OPTIONS] [ARGV]...

Arguments:
  [ARGV]...  Program and arguments, or a template name and its task. With neither argv nor line: that machine's own shell

Options:
      --json               JSON output even in a terminal
      --name <NAME>        Name, unique among live terminals: 1-32 of a-z 0-9 - _ 
      --cwd <CWD>          Working directory (default: where hc runs; through the API, the core's; with --on, that machine's home)
      --on <MACHINE>       Run it on another machine (see `hc machine ls`); its address is `machine/t7`
      --label <K=V>        Labels, key=value (repeatable)
      --parent <PARENT>    Parent terminal (default: the terminal it is started from)
      --no-parent          No parent, even when started from a terminal
      --no-notify          Don't type notes about it into its parent
      --outlive-parent     Keep it running when its parent's program ends (by default it ends too)
      --rm                 Remove it right after it exits (once a waiting parent has the exit code)
      --keep               Replace lost programs with a shell in place, never re-run the original command
      --bg                 Start it and come back at once (a server, several workers)
      --timeout <TIMEOUT>  Seconds before a wait checks in, leaving it running (default: config `wait_timeout`, else 180)
  -h, --help               Print help
```

## hc schema --help

```text
Every API method with its JSON Schema, for app builders

Usage: hc.EXE schema [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc send --help

```text
Paste text into a terminal and press Enter (waits for a person to pause)

Usage: hc.EXE send [OPTIONS] <TERMINAL> <TEXT>

Arguments:
  <TERMINAL>  The terminal: `t7`, a name, or `machine/t7`
  <TEXT>      Pasted, then submitted with Enter

Options:
      --force              Type even if the program is blocked (it may answer its dialog)
      --json               JSON output even in a terminal
      --if <STATUS>        Only type if the status is exactly this [possible values: idle, working]
      --wait               Then wait for the turn this send started
      --timeout <TIMEOUT>  With wait: seconds before it checks in (default: config, else 180)
  -h, --help               Print help
```

## hc server --help

```text
Start, stop or inspect the core

Usage: hc.EXE server [OPTIONS] <COMMAND>

Commands:
  start    
  stop     
  status   
  restart  Restart the core (e.g. after an update); programs keep running
  help     Print this message or the help of the given subcommand(s)

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc templates --help

```text
Templates you can run by name (~/.config/herdr-core/templates)

Usage: hc.EXE templates [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc update --help

```text
Swap this hc for another build and restart (terminals keep running)

Usage: hc.EXE update [OPTIONS]

Options:
      --from <FILE>      A herdr-core binary to use (default: download the latest release)
      --json             JSON output even in a terminal
      --version <X.Y.Z>  At least this release (`0.1.4`): nothing changes when this hc is already that or newer
      --force            Allow an older version (saved state only moves forward), or a release of another protocol generation
  -h, --help             Print help
```

## hc wait --help

```text
Wait for your children (--children any) or one terminal; a message to you also ends it

Usage: hc.EXE wait [OPTIONS] [TERMINAL]

Arguments:
  [TERMINAL]
          The terminal; with `children`, whose children (default: the caller)

Options:
      --children <CHILDREN>
          Wait on children instead: all = until none is working, any = next news or a message to you.
          
          `all`: until none of the children is working (one that hasn't reported yet counts as working). `any`: the parent's unseen news (a turn ended, it blocked, it hit an error, it exited), else the next child to stop working; for the parent itself, also a message typed into it while it worked (reason `message`). A child with a sent launch task counts as working until its turn advances past delivery, or it reports done, blocked, error, or exits. Startup idle does not complete that task in either mode. Without a launch task, idle still counts as stopped.
          
          [possible values: any, all]

      --json
          JSON output even in a terminal

      --output <OUTPUT>
          For programs, not agents: end when output printed after the wait started contains this text (plain text, escape sequences stripped). Blocked, error or exit end it too

      --timeout <TIMEOUT>
          Seconds before it checks in (default: config `wait_timeout`, else 180)

  -h, --help
          Print help (see a summary with '-h')
```

## hc file edit --help

```text
Replace exact text found once (--old X --new Y, repeatable); all or none

Usage: hc.EXE file edit [OPTIONS] --old <OLD> --new <NEW> <PATH>

Arguments:
  <PATH>  The file: absolute, or from `cwd`

Options:
      --json          JSON output even in a terminal
      --on <MACHINE>  On another machine (see `hc machine ls`)
      --cwd <CWD>     Where a relative path starts (default: where hc runs; through the API, the core's; with --on, that machine's home)
      --old <OLD>     Exact text found once in the file (repeatable, paired with --new in order)
      --new <NEW>     What replaces it
  -h, --help          Print help
```

## hc file read --help

```text
Print a text file, or lines of it (--offset, --limit)

Usage: hc.EXE file read [OPTIONS] <PATH>

Arguments:
  <PATH>  The file: absolute, or from `cwd`

Options:
      --json             JSON output even in a terminal
      --on <MACHINE>     On another machine (see `hc machine ls`)
      --cwd <CWD>        Where a relative path starts (default: where hc runs; through the API, the core's; with --on, that machine's home)
      --offset <OFFSET>  The first line to give, from 1
      --limit <LIMIT>    At most this many lines (default: all, up to 8 MB)
  -h, --help             Print help
```

## hc file write --help

```text
Write what is piped in as the file, making missing folders

Usage: hc.EXE file write [OPTIONS] <PATH>

Arguments:
  <PATH>  The file: absolute, or from `cwd`

Options:
      --json          JSON output even in a terminal
      --on <MACHINE>  On another machine (see `hc machine ls`)
      --cwd <CWD>     Where a relative path starts (default: where hc runs; through the API, the core's; with --on, that machine's home)
  -h, --help          Print help
```

## hc machine add --help

```text
Add a machine you reach with ssh: hc machine add vps

Usage: hc.EXE machine add [OPTIONS] [TARGET]

Arguments:
  [TARGET]  How ssh reaches it: `vps`, `can@10.0.0.7`, `can@10.0.0.7:2222`, a Host from ~/.ssh/config

Options:
      --json               JSON output even in a terminal
      --via <COMMAND>      Reach it with this command instead of ssh: it is given a shell line to run there as its last argument, like ssh (`ssh -p 2222 -i key user@ip`, `fly ssh console -a app --pty=false -C`). It must pass bytes both ways untouched and ask nothing. Needs --name
      --temp               Mark it short-lived (a sandbox for a task), so clients can show it apart from machines that stay. hc treats it like any other; remove it with `hc machine rm`
      --install            Copy this hc there when it has none or one too old, without asking (for scripts; in a terminal you are asked)
      --name <NAME>        What to call it here (default: the target's host)
      --session <SESSION>  The hc session on that machine (default: its default)
  -h, --help               Print help
```

## hc machine login --help

```text
Log in again (a password or code) after the machine says it needs one. On Windows: reconnect once its SSH keys work

Usage: hc.EXE machine login [OPTIONS] <MACHINE>

Arguments:
  <MACHINE>  The machine's name

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc machine ls --help

```text
List the machines added here

Usage: hc.EXE machine ls [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc machine rename --help

```text
Give a machine a new name here

Usage: hc.EXE machine rename [OPTIONS] <MACHINE> <NEW_NAME>

Arguments:
  <MACHINE>   The machine's name now
  <NEW_NAME>  Its new name. Addresses with the old one stop working

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc machine rm --help

```text
Forget a machine (its terminals keep running there)

Usage: hc.EXE machine rm [OPTIONS] <MACHINE>

Arguments:
  <MACHINE>  The machine's name

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc machine update --help

```text
Copy this hc there and restart hc there (its terminals keep running)

Usage: hc.EXE machine update [OPTIONS] <MACHINE>

Arguments:
  <MACHINE>  The machine's name

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc server restart --help

```text
Restart the core (e.g. after an update); programs keep running

Usage: hc.EXE server restart [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc server start --help

```text
Usage: hc.EXE server start [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc server status --help

```text
Usage: hc.EXE server status [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## hc server stop --help

```text
Usage: hc.EXE server stop [OPTIONS]

Options:
      --json  JSON output even in a terminal
  -h, --help  Print help
```

## herdr-app --help

```text
herdr-app: the Herdr desktop app. With no arguments it opens the window.

Usage:
  herdr-app                        open the window
  herdr-app ls                     spaces, their tabs and terminals, in the open window
  herdr-app do <command> [args]    run a command: --name api --argv '["pi"]', or one JSON object
  herdr-app feedback <text>        draft feedback for the person to review and send
  herdr-app commands               every command, its arguments, what it does
  herdr-app status                 what the window shows, and any errors
  herdr-app shot [file.png]        save the last window frame (default: herdr-shot.png)
  herdr-app check <mod folder>     load a mod once and report what's wrong
  herdr-app --skill                Agent Skill: driving the window, and where hc fits
  herdr-app --version

The terminals run in herdr-core (`hc`), which keeps them alive when the
window closes. `hc --help`: start, read, wait on and talk to terminals and
agents. The app shows them and arranges them in spaces and tabs.

Home: ~/.config/herdr-app (HERDR_APP_HOME picks another).
```

App 根帮助未声明逐命令 `--help`；完整公开操作与参数见 [API 索引](api-methods.md) 和 `herdr-app commands` 静态快照。
