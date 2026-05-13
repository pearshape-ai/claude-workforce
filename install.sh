#!/usr/bin/env bash
# claude-workforce installer.
#
# One-line install:
#   bash <(curl -fsSL https://raw.githubusercontent.com/pearshape-ai/claude-workforce/main/install.sh)
#
# Drops the workforce into a directory of your choice, wires the env, and
# installs the workestrator orchestrator. After this finishes, open Claude
# Code inside the install directory and use /spec + /workforce-run.

set -euo pipefail

REPO_URL="${CLAUDE_WORKFORCE_REPO:-https://github.com/pearshape-ai/claude-workforce.git}"
DEFAULT_PATH="$(pwd)/claude-workforce"

echo ""
echo "  claude-workforce installer"
echo "  ──────────────────────────"
echo ""

read -r -p "  Install path [$DEFAULT_PATH]: " install_path
install_path="${install_path:-$DEFAULT_PATH}"

if [ -e "$install_path" ]; then
    echo ""
    echo "  Path already exists: $install_path" >&2
    echo "  Move or remove it, then re-run." >&2
    exit 1
fi

read -r -s -p "  Anthropic API key: " anthropic_key
echo ""
[ -n "$anthropic_key" ] || { echo "  An Anthropic API key is required." >&2; exit 1; }

read -r -p "  PearScarf MCP URL (SSE endpoint, e.g. https://your-pearscarf/sse): " mcp_url
[ -n "$mcp_url" ] || { echo "  A PearScarf MCP URL is required." >&2; exit 1; }

echo ""
echo "  Cloning into $install_path..."
git clone --quiet --depth 1 "$REPO_URL" "$install_path"

cat > "$install_path/.env" <<EOF
ANTHROPIC_API_KEY=$anthropic_key
PEARSCARF_MCP_URL=$mcp_url
EOF
chmod 600 "$install_path/.env"

# Register the PearScarf MCP with Claude Code so it loads when the user opens
# Claude Code inside the install directory. SSE is the v0 default — pearscarf
# serves over SSE today. Edit `.mcp.json` if your server is HTTP.
cat > "$install_path/.mcp.json" <<EOF
{
  "mcpServers": {
    "pearscarf": {
      "type": "sse",
      "url": "$mcp_url"
    }
  }
}
EOF

echo "  Installing workestrator..."
if command -v uv >/dev/null 2>&1; then
    uv tool install --quiet "git+https://github.com/pearshape-ai/workestrator.git"
else
    echo ""
    echo "  uv not found — workestrator is a Python tool installable via uv."
    echo "  Install uv from https://docs.astral.sh/uv/getting-started/installation/"
    echo "  Then, from $install_path, run:"
    echo "    uv tool install git+https://github.com/pearshape-ai/workestrator.git"
fi

echo ""
echo "  Done."
echo ""
echo "  Next:"
echo "    cd $install_path"
echo "    claude login        # if not already (Claude Code uses OAuth, not .env)"
echo "    claude              # open Claude Code — pearscarf MCP auto-registers"
echo "    /spec <one-liner>   # seed the intent set on your PearScarf MCP"
echo "    /workforce-run      # boot the autonomous loop"
echo ""
