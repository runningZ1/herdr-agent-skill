# Herdr 0.9.5 CLI 帮助快照

本机二进制只读采集；使用时重新运行命令组确认语法。

## herdr workspace

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

## herdr worktree

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

## herdr tab

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

## herdr pane

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

## herdr agent

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

## herdr terminal

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

## herdr notification

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

## herdr session

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

## herdr machine

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

## herdr server

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

## herdr integration

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

## herdr plugin

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

## herdr config

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

## herdr channel

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

## herdr api

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
