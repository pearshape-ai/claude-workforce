# claude-workforce

Self-driving teams of AI coworkers, grounded in shared operational reality via PearScarf.

## Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/pearshape-ai/claude-workforce/main/install.sh)
```

The installer asks for a PearScarf MCP URL, drops the workforce into a directory of your choice, and installs the [workestrator](https://github.com/pearshape-ai/workestrator) orchestrator. Pre-req: a Claude Code subscription (Pro / Max) and one-time `claude login`.

## Auth

Workforce agents run on your **Claude Code subscription via OAuth** by default — same auth as your interactive Claude Code sessions. Run `claude login` once before `/wf-start` and the dispatched agents pick it up automatically.

No Claude Code subscription? Uncomment `ANTHROPIC_API_KEY` in `.env` (the installer creates it commented out) and agents will run on **per-token API billing** instead.

## Use

After install:

```bash
cd claude-workforce
claude          # open Claude Code in the workforce directory
/wf-start       # boot the autonomous workforce daemon
/wf-stop        # halt it
```

Intent creation happens through the PearScarf MCP — submit intents from any Claude session that has the MCP loaded; the always-on daemon picks them up.

## License

MIT.
