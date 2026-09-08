# Working instructions: Your Friendly Neighbourhood

## Read first

Read `docs/project-context.md`, `docs/requirements.md` and `docs/data-and-api.md`, then inspect the relevant files in `docs/references/`. Use the current user request and explicit corrections as the latest direction. The handover consolidates the discussion; it does not prove that every recommendation was approved.

## Product

- Build for renters unfamiliar with Melbourne, including new immigrants, international students and interstate migrants.
- Use the name **Your Friendly Neighbourhood**. UrbanLens Melbourne and the planner persona are superseded.
- Implement Home, Compare and Area Details according to the supplied wireframes and documented text corrections.
- Keep the interface simple, accessible and written in plain English. Icons and titles share a row; descriptions follow beneath them.
- Do not add a methodology section, map, accounts, forums, property listings, ML forecasts, Redis or an overall best-neighbourhood score without a scope change from the user.
- Keep source dates, measure explanations and material limitations discoverable without making the renter read technical documentation.

## Architecture

- JavaScript, Vue, Nuxt and Tailwind; Node.js for tooling and static generation.
- Python FastAPI REST API returning JSON; read-only SQLite at runtime.
- Separate Python pipeline for acquisition/profiling/cleansing/spatial aggregation/database construction.
- Render Static Site and Render Web Service, with GitHub checks and deployments. No Monash development server, per the user's OLA clarification.
- Keep UI, API and pipeline work independent through one shared contract and a synthetic seed database. Replace the database content, not the API shape, when verified real data arrives.

## Data correctness

- Treat wireframe numbers and fixture records as synthetic. Never publish them as real suburb statistics.
- Keep area codes as strings and record boundary edition. Do not join suburb and SA2 observations by similar names.
- An SA2 can cover part of a suburb or several suburbs. A suburb lookup can have several SA2 matches.
- Census 2021 rent must be labelled as 2021 Census reported rent. It is not current advertised rent.
- Preserve nulls, suppression and coverage flags. Unknown is not zero.
- Store every indicator's units, reference period, provenance and method version.
- Do not invent downloaded filenames, field codes, coverage thresholds, public-access filters or PTAL semantics. Inspect source metadata and sample records first.
- Benchmark relative scores against a fixed, versioned eligible set, never against the user's selected two or three areas.
- Resolve production scoring decisions listed in `docs/data-and-api.md` before publishing ratings.

## Workflow and verification

- Inspect existing code and uncommitted changes first; preserve unrelated work.
- Implement a small end-to-end slice early. Do not wait for the entire real-data pipeline to finish before starting the application.
- Validate response models, calculation edge cases, database integrity, the three-page journey, accessibility and deployed configuration in proportion to the change.
- Keep mock and real releases separate. Reject synthetic data in the final assessment release unless explicitly labelled as a demo and approved as such.
- Read the copied Assessment 2 instructions before claiming assessment compliance. Treat the user's specific OLA corrections as amendments; unrelated assessment requirements still apply.
- Update these documents when decisions change. Record assumptions, validation evidence and outstanding limitations honestly.
- Do not create recurring automation, contact teammates, push to GitHub or deploy to an external service unless that action is authorised by the user.
