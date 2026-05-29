#!/usr/bin/env python3
"""tail-workforce.py — surface PearScarf MCP calls + agent activity from the workforce stream.

Tails `.workforce/events.jsonl` and prints a clean, color-coded line for every
PearScarf MCP tool use — `recall`, `query_facts`, `submit_record`, … — so you
can see agents ground and write back in real time, separated from the noisy
main daemon output. Designed for a side terminal pane during recordings.

With `--rich`, also surface the agent's other activities (committing, pushing,
editing, browsing, typing, …) as visible labels — so a viewer can follow the
whole sequence by coworker, not just the MCP calls.

Usage:
  scripts/tail-workforce.py                    # tail; PearScarf MCP only (clean)
  scripts/tail-workforce.py --rich             # tail; + activity labels (commit/push/edit/...)
  scripts/tail-workforce.py --replay [--rich]  # print past events and exit
  scripts/tail-workforce.py <events.jsonl>     # tail a specific events file
  scripts/tail-workforce.py --roles-dir DIR    # override role→agent-name map
                                         # (auto-detected from workestrator.yaml)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

# ANSI
RESET = "\033[0m"
DIM = "\033[2m"
BOLD = "\033[1m"
GREEN = "\033[32m"      # PearScarf MCP read
MAGENTA = "\033[35m"    # write / mutation (MCP write, commit, push)
CYAN = "\033[36m"       # other activity
YELLOW = "\033[33m"     # agent label

# PearScarf MCP tool categorization
READ_TOOLS = {
    "recall", "query_facts", "query_records", "query_intents",
    "get_entity_context", "get_relationship", "get_record_status",
    "get_fact_history", "get_intent", "get_intent_tree", "get_schema",
}
WRITE_TOOLS = {
    "submit_record", "submit_intent",
    "set_intent_status", "set_intent_owner", "set_intent_owner_role",
    "set_intent_parent", "set_intent_dependencies",
}
ICON = {
    "recall": "🔍", "query_facts": "🔎", "query_records": "📚",
    "query_intents": "📋", "get_intent": "📋", "get_intent_tree": "🌳",
    "get_entity_context": "📄", "get_relationship": "↔",
    "get_record_status": "⏱ ", "get_fact_history": "🕒", "get_schema": "📐",
    "submit_record": "📤", "submit_intent": "📬",
    "set_intent_status": "✓ ", "set_intent_owner": "✓ ",
    "set_intent_owner_role": "✓ ", "set_intent_parent": "✓ ",
    "set_intent_dependencies": "✓ ",
}


# ----- discovery / setup -----

def find_default_events() -> Path | None:
    here = Path(__file__).resolve()
    for base in (here.parent.parent, Path.cwd(), Path.cwd().parent):
        cand = base / ".workforce" / "events.jsonl"
        if cand.exists():
            return cand
    return None


def find_roles_dir() -> Path | None:
    """Auto-detect roles.dir from workestrator.yaml; fall back to ../roles."""
    here = Path(__file__).resolve()
    for base in (here.parent.parent, Path.cwd()):
        cfg = base / "workestrator.yaml"
        if cfg.exists():
            m = re.search(r"^\s*dir:\s*(\S+)\s*$", cfg.read_text(), re.M)
            if m:
                p = Path(m.group(1))
                if p.exists():
                    return p
    fallback = here.parent.parent / "roles"
    return fallback if fallback.exists() else None


def load_roster(roles_dir: Path | None) -> dict[str, str]:
    """Map role slug → agent_name by reading config.yaml under each role."""
    roster: dict[str, str] = {}
    if not roles_dir or not roles_dir.exists():
        return roster
    for cfg in roles_dir.rglob("config.yaml"):
        try:
            text = cfg.read_text()
        except OSError:
            continue
        n = re.search(r"^name:\s*(\S+)\s*$", text, re.M)
        a = re.search(r"^agent_name:\s*(\S+)\s*$", text, re.M)
        if n and a:
            roster[n.group(1).strip()] = a.group(1).strip()
    return roster


# ----- formatting helpers -----

# Trim helpers — set by init_trim() once events_path is known.
_WORKSPACE_PREFIX: str | None = None
_HOME_PREFIX = str(Path.home())


def init_trim(events_path: Path) -> None:
    """Detect the workspace root from the events file location so renders strip it.

    Convention: events.jsonl lives at `<workspace>/<workforce-checkout>/.workforce/events.jsonl`,
    so the workspace root is two parents above `.workforce/`. Falls back to `$HOME → ~`.
    """
    global _WORKSPACE_PREFIX
    if events_path.parent.name == ".workforce":
        candidate = events_path.parent.parent.parent
        if candidate.is_dir():
            _WORKSPACE_PREFIX = str(candidate).rstrip("/") + "/"


def trim_paths(s: str) -> str:
    """Strip the workspace root from any rendered string; fall back to `$HOME → ~`."""
    if not s:
        return s
    if _WORKSPACE_PREFIX and _WORKSPACE_PREFIX in s:
        s = s.replace(_WORKSPACE_PREFIX, "")
    if _HOME_PREFIX in s:
        s = s.replace(_HOME_PREFIX, "~")
    return s


def short_path(p: str) -> str:
    if not p:
        return ""
    p = trim_paths(p)
    parts = p.rstrip("/").split("/")
    # Already short after trim? Keep as-is. Otherwise tail-clip.
    return "/".join(parts[-3:]) if len(parts) > 5 else p


def short_url(u: str) -> str:
    if not u:
        return ""
    return re.sub(r"^https?://", "", u)[:60]


def short_arg(summary: str) -> str:
    """One-line summary of a PearScarf MCP tool's args for display."""
    s = (summary or "").strip()
    try:
        args = json.loads(s)
    except json.JSONDecodeError:
        return s[:80].replace("\n", " ")
    if not isinstance(args, dict):
        return s[:80]
    for key in ("query", "entity_name"):
        if args.get(key):
            v = str(args[key])
            return f'"{v[:70]}{"…" if len(v) > 70 else ""}"'
    for key in ("id", "uri", "subject", "fact_id", "record_id", "source_record"):
        if args.get(key):
            return f"{key}={args[key]}"
    if args.get("body"):
        first = str(args["body"]).splitlines()[0]
        return f'body: "{first[:60]}{"…" if len(first) > 60 else ""}"'
    if not args:
        return ""
    keys = [f"{k}={str(v)[:25]}" for k, v in list(args.items())[:2] if v]
    return ", ".join(keys)


def categorize_activity(tool: str, summary: str):
    """Categorize a non-PearScarf-MCP tool into (icon, label, color, detail) or None to skip."""
    s = summary or ""

    # Noise / internal bookkeeping
    if tool in {"ToolSearch", "Glob"}:
        return None

    # Shell
    if tool == "Bash":
        cmd = s.strip().replace("\n", " ")
        # Order matters: push wins over commit (the chain's final action)
        if "git push" in cmd:
            return ("🚀", "pushing", MAGENTA, "")
        if "git commit" in cmd:
            return ("💾", "committing", MAGENTA, "")
        if "git pull" in cmd:
            return ("⬇ ", "pulling", CYAN, "")
        if "pre-commit" in cmd or "pytest" in cmd or "uv run pytest" in cmd:
            return ("🧪", "running gates", CYAN, "")
        if "git add" in cmd:
            return None  # silent staging, skip
        return None  # all other shell — too noisy to surface (ls/find/mkdir/cat/python -c/…)

    # File ops — summary is the path (string)
    if tool == "Write":
        return ("✏️ ", "writing", CYAN, short_path(s.strip()))
    if tool == "Edit":
        return ("✏️ ", "editing", CYAN, short_path(s.strip()))
    if tool == "Read":
        path = s.strip()
        # only show .md/.yaml/.yml/.json reads (specs, drafts, refs) — code reads are noise
        if not path.endswith((".md", ".yaml", ".yml", ".json")):
            return None
        return ("📜", "reading", CYAN, short_path(path))

    # MCP resources (pearscarf://format/record, pearscarf://guide/consumer, …)
    if tool == "ReadMcpResourceTool":
        try:
            d = json.loads(s)
            return ("📜", "reading", CYAN, str(d.get("uri", ""))[:80])
        except json.JSONDecodeError:
            return None

    # Browser (claude-in-chrome) MCP
    if tool.startswith("mcp__claude-in-chrome__"):
        action = tool.split("__")[-1]
        try:
            d = json.loads(s)
        except json.JSONDecodeError:
            d = {}
        if action == "navigate":
            return ("🌐", "navigating to", CYAN, short_url(d.get("url", "")))
        if action == "computer":
            ca = d.get("action", "")
            if ca == "type":
                text = str(d.get("text", "")).replace("\n", " ")
                return ("⌨ ", "typing", CYAN, f'"{text[:60]}{"…" if len(text) > 60 else ""}"' if text else "")
            if ca == "left_click":
                return ("🖱 ", "clicking", CYAN, "")
            if ca == "key":
                return ("⌨ ", "key", CYAN, str(d.get("text", ""))[:20])
            return None  # screenshot, wait, scroll — skip
        if action in ("read_page", "get_page_text"):
            return ("📖", "reading page", CYAN, "")
        if action == "browser_batch":
            return ("🌐", "browser batch", CYAN, "")
        if action.startswith("tabs_"):
            return ("🌐", action.replace("_", " "), CYAN, "")
        return None

    if tool in ("WebSearch", "WebFetch"):
        return ("🔎", "web search", CYAN, "")

    return None  # unknown tool


# ----- rendering -----

def render_pearscarf_mcp(ts: str, agent: str, tool: str, summary: str) -> str:
    bare = tool.split("__")[-1]
    color = GREEN if bare in READ_TOOLS else MAGENTA if bare in WRITE_TOOLS else CYAN
    icon = ICON.get(bare, "• ")
    arg = short_arg(summary)
    arg_disp = f" {DIM}({arg}){RESET}" if arg else ""
    return f"{DIM}{ts}{RESET}  {YELLOW}{agent:<10}{RESET}  {icon} {color}{BOLD}{bare}{RESET}{arg_disp}"


def render_activity(ts: str, agent: str, icon: str, label: str, color: str, detail: str) -> str:
    label_disp = f"{color}{BOLD}{label}{RESET}" if label else ""
    detail_disp = f" {DIM}{detail}{RESET}" if detail else ""
    return f"{DIM}{ts}{RESET}  {YELLOW}{agent:<10}{RESET}  {icon} {label_disp}{detail_disp}"


def format_event(e: dict, roster: dict[str, str], rich: bool) -> str | None:
    if e.get("event") != "agent_tool_use":
        return None
    tool = e.get("tool") or ""
    ts = (e.get("ts") or "")[11:19]
    role = e.get("role") or ""
    agent = roster.get(role, role.split("/")[-1] or "?")
    summary = e.get("summary") or ""

    if tool.startswith("mcp__pearscarf"):
        return render_pearscarf_mcp(ts, agent, tool, summary)

    if not rich:
        return None  # non-PearScarf-MCP tool in clean mode → skip

    cat = categorize_activity(tool, summary)
    if cat is None:
        return None
    icon, label, color, detail = cat
    return render_activity(ts, agent, icon, label, color, detail)


# ----- I/O -----

def replay(path: Path, roster: dict[str, str], rich: bool) -> None:
    with open(path) as f:
        for line in f:
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            out = format_event(e, roster, rich)
            if out:
                print(out)


def tail(path: Path, roster: dict[str, str], rich: bool) -> None:
    with open(path) as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.3)
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            out = format_event(e, roster, rich)
            if out:
                print(out, flush=True)


def main() -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    p.add_argument("path", nargs="?", help="path to .workforce/events.jsonl (auto-detect by default)")
    p.add_argument("--replay", action="store_true", help="print past events and exit (don't tail)")
    p.add_argument("--rich", action="store_true",
                   help="also show non-PearScarf activity labels (commit/push/edit/browse/…)")
    p.add_argument("--roles-dir", help="path to roles/ for the role→agent-name map")
    args = p.parse_args()

    path = Path(args.path) if args.path else find_default_events()
    if not path or not path.exists():
        print("events.jsonl not found — pass a path or run from a claude-workforce checkout", file=sys.stderr)
        return 1

    roles_dir = Path(args.roles_dir) if args.roles_dir else find_roles_dir()
    roster = load_roster(roles_dir)
    init_trim(path)

    mode = "rich (MCP + activity)" if args.rich else "PearScarf MCP only"
    print(f"{DIM}tailing {path} — {mode}, {len(roster)} roles known{RESET}\n", file=sys.stderr)
    try:
        if args.replay:
            replay(path, roster, args.rich)
        else:
            tail(path, roster, args.rich)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
