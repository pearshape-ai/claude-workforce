# Draft a launch blog post for `<your-project>` 1.2.3

**Spec ID:** 20260514-launch-post-1-2-3
**Date:** 2026-05-14T13:00:00Z
**Author:** &lt;operator-name&gt;
**Target agent:** Linda (comms)

---

## Goal

A drafted blog post announcing what shipped in `<your-project>` 1.2.3, grounded in the PearScarf graph (not in this spec body), saved at the operator's drafts path awaiting review.

## Scope

### In scope
- One blog post, ~400–800 words, builder voice (per your standard prompt).
- Anchored on the operational delta — what 1.2.3 makes possible that earlier versions didn't.
- Save to `<your-drafts-repo>/comms/drafts/20260514-launch-post-1-2-3.md`.

### Out of scope
- Social posts (X, LinkedIn, Reddit) — those are Cindy's territory, a separate intent.
- Publishing the blog post live (the drafts repo is `requires_approval` — operator reviews + commits).
- Visual assets (diagrams, screenshots) — Linda surfaces what's needed; operator handles asset creation.

## Pre-requisites (graph-extraction wait)

This intent should depend on the engineering / deploy intents that ship 1.2.3 (set `depends_on=[<eng-intent-id>, <deploy-intent-id>]` at submit time). But even after those reach `done`, the corresponding reality records may not yet be `indexed` in the graph.

Before relying on `query_facts`, verify the relevant records are indexed:

1. Call `query_records(since='<your-current-time-minus-15-minutes>', limit=10)` to find recent records about 1.2.3.
2. For each candidate `record_id`, check `get_record_status(record_id)`. If not yet `indexed`, sleep 30 seconds and retry up to 3 times (~90s total wait).
3. Once indexed, proceed to `query_facts(subject="<your-project>", edge_label="TRANSITIONED")` to ground the post.

If after the wait the records still aren't indexed, surface the situation clearly and stop — better to fail loudly than draft from stale state.

## Targets

| Target | What to do | Why |
|---|---|---|
| `<your-drafts-repo>/comms/drafts/20260514-launch-post-1-2-3.md` | New file, the blog post draft. Markdown body, no frontmatter required. | The artifact |

## Acceptance criteria

- [ ] Draft saved at the path above.
- [ ] Post text grounded in graph facts queried *this session* (not invented or paraphrased from training data).
- [ ] Builder voice — no hype words.
- [ ] Specific named handles for what 1.2.3 ships (CLI flags, MCP tools, env vars, function names — whatever the graph confirms).
- [ ] No fabricated install commands, package names, or CTAs (`pip install …`, *"available on PyPI"*, etc.) unless the graph confirms them.
- [ ] Drafts path is `requires_approval` per your config — leave the file uncommitted; end-of-session "pending review" note.
- [ ] **Reality record DEFERRED** — drafts at a `requires_approval` path aren't yet reality; the record waits until the operator commits/publishes. Surface `sor record deferred — pending operator commit`.
- [ ] This intent's status set to `done` (the deliverable — the draft — was completed; the record defers).

## Done definition

Blog draft exists at the path above (uncommitted, awaiting operator review), this intent's status is `done`, and a `sor record deferred — pending operator commit` note appears in the end-of-session summary.

## Notes / context

- **Working paths (operator's checkouts — fill in your absolute paths):**
  - workspace root: `/path/to/<your-workspace>/`
  - your drafts repo: `/path/to/<your-drafts-repo>/`
- **How to submit:** call `submit_intent` with `owner=linda`, `owner_role=comms`, `intent_type=task`, `depends_on=[<eng-intent-id>, <deploy-intent-id>]` if you want this gated on prior work.
