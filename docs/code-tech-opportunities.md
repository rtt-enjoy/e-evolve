# Code-Tech Earning Queue

Refreshed: 2026-06-24T15:12:48.693865+00:00
Daily target: $10.00

## Requirements

- Default to online research and the configured free/low-cost research LLM before local fallback.
- Prefer leveraged remote-service work: productized services, retainers, async delivery, and AI-assisted systems.
- Prefer work that can be reproduced from public logs, docs, or a clean checkout in under 30 minutes.
- Require a deterministic command, log, docs page, or issue thread that an AI agent can use as proof.
- Keep the first contribution small enough for the bot to patch, test, and explain automatically.
- Do not count discovery or speculative upside as earnings.

## Reference Sources

- [15 High-Paying Remote Jobs With a 4-Hour Work Week](https://freedium-mirror.cfd/https://medium.com/@startup_Ideas/15-high-paying-remote-jobs-with-a-4-hour-work-week-and-how-people-actually-get-them-7e8d3562ff99): Use specialization, automation, productized services, retainers, async work, and AI-powered systems to detach income from hours.

## Remote Service Niches

- AI prompt and workflow consulting
- no-code or low-code automation setup
- AI customer-support knowledge base cleanup
- analytics dashboard and reporting automation
- SEO/content operations systems
- CRM, spreadsheet, and data import/export automation
- developer productivity and CI maintenance retainers
- async technical documentation fixes
- productized audit/checklist services
- micro-SaaS setup, migration, and operations help

## Online AI Brief


## Underserved Focus

- AI prompt/workflow consulting where public before-after examples prove value
- productized automations that reduce repeated admin work for a small niche
- retainer-friendly reporting, CRM, and support-ops cleanup
- async deliverables that can be reviewed without meetings
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

- Use online sources first, then ask the research LLM to turn fresh demand signals into ranked owner actions.
- Borrow the article's leverage principle: sell outcomes, systems, and repeatable assets instead of hours.
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

1. [Built an automation for a local business and got paid $1500 — sharing the process](https://www.reddit.com/r/smallbusiness/comments/1rx0yi0/built_an_automation_for_a_local_business_and_got/)
   - Score: 100/100
   - Value signal: $1500.00
   - Why: visible or inferred value around $1500.00; public proof makes this suitable for automated AI patching
   - Next: Open the latest failed job, capture the failure signature, and patch only the failing path.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Built an automation for a local business and got paid $1500 — sharing the process
     Source: reddit:r/smallbusiness
     URL: https://www.reddit.com/r/smallbusiness/comments/1rx0yi0/built_an_automation_for_a_local_business_and_got/
     Why this is suitable: visible or inferred value around $1500.00; public proof makes this suitable for automated AI patching
     First step: Open the latest failed job, capture the failure signature, and patch only the failing path.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: A small win I wanted to share. Over the last several months I’ve been learning automation tools (APIs, scraping, Python, workflow tools etc.) mostly out of curiosity. Last month I decided to see if I could actually turn it into something useful for a business. I reached out to a few niche consulting firms and asked them about repetitive work in their workflow. One company told me they spend a lot of time manually pulling mapping and planning data from different websites when preparing reports. The process looked something like this: • Open multiple government websites • Search for a property address • Download maps and planning overlays • Copy information into their report template It wasn’t complex work — just very repetitive. So I built a small automation that: • Takes a property address as input • Pulls the relevant mapping data from the web • Downloads the required images/data • Orga
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Built an automation for a local business and got paid $1500 — sharing the process" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $1500.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/smallbusiness/comments/1rx0yi0/built_an_automation_for_a_local_business_and_got/
2. [Improvements](https://github.com/MiMinions-ai/MiMinions/issues/88)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Improvements
     Source: github
     URL: https://github.com/MiMinions-ai/MiMinions/issues/88
     Why this is suitable: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
     First step: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: # Codebase Improvements & Gaps  A survey of improvements, gaps, and feature ideas across the codebase (June 2026). Focused on substantive fixes and features, not style nits. File references point at the code in question.  ---  ## 1. Finish or remove half-built features  These are the biggest sources of confusion — features that exist in the tree but don't actually work:  - **Workflow CLI is fully written but disabled.** `cli/workflow.py` has complete   list/add/update/remove/start/pause/stop/show commands, but registration is   commented out in `cli/main.py` (`#TODO: workflow management is not yet   implemented`). Either wire it up and test it, or delete the module until it's   ready. - **`agent run --async` is a stub.** It prints a TODO message and returns without   running anything (`cli/agent.py:253-255`). Implement it (stream model output and   session events) or drop the flag — acce
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Improvements" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/MiMinions-ai/MiMinions/issues/88
3. [[BUG] pytest 10 will break install-script tests: class-scoped fixture defined as instance method](https://github.com/vig-os/devcontainer/issues/691)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: [BUG] pytest 10 will break install-script tests: class-scoped fixture defined as instance method
     Source: github
     URL: https://github.com/vig-os/devcontainer/issues/691
     Why this is suitable: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
     First step: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Description  The test suite emits a `PytestRemovedIn10Warning` from the class-scoped `install_workspace` fixture in `tests/test_install_script.py`:  ``` PytestRemovedIn10Warning: Class-scoped fixture defined as instance method is deprecated. Instance attributes set in this fixture will NOT be visible to test methods, as each test gets a new instance while the fixture runs only once per class. Use @classmethod decorator and set attributes on cls instead. ```  Today this is **cosmetic** — the fixture only `yield`s a value that the 17 tests consume via the fixture parameter; it never sets `self.` attributes that tests read, and warnings are not escalated to errors. But it is **latent forward-breakage**: the project pins `pytest==9.1.1`, and pytest **10 removes** this pattern. When Renovate/Dependabot bumps pytest to 10, the fixture will error at collection and take out the entire `TestIn
   - Owner-reviewed outreach draft:
     Hi, I found your request about "[BUG] pytest 10 will break install-script tests: class-scoped fixture defined as instance method" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/vig-os/devcontainer/issues/691
4. [PRD (Umbrella): Hydropattern Platform Reorganization and Merge-Back to 1.0](https://github.com/JohnRushKucharski/hydropattern/issues/1)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: PRD (Umbrella): Hydropattern Platform Reorganization and Merge-Back to 1.0
     Source: github
     URL: https://github.com/JohnRushKucharski/hydropattern/issues/1
     Why this is suitable: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
     First step: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Problem StatementHydropattern and hydropattern-doe have diverged across core logic, parsing, tests, CLI behavior, and GUI capabilities. The current state makes it difficult to merge improvements safely one slice at a time while preserving baseline behavior quality and keeping all workflows (CLI, GUI, library/notebook) coherent and testable.## SolutionEstablish a governed reorganization and merge-back program for Hydropattern 1.0 readiness:- Keep one repository.- Maintain separate adapter layers (CLI, GUI, notebook/library API) over a shared application service layer.- Execute work as tracer-bullet vertical slices with strict merge gates.- Use explicit human adjudication for baseline behavior changes in core computational and parser logic.## User Stories1. As a maintainer, I want to port improvements from hydropattern-doe in small slices, so that regressions are controlled.2. As a main
   - Owner-reviewed outreach draft:
     Hi, I found your request about "PRD (Umbrella): Hydropattern Platform Reorganization and Merge-Back to 1.0" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/JohnRushKucharski/hydropattern/issues/1
5. [Dependency Dashboard](https://github.com/prowler-cloud/prowler/issues/11301)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Dependency Dashboard
     Source: github
     URL: https://github.com/prowler-cloud/prowler/issues/11301
     Why this is suitable: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: > ℹ️ **Note** >  > This PR body was truncated due to platform limits.  This issue lists Renovate updates and detected dependencies. Read the [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/) docs to learn more.<br>[View this repository on the Mend.io Web Portal](https://developer.mend.io/github/prowler-cloud/prowler).  ## Repository Problems  These problems occurred while renovating this repository. [View logs](https://developer.mend.io//github/prowler-cloud/prowler).   - ⚠️ WARN: Error updating branch: update failure  - ⚠️ WARN: Package lookup failures  ## Deprecations / Replacements > [!WARNING] The following dependencies are either deprecated or have replacements available.  | Datasource | Package | Replacement PR? | |------------|------|--------------| | npm | [framer-motion](https://redirect.github.com/motiondivision/motion) | ![Available](https://img.shie
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Dependency Dashboard" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/prowler-cloud/prowler/issues/11301
6. [Dependency Dashboard](https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/issues/4)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Dependency Dashboard
     Source: github
     URL: https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/issues/4
     Why this is suitable: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: This issue lists Renovate updates and detected dependencies. Read the [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/) docs to learn more.<br>[View this repository on the Mend.io Web Portal](https://developer.mend.io/github/GoogleCloudPlatform/vertex-ai-creative-studio).  ## Deprecations / Replacements > [!WARNING] The following dependencies are either deprecated or have replacements available.  | Datasource | Package | Replacement PR? | |------------|------|--------------| | npm | [@genkit-ai/googleai](https://redirect.github.com/firebase/genkit) | ![Unavailable](https://img.shields.io/badge/unavailable-orange?style=flat-square) | | npm | `@types/marked` | ![Unavailable](https://img.shields.io/badge/unavailable-orange?style=flat-square) | | npm | [rolldown-vite](https://redirect.github.com/vitejs/rolldown-vite) | ![Available](https://img.shields.io/badge/avai
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Dependency Dashboard" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/GoogleCloudPlatform/vertex-ai-creative-studio/issues/4
7. [Add database dependency and migration tooling](https://github.com/Fundable-Protocol/Backend/issues/20)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Add database dependency and migration tooling
     Source: github
     URL: https://github.com/Fundable-Protocol/Backend/issues/20
     Why this is suitable: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
     First step: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Repository  This issue belongs in `Fundable-Protocol/Backend` under `indexer/`.  Migrated from https://github.com/Fundable-Protocol/stellar_indexer/issues/1.  ## Context  The indexer needs a PostgreSQL-backed persistence layer before cursor, event, stream, distribution, or API work can be implemented. This issue adds the database tooling foundation only.  ## Scope  - [ ] Add PostgreSQL database dependencies - [ ] Add Drizzle ORM and migration tooling - [ ] Add root/package scripts for generating and running migrations - [ ] Add an initial migrations directory structure - [ ] Document the migration workflow briefly in README or package scripts  ## Out of Scope  - Defining domain tables - Creating cursor or indexed-event tables - Implementing DB connection factories - Docker Compose setup  ## Acceptance Criteria  - [ ] Migration tooling is installed and configured - [ ] `bun run db:gene
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Add database dependency and migration tooling" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/Fundable-Protocol/Backend/issues/20
8. [Dependency Dashboard](https://github.com/it-at-m/mucgpt/issues/10)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Dependency Dashboard
     Source: github
     URL: https://github.com/it-at-m/mucgpt/issues/10
     Why this is suitable: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: This issue lists Renovate updates and detected dependencies. Read the [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/) docs to learn more.<br>[View this repository on the Mend.io Web Portal](https://developer.mend.io/github/it-at-m/mucgpt).  ## Deprecations / Replacements > [!WARNING] The following dependencies are either deprecated or have replacements available.  | Datasource | Package | Replacement PR? | |------------|------|--------------| | npm | `@types/dompurify` | ![Unavailable](https://img.shields.io/badge/unavailable-orange?style=flat-square) |  ## Abandoned Dependencies  The following dependencies have not received updates for an extended period and may be unmaintained.  <details> <summary>View abandoned dependencies (14)</summary>  > [!NOTE] Packages are marked as abandoned when they exceed the [`abandonmentThreshold`](https://docs.renovatebot.com/
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Dependency Dashboard" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/it-at-m/mucgpt/issues/10
