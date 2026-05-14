# Example intent bodies

Copy-paste-ready intent bodies, one per persona. Use them as starting points when authoring your own intents — or chain them together as a smoke test of the full workforce loop.

| File | Persona | Shape |
|---|---|---|
| `hex-ship-feature.md` | Hex (engineer) | Ships a small feature in your code repo, bumps version + CHANGELOG, commits + pushes, emits a reality record |
| `anton-deploy.md` | Anton (SRE) | Routine deploy of a new version to a target host, with verification + reality record |
| `linda-launch-post.md` | Linda (comms) | Drafts a blog post announcing what shipped, grounded in the graph, saved to drafts for operator review |
| `cindy-social-thread.md` | Cindy (social) | Drafts an X thread + LinkedIn post adapting Linda's narrative to platform shapes |

## How to use them

Each file is a **complete intent body** — the markdown content you'd pass as the `body` argument to the `pearscarf` MCP's `submit_intent` tool.

From a Claude Code session with the `pearscarf` MCP loaded (open one inside your `claude-workforce/` install — `.mcp.json` auto-registers it), say something like:

> *"Submit this as an intent. Use owner=hex, owner_role=eng, intent_type=task."* — then paste the body from `hex-ship-feature.md`.

Your Claude will call `submit_intent` for you. The intent lands in PearScarf with `status=todo`, and the running workestrator daemon (started via `/wf-start`) picks it up on the next poll.

## Chaining the four into a full ship → announce flow

If you want to watch the whole loop run end-to-end:

1. Submit `hex-ship-feature.md` first. Capture the returned `intent_id`.
2. Submit `anton-deploy.md` with `depends_on=[<hex-intent-id>]`.
3. Submit `linda-launch-post.md` with `depends_on=[<hex-intent-id>, <anton-intent-id>]`.
4. Submit `cindy-social-thread.md` with `depends_on=[<linda-intent-id>]`.

Workestrator will run them in order, gating each on its upstream reaching `done`. `/wf-status` shows the queue at any time.

## Customizing for your project

Each example uses placeholder strings — `<your-project>`, `<your-cli>`, `<your-records-repo>`, etc. Find-and-replace them with your real values before submitting. The bodies are intentionally generic so they read as templates, not toy examples.

## Authoring your own

The shape every intent body should follow:

- **Title** — single line, what the persona will ship.
- **Spec ID / Date / Author / Target agent** — small metadata block. `Date:` is always a full ISO 8601 datetime with timezone (e.g. `2026-05-14T10:30:00Z`), not a date-only string — this matches PearScarf's record format expectation and preserves submission ordering for same-day intents.
- **Goal** — one sentence stating the operational delta.
- **Scope** — In scope / Out of scope, explicit.
- **Targets** — table of file / what / why per target.
- **Acceptance criteria** — checklist the persona walks through before declaring done.
- **Done definition** — one sentence on what has to be true to consider the intent complete.
- **Notes / context** — absolute working paths, role-specific gotchas, how to submit.

The shape comes from the `roles/<persona>/skills.md` files that ship with claude-workforce — each persona's loop reads the intent body expecting this structure.
