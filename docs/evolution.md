# Self-Evolution

## How It Works

Every cycle, Phase 3 reads the entire codebase and asks the LLM to propose improvements.

```
1. Read source files (bot/**/*.py, config/*.json, requirements.txt)
   - Files truncated at 20,000 bytes before sending
2. Send to LLM with structured system prompt
3. Parse JSON response: { version, summary, changes[], suggestions[] }
4. Validate and apply each change (see safety rules)
5. Write version.txt
6. Commit changed files
```

## LLM Prompt Contract

The LLM receives:
- `status` dict (current state, active features, earnings, errors)
- Full codebase content

The LLM must return **only** a JSON object:

```json
{
  "version": "X.Y.Z",
  "summary": "one-sentence description",
  "suggestions": [
    {
      "title": "short title",
      "description": "what it unlocks or earns",
      "secret_needed": "SECRET_NAME or null",
      "estimated_weekly_usd": 0
    }
  ],
  "changes": [
    {
      "file": "bot/some_file.py",
      "content": "COMPLETE new file content — never a diff",
      "reason": "why"
    }
  ]
}
```

## Safety Rules

All enforced in `bot/evolution.py` — cannot be removed by the LLM evolving the file, because the evolution engine validates its own output before applying it.

| Rule | Detail |
|------|--------|
| Allowed paths | `bot/`, `docs/`, `config/`, `requirements.txt`, `version.txt` |
| Forbidden paths | `.github/`, `.git/`, anything with `..` |
| Max changes | 3 per cycle |
| Python validation | `ast.parse()` before write — syntax errors rejected |
| Backup | Original copied to `.evolution_backups/<name>.<timestamp>.bak` |

## Versioning

- LLM proposes new version in response
- Accepted if matches `^\d+\.\d+\.\d+$`
- Rejected → auto-bump current patch version

Convention:
- Patch: bug fixes
- Minor: new features
- Major: rewrites

## Skipping Evolution

```
skip evolution
```

Write to `command.txt`, commit. Phase 3 is skipped for that cycle; all other phases run normally.

## Evolution Backups

`.evolution_backups/` is gitignored. Each overwritten file gets a timestamped copy:

```
.evolution_backups/
  llm.py.20260430_171700.bak
  status.py.20260430_181700.bak
```

To recover: copy the `.bak` file back to its original path.
