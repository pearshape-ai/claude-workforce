# Draft X thread + LinkedIn post for `<your-project>` 1.2.3 launch

**Spec ID:** 20260514-social-1-2-3-launch
**Date:** 2026-05-14T14:30:00Z
**Author:** &lt;operator-name&gt;
**Target agent:** Cindy (social)

---

## Goal

Drafted social posts (one X thread, one LinkedIn post) announcing `<your-project>` 1.2.3, grounded in the PearScarf graph and adapted to each platform's shape.

## Scope

### In scope
- X thread (1–4 tweets, hook → meat → CTA shape).
- LinkedIn post (1300–1900 chars, builder-voice).
- Both saved to the operator's drafts repo for review before posting.

### Out of scope
- Reddit submission (subreddit choice + tone deserves its own intent).
- Actually posting the artifacts live — drafts only this iteration. The operator (or a future Cindy intent with platform credentials wired) publishes.
- Image / diagram creation. Surface what visuals would help; operator generates them.

## Pre-requisites

If Linda's blog-post intent ran before yours, prefer translating from her draft. Read it first:

```
<your-drafts-repo>/comms/drafts/20260514-launch-post-1-2-3.md
```

If the file exists, treat its claims and voice as the canonical narrative; adapt to platform shape. If it doesn't exist yet, ground directly in the PearScarf graph.

Either way, **re-query the graph immediately before saving the drafts** — social cadence moves faster than blog drafts; reality might have shifted.

## Targets

| Target | What to do | Why |
|---|---|---|
| `<your-drafts-repo>/social/drafts/20260514-1-2-3-x-thread.md` | The X thread, one tweet per markdown paragraph | The artifact |
| `<your-drafts-repo>/social/drafts/20260514-1-2-3-linkedin.md` | The LinkedIn post, single markdown body | The artifact |

## Acceptance criteria

- [ ] Both drafts saved at the paths above.
- [ ] Each draft is grounded in graph facts queried *this session*.
- [ ] No hype vocabulary (revolutionary, intelligent, next-generation, transform, empower, unleash, game-changing).
- [ ] No fabricated install commands or CTAs that the graph doesn't confirm.
- [ ] X thread leads with the operational delta (not "we shipped X"), tweet 1 reads in <240 chars.
- [ ] LinkedIn post has a strong first-line hook, 1300–1900 chars, ~3–5 paragraph body.
- [ ] Drafts path is `requires_approval` — leave the files uncommitted; end-of-session "pending review" note.
- [ ] **Reality records DEFERRED** — same rule as Linda. Posts aren't yet reality until they're actually published.
- [ ] This intent's status set to `done` (drafts delivered; reality records will land after the operator posts).

## Done definition

Both draft files exist at the paths above (uncommitted, awaiting operator review), this intent's status is `done`, and the end-of-session summary lists the drafts pending operator review + post + the deferred reality records.

## Notes / context

- **Working paths (operator's checkouts — fill in your absolute paths):**
  - your drafts repo: `/path/to/<your-drafts-repo>/`
- **No platform credentials assumed.** If your Cindy setup has LinkedIn / X MCP tools wired and the operator wants autonomous posting, drop the "draft only" framing from this example and add posting + reality-record submission to the acceptance criteria.
- **How to submit:** call `submit_intent` with `owner=cindy`, `owner_role=social`, `intent_type=task`, `depends_on=[<linda-intent-id>]` if you want this gated on Linda's blog draft completing first.
