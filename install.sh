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

if [ -t 1 ]; then
    BOLD=$'\033[1m'; DIM=$'\033[2m'; RESET=$'\033[0m'
    GREEN=$'\033[0;32m'; CYAN=$'\033[0;36m'
else
    BOLD=''; DIM=''; RESET=''; GREEN=''; CYAN=''
fi

banner() {
    printf '\n%s' "$GREEN"
    cat <<'BANNER'
         _                        _     __
    __ _(_)   __      _____  _ __| | __/ _| ___  _ __ ___ ___
   / _` | |   \ \ /\ / / _ \| '__| |/ / |_ / _ \| '__/ __/ _ \
  | (_| | |    \ V  V / (_) | |  |   <|  _| (_) | | | (_|  __/
   \__,_|_|     \_/\_/ \___/|_|  |_|\_\_|  \___/|_|  \___\___|
BANNER
    printf '%s' "$RESET"
    printf "\n  ${BOLD}installer${RESET}${DIM} ─ self-driving teams of AI coworkers, grounded in PearScarf${RESET}\n\n"
}

banner

read -r -p "  Install path [$DEFAULT_PATH]: " install_path
install_path="${install_path:-$DEFAULT_PATH}"

if [ -e "$install_path" ]; then
    echo ""
    echo "  Path already exists: $install_path" >&2
    echo "  Move or remove it, then re-run." >&2
    exit 1
fi

echo ""
echo "  Don't have a PearScarf MCP running yet? Install pearscarf locally first:"
echo "    bash <(curl -fsSL https://raw.githubusercontent.com/pearshape-ai/pearscarf/main/install.sh)"
echo "  It brings up a local pearscarf in Docker and prints the MCP URL — paste it below."
echo ""
read -r -p "  PearScarf MCP URL (SSE endpoint, e.g. http://localhost:8090/sse): " mcp_url
[ -n "$mcp_url" ] || { echo "  A PearScarf MCP URL is required." >&2; exit 1; }

echo ""
echo "  Cloning into $install_path..."
git clone --quiet --depth 1 "$REPO_URL" "$install_path"

cat > "$install_path/.env" <<EOF
PEARSCARF_MCP_URL=$mcp_url
EOF
cat >> "$install_path/.env" <<'EOF'

# Anthropic API key. OPTIONAL — leave commented out to use Claude Code
# subscription auth (via `claude login`, the default). Set this only if you
# don't have a Claude Code subscription and want per-token API billing.
# ANTHROPIC_API_KEY=
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

# Workestrator orchestrator config — read at every `/wf-start`. Sensible
# defaults; edit any knob in place. Full reference:
# https://github.com/pearshape-ai/workestrator
cat > "$install_path/workestrator.yaml" <<EOF
pearscarf:
  mcp_url: $mcp_url

orchestrator:
  poll_interval_seconds: 30
  max_concurrent_agents: 4

roles:
  dir: ./roles

agent:
  model: claude-sonnet-4-5
  max_turns: 50

workspace:
  dir: ./.workestrator/workspaces

events:
  log_path: ./.workforce/events.jsonl
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
echo "  Auth: workforce agents run on your Claude Code subscription via OAuth."
echo "  Make sure you've run \`claude login\` at least once. To use per-token API"
echo "  billing instead, uncomment ANTHROPIC_API_KEY in $install_path/.env."
echo ""
echo "  Config written:"
echo "    .env               (auth)"
echo "    .mcp.json          (Claude Code MCP registration)"
echo "    workestrator.yaml  (orchestrator settings — edit to tune)"
echo ""
echo "  Next:"
echo "    cd $install_path"
echo "    claude              # open Claude Code — pearscarf MCP auto-registers"
echo "    /wf-start           # boot the autonomous workforce daemon"
echo ""
