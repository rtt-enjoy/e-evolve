# Passive Product Income Queue

Refreshed: 2026-11-05T12:50:58.780011+00:00

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

The best zero-budget route is a product that costs nothing per user — a browser extension or client-side static tool — shipped free on GitHub Releases and the Chrome Web Store, monetised by the already-live Tron (TRC-20) receive address placed on the product page, in the README/FUNDING.yml, and in the tool's own output, plus a paid upgrade or one-time licence sold through a free-to-list storefront that settles USDT to the owner's own wallet. Every element runs on infrastructure already paid for (GitHub, dev.to publishing), so revenue is purely on-chain and no owner action happens per sale.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Embedded wallet ask (already live) | Puts the validated TRC-20 USDT receive address on the product page, README, FUNDING.yml, --help output and release notes | $0; no platform, no revenue cut | USDT on Tron, directly to the owner's own wallet — already validated | Paste the address into README, .github/FUNDING.yml (custom: field), release bodies, and the tool's about/--help output — one-time edits, no new account | Payment is peer-to-peer and delivery is the download itself; nothing per sale to do and no processor that can freeze funds |
| GitHub Releases | Free hosting of binaries, archives and downloadable files with release notes as the sales page | $0; free tier of the account already hosting the code | None itself — pairs with the embedded wallet address in release bodies | Tag a release and upload the artifact once per version | Downloads run forever with no per-sale action, no approval queue, no identity check, and cannot be frozen or geo-blocked |
| Chrome Web Store | Official distribution and organic discovery for browser extensions | One-time $5 developer registration per account; no renewal, no revenue cut on free extensions — the only non-zero cost here | None itself; monetise via the wallet address in the extension page/README or a paid upgrade sold on a crypto storefront | Pay the one-time $5 fee (the budget exception to weigh), package and submit the extension for review once | Store handles distribution, updates and discovery; each install needs no owner action |
| Getly | Digital-goods storefront with native stablecoin payouts and card checkout | No monthly fee; verify current terms for any revenue cut | USDT (TRC-20) and USDC settled directly to the seller's own wallet address; $15 minimum payout on Tron per the lead — verify current terms | One-time signup, product listing, and entering the existing Tron receive address | Storefront delivers the file and takes payment automatically; the owner only watches the on-chain balance |
| itch.io | Free listing for tools and downloadable assets with pay-what-you-want pricing | Free to upload; seller picks the platform cut (default ~10%) — but payout requires a tax interview with a TIN and a one-time $3 identity fee, so it fails the no-KYC constraint | Fiat only; verify current terms | Upload, pricing page, and the tax interview if pursued | Fully automated delivery per sale; listed only as a fiat fallback since payout needs identity verification |

## Product Ideas

1. **One-fix browser extension with paid upgrade**
   - Who buys: Chrome users annoyed by one specific behaviour (e.g. a cluttered site, missing keyboard shortcut, intrusive banner)
   - Deliverable: Free extension from the Chrome Web Store; paid tier unlocks extra options via a licence key bought on the storefront
   - Pricing model: Free tier plus paid upgrade
   - Cost per extra user: $0 per user — the extension runs client-side
   - Free stack: Chrome Web Store listing, GitHub repo for the paid build, embedded TRC-20 address in the store description and repo
2. **Single-purpose CLI/desktop utility as a GitHub Release**
   - Who buys: Developers hitting one recurring annoyance the tool automates
   - Deliverable: Downloadable binary/archive from GitHub Releases; licence key or payment address for the pro features
   - Pricing model: Pay-what-you-want with the wallet ask in README and --help output
   - Cost per extra user: $0 — the buyer runs it on their own machine
   - Free stack: GitHub Releases + repo, FUNDING.yml sponsor button, dev.to article on the problem
3. **Template/preset/asset pack download**
   - Who buys: Users of a popular tool who want a ready-made config, theme, or asset set
   - Deliverable: A downloadable file delivered by the storefront on payment
   - Pricing model: One-time licence
   - Cost per extra user: $0 per sale — file is built once
   - Free stack: Getly listing (USDT to own wallet), GitHub Releases mirror, README wallet address
4. **Client-side static web tool with paid tier**
   - Who buys: Anyone searching for the exact one-job tool (converter, formatter, generator)
   - Deliverable: Free tool on GitHub Pages; paid tier (batch mode, extra formats) unlocked via licence key
   - Pricing model: Free tier plus paid upgrade
   - Cost per extra user: $0 — runs entirely in the browser, no server
   - Free stack: GitHub Pages free tier, GitHub repo, embedded receive address on the page

## Next Actions

- Embed the validated TRC-20 address everywhere the product touches: README, .github/FUNDING.yml, --help/about output, docs footer, and the Chrome Web Store description.
- Ship v1 as a free GitHub Release and pick the one product shape to build first (extension, CLI utility, or asset pack).
- List the paid tier on Getly, entering the existing Tron wallet as the payout address, and verify current terms for fees, payout minimums, and any revenue cut before publishing the listing.
- Evaluate the Chrome Web Store's one-time $5 fee against zero budget; pay it only if the product is a browser extension and the fee is genuinely available.
- Write one problem-workaround article on dev.to (infrastructure already running) where the product is the fix and the existing article wallet footer is the ask.

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
8. [I built 142,000 lines of crypto tooling with AI and got 2 users. Now I'm selling it](https://dev.to/botlab/i-built-142000-lines-of-crypto-tooling-with-ai-and-got-2-users-now-im-selling-it-17ke)
   - Kind: asset
   - Score: 66/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building was the easy part. With AI doing most of the typing, I ended up with a full crypto bot...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T12:51:51+00:00 (0h ago)
9. [Ahmadkhattak1/awesome-downloader](https://github.com/Ahmadkhattak1/awesome-downloader)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; Open-source Windows download manager with browser video integration
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-24T17:58:52+00:00 (283h ago)
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
12. [Show HN: An Open Source Superhuman Email Client Clone](https://news.ycombinator.com/item?id=50366894)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I'm a long-time Superhuman user, and a few weeks ago I cloned it as a native Mac app. It's keyboard-first, with split inboxes,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T15:22:44+00:00 (22h ago)
13. [I spent £2.53 per install to earn about 10p per download. What would you do next with a kids’ app?](https://www.reddit.com/r/SideProject/comments/1xmc632/i_spent_253_per_install_to_earn_about_10p_per/)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’m a product designer, and I make small ad-free iPhone/iPad apps for under-5s. Melody Music is a music toy where every note stays in key,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T22:50:49+00:00 (62h ago)
14. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T21:46:38+00:00 (63h ago)
15. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (89h ago)
16. [yaojingang/GEOInflow](https://github.com/yaojingang/GEOInflow)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Self-hosted web and AI crawler analytics for Generative Engine Optimization (GEO). Track visitors, AI search referrals, crawl logs, content…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-26T03:12:45+00:00 (250h ago)
17. [How much do AI agent businesses make? Median $13,894/month across 25 verified ones](https://dev.to/soloearn/how-much-do-ai-agent-businesses-make-median-13894month-across-25-verified-ones-4p78)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Verified monthly recurring revenue for 25 AI agent businesses, with the median, range and what the numbers leave out.
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-23T09:07:35+00:00 (316h ago)
18. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (1558h ago)
19. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
20. [I Made $1,500 Selling Digital Products in 2 Hours and 45 Minutes. Here’s My Exact Blueprint](https://medium.com/@amnamuskan714/i-made-1-500-selling-digital-products-in-2-hours-and-45-minutes-heres-my-exact-blueprint-75193e553c5a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I need to be upfront about the headline: the 2 hours and 45 minutes was the launch window,
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:48:40+00:00 (0h ago)
21. [Audit One Digital Product Before You Change Its Price](https://medium.com/@madewithai/audit-one-digital-product-before-you-change-its-price-fb8da6924966)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: The examples are fictional and illustrate a method, not customer results.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:01:01+00:00 (1h ago)
22. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-05T11:54:16+00:00 (1h ago)
23. [How to Monetize a Chrome Extension: Revenue Models That Work for B2B and SaaS Products](https://medium.com/@ryagoel1994/how-to-monetize-a-chrome-extension-revenue-models-that-work-for-b2b-and-saas-products-923eea393877)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Introduction
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T11:30:56+00:00 (1h ago)
24. [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of awesome developer-first tools products.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T11:06:17+00:00 (2h ago)
25. [I Put My Stripe Revenue in My MacBook Notch (and Stopped Alt-Tabbing to the Dashboard)](https://dev.to/notchrevenue/i-put-my-stripe-revenue-in-my-macbook-notch-and-stopped-alt-tabbing-to-the-dashboard-200d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For about a year, my most-used "app" was not my editor. It was a browser tab with the Stripe...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T06:40:36+00:00 (6h ago)
26. [Can AI Make Online Forms Less Painful? Here's What We're Building.](https://dev.to/digitalwareshub/im-building-talking-links-a-different-approach-to-online-forms-2pdb)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Online forms haven't changed much in years. Whether it's customer feedback, student surveys, client...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T06:30:55+00:00 (6h ago)
27. [Which link actually brought the sale?](https://dev.to/moinulhaq/which-link-actually-brought-the-sale-1h32)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most of us share links everywhere. Instagram bio. WhatsApp groups. Email. Ads. A poster with a QR...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T04:32:20+00:00 (8h ago)
28. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T04:26:44+00:00 (8h ago)
29. [How to Get Your First 10 Paying Customers Without Spending Money on Ads](https://medium.com/@dealpilo/how-to-get-your-first-10-paying-customers-without-spending-money-on-ads-ef96e79665ac)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You don’t need a big audience, a viral launch, or a perfect product. You need to find the right people, solve a problem they care about…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T03:31:01+00:00 (9h ago)
30. [How to Offer a Yearly Plan in Your Vibe-Coded App (Annual Pricing Without Headaches)](https://medium.com/@deepak_42009/how-to-offer-a-yearly-plan-in-your-vibe-coded-app-annual-pricing-without-headaches-2643a0622e50)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Your app has a monthly plan and a few people pay for it. Then someone asks: “Can I just pay for the whole year?” It sounds small: a second…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T00:00:22+00:00 (13h ago)
31. [jnv/lists](https://github.com/jnv/lists)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The definitive list of lists (of lists) curated on GitHub and elsewhere
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T21:18:51+00:00 (16h ago)
32. [15 Digital Products You Can Build and Sell Today.](https://medium.com/@officialfaithmackenzi/15-digital-products-you-can-build-and-sell-today-66ae8b2139d3)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The biggest mistake people make when trying to earn money online is thinking they need to learn something completely new before they can…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T21:05:49+00:00 (16h ago)
33. [Show HN: Gauge – Open-Source CLI to recursively improve your docs](https://news.ycombinator.com/item?id=50371090)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I’m Evan from Gauge. We’re open-sourcing our CLI to recursively improve your docs for coding agents. The CLI includes a local…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T20:31:30+00:00 (16h ago)
34. [I put a live AI chat assistant on my side project's website. Here's what you need](https://medium.com/@hello_86179/i-put-a-live-ai-chat-assistant-on-my-side-projects-website-here-s-what-you-need-39d166326759)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T18:03:27+00:00 (19h ago)
35. [4 Micro-SaaS Opportunities You Can Build in 1–7 Days: From AI-Built Apps to the Kick Creator…](https://medium.com/@thebruteforceartist/4-micro-saas-opportunities-you-can-build-in-1-7-days-from-ai-built-apps-to-the-kick-creator-15e433f86675)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building software has become dramatically easier.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T15:33:21+00:00 (21h ago)
36. [Ship a SaaS in a weekend with Cursor + Supabase: the stack, the code, and the 'don't skip this' checklist](https://dev.to/mailvalid/ship-a-saas-in-a-weekend-with-cursor-supabase-the-stack-the-code-and-the-dont-skip-this-ifh)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: this post is from the MailValid team. MailValid appears in one checklist item, and that...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T13:22:26+00:00 (24h ago)
37. [Show HN: Shield KYA – Open-source audit trail and gate for AI agent tool calls](https://news.ycombinator.com/item?id=50364706)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T12:33:39+00:00 (24h ago)
38. [I Built a Daily Sports Card Game in a Month With AI Agents. Here's Everything It Broke.](https://dev.to/sambrovda/i-built-a-daily-sports-card-game-in-a-month-with-ai-agents-heres-everything-it-broke-n1p)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm not an engineer. I come from the sales world. But between June 18 and July 16, I pushed 172...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T12:27:52+00:00 (24h ago)
39. [My Side Project Went From 1 Submission to 17 a Week. Here's What I'm Learning](https://dev.to/ashraful2502/my-side-project-went-from-1-submission-to-17-a-week-heres-what-im-learning-573a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I finally crossed 50 submissions on LaunchNests. It's a small milestone, but it means a lot to me as...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T09:02:51+00:00 (28h ago)
40. [lucascodev/aura-datadock-db](https://github.com/lucascodev/aura-datadock-db)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Database manager for VS Code: browse, query, edit and chart Postgres, MySQL and MariaDB in Docker, local or remote over SSH.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T02:58:38+00:00 (34h ago)
41. [Show HN: Kairos – Open-source risk and fraud decisioning platform](https://news.ycombinator.com/item?id=50358314)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey HN, Ayan here from Finic. We’re launching Kairos, an open source alternative to Sift, Sardine, and other real-time fraud decisioning…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-03T21:16:48+00:00 (40h ago)
42. [Adam Robinson: A Legacy of Bootstrapping and Digital Innovation](https://medium.com/@couponfolloz/adam-robinson-a-legacy-of-bootstrapping-and-digital-innovation-cfafe360a9ad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The entrepreneur behind Retention.com and RB2B brought attention to building software businesses with lean teams and a clear commercial…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T16:49:13+00:00 (44h ago)
43. [KKKKhazix/agent-autoloop](https://github.com/KKKKhazix/agent-autoloop)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 让你的命令行 Agent 在后台自己接活、自己跟进到底；平时不烦你，遇到拿不准的事才发卡片找你拍板。
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T08:02:11+00:00 (53h ago)
44. [851-labs/honest-thumbnails](https://github.com/851-labs/honest-thumbnails)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Chrome extension that replaces YouTube's clickbait thumbnails with a real frame from the middle of the video.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T00:24:50+00:00 (84h ago)
45. [Shahrukhalid/nexonic-download-manager](https://github.com/Shahrukhalid/nexonic-download-manager)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Free, open-source download manager for Mac and Windows (IDM alternative): 32-connection downloads, pause/resume, scheduler, queues, batch,…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-31T15:06:09+00:00 (118h ago)
46. [How to schedule Shopify sale prices so they actually end on time (without leaving variants discounted)](https://dev.to/zhuanghua/how-to-schedule-shopify-sale-prices-so-they-actually-end-on-time-without-leaving-variants-4d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I build a small Shopify app, and the problem I hear about most isn't "how do I start a sale." It's...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-31T02:37:24+00:00 (130h ago)
47. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (137h ago)
48. [No-Code, AI Coding or Traditional Code: 5 Questions to Answer Before Building Your Micro-SaaS](https://pantpallavi13.medium.com/no-code-ai-coding-or-traditional-code-5-questions-to-answer-before-building-your-micro-saas-eebce1892bad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ll walk you through the five things I consider first.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T13:01:04+00:00 (144h ago)
49. [How I Built a $1.2M ARR SaaS Business Without Raising Funding](https://medium.com/@SteveBaltodano/how-i-built-a-1-2m-arr-saas-business-without-raising-funding-0fc560f4d1e6)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building a million-dollar SaaS business doesn’t always require venture capital, a large team, or millions in the bank. Sometimes, it…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T05:29:19+00:00 (151h ago)
50. [Show HN: DistractFree-Chrome extension and web app to stop doomscrolling](https://news.ycombinator.com/item?id=50299880)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T04:31:31+00:00 (152h ago)
51. [One merchant account, four side projects: how I keep the payment data from turning into a mess](https://dev.to/buhgalterapp/one-merchant-account-four-side-projects-how-i-keep-the-payment-data-from-turning-into-a-mess-4ojc)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most indie developers I know do not run one product. They run a VPN bot, a paid Discord or Telegram...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-29T21:04:03+00:00 (160h ago)
52. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (163h ago)
53. [6 months ago I couldn't code. Here's what I built for Shopify sellers](https://www.reddit.com/r/SideProject/comments/1xhtldd/6_months_ago_i_couldnt_code_heres_what_i_built/)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm 21 and I started learning to code this year. My friends selling on Shopify all had the same problem: they knew which products sold, but…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T16:53:57+00:00 (188h ago)
54. [The Median Paid Newsletter Converts 0.62% of Free Readers. Do the Math Before You Launch](https://dev.to/devinios/the-median-paid-newsletter-converts-062-of-free-readers-do-the-math-before-you-launch-5466)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The most useful number in beehiiv's 2026 paid-newsletter report is not a success story. It is the median: 0.62% conversion, $10/$100…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-27T11:27:29+00:00 (217h ago)
55. [Show HN: University of Malta LaTeX dissertation template, easily adapted](https://news.ycombinator.com/item?id=50255556)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-27T07:09:15+00:00 (222h ago)
56. [How to Price and Sell the AI Agent or n8n Workflow You Built: A Practical Guide for Creators](https://dev.to/aimarket24/how-to-price-and-sell-the-ai-agent-or-n8n-workflow-you-built-a-practical-guide-for-creators-1d8p)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You built something that works. Maybe it's an n8n workflow that turns inbound emails into CRM...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-25T15:53:28+00:00 (261h ago)
57. [Show HN: MegaKey (standardization and extension of the Hyper and Meh keys)](https://news.ycombinator.com/item?id=50207489)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: MegaKey is a proposed standardization + extension of Hyper and Meh - Mental tools for your mind: turn a mouthful like…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-23T11:49:27+00:00 (313h ago)
58. [When a Customer Asks for an Invoice With Their VAT Number and You Have Under 50 Customers](https://dev.to/posting-dude/when-a-customer-asks-for-an-invoice-with-their-vat-number-and-you-have-under-50-customers-f5h)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Say you have 30-something paying customers and one of them, a small agency in Germany, sends this...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-23T05:15:44+00:00 (320h ago)
59. [Primeira Assinatura em 24h Funciona? Descubra Como Criar Seu Próprio Micro SaaS](https://medium.com/@allansantoss777/primeira-assinatura-em-24h-funciona-descubra-como-criar-seu-pr%C3%B3prio-micro-saas-3e2e74541fb1)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Você já pensou em criar sua própria ferramenta online, disponibilizá-la para clientes e cobrar uma assinatura mensal pelo acesso?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-22T20:34:25+00:00 (328h ago)
60. [Show HN: Can a solo founder compete in the crowded Chrome extension market?](https://news.ycombinator.com/item?id=50076361)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-13T18:30:09+00:00 (546h ago)
61. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
62. [I’m a product manager, started vibe coding six months ago, and just released my first app](https://www.reddit.com/r/SideProject/comments/1xoh1bk/im_a_product_manager_started_vibe_coding_six/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey everyone, I’m Viktor, a product manager from Germany. I’ve been looking for a job for the past two years. About six months ago, I…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:08:55+00:00 (1h ago)
63. [7 Tools That Replace Expensive SaaS Marketing Subscriptions (2026)](https://medium.com/@antoine.valton/7-tools-that-replace-expensive-saas-marketing-subscriptions-2026-268a1c92932c)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Add up the marketing tools a small SaaS can end up paying for.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T14:21:01+00:00 (22h ago)
64. [composer/spdx-licenses](https://github.com/composer/spdx-licenses)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Tools for working with the SPDX license list and validating licenses.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T08:52:33+00:00 (52h ago)
65. [I failed at selling CV templates in 2016. Ten years later I came back and built the whole tool](https://www.reddit.com/r/SideProject/comments/1xm1w3b/i_failed_at_selling_cv_templates_in_2016_ten/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My first attempt in 2016 flopped. Ten years of product design later, I tried again Back in 2016 I sold CV templates on a small WordPress…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T16:30:07+00:00 (68h ago)
66. [As launching a new feature, I made the old paid feature free. Is this a stupid marketing choice?](https://www.reddit.com/r/SideProject/comments/1xllisu/as_launching_a_new_feature_i_made_the_old_paid/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My current marketing plan is apparently to change for fewer things. I made Wallpets. Its a desktop wallpaper app where cats, dogs,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T02:29:25+00:00 (82h ago)
67. [Citus Camera. An IOS camera app built by a Photographer.](https://www.reddit.com/r/SideProject/comments/1xld2dj/citus_camera_an_ios_camera_app_built_by_a/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My name is Leon, I am a commercial photographer. And I built a camera app for IOS. Why? My camera bag weighs around 20kg (44lbs) And film…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T20:10:05+00:00 (89h ago)
68. [I built an all-in-one system for small used car dealerships in Brazil, because most of them still run on spreadsheets and WhatsApp](https://www.reddit.com/r/SideProject/comments/1xl3lrx/i_built_an_allinone_system_for_small_used_car/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject ! I've been building AutoPainel, a web app for small used car dealerships in Brazil. The problem: a typical small…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T13:52:57+00:00 (95h ago)
69. [AGENTORY — I turned my "AI assistant" workflows into boxed AI Task Kits (instruction files, not another app)](https://www.reddit.com/r/SideProject/comments/1xk8wji/agentory_i_turned_my_ai_assistant_workflows_into/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi — I'm the person behind AGENTORY. Short version of how I got here: I spent about a year working hands-on with agentic AI tools at my day…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-31T12:26:03+00:00 (120h ago)
70. [After my paid clipboard manager went subscription, I built a free, open-source one for the Mac](https://www.reddit.com/r/SideProject/comments/1xhdlrk/after_my_paid_clipboard_manager_went_subscription/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For years I used a paid clipboard manager. I bought a license, then the developer changed everything: a subscription, a pricier paid…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-28T03:35:39+00:00 (201h ago)
71. [johackim/awesome-indiehackers](https://github.com/johackim/awesome-indiehackers)
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Awesome list about indie hackers
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T11:40:22+00:00 (1h ago)
72. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
73. [I built a self-hosted store in plain PHP. No Composer, no bundler, takes Bitcoin / Paypal / Stripe](https://www.reddit.com/r/SideProject/comments/1xoh5er/i_built_a_selfhosted_store_in_plain_php_no/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Got tired of every "simple" ecommerce option being either a SaaS taking a cut or a 40 MB vendor folder, so I built the store I actually…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:14:59+00:00 (1h ago)
74. [Digital Product Sellers Bookkeeping Services: A Complete Guide to Managing Online Business Finances](https://medium.com/@cloudaccgworld/digital-product-sellers-bookkeeping-services-a-complete-guide-to-managing-online-business-finances-8a3f4919cff6)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Selling digital products online can create exciting business opportunities. However, managing sales revenue, marketplace fees, payment…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T05:25:00+00:00 (8h ago)
75. [I built an Omni-Tracker + Digital Garden so I could stop using 5 different apps for my media and notes](https://www.reddit.com/r/SideProject/comments/1xo6liw/i_built_an_omnitracker_digital_garden_so_i_could/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject ! I was tired of my personal data and thoughts being scattered across the internet: Letterboxd for movies, Goodreads for…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T01:59:52+00:00 (11h ago)
76. [I built Folloverse, a creator platform with memberships, paid posts, a shop and community chat in one page](https://www.reddit.com/r/SideProject/comments/1xn71yx/i_built_folloverse_a_creator_platform_with/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, This is Folloverse (folloverse.com), a home page for creators where they can: - Run memberships with tiers - Sell paid posts that fans…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T22:19:34+00:00 (38h ago)
77. [Globatics - live web analytics on a globe. My own dashboard saw 1 of my last 4 sales, so here's how I'd count the buyers analytics can't see](https://www.reddit.com/r/SideProject/comments/1xms0mb/globatics_live_web_analytics_on_a_globe_my_own/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I make Globatics, a web analytics tool. I also sell a small €25 digital product on the side, paid through Polar, and of course I track that…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T12:46:12+00:00 (48h ago)
78. [Show HN: Mago, an open source AI video studio, runs locally with Comfy](https://news.ycombinator.com/item?id=50341649)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm Alvaro, one of the founders of Mago. With my co-founder Alex (creator of Warpfusion, open source video to video), we built an open…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T18:49:44+00:00 (66h ago)
79. [[Feedback Request] 1 month in, 0 sales on my digital product store — what am I doing wrong?](https://www.reddit.com/r/SideProject/comments/1xm1p6y/feedback_request_1_month_in_0_sales_on_my_digital/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject , I'll be honest — I thought "build it and they will come" was real. A month ago I launched my Gumroad store selling…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T16:22:56+00:00 (68h ago)
80. [How I Built an Autonomous 5-AI-Agent SaaS and Passed 13 Production Vetting Checks](https://dev.to/agenticcrewos/how-i-built-an-autonomous-5-ai-agent-saas-and-passed-13-production-vetting-checks-gbf)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Running a modern B2B agency or SaaS startup means fighting one constant enemy: Tool...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-29T16:24:31+00:00 (164h ago)
81. [Ask HN: Advise on monetization model for my freemium app wanted](https://news.ycombinator.com/item?id=50280505)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm an indie app dev and looking for some conceptual help with one of my freemium apps. I'm thinking about completely restructuring the…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T20:34:28+00:00 (184h ago)
82. [Show HN: Shop via CLI; for agents and software engineers](https://news.ycombinator.com/item?id=50264240)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hello HN! We're building a single search/browse API interface to thousands of ecommerce stores (hopefully, eventually, all of them).…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-27T19:12:20+00:00 (210h ago)
