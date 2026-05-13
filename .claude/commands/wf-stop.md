---
description: Stop the workestrator daemon and the event Monitor (if armed in this session)
---

Stop the workestrator daemon for this claude-workforce installation. Workestrator handles `SIGTERM` cleanly — it cancels in-flight agents, emits a `daemon_stopping` event, and exits — so this command should rarely need to escalate to `SIGKILL`.

## Steps

1. **Find the daemon.** Read `.workforce/workestrator.pid`. If the file is missing, or the PID it contains is not alive (`kill -0 <pid>` fails), report `No workestrator daemon is running.` and stop — there's nothing to do.

2. **Send SIGTERM.** Run `kill <pid>`. Do NOT use SIGKILL on the first attempt — `daemon_stopping` is one of the events the operator may want to see in this session, and SIGKILL skips the handler that emits it.

3. **Wait for graceful exit.** Poll `kill -0 <pid>` once per second for up to 30 seconds. If the process exits during the wait, move on.

4. **Force-kill if needed.** If the process is still alive after 30 seconds, warn the operator (`workestrator did not exit gracefully — sending SIGKILL`) and run `kill -9 <pid>`. Then wait a moment and verify it's gone.

5. **Clean up the PID file.** Remove `.workforce/workestrator.pid`.

6. **Stop the event Monitor if armed in this session.** Use TaskList to find any active Monitor task watching `.workforce/events.jsonl`. If one exists, TaskStop it. If `/wf-stop` is being run in a fresh session that didn't arm a Monitor, this step is a no-op — the daemon's death silences the event stream on its own.

7. **Report.** Confirm: `Workestrator stopped (PID was <pid>).` Note in the report whether SIGKILL was needed.
