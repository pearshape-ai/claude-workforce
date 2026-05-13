# claude-workforce

Self-driving teams of AI coworkers, grounded in shared operational reality via PearScarf.

## Install

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/pearshape-ai/claude-workforce/main/install.sh)
```

The installer asks for an Anthropic API key and a PearScarf MCP URL, drops the workforce into a directory of your choice, and installs the [workestrator](https://github.com/pearshape-ai/workestrator) orchestrator.

## Use

After install:

```bash
cd claude-workforce
claude               # open Claude Code in the workforce directory
/spec <one-liner>    # seed the intent set on your PearScarf MCP
/workforce-run       # boot the autonomous loop
```

## License

MIT.
