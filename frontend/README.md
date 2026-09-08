# Frontend workspace

Reserved for the Nuxt/Vue/JavaScript/Tailwind application. Application code and package files have not been created yet. See the root [README](../README.md#local-application-development) for the intended setup and commands.

Use `app/pages/` for Home, Compare and Area Details, `app/components/` for shared UI, `app/composables/` for a single API client, and `app/assets/css/` for styling. Keep tests in `tests/`, web-visible assets in `public/`, and Nuxt configuration and package/lockfiles here. The proposed `app/` convention targets Nuxt 4; confirm package compatibility when scaffolding.

`public/` must never contain SQLite, source snapshots or private configuration. Read the API base URL through Nuxt public runtime configuration. On static hosting that URL is baked into the generated site: changing it requires a rebuild. Preserve quality flags and source dates in the UI.
