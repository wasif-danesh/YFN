# Your Friendly Neighbourhood: development handover

**Historical handover.** The root [team README](README.md) is now the current onboarding and development guide. Real datasets and pipeline code have since been added; the original status statements and proposed layout below describe the earlier handover stage.

Prepared 8 September 2026 from this project conversation and the local documents listed in `docs/references/README.md`.

This is a portable development handover, not an application or a complete conversation export. It preserves the important implementation decisions, source documents and unresolved questions. No repository has been created, no code has been deployed, and no datasets have been downloaded or validated by creating this package.

## Start here

1. Copy the contents of this folder into your development repository. Keep `AGENTS.md` at the repository root and `docs/` beside it. Merge with existing files if names overlap; do not blindly overwrite them.
2. Open that repository as a project in Codex and select the desired model.
3. Start with the prompt below. The handover files provide context even in a fresh task.
4. Resolve the short decision list in `docs/project-context.md` before committing to production calculations. UI and API scaffolding can proceed with explicitly synthetic fixtures.

## Suggested first development prompt

> Read AGENTS.md and the three handover documents under docs/. Inspect the reference wireframes and existing repository. Build the Iteration 1 skeleton for Your Friendly Neighbourhood: a static Nuxt/Vue/JavaScript/Tailwind frontend, a FastAPI backend and a read-only SQLite database seeded with clearly synthetic data. Preserve the Home, Compare and Area Details layouts. Establish one shared API contract so frontend, backend and real-data preparation can proceed independently. Implement the full search-to-compare-to-details journey and meaningful tests. Record unresolved data decisions without inventing production values or treating provisional scoring as approved. Prepare Render configuration, but do not publish anything or modify an existing deployment unless requested.

## Contents

| Item | Purpose |
|---|---|
| `AGENTS.md` | Instructions and reading order for a development assistant |
| `docs/project-context.md` | Current direction, superseded ideas and decisions to resolve |
| `docs/requirements.md` | Page behaviour, iterations, parallel work and acceptance criteria |
| `docs/data-and-api.md` | Data preparation, proposed schema, calculations and JSON contract |
| `docs/references/` | Copies of the proposal, earlier specification, assessment guidelines and three wireframes |

The JSON fields, schema refinements and percentile tie rule in this handover are implementation proposals. They are not evidence of prior team approval. The copied documents are preserved unchanged and can contain wording superseded by later discussion.

## Initial build layout (proposed)

```text
AGENTS.md
docs/
frontend/
backend/
pipeline/
data/
  manifests/
  raw/         # original downloads, normally excluded from Git
  staging/     # generated source-specific tables
  curated/     # validated inputs for database builder
  releases/    # versioned database build artefacts
tests/
render.yaml
.github/workflows/
```

Use one repository for the four-person team initially. Keep production dataset downloads and generated artefacts out of Git unless their size and licences make inclusion appropriate. Never commit credentials. Resolve actual package/runtime versions during implementation, record them and commit lockfiles; this handover does not claim particular versions or hosting quotas are current.
