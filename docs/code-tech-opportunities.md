# Code-Tech Earning Queue

Refreshed: 2026-05-17T15:19:56.911459+00:00
Daily target: $10.00

## Requirements

- Prefer work that can be reproduced from public logs, docs, or a clean checkout in under 30 minutes.
- Prefer boring maintenance where the buyer already feels pain: failing CI, broken install paths, stale dependencies, or unusable examples.
- Require a visible owner, maintainer, sponsor, bounty, issue activity, or obvious business value before spending deep effort.
- Keep the first contribution small enough to review in one sitting, then convert repeated pain into a fixed-scope maintenance offer.
- Do not count discovery, estimates, or speculative upside as earnings until money is received or manually reconciled.

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

- Start from maintenance pain, not idea novelty: find places where a maintainer or small business already lost time.
- Use proof as the sales asset: failing command, failing log line, fixed branch, and a short before/after note.
- Favor repeatable chores that can become productized services: dependency upgrades, CI modernization, docs repair, packaging cleanup, and migration guides.
- Look below the obvious bounty surface: stale issues with recent users, forks carrying private fixes, unanswered install failures, and docs comments that expose conversion leaks.
- Bundle adjacent fixes only after trust exists; the first patch should make one painful thing obviously better.
- Treat content as deal flow: every solved niche issue can become a short article, comparison, checklist, or service page aimed at the same pain.

## Avoid

- Large rewrites, vague feature requests, design taste debates, and architecture arguments without a failing proof.
- Repos with no maintainer response, no recent users, no releases, and no business signal.
- Crowded beginner issues where dozens of contributors compete for low-value visibility.
- Unpaid speculative requests that need private context before value can be proven.
- Crypto/NFT hype work unless there is a concrete paid maintenance task and bounded risk.

## Ranked Leads

1. [[ Bounty $5k ] [ Solidity ] Fix AMMPool swap doesn't emit indexed events for off-chain indexing — v2 upgrade](https://github.com/ClankerNation/OpenAgents/issues/165)
   - Score: 100/100
   - Value signal: $5700.00
   - Why: visible or inferred value around $5700.00; CI/test work is concrete and easy for maintainers to accept
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
2. [[ Bounty $3k ] [ Solidity ] Fix VestingWallet doesn't support token change or migration — mainnet prep](https://github.com/ClankerNation/OpenAgents/issues/170)
   - Score: 100/100
   - Value signal: $3300.00
   - Why: visible or inferred value around $3300.00; CI/test work is concrete and easy for maintainers to accept
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
3. [Benchmark APIs with p50, p95, p99 latency, RPS, error rate and TTFB](https://github.com/SecureBananaLabs/bug-bounty/issues/30)
   - Score: 100/100
   - Value signal: $750.00
   - Why: visible or inferred value around $750.00; CI/test work is concrete and easy for maintainers to accept
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
4. [[RFC][epic] Out-of-process sidecar worker mode for crash-isolated DCC actions](https://github.com/loonghao/dcc-mcp-core/issues/998)
   - Score: 98/100
   - Value signal: $0.00
   - Why: CI/test work is concrete and easy for maintainers to accept; migration chores are neglected but urgent
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed‑price cleanup.
5. [[BOUNTY $150] AGENT: Claude Code sub-agent that reviews a PR and posts a structured comment](https://github.com/claude-builders-bounty/claude-builders-bounty/issues/4)
   - Score: 96/100
   - Value signal: $150.00
   - Why: visible or inferred value around $150.00; working docs convert into trust quickly
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
6. [[ Bounty $9k ] [ Solidity ] Fix reentrancy in StakingRewards withdraw and claimRewards — P0 bug](https://github.com/ClankerNation/OpenAgents/issues/86)
   - Score: 93/100
   - Value signal: $9000.00
   - Why: visible or inferred value around $9000.00; CI/test work is concrete and easy for maintainers to accept
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
7. [[ Bounty $2k ] [ API ] Fix ratelimit.py doesn't differentiate authenticated vs anonymous limits — backwards compat](https://github.com/ClankerNation/OpenAgents/issues/200)
   - Score: 93/100
   - Value signal: $2200.00
   - Why: visible or inferred value around $2200.00; CI/test work is concrete and easy for maintainers to accept
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
8. [[ Bounty $1k ] [ Solidity ] Fix cross-chain replay attack in TokenBridge signature verification — v2 implementation](https://github.com/ClankerNation/OpenAgents/issues/55)
   - Score: 93/100
   - Value signal: $1350.00
   - Why: visible or inferred value around $1350.00; CI/test work is concrete and easy for maintainers to accept
   - Next: Verify bounty rules, reproduce the issue, then prepare the smallest passing patch.
