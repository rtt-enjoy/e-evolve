# Code-Tech Earning Queue

Refreshed: 2026-05-18T03:34:09.632935+00:00
Daily target: $10.00

## Requirements

- Prefer work that can be reproduced from public logs, docs, or a clean checkout in under 30 minutes.
- Prefer boring maintenance where the failure and expected fix are visible without private context.
- Require a deterministic command, log, docs page, or issue thread that an AI agent can use as proof.
- Keep the first contribution small enough for the bot to patch, test, and explain automatically.
- Do not count discovery or speculative upside as earnings.

## Underserved Focus

- failing CI with a small, reproducible fix
- dependency migration or deprecation cleanup
- documentation examples that no longer run
- test flakiness with a clear failure signature
- type hints, packaging metadata, and release automation
- small compatibility fixes in niche developer tools
- abandoned but still-installed packages with open compatibility issues
- template repos and starter kits whose quickstarts fail on current runtimes
- internal-tool shaped repos where businesses need maintenance more than novelty
- release-note gaps after breaking API changes
- low-glamour data import/export bugs in small SaaS integrations

## Strategy Playbook

- Start from maintenance pain, not idea novelty.
- Use proof as the sales asset: failing command, failing log line, short before/after note.
- Favor repeatable chores that can become productized services.
- Look for AI-automatable chores: stale issues with logs, forks with small fixes, unanswered install failures.
- Bundle adjacent fixes only after trust exists.
- Treat content as deal flow from solved niche issues.

## Avoid

- Large rewrites, vague feature requests, design taste debates, and architecture arguments without a failing proof.
- Repos with no maintainer response, no recent users, no releases, and no business signal.
- Crowded prize or beginner issues where many contributors compete for low-value visibility.
- Unpaid speculative requests that need private context before value can be proven.
- Crypto/NFT hype work unless there is a concrete paid maintenance task and bounded risk.

## Ranked Leads

1. Starter template compatibility repair
   - Score: 94/100
   - Value signal: $0.00
   - Why: clean-checkout install/build proof fits automated AI patching; template compatibility fixes are easy for maintainers to review
   - Next: Pick one starter repo with a failing quickstart, capture the install/build error, patch the dependency or command, and offer the cleanup at a fixed price.
2. Package migration cleanup for small Python projects
   - Score: 86/100
   - Value signal: $0.00
   - Why: public proof makes this suitable for automated AI patching; CI/test work is concrete and easy for maintainers to accept
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
3. Deprecated GitHub Actions cleanup
   - Score: 86/100
   - Value signal: $0.00
   - Why: public proof makes this suitable for automated AI patching; CI/test work is concrete and easy for maintainers to accept
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
4. Flaky test triage for tiny open-source maintainers
   - Score: 64/100
   - Value signal: $0.00
   - Why: public proof makes this suitable for automated AI patching; CI/test work is concrete and easy for maintainers to accept
   - Next: Open the latest failed job, capture the failure signature, and patch only the failing path.
5. Broken README examples in niche SDK repos
   - Score: 60/100
   - Value signal: $0.00
   - Why: public proof makes this suitable for automated AI patching; working docs convert into trust quickly
   - Next: Run the documented example from a clean checkout and submit the corrected command or snippet.
