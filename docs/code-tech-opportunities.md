# Passive Product Income Queue

Refreshed: 2026-09-10T14:42:42.323656+00:00

Routes to passive income from a digital product on a zero budget: where it can
be listed and paid for (channels) and what can build or market it (assets).

**Freelance and contract postings are deliberately absent.** Income per hour of
the owner's time is a job, not passive income, so those sources were removed
rather than demoted.

No revenue figure appears on this page. Real revenue is the on-chain wallet
balance, and a listing is not a receipt.

## Requirements

- Every lead must move a digital product toward earning without the owner in the loop.
- Rank by how little owner action each unit of income needs, not by headline upside.
- Name where the money lands, and prefer stablecoin to the address this project already publishes.
- State every cost and every manual setup step out loud; zero budget is the constraint.
- Never suggest selling the owner's hours: a rate per hour is a job, not passive income.
- Stay inside policy: no social posting, no trading, no minting, no cold outreach.
- Do not count discovery, pipeline, or speculative upside as earnings. On-chain or nothing.

## Current Best Angle

Build a single digital product that costs nothing per user to run, host it on free infrastructure (GitHub Pages for static tools, Chrome Web Store for extensions), list it on every zero‑cost storefront (Getly for crypto payouts, itch.io for reach, Chrome Web Store for discovery), embed the existing Tron (TRC‑20) USDT receive address on the product page and in the README, and publish a dev.to article that frames the product as the solution to a specific problem — the article’s footer already carries the wallet address. All channels require only one‑time manual setup; after that, every sale or donation lands on‑chain with no further owner action.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Getly | Digital‑goods storefront with native stablecoin payouts | Free to list; platform takes a percentage per sale (verify current terms), no monthly fee | USDT/USDC on Tron (TRC‑20) and BNB Smart Chain (BEP‑20) directly to seller’s own wallet address, no KYC for crypto settlement | Create account, connect the existing Tron receive address, upload product file or licence‑key delivery details, set price (one‑time or pay‑what‑you‑want) | After listing, Getly handles payment, delivery, and on‑chain payout automatically; owner never touches a sale. |
| itch.io | Marketplace for tools, assets, and utilities (not only games) | Free to publish; seller chooses platform cut (default ~10%, can be set to 0%), no upfront or monthly fee | Fiat only (Stripe/PayPal) — crypto leg stays the wallet address on the product page | Sign up, create project page, upload downloadable artifact, set pricing (pay‑what‑you‑want supported), paste Tron address in description | Once published, itch.io handles hosting, payment, and file delivery; the wallet address in the description captures crypto tips/sales without platform involvement. |
| Chrome Web Store | Distribution channel for browser extensions with organic discovery | One‑time $5 developer registration fee (covers up to 20 extensions), no annual renewal, no revenue cut on free extensions | None (store does not process crypto); monetisation via wallet address in extension popup, options page, and store description | Pay $5 once, zip extension, upload via Developer Dashboard, write store listing with Tron address in description and in extension UI | Extension installs and updates are automatic; the wallet address is embedded in the extension and store page, so users can donate or pay for an upgrade without owner action. |
| Wallet address on product page & README | Direct crypto receive path with no platform at all | Zero | USDT on Tron (TRC‑20) to the existing validated address — already live on dev.to articles | Copy the same address into the product’s landing page (GitHub Pages), README, and any storefront description; no account creation needed | Every on‑chain transfer is final and requires zero owner interaction; the address is already generated and monitored by the project’s payout script. |
| GitHub Pages + GitHub Actions | Free static hosting and scheduled automation for client‑side tools | Free on public repositories (already used by the project) | Not a payment channel — serves the product page that displays the wallet address | Push product HTML/JS to a repo, enable Pages, add a workflow if scheduled tasks are needed; embed Tron address in the page footer | Hosting and CI run on GitHub’s free tier indefinitely; the page simply shows the product and the address — no server costs, no per‑user cost. |

## Product Ideas

1. **Single‑purpose browser extension (e.g., 'Hide YouTube Shorts shelf')**
   - Who buys: Desktop Chrome/Edge users annoyed by a specific UI element who want a one‑click toggle
   - Deliverable: CRX/ZIP installed via Chrome Web Store; paid upgrade unlocks custom CSS rules or schedule via a licence key delivered by Getly
   - Pricing model: Free core extension; one‑time licence for 'Pro' ruleset (sold on Getly) or pay‑what‑you‑want on itch.io
   - Cost per extra user: Zero — extension runs entirely client‑side, no backend
   - Free stack: Chrome Web Store (one‑time $5), GitHub Pages for landing page, Getly for crypto licence sales
2. **CLI utility that converts Figma design tokens to Tailwind config**
   - Who buys: Front‑end developers who hand off designs and want a reproducible token‑to‑CSS pipeline
   - Deliverable: Single binary (Go/Rust/Node) downloaded from GitHub Releases; paid tier adds watch‑mode and CI template via a licence file
   - Pricing model: Free binary with basic conversion; one‑time licence for advanced features (Getly) or pay‑what‑you‑want (itch.io)
   - Cost per extra user: Zero — binary is built once, served from GitHub Releases
   - Free stack: GitHub Actions for build/release, GitHub Pages for docs, Getly/itch.io for licence sales, wallet address in README
3. **Static web tool: 'SVG to React component' converter (client‑side only)**
   - Who buys: React developers who paste SVG markup and want a typed component instantly
   - Deliverable: Single HTML/JS page hosted on GitHub Pages; paid upgrade unlocks batch conversion and PropTypes via a licence key
   - Pricing model: Free single‑file conversion; one‑time licence for batch/TS features (Getly) or donation via wallet address
   - Cost per extra user: Zero — all processing in browser, static hosting free
   - Free stack: GitHub Pages, GitHub Actions (optional lint), Getly for licence, wallet address on page
4. **Asset pack: 'Accessible focus‑visible outlines' for Tailwind/CSS**
   - Who buys: Designers and devs who need WCAG‑compliant focus styles without designing them
   - Deliverable: CSS/SCSS/JS files + Figma library download; same pack sold as a one‑time purchase
   - Pricing model: Pay‑what‑you‑want on itch.io (including $0), fixed price on Getly for crypto buyers
   - Cost per extra user: Zero — digital files uploaded once
   - Free stack: itch.io, Getly, GitHub Pages for preview, wallet address in download README
5. **Developer library: 'Tiny idempotency key generator' for Node/Edge/Workers**
   - Who buys: Backend engineers building retry‑safe APIs who want a zero‑dependency key helper
   - Deliverable: npm package (public) + private repo access for TypeScript types and test suite via licence key
   - Pricing model: Free public package (MIT); one‑time licence for private repo with full types/tests (Getly)
   - Cost per extra user: Zero — npm publish is free, private repo on GitHub (free for personal use)
   - Free stack: npm, GitHub (private repo), Getly for licence delivery, wallet address in package README

## Next Actions

- Pick one product idea from the list that matches a personal annoyance or a clear search‑intent keyword; write the core tool in a weekend using only client‑side or single‑binary tech.
- Deploy the free version: push to GitHub, enable Pages for landing page, publish extension to Chrome Web Store (pay $5 once) or release CLI binary to GitHub Releases.

## Monetization Patterns

- Ship the tool free and sell the upgrade: the free tier buys discovery the owner cannot.
- One-time licence for a digital download, delivered by the storefront with no owner action.
- Put the published receive address on the product page and in the README, so a user can pay with no platform at all.
- Sell a template, preset, or asset pack built once and downloaded many times.
- Charge for the paid tier of a tool whose free tier costs nothing per user to run.
- List the same product on every zero-cost channel, since the artifact is already built.

## Free AI Focus Areas

- free-tier LLM APIs with no credit card requirement
- free speech-to-text, TTS, and transcription APIs
- free image generation and background-removal APIs
- free OCR, document parsing, and PDF extraction APIs
- free embedding and vector-search tiers
- free translation and summarization APIs
- free AI hosting, inference, and scheduled-compute tiers
- open-weight models that run on free CPU/GPU allowances

## Reference Sources

- [15 High-Paying Remote Jobs With a 4-Hour Work Week](https://freedium-mirror.cfd/https://medium.com/@startup_Ideas/15-high-paying-remote-jobs-with-a-4-hour-work-week-and-how-people-actually-get-them-7e8d3562ff99): The viable path is not easy money; it is rare skill, specialization, automation, retainers, async work, and results-based delivery.
- [OpenRouter free model list](https://openrouter.ai/models?max_price=0): Free (:free) models are capped at 20 req/min and only 50 req/day unless the account has ever purchased $10 in credits (then 1,000/day) -- verify current limit before relying on volume.
- [Google AI Studio (Gemini API)](https://aistudio.google.com/app/apikey): No credit card required. Gemini 2.5 Flash free tier is roughly 1,500 requests/day; much higher daily ceiling than OpenRouter's free chain -- verify current limit.
- [Cerebras Cloud free tier](https://cloud.cerebras.ai/): No credit card required. Roughly 1M tokens/day and 14,400 requests/day per model -- verify current limit.

## Underserved Niches

- storefronts that settle stablecoin straight to the seller's own wallet, no custodian
- one-task tools that solve a single annoyance well enough to be worth paying for
- products with zero marginal cost per user, so the free tier can stay free forever
- channels that are free to list on and have no approval queue to fail
- paying users who never open a storefront and would rather send stablecoin directly
- distribution with real organic discovery, so reach does not need ad spend
- products whose buyers are developers, since that is the audience already reached

## Strategy Playbook

- Build the product once, then spend every later cycle on distribution rather than on more product.
- Keep marginal cost per user at zero: client-side code, free hosting, free scheduler. Every dollar in is margin.
- Put the receive path on the artifact itself -- product page, README, article footer -- not only on a storefront.
- List on the free channels first; pay a listing fee only where discovery is worth it, and say what it cost.
- Let the articles this bot already publishes do the marketing: the problem is the post, the product is the fix.
- Price once and leave it. A price that needs renegotiating per buyer is a service in disguise.
- Measure only what arrives on-chain. Listings, views and pipeline are not revenue.

## Avoid

- Selling the owner's hours: freelance postings, contract work, retainers, consulting. Income per unit of work is a job.
- Anything requiring paid infrastructure, a monthly fee, or a credit-card-gated tier.
- Custodial payment processors that hold the money before the owner does, and anything demanding KYC to receive.
- Platforms that are dead, seized, or unverifiable. Sellix was seized in 2024 and is still widely recommended.
- Trading, minting, yield farming, staking and airdrops: refused in code, and not a product business.
- Offers needing a large audience, ad spend, or a following the owner does not have.
- Anything promising passive income without a product that delivers something.

## Refused Channels

Written down so a later cycle does not re-derive them, and so a dead
platform cannot climb back onto this page.

- **Sellix:** Seized and shut down in 2024. Still widely recommended as the crypto storefront, which is exactly why it is written down here as refused.
- **Gumroad (for crypto):** Does not natively accept crypto and pays out USD via Stripe only. Fine as a fiat storefront; it is not a crypto receive path, and mrr_ideas should not imply it is.
- **Buy Me a Coffee / Ko-fi (main platforms):** No native stablecoin field for a supporter's own wallet. Ko-fi Web3 is a separate product on BEP-20 only, so the wallet footer already covers this better.
- **Any custodial crypto payment processor:** Holds the money before the owner does. The published Tron address is non-custodial and already works; adding a custodian adds KYC risk for no gain.

## Ranked Leads

1. Wallet ask on the product page and in every article (already live)
   - Kind: channel
   - Score: 100/100
   - Cost: free to list
   - Owner must do: None. Already publishing.
   - Why: already running, so it needs no account and no owner action; pays in stablecoin, so the receive path is on-chain and verifiable
   - Next: Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
   - Verified: Live since 2026-09-04; coverage observed by receipt_check each cycle.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Wallet ask on the product page and in every article (already live)
     SOURCE         channel-table
     LINK           no public URL
     COST           $0.00 (free to list)
     OWNER MUST DO  None. Already publishing.
     NEXT STEP      Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
     FREE STACK     free-tier LLM APIs with no credit card requirement; free speech-to-text, TTS, and transcription APIs
     WHY IT RANKS   already running, so it needs no account and no owner action; pays in stablecoin, so the receive path is on-chain and verifiable
     
     Constraints:
     - Keep the first change narrowly scoped to one file or script.
     - Use free tiers or offline code paths only; no paid service.
     - Include the exact commands to run it and paste the real output.
     - Do not contact anyone, post to social media, trade, or mint anything.
     - Do not open an account or accept terms on the owner's behalf.
     - Do not state a price or an earnings figure that COST does not give.
     - Revenue is the on-chain balance only; never estimate it.
2. [Getly — sell a digital product, settle USDT on Tron to your own wallet](https://www.getly.store/sell/crypto)
   - Kind: channel
   - Score: 89/100
   - Cost: free to list
   - Owner must do: Owner signs up, adds the Tron receive address, and uploads the product once.
   - Why: settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time
   - Next: List the product once, set the price, and point the payout at the published Tron address. Owner does this by hand: Owner signs up, adds the Tron receive address, and uploads the product once.
   - Verified: Fees, networks, no-KYC and own-wallet payout confirmed on getly.store 2026-09-08.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Getly — sell a digital product, settle USDT on Tron to your own wallet
     SOURCE         channel-table
     LINK           https://www.getly.store/sell/crypto
     COST           $0.00 (free to list)
     OWNER MUST DO  Owner signs up, adds the Tron receive address, and uploads the product once.
     NEXT STEP      List the product once, set the price, and point the payout at the published Tron address. Owner does this by hand: Owner signs up, adds the Tron receive address, and uploads the product once.
     FREE STACK     free-tier LLM APIs with no credit card requirement; free speech-to-text, TTS, and transcription APIs
     WHY IT RANKS   settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time
     
     Constraints:
     - Keep the first change narrowly scoped to one file or script.
     - Use free tiers or offline code paths only; no paid service.
     - Include the exact commands to run it and paste the real output.
     - Do not contact anyone, post to social media, trade, or mint anything.
     - Do not open an account or accept terms on the owner's behalf.
     - Do not state a price or an earnings figure that COST does not give.
     - Revenue is the on-chain balance only; never estimate it.
3. [itch.io — free to publish, you set the platform cut (0-100%)](https://itch.io/docs/creators/faq)
   - Kind: channel
   - Score: 84/100
   - Cost: free to list
   - Owner must do: Owner creates an account and uploads the product; payment details for fiat payout.
   - Why: sells the product while nobody is working; the signup is one-time; free to list with no approval queue, so a refusal cannot block it
   - Next: List the product once and set the price. Owner does this by hand: Owner creates an account and uploads the product; payment details for fiat payout.
   - Verified: Free publishing and open revenue share confirmed on itch.io 2026-09-08.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           itch.io — free to publish, you set the platform cut (0-100%)
     SOURCE         channel-table
     LINK           https://itch.io/docs/creators/faq
     COST           $0.00 (free to list)
     OWNER MUST DO  Owner creates an account and uploads the product; payment details for fiat payout.
     NEXT STEP      List the product once and set the price. Owner does this by hand: Owner creates an account and uploads the product; payment details for fiat payout.
     FREE STACK     free-tier LLM APIs with no credit card requirement; free speech-to-text, TTS, and transcription APIs
     WHY IT RANKS   sells the product while nobody is working; the signup is one-time; free to list with no approval queue, so a refusal cannot block it
     
     Constraints:
     - Keep the first change narrowly scoped to one file or script.
     - Use free tiers or offline code paths only; no paid service.
     - Include the exact commands to run it and paste the real output.
     - Do not contact anyone, post to social media, trade, or mint anything.
     - Do not open an account or accept terms on the owner's behalf.
     - Do not state a price or an earnings figure that COST does not give.
     - Revenue is the on-chain balance only; never estimate it.
4. Ship the product free, sell the upgrade, ask in the README
   - Kind: channel
   - Score: 84/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Ship the product free, sell the upgrade, ask in the README
     SOURCE         local-playbook
     LINK           no public URL
     COST           not published - do not quote or invent a figure
     OWNER MUST DO  nothing
     NEXT STEP      List the product once and set the price. Owner does this by hand: open the account
     FREE STACK     free-tier LLM APIs with no credit card requirement; free speech-to-text, TTS, and transcription APIs
     WHY IT RANKS   sells the product while nobody is working; the signup is one-time
     
     Constraints:
     - Keep the first change narrowly scoped to one file or script.
     - Use free tiers or offline code paths only; no paid service.
     - Include the exact commands to run it and paste the real output.
     - Do not contact anyone, post to social media, trade, or mint anything.
     - Do not open an account or accept terms on the owner's behalf.
     - Do not state a price or an earnings figure that COST does not give.
     - Revenue is the on-chain balance only; never estimate it.
5. [Chrome Web Store — one-time $5, covers up to 20 extensions](https://developer.chrome.com/docs/webstore/register)
   - Kind: channel
   - Score: 74/100
   - Cost: $5.00 one-time
   - Owner must do: Owner pays the one-time $5 registration and submits the extension for review.
   - Why: sells the product while nobody is working; the signup is one-time; costs $5.00 once, stated rather than hidden
   - Next: List the product once and set the price. Owner does this by hand: Owner pays the one-time $5 registration and submits the extension for review.
   - Verified: One-time $5, no renewal, 20-extension limit confirmed on developer.chrome.com 2026-09-08.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Chrome Web Store — one-time $5, covers up to 20 extensions
     SOURCE         channel-table
     LINK           https://developer.chrome.com/docs/webstore/register
     COST           $5.00 one-time, published by the platform
     OWNER MUST DO  Owner pays the one-time $5 registration and submits the extension for review.
     NEXT STEP      List the product once and set the price. Owner does this by hand: Owner pays the one-time $5 registration and submits the extension for review.
     FREE STACK     free-tier LLM APIs with no credit card requirement; free speech-to-text, TTS, and transcription APIs
     WHY IT RANKS   sells the product while nobody is working; the signup is one-time; costs $5.00 once, stated rather than hidden
     
     Constraints:
     - Keep the first change narrowly scoped to one file or script.
     - Use free tiers or offline code paths only; no paid service.
     - Include the exact commands to run it and paste the real output.
     - Do not contact anyone, post to social media, trade, or mint anything.
     - Do not open an account or accept terms on the owner's behalf.
     - Do not state a price or an earnings figure that COST does not give.
     - Revenue is the on-chain balance only; never estimate it.
6. [One month og chili crunch: 360 jars, 6k in revenue, shipped to 24 states, and 3 retail locations](https://www.reddit.com/r/SideProject/comments/1w7bfon/one_month_og_chili_crunch_360_jars_6k_in_revenue/)
   - Kind: asset
   - Score: 68/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-04T17:47:28+00:00 (141h ago)
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           asset (what builds or promotes it)
     LEAD           One month og chili crunch: 360 jars, 6k in revenue, shipped to 24 states, and 3 retail locations
     SOURCE         reddit:r/SideProject
     LINK           https://www.reddit.com/r/SideProject/comments/1w7bfon/one_month_og_chili_crunch_360_jars_6k_in_revenue/
     COST           not published - do not quote or invent a figure
     OWNER MUST DO  nothing
     NEXT STEP      Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
     FREE STACK     free-tier LLM APIs with no credit card requirement; free speech-to-text, TTS, and transcription APIs
     WHY IT RANKS   pays in stablecoin, so the receive path is on-chain and verifiable; free tooling or reach to build and market the product with
     
     Constraints:
     - Keep the first change narrowly scoped to one file or script.
     - Use free tiers or offline code paths only; no paid service.
     - Include the exact commands to run it and paste the real output.
     - Do not contact anyone, post to social media, trade, or mint anything.
     - Do not open an account or accept terms on the owner's behalf.
     - Do not state a price or an earnings figure that COST does not give.
     - Revenue is the on-chain balance only; never estimate it.
7. One product, listed on every free channel at once
   - Kind: channel
   - Score: 67/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
8. Open-source the tool and take sponsorship on the repo
   - Kind: asset
   - Score: 67/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
9. [I acquired my first macOS app in 4 hours](https://www.reddit.com/r/SideProject/comments/1wcehvr/i_acquired_my_first_macos_app_in_4_hours/)
   - Kind: asset
   - Score: 60/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T09:45:03+00:00 (5h ago)
10. [I built a notebook system for handwritten notes that my AI can actually use](https://www.reddit.com/r/SideProject/comments/1w0otth/i_built_a_notebook_system_for_handwritten_notes/)
   - Kind: asset
   - Score: 59/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-28T12:10:44+00:00 (314h ago)
11. [While building my apps, I figured out about a third of what I paid for Claude Code bought me nothing. So our next app went after the waste.](https://www.reddit.com/r/SideProject/comments/1w0ec22/while_building_my_apps_i_figured_out_about_a/)
   - Kind: asset
   - Score: 59/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-28T02:38:12+00:00 (324h ago)
12. Write the article that the product is the answer to
   - Kind: asset
   - Score: 56/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
13. [mcanouil/awesome-quarto](https://github.com/mcanouil/awesome-quarto)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:41:35+00:00 (0h ago)
14. [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:41:29+00:00 (0h ago)
15. [FlorianBruniaux/claude-code-ultimate-guide](https://github.com/FlorianBruniaux/claude-code-ultimate-guide)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:36:07+00:00 (0h ago)
16. [maildev/maildev](https://github.com/maildev/maildev)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:34:20+00:00 (0h ago)
17. [paperclipai/paperclip](https://github.com/paperclipai/paperclip)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:36:22+00:00 (0h ago)
18. [dkhamsing/open-source-ios-apps](https://github.com/dkhamsing/open-source-ios-apps)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-09-10T14:35:55+00:00 (0h ago)
19. [superiorlu/AITreasureBox](https://github.com/superiorlu/AITreasureBox)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:30:45+00:00 (0h ago)
20. [nexu-io/open-design](https://github.com/nexu-io/open-design)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:32:36+00:00 (0h ago)
21. [Mr-xn/Penetration_Testing_POC](https://github.com/Mr-xn/Penetration_Testing_POC)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:32:32+00:00 (0h ago)
22. [SceneWorks/SceneWorks](https://github.com/SceneWorks/SceneWorks)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:30:10+00:00 (0h ago)
23. [readyready15728/awesome-programming-games](https://github.com/readyready15728/awesome-programming-games)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:26:25+00:00 (0h ago)
24. [mthcht/awesome-lists](https://github.com/mthcht/awesome-lists)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:26:13+00:00 (0h ago)
25. [wasm3/wasm3](https://github.com/wasm3/wasm3)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:23:59+00:00 (0h ago)
26. [pulkitxm/claude-directory](https://github.com/pulkitxm/claude-directory)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:22:51+00:00 (0h ago)
27. [Misterio77/Foundry](https://github.com/Misterio77/Foundry)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:23:14+00:00 (0h ago)
28. [nitefood/asn](https://github.com/nitefood/asn)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:22:19+00:00 (0h ago)
29. [ibuilder/massing](https://github.com/ibuilder/massing)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:24:25+00:00 (0h ago)
30. [jqueryscript/awesome-claude-code](https://github.com/jqueryscript/awesome-claude-code)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:17:19+00:00 (0h ago)
31. [martinkoutecky/tine](https://github.com/martinkoutecky/tine)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:14:54+00:00 (0h ago)
32. [truecourse-ai/truecourse](https://github.com/truecourse-ai/truecourse)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:12:41+00:00 (0h ago)
33. [ilhamnurrachman/claude-opus-dev-workbench](https://github.com/ilhamnurrachman/claude-opus-dev-workbench)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T14:12:17+00:00 (0h ago)
34. [datadrivenconstruction/OpenConstructionERP](https://github.com/datadrivenconstruction/OpenConstructionERP)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-09-10T13:59:37+00:00 (1h ago)
35. [sipyourdrink-ltd/bernstein](https://github.com/sipyourdrink-ltd/bernstein)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T13:47:19+00:00 (1h ago)
36. [ai-collection/ai-collection](https://github.com/ai-collection/ai-collection)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T13:20:05+00:00 (1h ago)
37. [Dominic789654/awesome-deepseek-harness](https://github.com/Dominic789654/awesome-deepseek-harness)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T13:01:53+00:00 (2h ago)
38. [imsai-sh/awesome-deepseek-harness-plugins](https://github.com/imsai-sh/awesome-deepseek-harness-plugins)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T12:39:44+00:00 (2h ago)
39. [hoilc/scoop-lemon](https://github.com/hoilc/scoop-lemon)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T12:14:47+00:00 (2h ago)
40. [awesome-selfhosted/awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-10T12:02:38+00:00 (3h ago)
