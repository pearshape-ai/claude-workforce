# Add `--verbose` flag to the main CLI

**Spec ID:** 20260514-cli-verbose-flag
**Date:** 2026-05-14T09:00:00Z
**Author:** &lt;operator-name&gt;
**Target agent:** Hex (engineer)

---

## Goal

Operators of `<your-cli>` can run any subcommand with `--verbose` to see debug-level output, instead of needing to set an environment variable.

## Scope

### In scope
- Add a top-level `--verbose` / `-v` flag to `<your-cli>` that, when set, raises the log level to `DEBUG`.
- Per-commit chores in `<your-project>`: bump `__version__` to the next patch and add a CHANGELOG entry.

### Out of scope
- A logger-config refactor — keep the existing logger; just adjust its level on `--verbose`.
- Per-subcommand verbose levels.
- A `--quiet` companion flag (separate ship if anyone asks).

## Targets

| Target | What to do | Why |
|---|---|---|
| `<your-project>/<your-package>/cli.py` (or wherever the top-level click group lives) | Add `--verbose / -v` flag; on True, set the root logger to `logging.DEBUG` before dispatching the subcommand | The feature itself |
| `<your-project>/<your-package>/__init__.py` | Bump `__version__` to the next patch | Per-commit chore |
| `<your-project>/CHANGELOG.md` | New entry, 1–2 sentences, high-level | Per-commit chore |

## Acceptance criteria

- [ ] `<your-cli> --verbose <subcommand>` prints `DEBUG`-level lines.
- [ ] `<your-cli> <subcommand>` (no flag) prints `INFO` and above (current behavior).
- [ ] `<your-cli> --help` lists the `--verbose / -v` flag.
- [ ] Pre-commit gates pass.
- [ ] Tests pass (no new tests required for this trivial flag).
- [ ] Per-commit chores done: version bumped, CHANGELOG entry present.
- [ ] Completion reality record drafted at `<your-records-repo>/eng/<your-project>/<YYYYMMDD>-cli-verbose-flag.md`, committed + pushed, and submitted via the `pearscarf` MCP `submit_record` with `op_area=reality`.

## Done definition

`--verbose` is on `<your-project>/main` at the bumped version, the reality record is in the graph, this intent's status is `done`.

## Notes / context

- **Working paths (operator's checkouts — fill in your absolute paths):**
  - your project: `/path/to/<your-project>/`
  - your records repo: `/path/to/<your-records-repo>/`
- This is a copy-paste example. Replace `<your-cli>`, `<your-project>`, `<your-package>`, `<your-records-repo>`, and `<operator-name>` with your real values before submitting.
- **How to submit:** in any Claude Code session with the `pearscarf` MCP loaded, ask Claude to call `submit_intent` with this body as `body`, `owner=hex`, `owner_role=eng`, `intent_type=task`.
