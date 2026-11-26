# Passive Product Income Queue

Refreshed: 2026-11-26T02:39:10.998390+00:00

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

The best zero-budget route is: build one small client-side product that costs nothing per user, ship it free everywhere (GitHub Releases, GitHub Pages, Chrome Web Store), and monetize through a paid upgrade sold via a storefront that settles USDT on Tron directly to the already-validated receive address, plus a plain wallet ask embedded in the README, product page, and the tool's own --help output. Chrome Web Store is the only non-zero cost (a one-time $5 registration), so a browser extension route should either skip it initially or treat that $5 as the entire budget. Everything else is free to list and requires no KYC or custodian when payouts go straight to the owner's wallet.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Wallet ask (already live) | A published Tron receive address on the product page and README accepts USDT directly. | Free. | USDT TRC-20, straight to the owner's own wallet; no custodian, no KYC. | Paste the address into the README, product page, FUNDING.yml custom field, docs footer, and --help output. | Payment is user-initiated; no invoice, no platform, no per-sale action. |
| Getly | Digital-goods storefront with card and crypto checkout. | No monthly fee; per-sale processing cut — verify current terms. | USDT/USDC to own wallet; Tron minimum payout ~$15, BNB Smart Chain ~$5 — verify current terms. | One-time account signup, product page creation, wallet address entry. Verify payout rules manually. | Storefront delivers the file or licence after payment with no owner involvement. |
| GitHub Releases + README + FUNDING.yml | Free hosting for binaries/archives with a sponsor/tip path in the repo. | Free. | Any the owner accepts at their published address; no platform involved. | Push the repo, create a release, add .github/FUNDING.yml with the receive address in the custom field. | Download links and the address are static; nothing to fulfill. |
| Chrome Web Store | Distribution for browser extensions with organic discovery. | One-time $5 developer registration, covers up to 20 extensions; no revenue cut on free extensions. The only non-zero cost in this plan. | None directly; monetize via a paid upgrade sold on Getly or the wallet ask in the extension's about/options screen. | One-time $5 registration and per-extension upload (verify current terms). | Store handles updates and installs; sales happen off-store via the licence path. |
| itch.io | Storefront for tools, assets, and games; pay-what-you-want supported. | Free to upload; seller chooses the platform's revenue share (default ~10%). | None — fiat payout only, and requires a tax interview with a TIN plus a one-time $3 identity fee. Include only if the owner accepts that KYC-style step; otherwise skip. | Account, tax interview, TIN, upload. One-time. | Buyers download after purchase; no owner action per sale. |
| dev.to article funnel (already running) | Daily publishing infrastructure whose footers already carry the receive address. | Free; uses existing automation. | USDT TRC-20 via the same validated address. | Write one problem-workaround article where the product is the fix and the footer is the ask. | Article and footer persist; back-catalogue readers keep hitting the ask. |

## Product Ideas

1. **Chrome extension: fixes one specific site annoyance (e.g. decluttering a popular web app)**
   - Who buys: Daily users of that site who hit the annoyance every session
   - Deliverable: Free extension with a pro unlock: extra options, custom rules, sync of settings
   - Pricing model: Free tier plus paid upgrade; licence delivered via Getly download or paid via the address in the options/about screen
   - Cost per extra user: $0 per user — client-side only, no server
   - Free stack: Chrome Web Store listing ($5 one-time) or GitHub Releases + manual install; static pro files on GitHub Pages
2. **Single-purpose CLI utility (e.g. batch-renames or converts one messy format)**
   - Who buys: Developers and technical users searching for exactly that fix
   - Deliverable: Free binary on GitHub Releases; paid tier unlocks batch mode or config presets
   - Pricing model: Free core, one-time licence for pro; wallet ask printed in --help
   - Cost per extra user: $0 — static binary, no backend
   - Free stack: GitHub Releases for hosting, GitHub Actions for builds, README/FUNDING.yml for the ask
3. **Static web tool that runs entirely client-side (e.g. a formatter or calculator for one niche)**
   - Who buys: Practitioners who bookmark and reuse the tool repeatedly
   - Deliverable: Free web tool; a paid downloadable offline/extended version via Getly
   - Pricing model: Free hosted tool plus one-time paid download; footer carries the receive address
   - Cost per extra user: $0 — GitHub Pages static hosting, free tier
   - Free stack: GitHub Pages, GitHub repo, Getly for the paid file
4. **Preset/asset pack for a tool people already use**
   - Who buys: Users of that tool who want results without building configs themselves
   - Deliverable: A downloadable pack of presets/templates compiled once
   - Pricing model: One-time licence or pay-what-you-want via Getly and itch.io; address in the pack's README
   - Cost per extra user: $0 — a file, built once, copied on download
   - Free stack: Getly delivery, GitHub Releases mirror, dev.to article as the discovery piece

## Next Actions

- Pick one product shape, build the free version client-side so marginal cost is zero, and host it on GitHub Releases (free).
- Ship the ask everywhere the artifact travels: README, .github/FUNDING.yml custom field, product page, docs footer, --help/about output — all using the existing validated Tron receive address.
- Sign up on Getly once, list the paid upgrade or pack, enter the Tron wallet for USDT payout, and verify current fees, payout minimums and terms by hand before relying on it.
- Write one problem-workaround article on dev.to (reusing the existing publishing pipeline) where the product is the fix and the footer carries the address.
- If the product is an extension and the $5 one-time Chrome Web Store fee is acceptable as the entire budget, register and list it there for organic discovery; verify current terms first.

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
- [Google AI Studio (Gemini API)](https://aistudio.google.com/app/apikey): No credit card required. Gemini 2.5 Flash free tier is roughly 1,500 requests/day -- verify current limit.

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
- **Coinbase Commerce:** DEFUNCT. Permanently shut down 2026-03-31 for merchants outside the US/Singapore, with no extensions offered. Its replacement (Coinbase Business) is fully custodial and US/Singapore only. Still recommended in current listicles -- a Sellix-class trap.
- **CoinPayments:** Geo-dead and KYC-mandatory. EU/EEA service discontinued after 2026-07-01 under MiCA, and the current platform requires identity verification for all users, not just above a threshold.
- **kofi.network:** IMPOSTOR RISK -- not affiliated with ko-fi.com despite the name and a '(c) 2026 Ko-fi' footer. No operator disclosure. It advertises wallet-to-wallet USDT on BEP-20, which is exactly the property that would rank it highly here, which is why it is written down as refused rather than left to be rediscovered.
- **NOWPayments (as a direct channel):** Marketed as non-custodial, but the default flow routes funds through their wallet and KYC triggers at volume and always for fiat. Reached indirectly anyway: it is the rail Getly uses to dispatch payouts, so using it directly adds a custodian without adding a storefront.
- **Gitcoin / Allo:** Wound down. Grants Lab and Grants Stack reached end-of-life 2025-05-31 and Allo is in maintenance mode. KYC applies above $15k matching regardless.
- **Drips Network:** Genuinely non-custodial and plausibly identity-free, but Ethereum ERC-20 only. It cannot reach the Tron address this project publishes, so it would need a second address and a second meter (Principle 3f) to earn a cent.
- **BTCPay Server:** The only fully non-custodial, fee-free, no-KYC option on the table -- and it needs a server. This project has none (GitHub Actions is outbound-only), and third-party hosting reintroduces the dependency it exists to avoid. Refused on infrastructure, not on merit.
- **Gumroad, Substack, Polar, GitHub Sponsors, Ko-fi, Buy Me a Coffee, Payhip, Liberapay, Lemon Squeezy, Paddle, Open Collective:** All require identity verification, directly or through Stripe/PayPal onboarding, and none settles crypto to a seller-controlled address. Verified 2026-09-15 after the owner hit exactly this wall on Gumroad and Substack. Buy Me a Coffee is the specific trap: it accepts crypto from buyers but converts to USD and pays out via Stripe, US accounts only.

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
2. [Put the receive address in the GitHub repo itself — FUNDING.yml, README, and releases](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository)
   - Kind: channel
   - Score: 95/100
   - Cost: free to list
   - Owner must do: None beyond committing a file to the repo the owner already controls.
   - Why: settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time
   - Next: Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
   - Verified: FUNDING.yml custom: field accepts arbitrary URLs and requires no Sponsors enrolment.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Put the receive address in the GitHub repo itself — FUNDING.yml, README, and releases
     SOURCE         local-playbook
     LINK           https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/displaying-a-sponsor-button-in-your-repository
     COST           $0.00 (free to list)
     OWNER MUST DO  None beyond committing a file to the repo the owner already controls.
     NEXT STEP      Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
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
3. Publish the product as a downloadable file, priced by an honest ask, hosted on GitHub Releases
   - Kind: channel
   - Score: 95/100
   - Cost: free to list
   - Owner must do: None. Uses the repo the owner already has.
   - Why: settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time
   - Next: Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Publish the product as a downloadable file, priced by an honest ask, hosted on GitHub Releases
     SOURCE         local-playbook
     LINK           no public URL
     COST           $0.00 (free to list)
     OWNER MUST DO  None. Uses the repo the owner already has.
     NEXT STEP      Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
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
4. Ask in the artifact, not only beside it — README, --help output, and docs footer
   - Kind: channel
   - Score: 95/100
   - Cost: free to list
   - Owner must do: None.
   - Why: settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time
   - Next: Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Ask in the artifact, not only beside it — README, --help output, and docs footer
     SOURCE         local-playbook
     LINK           no public URL
     COST           $0.00 (free to list)
     OWNER MUST DO  None.
     NEXT STEP      Put the same published receive address on the product page and in the README, then confirm a reader can see it -- receipt_check already proves this for the articles.
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
5. [Getly — sell a digital product, settle USDT on Tron to your own wallet](https://www.getly.store/sell/crypto)
   - Kind: channel
   - Score: 92/100
   - Cost: free to list
   - Owner must do: Owner signs up (no ID upload), adds the Tron receive address, and uploads the product once.
   - Why: settles to the wallet address this project already publishes; sells the product while nobody is working; the signup is one-time
   - Next: List the product once, set the price, and point the payout at the published Tron address. Owner does this by hand: Owner signs up (no ID upload), adds the Tron receive address, and uploads the product once.
   - Verified: Re-verified on getly.store/sell/crypto 2026-09-15: "Getly has no KYC process -- there are no ID documents to upload and nobody reviews them"; the only inputs are a wallet address and its network. Tron
   - Codex request:
     Move a digital product one step closer to earning without owner involvement.
     
     KIND           channel (where it gets paid)
     LEAD           Getly — sell a digital product, settle USDT on Tron to your own wallet
     SOURCE         channel-table
     LINK           https://www.getly.store/sell/crypto
     COST           $0.00 (free to list)
     OWNER MUST DO  Owner signs up (no ID upload), adds the Tron receive address, and uploads the product once.
     NEXT STEP      List the product once, set the price, and point the payout at the published Tron address. Owner does this by hand: Owner signs up (no ID upload), adds the Tron receive address, and uploads the product once.
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
6. Ship the product free, sell the upgrade, ask in the README
   - Kind: channel
   - Score: 81/100
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
7. [Chrome Web Store — one-time $5, covers up to 20 extensions](https://developer.chrome.com/docs/webstore/register)
   - Kind: channel
   - Score: 72/100
   - Cost: $5.00 one-time
   - Owner must do: Owner pays the one-time $5 registration and submits the extension for review.
   - Why: sells the product while nobody is working; the signup is one-time; costs $5.00 once, stated rather than hidden
   - Next: List the product once and set the price. Owner does this by hand: Owner pays the one-time $5 registration and submits the extension for review.
   - Verified: One-time $5, no renewal, 20-extension limit confirmed on developer.chrome.com 2026-09-08.
8. [cryptoapi/Bitcoin-Wordpress-Plugin](https://github.com/cryptoapi/Bitcoin-Wordpress-Plugin)
   - Kind: asset
   - Score: 66/100
   - Cost: not published
   - Owner must do: nothing
   - Why: GoUrl Official Bitcoin Payment Gateway for Wordpress 3.5+ (or higher). Sell Products, Files, Digital Downloads, Membership on your website.…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T13:22:06+00:00 (37h ago)
9. [balikunsh-bot/keepassxc-talroora](https://github.com/balikunsh-bot/keepassxc-talroora)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Keepassxc Talroora organizes credential records and manages encrypted password databases.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T20:10:03+00:00 (174h ago)
10. Open-source the tool and take sponsorship on the repo
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A public repository is discovery that keeps working after it is published, and the wallet address in the README is a receive path that…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
11. [itch.io — free to publish, but a payout needs a tax interview and a TIN](https://itch.io/docs/creators/payments)
   - Kind: channel
   - Score: 61/100
   - Cost: $3.00 one-time
   - Owner must do: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Verified: Tax interview, TIN requirement and the one-time $3.00 identity fee confirmed on itch.io/docs/creators/payments 2026-09-15. The earlier row said 'free to publish, no approval queue' and recorded cost_u
12. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T18:36:08+00:00 (8h ago)
13. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (583h ago)
14. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
15. [w01fb0ss/PiBot](https://github.com/w01fb0ss/PiBot)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; Open-source, local-first AI agent team for your desktop: multi-agent group chats, computer use, browser, MCP, routines and approvals.…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T06:54:24+00:00 (116h ago)
16. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (2051h ago)
17. [Why Your Gumroad Product Page Gets Visitors but No Sales (and What to Change First)](https://victore97.medium.com/why-your-gumroad-product-page-gets-visitors-but-no-sales-and-what-to-change-first-67fa1109f758)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Before you lower the price, read this. The problem is usually one of five things, and the price is rarely the first.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T23:09:02+00:00 (4h ago)
18. [I aimed for 90% form-fill accuracy on-device and got 80.7%: what a code gate around Gemini Nano taught me](https://dev.to/edycutjong/i-aimed-for-90-form-fill-accuracy-on-device-and-got-807-what-a-code-gate-around-gemini-nano-3937)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A Chrome form filler that reads customer messages on-device with Gemini Nano via Firebase AI Logic, and the three accuracy bars it missed.
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T19:54:27+00:00 (7h ago)
19. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T19:04:40+00:00 (8h ago)
20. [Show HN: Eight invisible personal Mac tools in one open source app](https://news.ycombinator.com/item?id=50645131)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T17:48:04+00:00 (9h ago)
21. [Day 5: I read about 570 posts looking for paying work and found none](https://dev.to/work247ia/day-5-i-read-about-570-posts-looking-for-paying-work-and-found-none-pac)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: I'm Moonlighter, an AI (Claude, made by Anthropic). I wrote this post myself. A human...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T17:15:03+00:00 (9h ago)
22. [I made $44,645 selling digital products. Here’s what I did wrong](https://travisnicholson.medium.com/i-made-44-645-selling-digital-products-heres-what-i-did-wrong-f471b1ed4008)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Since I started selling digital products online last year, I’ve generated $44,645 in revenue.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T17:04:54+00:00 (10h ago)
23. [This app changed how much I pay for email across my side projects](https://medium.com/@Yogesh_H/this-app-changed-how-much-i-pay-for-email-across-my-side-projects-f923d326d108)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 8 ways to put email on your own domain, what each costs for five projects, and the free trick that stops working in January 2027
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T12:48:55+00:00 (14h ago)
24. [9 self-hosted apps that replace $170 a month of SaaS bills on a side project](https://medium.com/@Yogesh_H/9-self-hosted-apps-that-replace-170-a-month-of-saas-bills-on-a-side-project-d2b174d4d72a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Analytics, automation, newsletters, uptime, forms, support chat, error tracking and email: $169.99 a month at list price, or one small…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T12:32:32+00:00 (14h ago)
25. [Every side project needs an email address](https://medium.com/@sightradar.connect/every-side-project-needs-an-email-address-fd427a0aa84c)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I stopped paying per seat for them
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T10:31:51+00:00 (16h ago)
26. [Talking to 15 founders about launch distribution — free AI-visibility snapshot of your product in return](https://dev.to/visionwei/talking-to-15-founders-about-launch-distribution-free-ai-visibility-snapshot-of-your-product-in-e6l)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm researching how indie founders actually handle launch distribution, and I'd like to interview 15...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T06:22:21+00:00 (20h ago)
27. [Shirtep/WA-audio-stickers](https://github.com/Shirtep/WA-audio-stickers)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Extensión para Chrome/Edge/Brave que crea stickers con sonido a partir de un video y los envía desde WhatsApp Web (no oficial).
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T22:44:06+00:00 (28h ago)
28. [SilverFeit/StikSound](https://github.com/SilverFeit/StikSound)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: StikSound — Ponle sonido de hasta 5 segundos a tus stickers PNG y GIFs animados para WhatsApp (Windows, macOS & Chrome Extension, 100%…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T21:55:25+00:00 (29h ago)
29. [When do you call a side project done — ship it, shelve it, or kill it?](https://dev.to/userxnom/when-do-you-call-a-side-project-done-ship-it-shelve-it-or-kill-it-1g2k)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Every side project I start reaches the same awkward point: it works, mostly. It's not polished, it's...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-24T21:39:46+00:00 (29h ago)
30. [What kept you going on a side project when almost nobody was using it?](https://dev.to/userxnom/what-kept-you-going-on-a-side-project-when-almost-nobody-was-using-it-23ho)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm a solo developer, and my first app is live. The part nobody talks about much is the quiet stretch...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-24T20:32:50+00:00 (30h ago)
31. [Micro SaaS Without Coding: How Solo Founders Are Building $1,000/Month Tools in a Weekend](https://medium.com/@fazak22344/micro-saas-without-coding-how-solo-founders-are-building-1-000-month-tools-in-a-weekend-535aeb281ed7)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You don’t need a tech co-founder or venture capital. Here is how to spot a profitable Micro SaaS idea, validate it fast, and grab a free…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T12:27:36+00:00 (38h ago)
32. [Plausible Spent 324 Days Stuck Near $400 a Month. Then It Picked a Fight With Google Analytics](https://abhinayguptha.medium.com/plausible-spent-324-days-stuck-near-400-a-month-then-it-picked-a-fight-with-google-analytics-ff008de63734)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: How a bootstrapped analytics SaaS reached $1M a year in revenue without paying for a single ad, and the quiet moves behind the viral post
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T09:07:41+00:00 (42h ago)
33. [Show HN: Alter – Restyle any website by typing what you want (extension, BYOK)](https://news.ycombinator.com/item?id=50617387)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Alter is a Chrome extension: open it on any site, type something like "hide the sidebar and display articles in Hacker News format", or…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-23T19:11:59+00:00 (56h ago)
34. [I emailed 95 indie iOS devs their real App Store ranks. Here's what actually happened](https://dev.to/eunice99x/i-emailed-95-indie-ios-devs-their-real-app-store-ranks-heres-what-actually-happened-en0)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: so for 11 days i did the thing everyone says to do. i replied to people launching their iOS apps on...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-23T16:41:39+00:00 (58h ago)
35. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-23T15:27:09+00:00 (59h ago)
36. [giauphan/google-qr-sms](https://github.com/giauphan/google-qr-sms)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Chrome Extension (MV3) to downgrade Google cross-device QR code verification back to 6-digit SMS verification.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-23T10:20:59+00:00 (64h ago)
37. [MVP Funding: 8 Ways to Pay for Your First Version](https://medium.com/@shipgrants/mvp-funding-8-ways-to-pay-for-your-first-version-ec0bc3d3343f)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: TL;DR: MVP funding does not have to come from investors. The eight main non-dilutive routes are pre-sales and paid pilots, cloud and AI…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-23T08:53:09+00:00 (66h ago)
38. [Show HN: OpenComputer – an open source alternative to Devin](https://news.ycombinator.com/item?id=50581403)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN! Utpal here, I'm one of the founders of OpenComputer. OpenComputer is an open source cloud coding agent for teams that can run in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T20:19:56+00:00 (126h ago)
39. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T15:11:47+00:00 (132h ago)
40. [ngiken/KenEasy-Gemini-MCP-Auto-Helper](https://github.com/ngiken/KenEasy-Gemini-MCP-Auto-Helper)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Google Gemini MCP 自动化放行与连续对话助手：MV3 永不断线后台引擎 + 智能点击重试，自动点击「始终允许」与「继续/Yes」、4 语言黑白双模式、零飞角自由拖拽悬浮窗、超时桌面通知及 6 层防刷熔断保护。
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T07:20:09+00:00 (139h ago)
41. [Show HN: Mastra Factory, the open-source software factory we use to build Mastra](https://news.ycombinator.com/item?id=50548660)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, we're Shane, Sam, and Abhi. Almost two years ago, we shared Mastra, our open-source TypeScript agent framework, on Show HN:…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-18T16:53:42+00:00 (178h ago)
42. [wittiden/glasshour](https://github.com/wittiden/glasshour)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Glasshour is a custom Chrome new tab page inspired by Apple's Liquid Glass. Built with vanilla HTML, CSS, and JavaScript (Manifest V3), it…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T10:53:21+00:00 (208h ago)
43. [Show HN: Cookiecutter-uv-core – uv template with an agent SDLC and quality gates](https://news.ycombinator.com/item?id=50519945)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T17:09:48+00:00 (226h ago)
44. [telekom/scale](https://github.com/telekom/scale)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Scale is the digital design system for Telekom products and experiences.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T15:07:10+00:00 (228h ago)
45. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (631h ago)
46. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (656h ago)
47. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
48. [Show HN: A tiny macOS app that turns off the MacBook display [free license]](https://news.ycombinator.com/item?id=50507722)
   - Kind: asset
   - Score: 45/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, I made a tiny app that lets you turn off the MacBook screen when you work on external monitors. It does NOT just dim the brightness to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-15T15:37:52+00:00 (251h ago)
49. [How I Self-Host 4 Free Browser Tools (0.3s AI Cutout, Fee Math, Bulk WebP, PDF Invoice) on a Home Mac mini](https://dev.to/flymilkbear/how-i-self-host-4-free-browser-tools-03s-ai-cutout-fee-math-bulk-webp-pdf-invoice-on-a-home-5dcf)
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most small e-commerce sellers and freelancers end up paying $40–$60/month across 4 separate SaaS apps...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-24T13:21:21+00:00 (37h ago)
50. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
51. [How Claude AI Can Help You Build and Sell Digital Products on Gumroad](https://blog.venturemagazine.net/how-claude-ai-can-help-you-build-and-sell-digital-products-on-gumroad-31b7d2c59590)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A practical guide to using Claude AI to research, create, package, and sell digital products on Gumroad — even if you’re starting from……
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-26T01:49:07+00:00 (1h ago)
52. [We sell an RDLC report engine. Our customers asked for the way out. So we built it.](https://dev.to/antoine_ssrs2/we-sell-an-rdlc-report-engine-our-customers-asked-for-the-way-out-so-we-built-it-3p00)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: We make SSRS2, an engine that runs RDLC reports (the format of SQL Server Reporting Services and...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T23:18:13+00:00 (3h ago)
53. [How to Sell One Digital Product From One Page (You Don’t Need a Store)](https://blog.wealthbuildingbaddie.com/how-to-sell-one-digital-product-from-one-page-you-dont-need-a-store-a874f760f54b)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One product and one clear message can be your entire store. Continue reading on Wealth Building Baddie »
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T14:01:02+00:00 (13h ago)
54. [Your Content Is Getting Attention. So Why Is Nobody Buying?](https://medium.com/@madewithai/your-content-is-getting-attention-so-why-is-nobody-buying-44659fe37b39)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The uncomfortable difference between attracting an audience and attracting customers.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T14:01:02+00:00 (13h ago)
55. [I run my whole marketing desk in 30 minutes, from my phone. Here's the exact Grok Bot setup.](https://medium.com/@meestierolff/i-run-my-whole-marketing-desk-in-30-minutes-from-my-phone-heres-the-exact-grok-bot-setup-812099f06dec)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 5 sign-ups, $0 revenue, and a weekday 08:15 Grok Bot prompt you can paste. I still press send myself.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T09:34:44+00:00 (17h ago)
56. [I'm an AI agent running a tiny software business from A$0. Week one: A$0 revenue, 2 users](https://dev.to/snakbacks_sheets/im-an-ai-agent-running-a-tiny-software-business-from-a0-week-one-a0-revenue-2-users-159e)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm Claude, an AI agent. Six days ago a human gave me a domain, an email inbox and one instruction:...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T00:37:47+00:00 (26h ago)
57. [Show HN: Wakeshift – Open-Source MCP Events for Claude Code, Codex and More](https://news.ycombinator.com/item?id=50634239)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: tl;dr: We just open-sourced Wakeshift, which lets any MCP server serve interoperable events via MCP Events or harness-specific bridges.…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-24T20:27:48+00:00 (30h ago)
58. [I Built a Micro SaaS With AI. Here Is How I Would Monetize It](https://ai.plainenglish.io/i-built-a-micro-saas-with-ai-here-is-how-i-would-monetize-it-61351deac7c1)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building it took a weekend. Charging for it took a plan. Here is the pricing playbook I wish I had. Continue reading on Artificial…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T14:52:13+00:00 (36h ago)
59. [Vibe Coding: Build Tiny AI Tools and Sell Them as Micro-SaaS](https://medium.com/ai-made-practical/vibe-coding-build-tiny-ai-tools-and-sell-them-as-micro-saas-34db0675dca3)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You describe what you want in plain English, the AI writes the code, and you sell the result. Tiny tools, real revenue. Continue reading on…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T01:01:02+00:00 (50h ago)
60. [Show HN: Budget – an open-source private budgeting app for Mac and Windows](https://news.ycombinator.com/item?id=50619761)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Budget is a free, open-source app for Mac and Windows. With the simple mode, it gives you what you'd expect of a budgeting app: configure…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-23T21:39:57+00:00 (53h ago)
61. [Lemon Squeezy is shutting down. What should you switch to, by country and by what you sell?](https://dev.to/panchei/lemon-squeezy-is-shutting-down-what-should-you-switch-to-by-country-and-by-what-you-sell-3egb)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Short answer: if your business is in one of Stripe's 37 locations and you sell software or digital...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-23T13:00:00+00:00 (62h ago)
62. [Show HN: Relaticle, an open-source CRM that Claude and ChatGPT can work in](https://news.ycombinator.com/item?id=50600315)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I asked rela (the assistant inside my open source crm relaticle) once for a task and a note (in a test workspace). It shows me a plan, one…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-22T14:59:49+00:00 (84h ago)
63. [title: The Zero-Backend Mobile App: How Cutting Cloud Infrastructure Eliminated My Monthly SaaS Bill published: false](https://dev.to/itech_accesories_b86af4c5/title-the-zero-backend-mobile-app-how-cutting-cloud-infrastructure-eliminated-my-monthly-saas-a58)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A look at the engineering and unit-economics math behind shipping My Momentum with zero servers, zero...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-19T10:16:40+00:00 (160h ago)
