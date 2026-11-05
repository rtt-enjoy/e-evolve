# Passive Product Income Queue

Refreshed: 2026-11-05T09:50:32.260183+00:00

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

The best route is to build one small, client-side or downloadable product, ship it free where it can discover itself (GitHub Releases, GitHub Pages, Chrome Web Store), and monetise with an upgrade or honest ask settled in TRC-20 USDT to the wallet address this project already publishes. The receive address in every article, README, FUNDING.yml, release notes, and --help output needs no account, no KYC, no custodian, and zero per-sale work; Getly is the only storefront suggested for structured licence sales because it settles USDT on Tron directly to the owner's wallet, but its terms should be verified before listing. Chrome Web Store is the one justified non-zero cost: a one-time $5 that unlocks organic discovery for extensions, with monetisation handled by the wallet ask rather than the store.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Wallet ask (already live) | The published TRC-20 receive address on the product page, README, and inside the tool itself | Zero | USDT (TRC-20) directly to the owner's own validated wallet; no custodian, no KYC | None new — paste the existing address into the README, FUNDING.yml custom field, release notes, and the tool's about/--help output | Every copy carries its own payment path; payment happens on-chain with no owner action |
| Getly | Digital-goods storefront with card and crypto payment, stablecoin payout | No monthly fee per lead; verify current revenue-cut and payout terms before listing | USDT/USDC; TRC-20 supported per lead, minimum payout ~$15 on Tron (verify current terms), paid to the seller's own wallet address, no KYC for crypto settlement per lead | One-time manual account signup, product listing with the deliverable file, and payout wallet address entry | Storefront delivers the file or licence and settles to the wallet with no per-sale owner work |
| GitHub Releases + FUNDING.yml | Free hosting of binaries/archives with a Sponsor button and markdown payment links | Zero; included in the existing GitHub account | Direct to the Tron address placed in release bodies, README, and FUNDING.yml custom field; no platform holds funds | Commit FUNDING.yml once, attach the built artifact to a release once, update README once | Downloads and reads of the payment line require nothing from the owner afterwards |
| Chrome Web Store | Official distribution with organic search for browser extensions | One-time $5 developer registration per account, covers up to 20 extensions; no store cut on free extensions | None natively — the store lists a free extension and monetisation runs through the wallet ask or a licence sold via Getly | One-time $5 registration (credit/debit card required — the only cash outlay), then upload and review submission | Store search delivers installs indefinitely; payment path is embedded in the extension's own about/options page |
| dev.to articles (already running) | Daily published articles whose footer already carries the receive address | Zero; existing infrastructure | USDT (TRC-20) to the existing address | Write one problem-workaround article where the product is the fix, matching the shape that outperforms ~25x on this account | Article back catalogue keeps routing readers to the address after publication |

## Product Ideas

1. **One-annoyance browser extension with Pro unlock**
   - Who buys: Users hitting a specific friction daily (e.g. a tab-management or clipboard annoyance the Chrome store search surfaces)
   - Deliverable: Free extension from Chrome Web Store; Pro features unlock with a licence key purchased via Getly or paid to the Tron address
   - Pricing model: Free tier plus paid upgrade (one-time licence)
   - Cost per extra user: Zero — client-side code, no server per user
   - Free stack: Chrome Web Store listing ($5 one-time), GitHub repo for issues, licence delivered by Getly or manual key generation at release time
2. **Single-purpose CLI utility on GitHub Releases**
   - Who buys: Developers who found the repo searching for exactly one fix
   - Deliverable: Free open-source binary/source on GitHub Releases, with the Tron address in README, FUNDING.yml, release notes, and --help output
   - Pricing model: Pay-what-you-want honest ask (no enforcement)
   - Cost per extra user: Zero — runs on the buyer's own machine
   - Free stack: GitHub Releases hosting, GitHub Actions for build, README/FUNDING.yml for the ask
3. **Template/preset/asset pack for a tool people already use**
   - Who buys: Users of an existing ecosystem (editor, framework, design tool) wanting a ready-made setup
   - Deliverable: A downloadable archive sold via Getly or GitHub Releases with the wallet ask in the release body
   - Pricing model: One-time licence or pay-what-you-want
   - Cost per extra user: Zero — built once, downloaded many times
   - Free stack: GitHub Releases hosting, GitHub Pages product page, dev.to article as the discovery engine
4. **Static client-side web tool**
   - Who buys: Anyone with the recurring annoyance the tool solves, arriving via search or the dev.to article
   - Deliverable: Free tool on GitHub Pages; advanced output or batch mode gated behind a licence paid to the Tron address
   - Pricing model: Free tier plus paid upgrade
   - Cost per extra user: Zero — static files, no backend
   - Free stack: GitHub Pages (free tier), no server, receive address in the page footer

## Next Actions

- Paste the validated TRC-20 address into the product's README, .github/FUNDING.yml custom field, release notes, and the tool's own about/--help output so every copy carries a payment path
- Build the smallest client-side artifact (extension, CLI, or asset pack), attach it to a GitHub Release, and write one problem-workaround dev.to article where the product is the fix
- Create a Getly account, verify its current payout minimums and revenue cut, and list the paid tier with the Tron wallet as the payout address
- If shipping an extension, pay the one-time $5 Chrome Web Store registration once and submit the free version with the wallet ask in its options/about page
- Ship the free tier first and check the on-chain balance after a fixed window before investing in any further channel

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
8. [Ahmadkhattak1/awesome-downloader](https://github.com/Ahmadkhattak1/awesome-downloader)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; Open-source Windows download manager with browser video integration
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-24T17:58:52+00:00 (280h ago)
9. Open-source the tool and take sponsorship on the repo
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A public repository is discovery that keeps working after it is published, and the wallet address in the README is a receive path that…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
10. [itch.io — free to publish, but a payout needs a tax interview and a TIN](https://itch.io/docs/creators/payments)
   - Kind: channel
   - Score: 61/100
   - Cost: $3.00 one-time
   - Owner must do: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Verified: Tax interview, TIN requirement and the one-time $3.00 identity fee confirmed on itch.io/docs/creators/payments 2026-09-15. The earlier row said 'free to publish, no approval queue' and recorded cost_u
11. [Show HN: An Open Source Superhuman Email Client Clone](https://news.ycombinator.com/item?id=50366894)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I'm a long-time Superhuman user, and a few weeks ago I cloned it as a native Mac app. It's keyboard-first, with split inboxes,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T15:22:44+00:00 (18h ago)
12. [I spent £2.53 per install to earn about 10p per download. What would you do next with a kids’ app?](https://www.reddit.com/r/SideProject/comments/1xmc632/i_spent_253_per_install_to_earn_about_10p_per/)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’m a product designer, and I make small ad-free iPhone/iPad apps for under-5s. Melody Music is a music toy where every note stays in key,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T22:50:49+00:00 (59h ago)
13. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T21:46:38+00:00 (60h ago)
14. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (86h ago)
15. [Perpetual License vs Subscription License: Which Should You Sell?](https://dev.to/permitcore/perpetual-license-vs-subscription-license-which-should-you-sell-16gl)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Originally published on the PermitCore blog. Perpetual and subscription aren't really about the...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-01T09:27:06+00:00 (96h ago)
16. [yaojingang/GEOInflow](https://github.com/yaojingang/GEOInflow)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Self-hosted web and AI crawler analytics for Generative Engine Optimization (GEO). Track visitors, AI search referrals, crawl logs, content…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-26T03:12:45+00:00 (247h ago)
17. [How much do AI agent businesses make? Median $13,894/month across 25 verified ones](https://dev.to/soloearn/how-much-do-ai-agent-businesses-make-median-13894month-across-25-verified-ones-4p78)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Verified monthly recurring revenue for 25 AI agent businesses, with the median, range and what the numbers leave out.
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-23T09:07:35+00:00 (313h ago)
18. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (1554h ago)
19. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
20. [Can AI Make Online Forms Less Painful? Here's What We're Building.](https://dev.to/digitalwareshub/im-building-talking-links-a-different-approach-to-online-forms-2pdb)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Online forms haven't changed much in years. Whether it's customer feedback, student surveys, client...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T06:30:55+00:00 (3h ago)
21. [Which link actually brought the sale?](https://dev.to/moinulhaq/which-link-actually-brought-the-sale-1h32)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most of us share links everywhere. Instagram bio. WhatsApp groups. Email. Ads. A poster with a QR...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T04:32:20+00:00 (5h ago)
22. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T04:26:44+00:00 (5h ago)
23. [jnv/lists](https://github.com/jnv/lists)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The definitive list of lists (of lists) curated on GitHub and elsewhere
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T21:18:51+00:00 (13h ago)
24. [Show HN: Gauge – Open-Source CLI to recursively improve your docs](https://news.ycombinator.com/item?id=50371090)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I’m Evan from Gauge. We’re open-sourcing our CLI to recursively improve your docs for coding agents. The CLI includes a local…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T20:31:30+00:00 (13h ago)
25. [I put a live AI chat assistant on my side project's website. Here's what you need](https://medium.com/@hello_86179/i-put-a-live-ai-chat-assistant-on-my-side-projects-website-here-s-what-you-need-39d166326759)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T18:03:27+00:00 (16h ago)
26. [Want to try a red-paperclip side project from A$10? Here’s the honest setup we use](https://medium.com/@hello_86179/want-to-try-a-red-paperclip-side-project-from-a-10-heres-the-honest-setup-we-use-a10e2566892c)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The rules, the tracker and the first ideas, without the public scoreboard.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T16:08:26+00:00 (18h ago)
27. [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of awesome developer-first tools products.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T13:50:37+00:00 (20h ago)
28. [Ship a SaaS in a weekend with Cursor + Supabase: the stack, the code, and the 'don't skip this' checklist](https://dev.to/mailvalid/ship-a-saas-in-a-weekend-with-cursor-supabase-the-stack-the-code-and-the-dont-skip-this-ifh)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: this post is from the MailValid team. MailValid appears in one checklist item, and that...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T13:22:26+00:00 (20h ago)
29. [Show HN: Shield KYA – Open-source audit trail and gate for AI agent tool calls](https://news.ycombinator.com/item?id=50364706)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T12:33:39+00:00 (21h ago)
30. [I Built a Daily Sports Card Game in a Month With AI Agents. Here's Everything It Broke.](https://dev.to/sambrovda/i-built-a-daily-sports-card-game-in-a-month-with-ai-agents-heres-everything-it-broke-n1p)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm not an engineer. I come from the sales world. But between June 18 and July 16, I pushed 172...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T12:27:52+00:00 (21h ago)
31. [The Biggest Vibe Coding Trap: Mistaking a Launch for a Business](https://dev.to/nodex/the-biggest-vibe-coding-trap-mistaking-a-launch-for-a-business-2dbh)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My feed is full of weekend SaaS launches lately. Someone builds an AI tool in 48 hours, ships a...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T09:21:57+00:00 (24h ago)
32. [My Side Project Went From 1 Submission to 17 a Week. Here's What I'm Learning](https://dev.to/ashraful2502/my-side-project-went-from-1-submission-to-17-a-week-heres-what-im-learning-573a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I finally crossed 50 submissions on LaunchNests. It's a small milestone, but it means a lot to me as...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T09:02:51+00:00 (25h ago)
33. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T08:45:24+00:00 (25h ago)
34. [Custom B2B Dataset: How to Spot a Ready‑to‑Use Data Feed](https://dev.to/socialintel/custom-b2b-dataset-how-to-spot-a-ready-to-use-data-feed-1n81)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A step‑by‑step guide for indie founders to evaluate dataset quality signals before buying a custom B2B feed from $18.
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-04T06:01:29+00:00 (28h ago)
35. [Show HN: Kairos – Open-source risk and fraud decisioning platform](https://news.ycombinator.com/item?id=50358314)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey HN, Ayan here from Finic. We’re launching Kairos, an open source alternative to Sift, Sardine, and other real-time fraud decisioning…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-03T21:16:48+00:00 (37h ago)
36. [KKKKhazix/agent-autoloop](https://github.com/KKKKhazix/agent-autoloop)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 让你的命令行 Agent 在后台自己接活、自己跟进到底；平时不烦你，遇到拿不准的事才发卡片找你拍板。
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T08:02:11+00:00 (50h ago)
37. [851-labs/honest-thumbnails](https://github.com/851-labs/honest-thumbnails)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Chrome extension that replaces YouTube's clickbait thumbnails with a real frame from the middle of the video.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T00:24:50+00:00 (82h ago)
38. [Shahrukhalid/nexonic-download-manager](https://github.com/Shahrukhalid/nexonic-download-manager)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Free, open-source download manager for Mac and Windows (IDM alternative): 32-connection downloads, pause/resume, scheduler, queues, batch,…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-31T15:06:09+00:00 (115h ago)
39. [How to schedule Shopify sale prices so they actually end on time (without leaving variants discounted)](https://dev.to/zhuanghua/how-to-schedule-shopify-sale-prices-so-they-actually-end-on-time-without-leaving-variants-4d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I build a small Shopify app, and the problem I hear about most isn't "how do I start a sale." It's...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-31T02:37:24+00:00 (127h ago)
40. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (134h ago)
41. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T15:06:17+00:00 (139h ago)
42. [No-Code, AI Coding or Traditional Code: 5 Questions to Answer Before Building Your Micro-SaaS](https://pantpallavi13.medium.com/no-code-ai-coding-or-traditional-code-5-questions-to-answer-before-building-your-micro-saas-eebce1892bad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ll walk you through the five things I consider first.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T13:01:04+00:00 (141h ago)
43. [harshsinghsv/swiftdl](https://github.com/harshsinghsv/swiftdl)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Fast, resumable download manager with a browser extension. Many connections per file, instant resume, IDM-style download windows. Rust +…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T04:59:50+00:00 (149h ago)
44. [Show HN: DistractFree-Chrome extension and web app to stop doomscrolling](https://news.ycombinator.com/item?id=50299880)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T04:31:31+00:00 (149h ago)
45. [One merchant account, four side projects: how I keep the payment data from turning into a mess](https://dev.to/buhgalterapp/one-merchant-account-four-side-projects-how-i-keep-the-payment-data-from-turning-into-a-mess-4ojc)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most indie developers I know do not run one product. They run a VPN bot, a paid Discord or Telegram...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-29T21:04:03+00:00 (157h ago)
46. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (160h ago)
47. [6 months ago I couldn't code. Here's what I built for Shopify sellers](https://www.reddit.com/r/SideProject/comments/1xhtldd/6_months_ago_i_couldnt_code_heres_what_i_built/)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm 21 and I started learning to code this year. My friends selling on Shopify all had the same problem: they knew which products sold, but…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T16:53:57+00:00 (185h ago)
48. [The Median Paid Newsletter Converts 0.62% of Free Readers. Do the Math Before You Launch](https://dev.to/devinios/the-median-paid-newsletter-converts-062-of-free-readers-do-the-math-before-you-launch-5466)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The most useful number in beehiiv's 2026 paid-newsletter report is not a success story. It is the median: 0.62% conversion, $10/$100…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-27T11:27:29+00:00 (214h ago)
49. [Show HN: University of Malta LaTeX dissertation template, easily adapted](https://news.ycombinator.com/item?id=50255556)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-27T07:09:15+00:00 (219h ago)
50. [How to Price and Sell the AI Agent or n8n Workflow You Built: A Practical Guide for Creators](https://dev.to/aimarket24/how-to-price-and-sell-the-ai-agent-or-n8n-workflow-you-built-a-practical-guide-for-creators-1d8p)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You built something that works. Maybe it's an n8n workflow that turns inbound emails into CRM...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-25T15:53:28+00:00 (258h ago)
51. [Show HN: MegaKey (standardization and extension of the Hyper and Meh keys)](https://news.ycombinator.com/item?id=50207489)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: MegaKey is a proposed standardization + extension of Hyper and Meh - Mental tools for your mind: turn a mouthful like…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-23T11:49:27+00:00 (310h ago)
52. [When a Customer Asks for an Invoice With Their VAT Number and You Have Under 50 Customers](https://dev.to/posting-dude/when-a-customer-asks-for-an-invoice-with-their-vat-number-and-you-have-under-50-customers-f5h)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Say you have 30-something paying customers and one of them, a small agency in Germany, sends this...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-23T05:15:44+00:00 (317h ago)
53. [Primeira Assinatura em 24h Funciona? Descubra Como Criar Seu Próprio Micro SaaS](https://medium.com/@allansantoss777/primeira-assinatura-em-24h-funciona-descubra-como-criar-seu-pr%C3%B3prio-micro-saas-3e2e74541fb1)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Você já pensou em criar sua própria ferramenta online, disponibilizá-la para clientes e cobrar uma assinatura mensal pelo acesso?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-22T20:34:25+00:00 (325h ago)
54. [Show HN: Can a solo founder compete in the crowded Chrome extension market?](https://news.ycombinator.com/item?id=50076361)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-13T18:30:09+00:00 (543h ago)
55. [Show HN: Helicon – Desktop App for Meta's Muse Code CLI (Linux, Windows, macOS)](https://news.ycombinator.com/item?id=50070313)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi Hacker News, I'm Harjot. I've been using Meta's Muse Code CLI daily for a few weeks now. One thing that I found difficult to handle was…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-13T12:02:10+00:00 (550h ago)
56. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
57. [7 Tools That Replace Expensive SaaS Marketing Subscriptions (2026)](https://medium.com/@antoine.valton/7-tools-that-replace-expensive-saas-marketing-subscriptions-2026-268a1c92932c)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Add up the marketing tools a small SaaS can end up paying for.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T14:21:01+00:00 (20h ago)
58. [composer/spdx-licenses](https://github.com/composer/spdx-licenses)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Tools for working with the SPDX license list and validating licenses.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T08:52:33+00:00 (49h ago)
59. [I failed at selling CV templates in 2016. Ten years later I came back and built the whole tool](https://www.reddit.com/r/SideProject/comments/1xm1w3b/i_failed_at_selling_cv_templates_in_2016_ten/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My first attempt in 2016 flopped. Ten years of product design later, I tried again Back in 2016 I sold CV templates on a small WordPress…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T16:30:07+00:00 (65h ago)
60. [As launching a new feature, I made the old paid feature free. Is this a stupid marketing choice?](https://www.reddit.com/r/SideProject/comments/1xllisu/as_launching_a_new_feature_i_made_the_old_paid/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My current marketing plan is apparently to change for fewer things. I made Wallpets. Its a desktop wallpaper app where cats, dogs,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T02:29:25+00:00 (79h ago)
61. [Citus Camera. An IOS camera app built by a Photographer.](https://www.reddit.com/r/SideProject/comments/1xld2dj/citus_camera_an_ios_camera_app_built_by_a/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My name is Leon, I am a commercial photographer. And I built a camera app for IOS. Why? My camera bag weighs around 20kg (44lbs) And film…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T20:10:05+00:00 (86h ago)
62. [I built an all-in-one system for small used car dealerships in Brazil, because most of them still run on spreadsheets and WhatsApp](https://www.reddit.com/r/SideProject/comments/1xl3lrx/i_built_an_allinone_system_for_small_used_car/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject ! I've been building AutoPainel, a web app for small used car dealerships in Brazil. The problem: a typical small…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T13:52:57+00:00 (92h ago)
63. [AGENTORY — I turned my "AI assistant" workflows into boxed AI Task Kits (instruction files, not another app)](https://www.reddit.com/r/SideProject/comments/1xk8wji/agentory_i_turned_my_ai_assistant_workflows_into/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi — I'm the person behind AGENTORY. Short version of how I got here: I spent about a year working hands-on with agentic AI tools at my day…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-31T12:26:03+00:00 (117h ago)
64. [After my paid clipboard manager went subscription, I built a free, open-source one for the Mac](https://www.reddit.com/r/SideProject/comments/1xhdlrk/after_my_paid_clipboard_manager_went_subscription/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For years I used a paid clipboard manager. I bought a license, then the developer changed everything: a subscription, a pricier paid…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-28T03:35:39+00:00 (198h ago)
65. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
66. [I built an Omni-Tracker + Digital Garden so I could stop using 5 different apps for my media and notes](https://www.reddit.com/r/SideProject/comments/1xo6liw/i_built_an_omnitracker_digital_garden_so_i_could/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject ! I was tired of my personal data and thoughts being scattered across the internet: Letterboxd for movies, Goodreads for…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T01:59:52+00:00 (8h ago)
67. [I built Folloverse, a creator platform with memberships, paid posts, a shop and community chat in one page](https://www.reddit.com/r/SideProject/comments/1xn71yx/i_built_folloverse_a_creator_platform_with/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, This is Folloverse (folloverse.com), a home page for creators where they can: - Run memberships with tiers - Sell paid posts that fans…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T22:19:34+00:00 (36h ago)
68. [Globatics - live web analytics on a globe. My own dashboard saw 1 of my last 4 sales, so here's how I'd count the buyers analytics can't see](https://www.reddit.com/r/SideProject/comments/1xms0mb/globatics_live_web_analytics_on_a_globe_my_own/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I make Globatics, a web analytics tool. I also sell a small €25 digital product on the side, paid through Polar, and of course I track that…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T12:46:12+00:00 (45h ago)
69. [Show HN: Mago, an open source AI video studio, runs locally with Comfy](https://news.ycombinator.com/item?id=50341649)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm Alvaro, one of the founders of Mago. With my co-founder Alex (creator of Warpfusion, open source video to video), we built an open…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T18:49:44+00:00 (63h ago)
70. [[Feedback Request] 1 month in, 0 sales on my digital product store — what am I doing wrong?](https://www.reddit.com/r/SideProject/comments/1xm1p6y/feedback_request_1_month_in_0_sales_on_my_digital/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject , I'll be honest — I thought "build it and they will come" was real. A month ago I launched my Gumroad store selling…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T16:22:56+00:00 (66h ago)
71. [I published my first practical Excel finance eBook with 20 downloadable workbooks](https://www.reddit.com/r/SideProject/comments/1xls68k/i_published_my_first_practical_excel_finance/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi everyone! I've recently published my first eBook, Excel for Your First Finance Job , as a side project. I have a background in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T08:53:55+00:00 (73h ago)
72. [I’m building a way to browse what your town wants to sell](https://www.reddit.com/r/SideProject/comments/1xlb0ta/im_building_a_way_to_browse_what_your_town_wants/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ve been working on a side project called Something Noticed, starting in my hometown of Kingman, Arizona. The simplest way I’ve found to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T18:49:28+00:00 (87h ago)
73. [The Micro-SaaS Playbook: How Anyone Can Build a Tiny Online Tool and Earn Their First $1,000](https://medium.com/@growtricks1/the-micro-saas-playbook-how-anyone-can-build-a-tiny-online-tool-and-earn-their-first-1-000-346f4c52dd00)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You don't need to be a programmer, a startup founder, or a tech genius to build something people will pay for. Right now, ordinary people…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T16:09:46+00:00 (138h ago)
74. [Ask HN: Advise on monetization model for my freemium app wanted](https://news.ycombinator.com/item?id=50280505)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm an indie app dev and looking for some conceptual help with one of my freemium apps. I'm thinking about completely restructuring the…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T20:34:28+00:00 (181h ago)
75. [8 Micro-SaaS Ideas Developers Can Build Without Investors](https://medium.com/skillstuff/8-micro-saas-ideas-developers-can-build-without-investors-6c301d84cb02)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You do not need venture capital or a large engineering team to start a software business. You need a specific problem, a useful solution……
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T19:59:54+00:00 (182h ago)
76. [How to Build a Micro-SaaS Without Building Too Much?](https://blog.startupstash.com/how-to-build-a-micro-saas-without-building-too-much-d4cc1f8ee322)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Yes, I am going to talk about “how to build a micro-SaaS”, as simple as that, but it’s not a copy+paste of what’s already there. Continue…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T05:52:21+00:00 (196h ago)
77. [Solo Operators Building $10K+/Month AI Micro-SaaS With No Code Tools (Bubble, Softr, Make, n8n)](https://ai.plainenglish.io/solo-operators-building-10k-month-ai-micro-saas-with-no-code-tools-bubble-softr-make-n8n-2c837cb38e48)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I can’t write code, but I built a software product with 140 paying customers using Bubble, Softr, Make, and n8n. Continue reading on…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-24T13:27:08+00:00 (284h ago)
