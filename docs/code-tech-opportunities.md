# Passive Product Income Queue

Refreshed: 2026-11-21T17:10:50.759407+00:00

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

The best zero-budget route is to build a small digital product once, host it free on GitHub (repo, Releases, and GitHub Pages), and let discovery come from channels that cost nothing to list on: the product page itself, the README, the release notes, dev.to articles that already run, and one or two free storefronts. The receive path that needs no platform at all is the validated Tron (TRC-20) USDT address the project already publishes: put it on the product page, in the README, in --help output, and in .github/FUNDING.yml, so a user can pay with no storefront, no custodian, and no owner action per sale. Where a storefront is wanted, prefer one that is free to list and settles stablecoin directly to the seller's own wallet with no KYC; treat every fee, minimum payout, and payout rule as something to confirm before relying on it, because dead platforms and changed terms are the main failur

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Direct wallet ask (TRC-20 USDT to the validated address) | Turns any page, README, release note, or CLI help text into a payment point with no platform | $0 to set up, $0 per sale, no revenue cut; the buyer may pay a network fee | USDT on Tron (TRC-20), settled directly to the owner's own wallet, no custodian, no KYC | Paste the already-validated address into the product page, README, --help output, docs footer, and .github/FUNDING.yml (custom: field) once | Payment arrives on-chain with no intermediary and no per-sale action; the address is reused output the project already publishes |
| GitHub Releases + public repo | Hosts the downloadable product and its source free, with no approval queue and no identity check | $0 listing, $0 hosting, no revenue cut | None built in; the release notes and README carry the wallet ask, so payout is the direct channel above | Create the release and write the ask into the release body once per version | Downloads are served automatically from the same account that hosts the code; nothing is held and nothing can be seized |
| Getly | Digital-goods storefront that lets buyers pay by card or crypto and pays the seller in stablecoin | No monthly fee and free listing are claimed; verify current terms before listing | USDT/USDC including TRC-20 to the seller's own wallet, with no KYC for crypto settlement claimed; a minimum payout applies (reported as $15 on Tron) — verify current terms | One manual signup, one product listing, and entering the TRC-20 receive address | Delivery and settlement are handled by the storefront, so a sale needs no owner action; verify payout minimums and current fee terms before relying on it |
| itch.io | Free-to-publish storefront that lists tools and asset packs, not only games, with pay-what-you-want pricing | Free to upload and no approval queue; the platform cut is seller-chosen (open revenue sharing, default around 10%) | Fiat payouts only; being paid requires a completed tax interview with a TIN and a one-time identity verification fee (reported as $3.00) — verify current terms | One signup, one upload, pricing set once | Files are delivered by the platform after a one-time listing; the identity and fiat-only payout is the tradeoff |
| Chrome Web Store (for an extension product) | The distribution channel with real organic discovery for browser extensions | One-time $5 developer registration per account, no renewal, no per-extension fee, no cut of a free extension; this is the only non-zero cost on this list and must be stated as such | None; monetisation is the wallet ask in the extension's own pages, or a paid upgrade sold through a storefront above | Pay the one-time fee, upload the extension, publish once | The store serves installs and updates automatically; the $5 is a one-time cost, not a per-sale one |

## Product Ideas

1. **Single-purpose browser extension that fixes one annoyance**
   - Who buys: Users of a specific site or workflow who hit one repeated friction point and want it gone
   - Deliverable: Free extension in the Chrome Web Store; a paid upgrade (extra features, settings sync, or a pro mode) delivered as a licence key or a second build
   - Pricing model: Free tier for discovery, one-time licence for the upgrade, wallet ask in the extension's about page
   - Cost per extra user: Near zero: the extension runs client-side and updates are served by the store
   - Free stack: Chrome Web Store distribution (one-time $5), GitHub repo for source and issues, wallet address for the upgrade
2. **CLI utility that automates one small, tedious task**
   - Who buys: Developers and power users who run that task by hand often enough to want a one-command version
   - Deliverable: Binary or archive on GitHub Releases; the README and --help output carry the address, and a paid tier adds presets, profiles, or batch mode
   - Pricing model: Free tier with an honest paid upgrade, plus pay-what-you-want via the wallet ask
   - Cost per extra user: Zero: downloads are static files served by GitHub Releases
   - Free stack: GitHub Releases for binaries, GitHub Actions for free CI builds, README and --help for the ask
3. **Static client-side web tool (no server)**
   - Who buys: People who need the calculation, conversion, or lookup occasionally and do not want to install anything
   - Deliverable: A single-page tool hosted free; a paid tier unlocks saved profiles, bulk mode, or an export format
   - Pricing model: Free tier, one-time licence for the upgrade, wallet ask in the page footer
   - Cost per extra user: Zero per user: all work happens in the browser
   - Free stack: GitHub Pages for hosting, the repo for source, the product page footer for the ask
4. **Template, preset, or asset pack for a tool people already use**
   - Who buys: Existing users of that tool who want a head start and will pay a small amount to skip the setup work
   - Deliverable: A downloadable pack sold as a one-time licence on the free storefronts, with a free sample pack for discovery
   - Pricing model: One-time licence, pay-what-you-want above a floor on itch.io, wallet ask on the pack's page
   - Cost per extra user: Zero: the pack is a static file delivered by the storefront
   - Free stack: GitHub Releases or the storefront's own delivery, repo for the free sample, wallet ask everywhere
5. **Compiled data set or reference, sold as a download**
   - Who buys: Users who need the reference in a usable form and do not want to assemble it themselves
   - Deliverable: A structured file (JSON, CSV, or a small database) updated on a published schedule, sold as a one-time or versioned download
   - Pricing model: One-time licence per major version, free sample slice for discovery, wallet ask in the README
   - Cost per extra user: Zero per download; the compile work is done once per version
   - Free stack: GitHub Releases for the file, GitHub Actions for scheduled rebuilds, README for the ask

## Next Actions

- Pick one product shape whose free tier costs nothing per user to run (client-side tool, CLI utility, or template pack) and build the smallest version that solves one specific annoyance.
- Create the public GitHub repo, publish the build on GitHub Releases, and put the validated TRC-20 USDT address in the README, the release notes, .github/FUNDING.yml, and the tool's own --help or about output.
- Add the same address to the product page footer so the page sells the product and collects payment with no platform at all.
- List the product on the free-to-list storefronts, starting with the one that pays stablecoin to the owner's own wallet; confirm its current fees, minimum payout, and payout rules before depending on it, and keep the direct wallet ask as the fallback that no platform can disable.
- Write the dev.to article about the problem the product solves, with the product as the fix and the existing footer as the ask, reusing publishing infrastructure that is already running.

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
8. Open-source the tool and take sponsorship on the repo
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A public repository is discovery that keeps working after it is published, and the wallet address in the README is a receive path that…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
9. [itch.io — free to publish, but a payout needs a tax interview and a TIN](https://itch.io/docs/creators/payments)
   - Kind: channel
   - Score: 61/100
   - Cost: $3.00 one-time
   - Owner must do: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Verified: Tax interview, TIN requirement and the one-time $3.00 identity fee confirmed on itch.io/docs/creators/payments 2026-09-15. The earlier row said 'free to publish, no approval queue' and recorded cost_u
10. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (477h ago)
11. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
12. [Stop Paying Designers $500: How I Built and Packaged a $19 Guide in 48 Hours With Claude](https://medium.com/@nolancaldwell/stop-paying-designers-500-how-i-built-and-packaged-a-19-guide-in-48-hours-with-claude-60b3fe60bd21)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: After I shared my 7-prompt system for planning a digital product, dozens of readers asked the same thing.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T16:56:01+00:00 (0h ago)
13. [Should You Share a Public Roadmap for Your Side Project?](https://ehsan-yazdanparast.medium.com/should-you-share-a-public-roadmap-for-your-side-project-975a1f53f183)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Mine is three short lines. I think that is enough.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T15:44:52+00:00 (2h ago)
14. [Distribution Is the New Bottleneck for Solo Founders](https://medium.com/@sambuild/distribution-is-the-new-bottleneck-for-solo-founders-3f28f346be33)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You can build a great SaaS product in a few weeks.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T15:31:01+00:00 (2h ago)
15. [I built a place for Korean indie apps to be discovered, and the hardest part is exactly what you'd guess](https://dev.to/cpcai_studio/i-built-a-place-for-korean-indie-apps-to-be-discovered-and-the-hardest-part-is-exactly-what-youd-5657)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm not selling anything in this post. I want one question answered at the end. I run a one-person...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-21T13:56:49+00:00 (3h ago)
16. [AI agent toolkits store, week 2: 20 products, still $0 — here's what changed](https://dev.to/nexusfoundry/ai-agent-toolkits-store-week-2-20-products-still-0-heres-what-changed-3j2o)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One week after the honest-numbers post, the scoreboard is unchanged where it counts: $0 revenue. But...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-21T12:20:54+00:00 (5h ago)
17. [What Makes a Digital Product Worth Paying For?](https://medium.com/@amnamuskan714/what-makes-a-digital-product-worth-paying-for-f2df1740ec67)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I once bought a $19 template that looked great on the sales page and turned out to be unusable.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T10:20:59+00:00 (7h ago)
18. [Why 95% of AI-Made Digital Products Never Sell (And 4 Claude Prompts That Fix It)](https://medium.com/@nolancaldwell/why-95-of-ai-made-digital-products-never-sell-and-4-claude-prompts-that-fix-it-61505f848284)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Every time I log onto social media, I see people making the exact same bold claim:
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T09:51:26+00:00 (7h ago)
19. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T06:24:28+00:00 (11h ago)
20. [Show HN: OpenComputer – an open source alternative to Devin](https://news.ycombinator.com/item?id=50581403)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN! Utpal here, I'm one of the founders of OpenComputer. OpenComputer is an open source cloud coding agent for teams that can run in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T20:19:56+00:00 (21h ago)
21. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T15:11:47+00:00 (26h ago)
22. [My first sale came three hours before I published “no sales”](https://medium.com/@refineco/my-first-sale-came-three-hours-before-i-published-no-sales-a492afc2c457)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My money tracker sold its first unlock on the afternoon my article said it hadn’t. The second buyer was offered the unlock for free and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T13:01:04+00:00 (28h ago)
23. [Top 5 Text-to-Speech Chrome Extensions for Reading Articles in 2026 (And the Free AI Alternative…](https://medium.com/@abuzar0013/top-5-text-to-speech-chrome-extensions-for-reading-articles-in-2026-and-the-free-ai-alternative-7f74c4bfff9f)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Stop paying $139/year or settling for robotic voices just to listen to web articles. Here is how the 5 biggest Chrome TTS tools actually…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T12:54:45+00:00 (28h ago)
24. [How To Monetize A Micro-SaaS Built With Claude Code: Pricing, Customers, And Revenue Strategies](https://medium.com/@alisha123.viacon/how-to-monetize-a-micro-saas-built-with-claude-code-pricing-customers-and-revenue-strategies-ddfe4608f33d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You built the thing. It works. Your mum said “nice” in that tone she uses when she doesn’t understand but wants to be supportive.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T11:53:49+00:00 (29h ago)
25. [Indie Hacker Stack 2026: Next.js, Supabase, and Creem for SaaS](https://dev.to/publiflow/indie-hacker-stack-2026-nextjs-supabase-and-creem-for-saas-2690)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The modern lean stack for solo founders: Next.js App Router, Supabase, Creem for payments, Resend for email. How a boilerplate wires it…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-19T01:25:48+00:00 (64h ago)
26. [Show HN: Mastra Factory, the open-source software factory we use to build Mastra](https://news.ycombinator.com/item?id=50548660)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, we're Shane, Sam, and Abhi. Almost two years ago, we shared Mastra, our open-source TypeScript agent framework, on Show HN:…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-18T16:53:42+00:00 (72h ago)
27. [Show HN: Dez – plaintext open source AI multimedia studio](https://news.ycombinator.com/item?id=50547934)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN! Dez is a free open source way to interact with AIs across providers in a full-featured text editor. I really loved Zed's text…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T16:01:28+00:00 (73h ago)
28. [The free tier of a directory costs a link, not money](https://dev.to/copero_games/the-free-tier-of-a-directory-costs-a-link-not-money-4i9c)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The pricing page said Free. The button said Submit. Then, one screen later, after the logo upload and...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T15:14:35+00:00 (74h ago)
29. [Why I Built an All-in-One Restaurant SaaS as a Solo Founder](https://medium.com/@gabriel.vignes/why-i-built-an-all-in-one-restaurant-saas-as-a-solo-founder-53bedf21569b)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: It all started with a trip to Greece. It all started with a trip to Greece. As a vegan, I spent an entire evening struggling to decipher…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T13:54:00+00:00 (75h ago)
30. [Show HN: Fundlark-open source tool help early-career researcher find funding](https://news.ycombinator.com/item?id=50526177)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I just finished my PhD and am trying to get some funding to start off. I found that opportunities are scattered and it is a pain to find…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T01:21:51+00:00 (112h ago)
31. [Show HN: Cookiecutter-uv-core – uv template with an agent SDLC and quality gates](https://news.ycombinator.com/item?id=50519945)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T17:09:48+00:00 (120h ago)
32. [Get a Free .is-an.ai Domain for Your AI SaaS (2026)](https://dev.to/f9xrteam/get-a-free-is-anai-domain-for-your-ai-saas-2026-lc8)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Claim a free your-project.is-an.ai subdomain for your AI SaaS. Register via web, the new CLI, or Claude Code and OpenClaw plugins. Signups…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-16T17:14:39+00:00 (120h ago)
33. [I calculated how much payment fees actually eat from a $10 sale](https://dev.to/__a275a1bef4/i-calculated-how-much-payment-fees-actually-eat-from-a-10-sale-14ll)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Every indie hacker knows "Stripe takes ~3%." But when I broke down a real $10 sale, the number was...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-14T19:27:12+00:00 (166h ago)
34. [Build Your First Micro-SaaS in 30 Days: A Step-by-Step Roadmap](https://medium.com/@heshan.imedha/build-your-first-micro-saas-in-30-days-a-step-by-step-roadmap-94236bd61ced)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building a software business doesn’t always require a big team, expensive infrastructure, or venture capital.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-13T06:30:08+00:00 (203h ago)
35. [gabrielbuzziv/emissor-nfse-nacional](https://github.com/gabrielbuzziv/emissor-nfse-nacional)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Emissor de NFS-e direto na API do Sistema Nacional NFS-e, sem custo por nota, rodando na sua conta da Cloudflare.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T23:02:35+00:00 (210h ago)
36. [Instagram comment-to-DM for coaches: one keyword, one private link](https://dev.to/amitdobal/instagram-comment-to-dm-for-coaches-one-keyword-one-private-link-4p9b)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Coaches sell in DMs. Reels get comments like "LINK" or "PRICE" — but Instagram comments are not...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-12T20:04:47+00:00 (213h ago)
37. [Okay, I QUITEEEE: My Final Micro-SaaS Ideas List for 2026](https://pantpallavi13.medium.com/okay-i-quiteeee-my-final-micro-saas-ideas-list-for-2026-9cd68d20e3da)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Not recycled, not your typical ChatGPT recommendations — just 18 fresh Micro-SaaS ideas 2026 that are worth exploring.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T13:16:01+00:00 (220h ago)
38. [jackson-cmd/zeus-options-terminal](https://github.com/jackson-cmd/zeus-options-terminal)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Self-hosted, all-in-one options trading terminal: live positions & Greeks, P/L and risk, exit alerts, paper trading, stock screener,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T07:16:02+00:00 (226h ago)
39. [rivet-dev/open-orange](https://github.com/rivet-dev/open-orange)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Run Cloudflare Workers and Durable Objects unchanged on AWS, GCP, Azure or your own servers.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T00:44:12+00:00 (232h ago)
40. [PersiOnOff/tenlith](https://github.com/PersiOnOff/tenlith)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open-source .NET + React SaaS starter with multi-tenancy, authentication, teams, Stripe billing and Docker.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T19:06:58+00:00 (262h ago)
41. [HolyArrs/HolyArrs](https://github.com/HolyArrs/HolyArrs)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One self-hosted app for your shows, movies and music.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T23:53:25+00:00 (281h ago)
42. [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of awesome developer-first tools products.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T17:05:35+00:00 (288h ago)
43. [nickvasilescu/orgo-teammates](https://github.com/nickvasilescu/orgo-teammates)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open-source, self-hosted AI teammates, each with its own Orgo cloud computer, connected apps and memory. Works with xAI's Grok API.…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-09T07:50:15+00:00 (297h ago)
44. [serveroshq/panel](https://github.com/serveroshq/panel)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The open source ServerOS panel: one place to run the Linux servers you already own.
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-09T00:47:33+00:00 (304h ago)
45. [Build, Secure & Monetize Your First ChatGPT Plugin](https://dev.to/leojulieta/build-secure-monetize-your-first-chatgpt-plugin-4155)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Build, Secure, and Monetize Your First ChatGPT Plugin (June 2026 Launch) ...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-08T20:10:53+00:00 (309h ago)
46. [jnv/lists](https://github.com/jnv/lists)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The definitive list of lists (of lists) curated on GitHub and elsewhere
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T23:20:38+00:00 (378h ago)
47. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (526h ago)
48. [awesomemotive/easy-digital-downloads](https://github.com/awesomemotive/easy-digital-downloads)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Sell digital downloads through WordPress
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T21:10:25+00:00 (548h ago)
49. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (551h ago)
50. [satendra02/react-chrome-extension](https://github.com/satendra02/react-chrome-extension)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: chrome extension boilerplate with ReactJs using inject page strategy
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-22T19:49:46+00:00 (717h ago)
51. [DirectorySurf/awesome-launch-platforms](https://github.com/DirectorySurf/awesome-launch-platforms)
   - Kind: asset
   - Score: 50/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Curated list of platforms where you can launch, promote, and showcase your startup, product, or side project.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-15T11:03:13+00:00 (894h ago)
52. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
53. [Show HN: A tiny macOS app that turns off the MacBook display [free license]](https://news.ycombinator.com/item?id=50507722)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, I made a tiny app that lets you turn off the MacBook screen when you work on external monitors. It does NOT just dim the brightness to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-15T15:37:52+00:00 (146h ago)
54. [Your tool subscriptions are quietly getting more expensive — here's the checklist I use to catch it](https://dev.to/zhi_shen_da3713e5b0a88b00/your-tool-subscriptions-are-quietly-getting-more-expensive-heres-the-checklist-i-use-to-catch-it-2fl5)
   - Kind: asset
   - Score: 45/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most indie hackers and small teams I talk to can name their hosting bill to the dollar, but not their...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-12T17:06:15+00:00 (216h ago)
55. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
56. [I’m building a discovery space for indie games and interactive projects](https://dev.to/eosen1114/im-building-a-discovery-space-for-indie-games-and-interactive-projects-2coa)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: I’m posting on behalf of EOSEN. A lot of indie discovery is organized around a format or...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-21T15:03:06+00:00 (2h ago)
57. [I Thought Pinterest Was for Recipes and Wedding Dresses. Then My Phone Went “Ting” at Work.](https://victore97.medium.com/i-thought-pinterest-was-for-recipes-and-wedding-dresses-then-my-phone-went-ting-at-work-e90456636cc3)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The platform I almost ignored became the place my first sale came from. Here is what I understood during the week I waited.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T14:01:02+00:00 (3h ago)
58. [Before You Export a WhatsApp Group List: A Short Checklist for Organisers](https://medium.com/@yasinmuratogullari/before-you-export-a-whatsapp-group-list-a-short-checklist-for-organisers-2f57e35cef75)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: If you run a class, a club, a team or a customer community, the member list probably lives in a WhatsApp group. Getting it into a…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T11:40:35+00:00 (6h ago)
59. [My Mac App Took 18 Days to Get Its First Sale](https://medium.com/write-a-catalyst/my-mac-app-took-18-days-to-get-its-first-sale-991749f6a50c)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Nobody showed up on launch day. Here’s what I learned from waiting. Continue reading on Write A Catalyst »
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T07:13:50+00:00 (10h ago)
60. [Show HN: Musset, open-source Scrivener alternative with an AI that never writes](https://news.ycombinator.com/item?id=50586323)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’m writing my first novel and could not find an app that fit my workflow: quiet like iA Writer, organized like Scrivener, and with AI so I…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-21T05:42:49+00:00 (12h ago)
61. [title: The Zero-Backend Mobile App: How Cutting Cloud Infrastructure Eliminated My Monthly SaaS Bill published: false](https://dev.to/itech_accesories_b86af4c5/title-the-zero-backend-mobile-app-how-cutting-cloud-infrastructure-eliminated-my-monthly-saas-a58)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A look at the engineering and unit-economics math behind shipping My Momentum with zero servers, zero...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-19T10:16:40+00:00 (55h ago)
62. [Best Guest Posting Services in 2026: I Checked 7 Vendors' Own Pricing Pages. 5 Let You Pick the Site First](https://dev.to/posting-dude/best-guest-posting-services-in-2026-i-checked-7-vendors-own-pricing-pages-5-let-you-pick-the-3865)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most "best guest posting services" lists are written by one of the services. So I skipped the lists...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T04:52:42+00:00 (84h ago)
63. [Show HN: DecksMD – local first, Markdown flashcards app and plugin for Obsidian](https://news.ycombinator.com/item?id=50539204)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I built a flashcards app and plugin for obsidian, based on markdown syntax. You use headers and paragraphs, tables or highlighted text to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T22:31:25+00:00 (91h ago)
64. [AI Referral Traffic Benchmark (Nov 2026): Which SaaS & AI Tools Actually Get Traffic from ChatGPT, Gemini, and Perplexity?](https://dev.to/jack_yu_0909/ai-referral-traffic-benchmark-nov-2026-which-saas-ai-tools-actually-get-traffic-from-chatgpt-260o)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Everyone talks about GEO (Generative Engine Optimization)—getting cited inside ChatGPT Search,...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-16T08:40:02+00:00 (128h ago)
65. [Chess Platform Facing Private Equity Backlash Over Monetization and Reduced Community Reinvestment](https://dev.to/miraslave/chess-platform-facing-private-equity-backlash-over-monetization-and-reduced-community-reinvestment-75h)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The Golden Age vs. The Private Equity Shift To understand why modern commercial chess...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-11T14:19:06+00:00 (243h ago)
