# E-Evolve Dashboard Frontend

This is the React/Vite/Tailwind dashboard for GitHub Pages.

Python remains the backend data publisher. During Phase 5, `bot/dashboard.py`
writes:

- `../docs/status.json`
- `../docs/earnings-log.md`

The frontend reads those files in the browser and polls `status.json` every
minute.

## Local Development

```bash
pnpm install
pnpm dev
```

Local dev shows the offline agent screens by default. Those screens are hidden
from production builds unless `VITE_ENABLE_OFFLINE_AGENT_UI=1` is set.

## Build For GitHub Pages

```bash
pnpm build
```

Vite writes the static app to `../docs` without deleting existing documentation
files.

## CI Deployment

Frontend changes are built and deployed by `.github/workflows/frontend.yml`.
The workflow uses pnpm, uploads the generated `docs/` directory as a GitHub
Pages artifact, and deploys it through GitHub Pages Actions.
