# Code-Tech Earning Queue

Refreshed: 2026-07-29T06:45:38.618518+00:00
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

Online AI brief failed; used online search and local scoring only. Error: Could not get valid JSON from LLM (role=research): No valid JSON object found in LLM response. First 200 chars: ''

- Use the top ranked lead with the clearest public proof.
- Keep local Codex implementation to one small deliverable.

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
2. [Implement Secure Payment Gateway and Payment Service](https://github.com/SecureBananaLabs/bug-bounty/issues/1)
   - Score: 100/100
   - Value signal: $350.00
   - Why: visible or inferred value around $350.00; can become a repeatable async offer instead of hourly labor
   - Next: Skip unless the issue also has public reproduction steps the AI agent can patch and verify automatically.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Implement Secure Payment Gateway and Payment Service
     Source: github
     URL: https://github.com/SecureBananaLabs/bug-bounty/issues/1
     Why this is suitable: visible or inferred value around $350.00; can become a repeatable async offer instead of hourly labor
     First step: Skip unless the issue also has public reproduction steps the AI agent can patch and verify automatically.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Relevant Code  ```js export async function createPaymentIntent(payload) {   // TODO: integrate Stripe SDK and return client secret.   return {     paymentId: `pay_${Date.now()}`,     amount: payload.amount,     currency: payload.currency ?? "usd",     provider: "stripe"   }; } ```  **Goals** - Replace the stub implementation with a real Stripe `PaymentIntent` via the Stripe Node.js SDK - Return the `client_secret` from the created `PaymentIntent` to the caller - Handle Stripe API errors and surface them with meaningful error messages - Ensure `amount`, `currency`, and any required metadata are validated before the API call  Important: Star the repository https://github.com/SecureBananaLabs/bug-bounty   **Acceptance Criteria** - [ ] `stripe` npm package is installed and a `STRIPE_SECRET_KEY` environment variable is used to initialise the client — no hardcoded keys - [ ] `payload.amount
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Implement Secure Payment Gateway and Payment Service" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $350.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/SecureBananaLabs/bug-bounty/issues/1
3. [Dependency Dashboard](https://github.com/ah-ha-admin/refactored-memory/issues/49)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Dependency Dashboard
     Source: github
     URL: https://github.com/ah-ha-admin/refactored-memory/issues/49
     Why this is suitable: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: This issue lists Renovate updates and detected dependencies. Read the [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/) docs to learn more.<br>[View this repository on the Mend.io Web Portal](https://developer.mend.io/github/ah-ha-admin/refactored-memory).  ## Config Migration Needed   - [ ] <!-- create-config-migration-pr --> Select this checkbox to let Renovate create an automated Config Migration PR.  ## Rate-Limited  The following updates are currently rate-limited. To force their creation now, click on a checkbox below.   - [ ] <!-- unlimit-branch=renovate/github.com-mattn-go-isatty-0.x -->Update module github.com/mattn/go-isatty to v0.0.24  - [ ] <!-- unlimit-branch=renovate/github.com-sirupsen-logrus-1.x -->Update module github.com/sirupsen/logrus to v1.9.4  - [ ] <!-- unlimit-branch=renovate/actions-checkout-3.x -->Update actions/checkout action to v3.7
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Dependency Dashboard" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/ah-ha-admin/refactored-memory/issues/49
4. [docs: ADR-008 describes WebSocket delivery as a future possibility, but it's already fully implemented](https://github.com/C-Address-Onboarding-Bridge/C-Address-Onboarding-Bridge-Backend/issues/310)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
   - Next: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: docs: ADR-008 describes WebSocket delivery as a future possibility, but it's already fully implemented
     Source: github
     URL: https://github.com/C-Address-Onboarding-Bridge/C-Address-Onboarding-Bridge-Backend/issues/310
     Why this is suitable: visible or inferred value around $10.00; public proof makes this suitable for automated AI patching
     First step: Find one outdated dependency path, reproduce the breakage, and propose a fixed-price cleanup.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Summary  ADR-008's decision text is phrased forward-looking ("a clear path to WebSocket delivery once the platform needs it"). But `websocket.ts` is a complete implementation mounted at a `/ws` upgrade endpoint with its own test suite and `ws` as a production dependency.  ## Checklist  - [ ] Update ADR-008 to reflect that WebSocket delivery is implemented, not a future possibility  ## Difficulty  🟢 **Good First Issue**  **File(s):** `docs/adr/adr-008-event-driven-architecture-for-status-updates.md`, `api/src/services/websocket.ts`  ## Getting started  This is a self-contained task — no additional repo access or secrets needed.  ```bash git clone https://github.com/<your-fork>/C-Address-Onboarding-Bridge-Backend.git cd C-Address-Onboarding-Bridge-Backend ```  If this issue touches a GitHub Actions workflow, the easiest way to verify your change is to open a draft PR — the workflow will
   - Owner-reviewed outreach draft:
     Hi, I found your request about "docs: ADR-008 describes WebSocket delivery as a future possibility, but it's already fully implemented" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/C-Address-Onboarding-Bridge/C-Address-Onboarding-Bridge-Backend/issues/310
5. [[Program] Complete TypeScript stack health, security, standardization, testing, docs, and performance](https://github.com/bsv-blockchain/ts-stack/issues/324)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: [Program] Complete TypeScript stack health, security, standardization, testing, docs, and performance
     Source: github
     URL: https://github.com/bsv-blockchain/ts-stack/issues/324
     Why this is suitable: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Purpose  This is the authoritative execution tracker for bringing the consolidated TypeScript stack to a fully healthy, current, secure, uniform, documented, tested, publishable, browser-aware, and operationally maintainable end state.  It captures the full-repository audit as of **2026-07-24** and converts every material finding into explicit work, ordering, evidence requirements, and completion gates. Child issues and PRs should link here, and this issue should be updated as facts change so no work remains implicit or gets lost between PRs.  ## Scope, assumptions, and explicit exclusions  - Baseline: [`main@f9137ff`](https://github.com/BSV-blockchain/ts-stack/commit/f9137ff037c6d608019d04b4e2f984812b0385b7). - Treat PRs #289 and #290, and all other non-draft consolidation/dependency work preceding this baseline, as merged. - **Operator hold (2026-07-27): do not modify, rebase, comme
   - Owner-reviewed outreach draft:
     Hi, I found your request about "[Program] Complete TypeScript stack health, security, standardization, testing, docs, and performance" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/bsv-blockchain/ts-stack/issues/324
6. [docs: v1.0.0 documentation overhaul — tracking issue](https://github.com/bioedca/tether/issues/187)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: docs: v1.0.0 documentation overhaul — tracking issue
     Source: github
     URL: https://github.com/bioedca/tether/issues/187
     Why this is suitable: visible or inferred value around $10.00; ops cleanup has clear business value and bounded deliverables
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Tracking issue for the documentation overhaul that ships with **v1.0.0**. Every child issue below is independently mergeable and carries its own evidence, deliverables and acceptance criteria.  The work was scoped by auditing every documentation surface in this repository against the [INTERSECT "Better Documentation" lesson](https://intersect-training.org/Documentation/) — a research-software documentation curriculum covering audience analysis, the four Diátaxis modes (tutorial / how-to / reference / explanation), README contents, and documentation maintenance. That produced a 41-item rubric; this repository was then scored against every row.  ## The two defects that are live right now  Both are on the public site today, and **every existing gate is blind to both** — `mkdocs build --strict` builds 61 pages with zero warnings, because neither produces an unresolvable link.  - **#156** — a
   - Owner-reviewed outreach draft:
     Hi, I found your request about "docs: v1.0.0 documentation overhaul — tracking issue" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/bioedca/tether/issues/187
7. [Dependency Dashboard](https://github.com/IBM/tensorlakehouse-openeo-driver/issues/41)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Dependency Dashboard
     Source: github
     URL: https://github.com/IBM/tensorlakehouse-openeo-driver/issues/41
     Why this is suitable: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: This issue lists Renovate updates and detected dependencies. Read the [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/) docs to learn more.<br>[View this repository on the Mend.io Web Portal](https://developer.mend.io/github/IBM/tensorlakehouse-openeo-driver).  ## Rate-Limited  The following updates are currently rate-limited. To force their creation now, click on a checkbox below.   - [ ] <!-- unlimit-branch=renovate/asttokens-3.x -->Update dependency asttokens to v3.0.2  - [ ] <!-- unlimit-branch=renovate/branca-0.x -->Update dependency branca to v0.8.2  - [ ] <!-- unlimit-branch=renovate/cdsapi-0.x -->Update dependency cdsapi to v0.7.7  - [ ] <!-- unlimit-branch=renovate/cfgrib-0.x -->Update dependency cfgrib to v0.9.15.1  - [ ] <!-- unlimit-branch=renovate/cftime-1.x -->Update dependency cftime to v1.6.5  - [ ] <!-- unlimit-branch=renovate/charset-normalize
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Dependency Dashboard" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/IBM/tensorlakehouse-openeo-driver/issues/41
8. [Dependency Dashboard](https://github.com/nolte/kamerplanter/issues/12)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
   - Next: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Dependency Dashboard
     Source: github
     URL: https://github.com/nolte/kamerplanter/issues/12
     Why this is suitable: visible or inferred value around $10.00; can become a repeatable async offer instead of hourly labor
     First step: Collect the visible workflow or docs, identify one repeated pain, and propose an async fixed-price cleanup with proof.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: This issue lists Renovate updates and detected dependencies. Read the [Dependency Dashboard](https://docs.renovatebot.com/key-concepts/dashboard/) docs to learn more.<br>[View this repository on the Mend.io Web Portal](https://developer.mend.io/github/nolte/kamerplanter).  ## Repository Problems  These problems occurred while renovating this repository. [View logs](https://developer.mend.io//github/nolte/kamerplanter).   - ⚠️ WARN: pip-compile: dependency not found in lock file  ## Deprecations / Replacements > [!WARNING] The following dependencies are either deprecated or have replacements available.  | Datasource | Package | Replacement PR? | |------------|------|--------------| | npm | `@types/react-grid-layout` | ![Unavailable](https://img.shields.io/badge/unavailable-orange?style=flat-square) |  ## Awaiting Schedule  The following updates are awaiting their schedule. To get an updat
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Dependency Dashboard" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/nolte/kamerplanter/issues/12
