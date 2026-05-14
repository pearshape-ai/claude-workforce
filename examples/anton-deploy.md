# Deploy `<your-project>` 1.2.3 to staging

**Spec ID:** 20260514-deploy-1-2-3-staging
**Date:** 2026-05-14T10:30:00Z
**Author:** &lt;operator-name&gt;
**Target agent:** Anton (SRE)

---

## Goal

`<your-project>` 1.2.3 is the running version on `<your-staging-host>`, verified healthy, with a reality record submitted describing the deploy.

## Scope

### In scope
- Routine recreate of the `<your-project>` service container on `<your-staging-host>` against the `:latest` image tag (1.2.3 just got pushed).
- Verification: health endpoint, container status, log tail.

### Out of scope
- Schema migration (1.2.3 doesn't include one; if it ever does, this becomes a different shape of intent).
- Profile flip — keep whatever profile is currently active.
- Terraform changes.
- Secret rotation.

## Pre-approved defaults

- `COMPOSE_PROFILES`: whatever's currently active. No flip.
- Image tag: `:latest`.
- Mechanism: `docker compose pull && docker compose up -d <service-name>`.
- No bootstrap, no terraform.

State the classification + planned mechanism upfront in your turn 1; then execute without re-asking the operator about these defaults.

## Targets

| Target | What to do | Why |
|---|---|---|
| `<your-staging-host>` | Recreate `<service-name>` container from the new image | The deploy itself |
| `<your-records-repo>/eng/<your-infra-repo>/<YYYYMMDD>-deploy-1-2-3-staging.md` | Reality record describing the deploy | Operational delta in the graph |

## Acceptance criteria

- [ ] `<service-name>` container is running on `<your-staging-host>` against the new image digest.
- [ ] Health endpoint returns 200 (e.g. `curl https://<your-staging-host>/health`).
- [ ] No startup errors in the container's first ~20 log lines.
- [ ] Reality record committed + pushed, submitted via the `pearscarf` MCP with `op_area=reality`.
- [ ] This intent's status set to `done`.

## Done definition

1.2.3 is live on staging, the reality record is in the graph, this intent's status is `done`. If health fails, the intent is `cancelled` with the failure surfaced in the reality record.

## Notes / context

- **Working paths (operator's checkouts — fill in your absolute paths):**
  - your infra repo: `/path/to/<your-infra-repo>/`
  - your records repo: `/path/to/<your-records-repo>/`
- **Deploy mechanism**: use whatever script the operator's infra repo provides (e.g. `runtime/redeploy.sh`). Don't invent a new one in this session.
- **How to submit:** call `submit_intent` with `owner=anton`, `owner_role=sre`, `intent_type=task`. If you want Linda's launch post to depend on this deploy completing first, set `depends_on=[<this-intent-id>]` on Linda's intent after submitting this one.
