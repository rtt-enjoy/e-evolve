# Passive Product Income Queue

Refreshed: 2026-11-11T18:15:37.530611+00:00

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

Build the product so it costs nothing per user (client-side, self-hosted, or a downloadable asset), ship the free tier on channels with organic discovery, and collect payment through the validated Tron (TRC-20) receive address already appended to every published article. The core pattern is: free distribution does the discovery, and the wallet ask — placed in the README, FUNDING.yml, --help output, and product page — converts without a storefront. Getly is the one zero-fee storefront found that settles USDT directly to the owner's own Tron wallet with no KYC, so it covers buyers who want a card/paywall flow; GitHub Releases and dev.to articles carry the same product at no cost. The only unavoidable cost on the table is Chrome Web Store's one-time $5 developer registration if the product is a browser extension. No revenue is estimated: real income is the on-chain balance only.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Direct wallet address (already live) | TRC-20 USDT receive address on product page, README, FUNDING.yml, --help output | Zero. No account, no platform, no fee. | USDT on Tron (TRC-20), direct to the owner's own wallet; already validated | Paste the address into the README, .github/FUNDING.yml custom field, product page, and the tool's about/--help output — one-time | Payment goes straight on-chain; no processor can freeze it and no owner action happens per sale |
| Getly (getly.store) | Digital-goods storefront with native stablecoin payouts | No monthly fee; network fee on payout. Verify current terms for the revenue cut. | USDT/USDC to the seller's own wallet; Tron (TRC-20) supported — same network/asset as the existing address. Stated minimum payout $15 on Tron (verify current terms) | One-time account signup, product listing with download file, wallet address entered for payout | Storefront handles payment and automated file delivery per sale; owner does nothing per transaction |
| GitHub Releases + FUNDING.yml | Free hosting for binaries/archives with a sponsor button and in-repo wallet ask | Zero — same account that already hosts the code | Direct to the existing TRC-20 address via README/FUNDING.yml custom URL | Cut a release, write release notes carrying the ask, add FUNDING.yml — one-time | Files download automatically forever; the ask travels with every copy and fork |
| Chrome Web Store | Distribution with real organic discovery for browser extensions | One-time $5 developer registration; covers up to 20 extensions; no cut on free extensions. This is the only non-zero cost in this plan. | None natively — monetisation is the in-extension wallet ask or a paid upgrade delivered via Getly | Pay $5 once, package and upload the extension, write the listing — one-time | Store handles installs and updates; paid upgrades delivered by storefront or licence key need no per-sale work |
| itch.io | Lists tools and asset packs, not just games; free to upload | Free to publish; open revenue share (default ~10%, seller-adjustable). Verify current terms. | Fiat only — payout requires a tax interview with a TIN and a one-time $3 identity fee. Listed for reach, not for crypto settlement. | One-time upload and page setup; payout setup only if fiat settlement is acceptable | Buyers download instantly after purchase; no owner action per sale |
| dev.to articles (already running) | Problem-focused articles whose footer carries the product link and wallet address | Zero — publishing pipeline already exists | Direct to the existing TRC-20 address | None beyond writing the article the product answers; reuses existing infrastructure | Published articles keep reaching readers indefinitely with no upkeep |

## Product Ideas

1. **One-annoyance browser extension**
   - Who buys: Users of a specific site or workflow who hit one repeated friction daily
   - Deliverable: Free extension from Chrome Web Store; paid tier unlocks the advanced feature via licence key delivered by Getly
   - Pricing model: Free tier plus paid upgrade (one-time licence)
   - Cost per extra user: Zero — extensions run client-side
   - Free stack: Chrome Web Store listing ($5 one-time), Getly for licence delivery, GitHub for code and wallet ask
2. **Single-purpose CLI/desktop utility**
   - Who buys: Developers or power users searching for exactly this one fix
   - Deliverable: Free binary on GitHub Releases; paid upgrade or convenience build as a Getly download
   - Pricing model: Free tier plus paid upgrade, with a direct wallet ask in --help output
   - Cost per extra user: Zero — self-hosted, runs on the buyer's machine
   - Free stack: GitHub Releases hosting, GitHub Pages landing page, FUNDING.yml wallet ask
3. **Template/preset/asset pack**
   - Who buys: Users of an existing tool who want a polished starting point
   - Deliverable: A downloadable file bundle built once
   - Pricing model: One-time licence or pay-what-you-want via Getly; free sample pack with wallet ask as funnel
   - Cost per extra user: Zero — static files, no server
   - Free stack: Getly storefront, GitHub Releases for the free sample, itch.io for extra reach
4. **Static client-side web tool**
   - Who buys: Anyone with the problem the tool solves, arriving via search or articles
   - Deliverable: Free hosted tool; paid tier is a downloadable enhanced version or licence unlock
   - Pricing model: Free tier plus paid upgrade
   - Cost per extra user: Zero — runs entirely in the browser, no server
   - Free stack: GitHub Pages hosting, GitHub Actions for scheduled builds, dev.to articles for discovery

## Next Actions

- Paste the validated TRC-20 address into the product's README, .github/FUNDING.yml (custom field), product page, and the tool's --help/about output so every copy carries the ask
- Build the product as a free tier with a clearly separated paid upgrade, and cut a GitHub Release hosting the files with the ask in the release notes
- Sign up on Getly once, list the paid tier with the Tron wallet as the payout address, and confirm the payout minimum and revenue cut against current terms before relying on it
- If it is a browser extension, pay the one-time $5 Chrome Web Store registration and publish the free tier there for organic discovery
- Write one dev.to problem-workaround article where the product is the fix and the footer carries both the product link and the wallet address, reusing the existing publishing pipeline

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
8. [Lowbetweentrim/crypto-portfolio-tracker](https://github.com/Lowbetweentrim/crypto-portfolio-tracker)
   - Kind: asset
   - Score: 71/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Self-hosted, privacy-first crypto portfolio tracker. Import transactions via CSV, track real-time PnL, and manage your assets locally. No…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-06T09:58:59+00:00 (128h ago)
9. [mdiri-ai/SoduWork](https://github.com/mdiri-ai/SoduWork)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; The AI-native engine for teams and their agents. Multi-harness, multi-agent, self-hosted.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T02:43:14+00:00 (328h ago)
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
12. [Show HN: Perch by mxRaven, a self-hosted mailbox and CLI in 1 file](https://news.ycombinator.com/item?id=50454221)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I have been working on mxRaven: https://mxraven.com for the past couple of months, and it has been hard to explain the idea without…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T14:57:04+00:00 (3h ago)
13. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T22:37:28+00:00 (20h ago)
14. [A license-key server on Cloudflare Workers + KV, with signed keys and activation limits](https://dev.to/kitebyte/a-license-key-server-on-cloudflare-workers-kv-with-signed-keys-and-activation-limits-ja4)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: If you sell a desktop app, CLI, plugin or template, you eventually need license keys: one per sale,...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-10T20:27:55+00:00 (22h ago)
15. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (238h ago)
16. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (1707h ago)
17. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
18. [Gumroad Fees in 2027: What You Actually Pay Per Sale](https://kotakmdshahil.medium.com/gumroad-fees-in-2027-what-you-actually-pay-per-sale-1f276bef4b20)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: If you’re about to sell your first digital product, the fee question comes before the pricing question. Because a $29 product isn’t $29 in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T14:06:49+00:00 (4h ago)
19. [How to Sell Digital Products on Gumroad in 2027 (Beginner Guide)](https://kotakmdshahil.medium.com/how-to-sell-digital-products-on-gumroad-in-2027-beginner-guide-9c2d6f7e09b0)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Type “how to sell digital products” into Google and you’ll get a thousand guides.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T13:54:43+00:00 (4h ago)
20. [Show HN: Whisperstream – Free, open-source local dictation for Windows](https://news.ycombinator.com/item?id=50453372)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I built Whisperstream, a free and open-source dictation app for Windows. You've seen a dozen of these, so what makes it different…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-11T13:47:45+00:00 (4h ago)
21. [I built an offline-first PC game launcher that calculated my 18,838-hour backlog debt](https://dev.to/riteshsonilogpile/i-built-an-offline-first-pc-game-launcher-that-calculated-my-18838-hour-backlog-debt-52a9)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Like a lot of PC gamers, my library is scattered across 8 different storefronts. Between Steam sales,...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-11T13:44:35+00:00 (4h ago)
22. [8 Digital Products That Actually Sell in 2027 (With Real Gumroad Data)](https://kotakmdshahil.medium.com/8-digital-products-that-actually-sell-in-2027-with-real-gumroad-data-3b50d8830dee)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Forget generic planners and “make money online” courses.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T13:39:43+00:00 (5h ago)
23. [I Built Habla: A Spanish Learning App with React Native and Expo](https://dev.to/el_brah_a71d5a2c0b3862e9f/i-built-habla-a-spanish-learning-app-with-react-native-and-expo-2d4l)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: As an indie developer, I built Habla – Learn Spanish Fast to make Spanish practice fit into everyday...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-11T12:00:51+00:00 (6h ago)
24. [Why Your First Gumroad Product Got Zero Sales (And the 14-Day Plan I’d Follow Instead)](https://medium.com/@ytzoom/why-your-first-gumroad-product-got-zero-sales-and-the-14-day-plan-id-follow-instead-5ebbcd41b712)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You finished the PDF. You made a cover in Canva. You set a price, hit publish, shared the link once, and waited.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T11:54:31+00:00 (6h ago)
25. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T09:26:35+00:00 (9h ago)
26. [50 Micro SaaS Business Ideas You Can Build Without Coding in 2026](https://medium.com/@fazak22344/50-micro-saas-business-ideas-you-can-build-without-coding-in-2026-f6cdad482e71)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Have you ever wanted to start an online business but felt that you needed coding skills, technical knowledge, or a big budget?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T06:41:28+00:00 (12h ago)
27. [How to Launch a Side Project in One Week: A Realistic Plan](https://medium.com/@kanisshka12/how-to-launch-a-side-project-in-one-week-a-realistic-plan-26f34f8b04fa)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Seven days, no budget, and a clear goal: get your first real visitors and feedback
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T03:31:01+00:00 (15h ago)
28. [A Small Laptop Is a Full Build Kit: Bootstrapping with a Chromebook, Claude, and GitHub](https://dev.to/earlgreyhot1701d/a-small-laptop-is-a-full-build-kit-bootstrapping-with-a-chromebook-claude-and-github-4j16)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A small laptop is a full build kit. Here's how far mine went. TL;DR: A reader suggested I publish...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-11T02:41:57+00:00 (16h ago)
29. [Building Introworth: Pricing Attention Starts With an Audit, Not a Rate Card — What Worked, What Broke](https://dev.to/onelifevibe/building-introworth-pricing-attention-starts-with-an-audit-not-a-rate-card-what-worked-what-3ddl)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Nobody can price something they have never measured. That sounds obvious in every other market, and...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-11T00:42:52+00:00 (18h ago)
30. [I Left My Job and Started Building My Own Startup: The Journey Behind Design Toolkit](https://medium.com/@himido551/i-left-my-job-and-started-building-my-own-startup-the-journey-behind-design-toolkit-26d5820b42c3)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: From UI/UX designer to solo founder — how I turned everyday design problems into a Chrome extension, launched it, found my first customers…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T20:58:29+00:00 (21h ago)
31. [PersiOnOff/tenlith](https://github.com/PersiOnOff/tenlith)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open-source .NET + React SaaS starter with multi-tenancy, authentication, teams, Stripe billing and Docker.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T19:06:58+00:00 (23h ago)
32. [6 Developer Tools That Pay for Themselves in a Week (Mac + SaaS Edition)](https://fahadh.medium.com/6-developer-tools-that-pay-for-themselves-in-a-week-mac-saas-edition-bdaca567c3ca)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A shortlist of developer tools for indie hackers who ship on Mac and need auth, payments, and product signal without drowning in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T16:59:34+00:00 (25h ago)
33. [I built a launch board where your backlink doesn’t depend on a badge](https://medium.com/@karthi.98p/i-built-a-launch-board-where-your-backlink-doesnt-depend-on-a-badge-895f97ab0cdb)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: If you’ve launched a side project on a few directories, you know the deal. They give you a dofollow link, but only while their badge sits…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T16:50:43+00:00 (25h ago)
34. [A weekend launch checklist for a side project with no audience](https://dev.to/ship_stack/a-weekend-launch-checklist-for-a-side-project-with-no-audience-1ndm)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most first launches fail for a boring reason: the product is ready on Friday night, and Saturday is...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-10T08:47:23+00:00 (34h ago)
35. [The 5 Best Chrome Extensions For Designers In 2026](https://medium.com/@nikhilsaiankilla/the-5-best-chrome-extensions-for-designers-in-2026-8c5f250a3ef4)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Compare 5 Chrome extension for designers: Hueclip, CSS Peeper, Fonts Ninja, Color Zilla, and Inspo AI. Pros, cons and pricing for each.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T07:54:39+00:00 (34h ago)
36. [Selling Has No Error Message](https://dev.to/priyanshudotsol/selling-has-no-error-message-1hmi)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: ~/actuity ❯ npm run build ✓ compiled in 1.24s ~/actuity ❯ npm run deploy ✓ live at...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-10T07:10:31+00:00 (35h ago)
37. [HolyArrs/HolyArrs](https://github.com/HolyArrs/HolyArrs)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One self-hosted app for your shows, movies and music.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T23:53:25+00:00 (42h ago)
38. [22 free places to launch a side project (and what each one asks in return)](https://dev.to/theavgdev_cd728e501377f9f/22-free-places-to-launch-a-side-project-and-what-each-one-asks-in-return-n42)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I kept finishing small projects and then staring at a list of "100+ places to launch your startup"...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T22:08:47+00:00 (44h ago)
39. [AgriciDaniel/obsidian-herdr](https://github.com/AgriciDaniel/obsidian-herdr)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Run Claude Code, Codex, Antigravity and OpenCode in persistent Herdr terminals inside Obsidian, with Mission Control and a safe, undoable…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T18:37:49+00:00 (48h ago)
40. [Five TikTok Formats, One Ceiling: What 2.5 Seconds Told Me](https://dev.to/marcoblch/five-tiktok-formats-one-ceiling-what-25-seconds-told-me-2532)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I tested five short-video formats for OutfitMaker in two weeks. Same audience, same ceiling at about 2.5 seconds, and every customer I…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T18:22:31+00:00 (48h ago)
41. [Three sales from 27 views, and three paid pages beside it that sold nothing](https://dev.to/bananafestdestiny/three-sales-from-27-views-and-three-paid-pages-beside-it-that-sold-nothing-5801)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Four paid pages by the same maker, on the same storefront, in the same weeks. One of them has sold three copies at $6. The other three have…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T18:16:51+00:00 (48h ago)
42. [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of awesome developer-first tools products.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T17:05:35+00:00 (49h ago)
43. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-09T00:36:30+00:00 (66h ago)
44. [Build, Secure & Monetize Your First ChatGPT Plugin](https://dev.to/leojulieta/build-secure-monetize-your-first-chatgpt-plugin-4155)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Build, Secure, and Monetize Your First ChatGPT Plugin (June 2026 Launch) ...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-08T20:10:53+00:00 (70h ago)
45. [Victor-Go/VictorLoad](https://github.com/Victor-Go/VictorLoad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Chrome/Edge extension to download videos and images from YouTube, X and Bilibili in a side panel
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-07T20:44:57+00:00 (94h ago)
46. [Sell software through your own Paddle or Lemon Squeezy account—with licensing connected](https://dev.to/permitcore/sell-software-through-your-own-paddle-or-lemon-squeezy-account-with-licensing-connected-1jbn)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You want to sell your app, not spend every release maintaining a second product made of checkout...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-07T19:31:56+00:00 (95h ago)
47. [What “scheduled” means on IndieNeed before a product goes live](https://dev.to/indieneed/what-scheduled-means-on-indieneed-before-a-product-goes-live-heh)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: IndieNeed is a small launch site for indie makers. A launch is tied to a specific day: the product is...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-07T15:12:48+00:00 (99h ago)
48. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T15:11:13+00:00 (123h ago)
49. [silentprovider423/HomeRoll](https://github.com/silentprovider423/HomeRoll)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Native iOS photos app for your own Immich server
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T00:38:42+00:00 (138h ago)
50. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (287h ago)
51. [Show HN: DistractFree-Chrome extension and web app to stop doomscrolling](https://news.ycombinator.com/item?id=50299880)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T04:31:31+00:00 (302h ago)
52. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (312h ago)
53. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
54. [Show HN: Yogurt – Free, private, open-source alternative to Granola](https://news.ycombinator.com/item?id=50454625)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey HN, I’m Eric and I want to share an OSS project that I’ve been building in my free time. Yogurt is a free, MIT licensed desktop app…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-11T15:33:06+00:00 (3h ago)
55. [Do You Pay Microsoft Store Fees If You Use Your Own Payment System?](https://medium.com/@nookeshkarri7/do-you-pay-microsoft-store-fees-if-you-use-your-own-payment-system-af3cde9229eb)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I sell a $49 Windows licence through Lemon Squeezy inside a Microsoft Store listing. Here is what Microsoft takes and what it doesn’t.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T03:44:00+00:00 (14h ago)
56. [johackim/awesome-indiehackers](https://github.com/johackim/awesome-indiehackers)
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Awesome list about indie hackers
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T13:35:11+00:00 (5h ago)
57. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
58. [I Built 5 Websites in One Day](https://medium.com/@banedigital/i-built-5-websites-in-one-day-d813be054263)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: And I still had zero sales to show for it — so I am starting here, from zero, in public
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T06:48:42+00:00 (12h ago)
59. [My customer got 11 clients in a month by renting keywords from directories](https://dev.to/submitmap/my-customer-got-11-clients-in-a-month-by-renting-keywords-from-directories-2921)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A customer of mine got 11 paying clients in their first month from search, and their own site still...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-10T22:51:21+00:00 (19h ago)
60. [How to Rank a Brand-New SaaS Site With Zero Authority: A 7-Step Playbook for Indie Developers](https://pub.aeosoup.com/how-to-rank-a-brand-new-saas-site-with-zero-authority-a-7-step-playbook-for-indie-developers-1402f12cc6e3)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Your SaaS site is three months old. Google sends you almost nothing. Continue reading on AEO Soup »
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T16:59:21+00:00 (25h ago)
61. [Show HN: Monoprint – Beautiful code images, GPUI desktop app, CLI, Rust library](https://news.ycombinator.com/item?id=50440754)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I built Monoprint in Rust as a CLI tool for generating code screenshots for an in-house programming language. I liked it so much that I…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T14:19:18+00:00 (28h ago)
62. [7 Truly Free Chrome Extensions That Replace Paid Software (No Premium Plan, No Catch)](https://medium.com/inbox-growth/7-truly-free-chrome-extensions-that-replace-paid-software-no-premium-plan-no-catch-be2e68331df0)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Many “free” extensions hide a paid upgrade. These don’t. They’re open-source or fully free, and each one saves you from paying for……
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T10:16:50+00:00 (32h ago)
63. [Ask HN: Advise on monetization model for my freemium app wanted](https://news.ycombinator.com/item?id=50280505)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm an indie app dev and looking for some conceptual help with one of my freemium apps. I'm thinking about completely restructuring the…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T20:34:28+00:00 (334h ago)
