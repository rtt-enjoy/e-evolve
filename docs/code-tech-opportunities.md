# Passive Product Income Queue

Refreshed: 2026-09-08T18:44:05.161497+00:00

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

The most viable zero-budget route is to ship a free, client-side tool (browser extension, CLI utility, or static web tool) that solves one sharp annoyance, embed the existing Tron (TRC-20) USDT receive address on the product page, in the README, and in the dev.to article footer, and list the paid upgrade on Getly for direct stablecoin settlement to that same wallet. Simultaneously publish the free version on the Chrome Web Store (one-time $5 registration) for organic discovery, list a pay-what-you-want version on itch.io for additional reach, and host all static assets on GitHub Pages with GitHub Actions so marginal cost per user is zero. Every channel requires only a one-time manual setup; after that, sales and crypto payouts occur without owner action.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Getly | Digital-goods storefront with native stablecoin payouts to seller's own wallet | No monthly fee; platform cut verify current terms; minimum payout $15 on Tron (network fee ~$0.50-1) | USDT/USDC on Tron (TRC-20) and BNB Smart Chain directly to seller's wallet address; no KYC for crypto settlement | Create account, add product with upgrade tier, set payout wallet to the existing Tron address, configure pricing | Buyer pays via card or crypto; Getly automatically sends stablecoin to the owner's wallet on each sale; no owner action per transaction |
| itch.io | Marketplace for digital tools, assets, and utilities with pay-what-you-want pricing | Free to publish; seller sets platform revenue share (0-100%), default ~10%; no monthly fee | Fiat only (Stripe/PayPal); crypto leg remains the owner's wallet address on the product page | Sign up, upload product files, set price to pay-what-you-want, add wallet address in description | Once listed, buyers download and pay voluntarily; platform handles delivery; owner only receives fiat payouts periodically, while crypto payments go direct via wallet address |
| Chrome Web Store | Official distribution channel for browser extensions with organic discovery | One-time $5 developer registration fee per account (covers up to 20 extensions); no annual renewal; store takes no cut of free extensions | None (free extensions); monetisation via wallet ask or paid upgrade sold through Getly | Pay $5, create developer account, package extension, submit for review, publish free version; add upgrade link to Getly in description | Free extension gets discovered organically; upgrade sales happen on Getly; no per-sale owner work |
| Wallet ask (dev.to footer, product page, README) | Direct crypto receive address displayed wherever the product is documented | Zero | USDT on Tron (TRC-20) directly to owner's wallet; no platform, no KYC | Ensure the validated Tron address is appended to every dev.to article (already automated), placed on the product landing page, and included in the repository README | Users who value the tool can send payment instantly without any storefront; the address is static and requires zero maintenance |
| GitHub Pages + GitHub Actions | Free static hosting and scheduled automation for product landing page and delivery | Free on GitHub free tier | N/A (hosting only); crypto payments via wallet address | Create repository, enable GitHub Pages, add product page HTML, configure Actions for any automated tasks (e.g., build, deploy) | Zero marginal cost per user; the site serves the product page and download links indefinitely without owner intervention |

## Product Ideas

1. **Tab Cleaner Pro**
   - Who buys: Developers and power users who drown in dozens of open tabs and want a one-click cleanup with session restore
   - Deliverable: Browser extension (Chrome/Firefox/Edge) that groups, archives, and restores tab sessions; paid upgrade unlocks auto-archive rules and cloud sync via user's own storage
   - Pricing model: Free tier: manual clean and restore; Paid upgrade: one-time licence for auto-rules and sync (sold via Getly)
   - Cost per extra user: Zero (client-side only, no server)
   - Free stack: Extension runs entirely in browser; landing page on GitHub Pages; distribution via Chrome Web Store and itch.io
2. **CLI Log Formatter**
   - Who buys: DevOps engineers and backend developers who parse messy JSON/CSV logs daily
   - Deliverable: Single binary (Go/Rust) that reads stdin, applies configurable formatting, outputs colored or structured logs; paid version adds custom template engine and plugin API
   - Pricing model: Free binary with core formatters; Paid upgrade: one-time licence for template engine (delivered via Getly download)
   - Cost per extra user: Zero (self-hosted binary, no server)
   - Free stack: GitHub Releases for binary distribution; GitHub Pages for docs; itch.io for pay-what-you-want; Getly for paid upgrade
3. **Static Color Palette Generator**
   - Who buys: UI designers and frontend developers needing instant, accessible color palettes
   - Deliverable: Client-side web tool (HTML/JS) that generates palettes from a base color, exports CSS/JSON/Figma tokens; paid tier unlocks palette history, team sharing via user's own GitHub Gist
   - Pricing model: Free tool with all core features; Paid upgrade: one-time licence for history and export integrations (Getly)
   - Cost per extra user: Zero (static files only)
   - Free stack: Hosted on GitHub Pages; listed on itch.io and Getly; wallet address in README
4. **VS Code Snippet Pack: React Testing Library**
   - Who buys: React developers writing tests who want ready-made, best-practice snippets
   - Deliverable: JSON snippet file for VS Code; paid version includes additional snippets for Jest, Cypress, and custom test utilities
   - Pricing model: Free base pack (10 snippets); Paid upgrade: expanded pack (50+ snippets) one-time licence via Getly
   - Cost per extra user: Zero (digital download)
   - Free stack: Published on VS Code Marketplace (free), itch.io, Getly; wallet address in repo README
5. **Self-Hosted Backup Script**
   - Who buys: Homelab enthusiasts and small teams needing simple, encrypted backups to S3-compatible storage
   - Deliverable: Bash/Python script with config file; paid version adds incremental encryption, health-check webhook, and multi-target rotation
   - Pricing model: Free script with basic full backup; Paid upgrade: one-time licence for advanced features (Getly)
   - Cost per extra user: Zero (script runs on buyer's machine)
   - Free stack: GitHub repo with releases; GitHub Pages for docs; itch.io and Getly for distribution
6. **Curated Public API Reference Dataset**
   - Who buys: Developers building API integrations who want a searchable, offline reference of popular public APIs
   - Deliverable: SQLite/JSON dataset with endpoints, auth methods, rate limits, example requests; paid version includes quarterly updates and OpenAPI specs
   - Pricing model: Free snapshot (one-time download); Paid subscription? No, one-time licence for lifetime updates via Getly (verify current terms for recurring)
   - Cost per extra user: Zero (static file)
   - Free stack: Hosted on GitHub Releases; listed on itch.io (pay-what-you-want) and Getly

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
   - Posted: 2026-09-04T17:47:28+00:00 (97h ago)
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
8. [I’m 16, built a local marketplace with 600 organic App Store downloads, but I’m not sure I want to operate this kind of business](https://www.reddit.com/r/SideProject/comments/1vydksc/im_16_built_a_local_marketplace_with_600_organic/)
   - Kind: asset
   - Score: 67/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-25T21:43:55+00:00 (333h ago)
9. Open-source the tool and take sponsorship on the repo
   - Kind: asset
   - Score: 67/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
10. [I built a notebook system for handwritten notes that my AI can actually use](https://www.reddit.com/r/SideProject/comments/1w0otth/i_built_a_notebook_system_for_handwritten_notes/)
   - Kind: asset
   - Score: 59/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-28T12:10:44+00:00 (271h ago)
11. [While building my apps, I figured out about a third of what I paid for Claude Code bought me nothing. So our next app went after the waste.](https://www.reddit.com/r/SideProject/comments/1w0ec22/while_building_my_apps_i_figured_out_about_a/)
   - Kind: asset
   - Score: 59/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-28T02:38:12+00:00 (280h ago)
12. Write the article that the product is the answer to
   - Kind: asset
   - Score: 56/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
13. [hashgraph-online/awesome-codex-plugins](https://github.com/hashgraph-online/awesome-codex-plugins)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:42:12+00:00 (0h ago)
14. [samdauwe/webgpu-native-examples](https://github.com/samdauwe/webgpu-native-examples)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:41:31+00:00 (0h ago)
15. [superiorlu/AITreasureBox](https://github.com/superiorlu/AITreasureBox)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:40:48+00:00 (0h ago)
16. [mthcht/awesome-lists](https://github.com/mthcht/awesome-lists)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:31:41+00:00 (0h ago)
17. [TIGER-AI-Lab/ClawBench](https://github.com/TIGER-AI-Lab/ClawBench)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:24:18+00:00 (0h ago)
18. [lissy93/awesome-privacy](https://github.com/lissy93/awesome-privacy)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:18:59+00:00 (0h ago)
19. [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:12:26+00:00 (0h ago)
20. [omnivore-app/omnivore](https://github.com/omnivore-app/omnivore)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T18:10:05+00:00 (1h ago)
21. [PatrickJS/awesome-angular](https://github.com/PatrickJS/awesome-angular)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T17:34:14+00:00 (1h ago)
22. [ripienaar/free-for-dev](https://github.com/ripienaar/free-for-dev)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T15:24:18+00:00 (3h ago)
23. [marcelscruz/dev-resources](https://github.com/marcelscruz/dev-resources)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T14:43:25+00:00 (4h ago)
24. [avelino/awesome-go](https://github.com/avelino/awesome-go)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T13:39:01+00:00 (5h ago)
25. [Dicklesworthstone/agentic_coding_flywheel_setup](https://github.com/Dicklesworthstone/agentic_coding_flywheel_setup)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T12:21:25+00:00 (6h ago)
26. [web-padawan/awesome-web-components](https://github.com/web-padawan/awesome-web-components)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T12:10:02+00:00 (7h ago)
27. [webLiang/Pornhub-Video-Downloader-Plugin-v3](https://github.com/webLiang/Pornhub-Video-Downloader-Plugin-v3)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T06:22:23+00:00 (12h ago)
28. [angristan/awesome-stars](https://github.com/angristan/awesome-stars)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-08T05:12:45+00:00 (14h ago)
29. [My problem? I didn't understand or knew how schools, institutes and organisations actually work](https://www.reddit.com/r/SideProject/comments/1w8zxno/my_problem_i_didnt_understand_or_knew_how_schools/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-06T15:57:45+00:00 (51h ago)
30. [Baby Sleep AI - I read baby sleep research for 4 months because no tracker would tell me when to put my kid down](https://www.reddit.com/r/SideProject/comments/1w85z2b/baby_sleep_ai_i_read_baby_sleep_research_for_4/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-05T16:54:12+00:00 (74h ago)
31. [launched my family caregiving app on product hunt today — solo, no dev background, honest numbers inside](https://www.reddit.com/r/SideProject/comments/1w84ze4/launched_my_family_caregiving_app_on_product_hunt/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-05T16:16:11+00:00 (74h ago)
32. [work night shifts at a supermarket and flip liquidation hauls on the side. I built an AI AR scanner to process items 10x faster so I can fin](https://www.reddit.com/r/SideProject/comments/1w7w46l/work_night_shifts_at_a_supermarket_and_flip/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-05T09:34:06+00:00 (81h ago)
33. [Searching for jobs in tech sucks, so I made my own job search app to make it suck less. It won't do one thing that most other job search app](https://www.reddit.com/r/SideProject/comments/1w5t2qs/searching_for_jobs_in_tech_sucks_so_i_made_my_own/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-03T01:08:58+00:00 (138h ago)
34. [Built a crowd-source platform for homebuyers to share feedback on homes they have visited for other homebuyers before they step foot in the ](https://www.reddit.com/r/SideProject/comments/1w3kqdt/built_a_crowdsource_platform_for_homebuyers_to/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-31T17:33:20+00:00 (193h ago)
35. [If you had my skill set, what kind of business would you start?](https://www.reddit.com/r/SideProject/comments/1w2k0wy/if_you_had_my_skill_set_what_kind_of_business/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-30T15:07:19+00:00 (220h ago)
36. [I turned years of Minecraft Redstone projects into rednw.com — my first digital product marketplace](https://www.reddit.com/r/SideProject/comments/1w2e3v9/i_turned_years_of_minecraft_redstone_projects/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-30T10:35:53+00:00 (224h ago)
37. [I Built a 81K+ Reddit Community as a Student — Now I’m Trying to Figure Out What to Build Around It](https://www.reddit.com/r/SideProject/comments/1w28w4m/i_built_a_81k_reddit_community_as_a_student_now/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-30T05:38:02+00:00 (229h ago)
38. [I turned one sold-out ticket monitor into five attraction-specific products — what I learned](https://www.reddit.com/r/SideProject/comments/1w1y1b2/i_turned_one_soldout_ticket_monitor_into_five/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-29T21:05:19+00:00 (238h ago)
39. [I vibe coded DECENT, A portfolio app/website for designers that uses Figma with more feature coming soon.](https://www.reddit.com/r/SideProject/comments/1w0sbfu/i_vibe_coded_decent_a_portfolio_appwebsite_for/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-28T14:35:21+00:00 (268h ago)
40. [I built an alternative to Vestaboard that doesn't cost 199/year](https://www.reddit.com/r/SideProject/comments/1vz9hy0/i_built_an_alternative_to_vestaboard_that_doesnt/)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-08-26T20:54:32+00:00 (310h ago)
