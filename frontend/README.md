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

Dev and production render the same sections; there is no gated UI mode.

## Structure

```
src/sections/registry.ts   ← declares sections + which status.json keys they use
src/sections/*Section.tsx  ← one lazy-loaded page per route
src/components/ui.tsx      ← shared primitives (Tile, Card, Disclosure, …)
src/components/JsonNode.tsx ← generic renderer for unmapped/new bot fields
src/utils/route.ts         ← hash router (#/leads, #/leads/3)
```

Adding a section means adding one entry to `registry.ts` and one component. A
section is auto-hidden when the keys it declares are empty, and any status.json
key no section claims is rendered generically in the Data section — so new
backend fields show up without touching the frontend. See
`../docs/frontend-dashboard.md` for the full contract.

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
