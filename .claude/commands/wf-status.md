---
description: Snapshot the workforce — daemon health, in-flight intents, recent completions, queue
---

Produce a one-screen snapshot of the workforce state. Useful when you open a fresh Claude Code session in this workforce directory and want to see what's happening without scrolling through prior events.

## Steps

1. **Daemon health.** Read `.workforce/workestrator.pid` if it exists:
   - File missing → **not running**.
   - File present + `kill -0 <pid>` succeeds → **alive (PID `<pid>`)**.
   - File present + `kill -0 <pid>` fails → **stale-pid** (the daemon died without cleaning up).

2. **Daemon config** (if alive). Read `workestrator.yaml` and surface: `orchestrator.poll_interval_seconds`, `orchestrator.max_concurrent_agents`, `roles.dir`.

3. **In-flight intents.** Query the `pearscarf` MCP via `query_intents(status="in_progress", limit=10)`. For each result, extract:
   - `intent_id`
   - `owner` and/or `owner_role`
   - The Title line from the intent body (first `Title:` or first `# ` heading)
   - `set_at` (when workestrator claimed it), rendered as relative time

4. **Recent completions / failures.** Read the last ~40 lines of `.workforce/events.jsonl` (if it exists). Filter to events of type `intent_completed` and `intent_failed`. Show the last 5 most recent in chronological order (newest first) with:
   - intent_id
   - role and owner
   - `done` / `failed` (and `error` snippet if failed)
   - Relative timestamp from the event's `ts` field

5. **Queue.** Query `pearscarf` MCP via `query_intents(status="todo", limit=20)`. For each, check whether every upstream in `depends_on` is `done` (call `get_intent` on each dep id). Split into:
   - **eligible** — every upstream `done` (workestrator could dispatch now)
   - **blocked on deps** — at least one upstream still in `todo` / `in_progress`

6. **Format the snapshot** as a single fenced block:

```
Workestrator: <alive (PID X) | stale-pid | not running>
Polling: every <N>s · max <K> concurrent · roles: <path>

In flight:
  <intent_id> (<owner> / <role>) — "<title snippet>" — started <Xm> ago

Recent completions (last 5):
  ✓ <intent_id> (<owner> / <role>) — done — <Xm> ago
  ✗ <intent_id> (<owner> / <role>) — failed: <error snippet> — <Xm> ago

Queue:
  todo intents: <N>
    eligible (deps done): <K> — <comma-separated intent_ids or "—">
    blocked on deps:      <N-K>
```

Replace empty sections with a single dash (`—`). If the daemon is **not running**, skip the polling / in-flight sections and replace them with:

```
Workestrator: not running
Run /wf-start to boot it.
```

If the daemon is alive but the PearScarf MCP is unreachable mid-query, surface `(MCP unreachable: <error>)` next to the section that couldn't load — don't silently return empty.

After printing the snapshot, do not prompt the user for follow-up. The operator reads the snapshot and decides next moves themselves.
