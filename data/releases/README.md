# Runtime database releases

This folder is reserved for a reviewed runtime database and its matching release manifest. There is no production-approved database here yet.

The initial deployment convention is `active.sqlite` plus `manifest.json`, committed together after validation. The manifest should identify the release, database SHA-256, data mode, boundary edition, method versions, source-manifest hash and approval/validation status. Git commit history versions this pair. Never hand-edit the database in Render.

Keep development samples in `../samples/`. The current sample has `publication_ready=false`; moving or renaming it does not approve its methods or make it a production release. The application implementation must define and test release validation before enabling deployment. A clearly labelled demonstration release requires its own explicit approval.

When updating real data, rebuild offline, validate, review changes in values/coverage, then submit the database and manifest in one PR. The API build packages this small artifact from the same commit as its code. Raw spatial downloads do not run during application deployment. If the artifact later becomes too large for Git, switch to an immutable, checksummed artifact download during the build and document the new process.
