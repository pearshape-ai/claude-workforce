# claude-workforce

Self-driving teams of AI coworkers, grounded in shared operational reality via [PearScarf](https://github.com/pearshape-ai/pearscarf).

Four roles ship out of the box — **Hex** (engineer), **Anton** (SRE), **Linda** (comms), **Cindy** (social). You queue work as intents on your PearScarf MCP; the always-on workforce daemon picks them up, dispatches the matching persona, watches the agent ship, and moves on to the next intent.

## Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/pearshape-ai/claude-workforce/main/install.sh)
```

The installer asks for a PearScarf MCP URL, drops the workforce into a directory of your choice, generates `.env` + `.mcp.json` + `workestrator.yaml`, and installs the [workestrator](https://github.com/pearshape-ai/workestrator) daemon. Pre-req: a Claude Code subscription (Pro / Max) and a one-time `claude login`.

## Auth

Workforce agents run on your **Claude Code subscription via OAuth** by default. Run `claude login` once; dispatched agents pick it up automatically.

No subscription? Uncomment `ANTHROPIC_API_KEY` in `.env` and agents run on per-token API billing instead.

## Use

```bash
cd claude-workforce
claude          # open Claude Code; pearscarf MCP auto-registers
/wf-start       # boot the autonomous workforce daemon
/wf-status      # snapshot of what's running
/wf-stop        # halt it
```

Intents arrive on the PearScarf MCP from any Claude session that has it loaded. The daemon polls, gates on `depends_on`, dispatches the matching persona. Start with [`examples/`](./examples/) for copy-paste intent bodies, one per persona shape.

## The personas

| Persona | Role | Ships |
|---|---|---|
| **Hex** | engineer | Code changes in your main repo. Commits, pushes, emits a reality record. |
| **Anton** | SRE | Routine deploys with verification. Emits a deploy record. |
| **Linda** | comms | Blog drafts, announcements, brand-voice copy. Drafts to your wiki for review. |
| **Cindy** | social | X / LinkedIn / Reddit posts, adapted per platform from Linda's narrative. |

Each persona's prompt splits into `roles/<persona>/soul.md` (identity + working style) and `roles/<persona>/skills.md` (loop + conventions + boundaries). Edit either to customize for your project. A shared `roles/_pearscarf.md` describes PearScarf mechanics for any role — drop-in foundation for any future persona you add.

## How it works

PearScarf is the queue and the shared graph. Workestrator is the always-on daemon polling the queue. When an intent arrives with `status=todo` and every `depends_on` upstream `done`, the daemon spawns a Claude Agent SDK session for the persona that matches the intent's `owner_role`, hands it the intent body as its spec, and watches for the agent to flip status to `done`.

No agent messages another agent. Reality — the graph — is the medium. Each persona's reality record lands in the graph; the next persona queries the graph for what's now true; the workforce composes itself.

## License

MIT.
