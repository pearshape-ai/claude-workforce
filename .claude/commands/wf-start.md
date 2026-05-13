---
description: Start the workestrator daemon and stream its events into this session
---

Start the workestrator daemon for this claude-workforce installation, then arm a Monitor on its event stream so the daemon's progress surfaces in this Claude Code session as it happens.

Workestrator polls the configured PearScarf MCP, picks up intents where `status="todo"` and every upstream `depends_on` is `"done"`, and dispatches each one to the persona that matches its `owner_role`. The daemon runs in the background and survives this Claude Code session closing.

## Steps

1. **Check for an already-running daemon.** Read `.workforce/workestrator.pid` if it exists. If the PID is alive (`kill -0 <pid>` succeeds), report `Workestrator is already running (PID <pid>).` and stop — do not start a second instance.

2. **Prepare the runtime directory.** Ensure `.workforce/` exists. Ensure `.workforce/events.jsonl` exists (`touch` it) so the Monitor has something to attach to even before the daemon writes its first line.

3. **Launch workestrator in the background.** Run:
   ```bash
   nohup workestrator run --config workestrator.yaml \
     > .workforce/workestrator.log 2>&1 &
   ```
   Capture the PID and write it to `.workforce/workestrator.pid`.

4. **Verify the daemon started cleanly.** Wait 2 seconds. Read the last 5 lines of `.workforce/workestrator.log`. If those lines show a crash, missing-config error, or auth failure, report the error to the operator and stop. Otherwise proceed.

5. **Arm a persistent Monitor on the event stream.** Use the Monitor tool with `persistent: true` watching `.workforce/events.jsonl`. Each line workestrator writes to that file is a JSON event that will arrive in this session as a `<task-notification>`.

6. **Handle notifications as they arrive.** Each event is one JSON object per line:
   ```
   {"ts": "<iso8601>", "event": "<type>", "intent_id": "<id>", "role": "<role>", "owner": "<persona>", "title": "<intent-title>", ...}
   ```
   Event types you may see:
   - `daemon_started` — daemon booted and is polling.
   - `intent_dispatched` — a persona session is starting on this intent.
   - `intent_completed` — persona finished, intent moved to `done`.
   - `intent_failed` — persona errored; the event has an `error` field.
   - `daemon_stopping` — `/wf-stop` was invoked.

   For each notification, parse the JSON and write a one-line human update to the operator. Examples:
   - `intent_dispatched`: `Hex (head-eng) is starting on intent_abc123 — "ship parked logging feature".`
   - `intent_completed`: `Hex finished intent_abc123.`
   - `intent_failed`: `Anton failed intent_def456: <error>.`

   Surface events as they arrive, one at a time. Do not batch-summarize.

7. **Report initial state.** After the Monitor is armed, report:
   ```
   Workestrator started (PID <pid>).
   Logs:   .workforce/workestrator.log
   Events: .workforce/events.jsonl (streaming into this session)
   ```
