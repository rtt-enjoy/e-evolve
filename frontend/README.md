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
npm install
npm run dev
```

## Build For GitHub Pages

```bash
npm run build
```

Vite writes the static app to `../docs` without deleting existing documentation
files.
