# Passive Product Income Queue

Refreshed: 2026-11-18T09:24:08.517180+00:00

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

The most reliable zero-budget route is: build a client-side product that costs nothing per user, ship it free on channels that already exist (GitHub Releases, Chrome Web Store for extensions), and collect payment through the validated TRC-20 USDT receive address already running on the dev.to articles — placed in the README, product page, FUNDING.yml, and inside the tool itself. For buyers who want a proper checkout, Getly is the storefront that settles USDT on Tron directly to the seller's own wallet with no monthly fee and no KYC for crypto settlement. Every sale is fully automated: the artifact and the receive path are published once, and the on-chain balance is the only revenue metric.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Getly | Storefront for digital downloads with native stablecoin payouts | No monthly fee; network fee ~$0.50–1 on Tron per payout — verify current terms | USDT/USDC to the seller's own wallet; TRC-20 supported; $15 minimum payout on Tron ($5 on BNB Smart Chain) — verify current terms | One-time signup, list the product, enter the existing TRC-20 payout address | Storefront handles checkout and licence delivery automatically; owner does nothing per sale |
| GitHub Releases + README + FUNDING.yml wallet ask | Free hosting of downloadable binaries/releases with a receive address alongside | Free, no listing fee, no revenue cut | TRC-20 USDT directly to the existing validated receive address — no platform involved | Push the release once; add the address to README, FUNDING.yml custom: field, and release bodies | Payment is a direct on-chain transfer from the buyer; nothing can freeze it and no owner action occurs |
| Chrome Web Store | Official distribution with organic discovery for browser extensions | One-time $5 developer registration per account, covers up to 20 extensions, no renewal; this is the only non-zero cost in the plan | None directly — the store lists free extensions; monetise via the wallet ask inside the extension or a paid unlock sold through Getly | One-time $5 registration (credit/debit card needed) and extension submission | The store handles discovery and updates; every install carries the built-in payment path |
| itch.io (asset/tool listings) | Free storefront for tools and asset packs, pay-what-you-want supported | Free to upload; open revenue share (default ~10%); payout requires a tax interview with a TIN and a one-time $3.00 Tax Identity fee — verify current terms | None — fiat payouts only, identity verification required | Upload listing; complete tax interview (blocks the no-KYC constraint, so treat as optional/disqualified for crypto-only payout) | Storefront handles delivery; but note the KYC/TIN requirement conflicts with the no-KYC preference |

## Product Ideas

1. **One-annoyance browser extension (e.g. site-specific fix or declutterer)**
   - Who buys: Users of one specific site who hit one specific annoyance daily
   - Deliverable: Free extension on the Chrome Web Store; paid tier unlocks advanced options via licence key, plus the wallet address in the about/--help panel
   - Pricing model: Free tier plus paid upgrade (key sold on Getly), with a direct wallet ask for buyers who skip the storefront
   - Cost per extra user: Zero — all logic runs client-side
   - Free stack: Chrome Web Store listing, client-side JS, GitHub repo for issues
2. **Single-purpose CLI utility**
   - Who buys: Developers with one recurring task (format conversion, log cleaning, config generation)
   - Deliverable: Binary/archive on GitHub Releases, free; wallet address in README, FUNDING.yml, and --help output
   - Pricing model: Free with an honest pay-what-you-want wallet ask; optional paid 'pro' build via Getly
   - Cost per extra user: Zero — buyer runs it on their own machine
   - Free stack: GitHub Releases hosting, GitHub Actions builds, no server
3. **Template/preset/asset pack for a popular tool**
   - Who buys: Users of an existing ecosystem who want a ready-made starting point
   - Deliverable: Static downloadable pack; listed on Getly with USDT checkout, and the raw files mirrored free on GitHub Releases with the wallet ask in the README
   - Pricing model: One-time licence per pack, delivered automatically by the storefront
   - Cost per extra user: Zero — built once, downloaded many times
   - Free stack: GitHub Releases storage, Getly delivery, static product page on GitHub Pages
4. **Client-side static web tool**
   - Who buys: Anyone needing one transformation (converter, generator, checker) without installing anything
   - Deliverable: Static page, free to use; wallet address in the page footer as the payment path
   - Pricing model: Free tool with wallet ask; paywall-free freemium
   - Cost per extra user: Zero — static files, no backend
   - Free stack: GitHub Pages hosting, no server, no secrets

## Next Actions

- Pick one product shape and ship v1 as a free download on GitHub Releases with the validated TRC-20 address in the README, .github/FUNDING.yml custom: field, release body, and inside the tool's --help/about output
- Sign up on Getly, list the same product with a one-time price, and set the TRC-20 USDT payout address to the existing wallet — one-time setup, then zero per-sale work
- If the product is a browser extension, pay the one-time $5 Chrome Web Store registration and publish the free tier there for organic discovery, with the paid upgrade sold via Getly
- Write a dev.to article about the problem the product solves (problem-workaround shape), reusing the existing publishing pipeline, with the receive address in the footer as the ask
- Record the on-chain balance as the only revenue metric — never estimate or promise an amount

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
8. [Show DEV: Monetizing an Open Source WebRTC App Without Stripe, Subscriptions, or Paywalls (Part 2)](https://dev.to/quantumtechcoder/show-dev-monetizing-an-open-source-webrtc-app-without-stripe-subscriptions-or-paywalls-part-2-2kgb)
   - Kind: asset
   - Score: 71/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; How I built an on-chain, zero-trust micropayment and licensing engine with USDC on Base and Polygon—keeping P2P free forever while selling…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T07:14:07+00:00 (2h ago)
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
11. [Rising lifetime pricing for a Chrome extension: $1, then +$1 every 10 sales with Google](https://medium.com/@md_kadiwal/rising-lifetime-pricing-for-a-chrome-extension-1-then-1-every-10-sales-with-google-92fb125ef7a2)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: How I sell lifetime Pro for my extension with a price that rises $1 every 10 sales unlock it with Google sign-in instead of license keys
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T04:56:01+00:00 (4h ago)
12. [I built my own licence server so a stranger could pay me while I slept](https://coolsoftware.medium.com/i-built-my-own-licence-server-so-a-stranger-could-pay-me-while-i-slept-3e67d8d33d36)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What it takes for a solo developer to sell a Windows app: payments, keys, emails that land in junk, and the one file I can never lose
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T20:26:01+00:00 (13h ago)
13. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T21:17:25+00:00 (36h ago)
14. [A license-key server on Cloudflare Workers + KV, with signed keys and activation limits](https://dev.to/kitebyte/a-license-key-server-on-cloudflare-workers-kv-with-signed-keys-and-activation-limits-ja4)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: If you sell a desktop app, CLI, plugin or template, you eventually need license keys: one per sale,...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-10T20:27:55+00:00 (181h ago)
15. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (398h ago)
16. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
17. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (1866h ago)
18. [Decoding Predatory QR SaaS: How We Built Free, Offline Vector QR Generation in Your Browser](https://dev.to/khaithisran/decoding-predatory-qr-saas-how-we-built-free-offline-vector-qr-generation-in-your-browser-1gkp)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Alright, fellow engineers, let's talk about something that's been nagging at me, and honestly, it...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T09:15:26+00:00 (0h ago)
19. [I Built a Small Scheduling App. Somehow People Found It.](https://dev.to/skglnd/i-built-a-small-scheduling-app-somehow-people-found-it-35m1)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A few weeks ago, I launched a little side project called DaysWeCan. It's a simple tool for finding a...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T08:21:43+00:00 (1h ago)
20. [Everything Inside an AI Agent With $0 in Sales (5 Days Left)](https://dev.to/askkarenai/everything-inside-an-ai-agent-with-0-in-sales-5-days-left-fj4)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm KAREN, an AI agent. My goal is simple: make my first sale by November 23. Today is November 18....
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T08:05:21+00:00 (1h ago)
21. [Form submitted, invoice sent: building a Form-to-Invoice flow in n8n](https://dev.to/chong_newbee_c74302531d2e/form-submitted-invoice-sent-building-a-form-to-invoice-flow-in-n8n-i70)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: If you sell services, the gap between "the client filled in the order form" and "the invoice is in...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T07:09:12+00:00 (2h ago)
22. [My Digital Product Sales Dropped in September and I Still Don’t Know Why](https://sarahwithanh-xo.medium.com/my-digital-product-sales-dropped-in-september-and-i-still-dont-know-why-f2d6f7424c87)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I looked for the cause properly. Sometimes the honest answer is that there isn’t an obvious one.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T06:56:01+00:00 (2h ago)
23. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-18T06:51:29+00:00 (3h ago)
24. [I'm an AI that was given $100 and told to turn a profit. Day 2: three products live, $0 revenue](https://dev.to/john_bowergana_99eb8444e2/im-an-ai-that-was-given-100-and-told-to-turn-a-profit-day-2-three-products-live-0-revenue-200a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This post was written by an AI model, Claude (Fable 5.2), made by Anthropic. A human owner posts it...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T06:50:09+00:00 (3h ago)
25. [How To Actually Sell Your First Digital Product (A Beginner’s Guide)](https://travisnicholson.medium.com/how-to-actually-sell-your-first-digital-product-a-beginners-guide-5418e96a0d48)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You don’t need a big audience, an expensive course, or a complicated business plan. You just need to make your first $5.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T20:57:17+00:00 (12h ago)
26. [I Measured 62 Gumroad Products. 13 Look Like $5K a Month](https://medium.com/@e2larsen/i-measured-62-gumroad-products-13-look-like-5k-a-month-5c96d96c20d8)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What the products that sell have in common, from sales counts I could read, and where my own store lands.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T17:01:03+00:00 (16h ago)
27. [How to Sell Digital Products and Make Your First $500 in Your First Month (Beginner Guide)](https://kotakmdshahil.medium.com/how-to-sell-digital-products-and-make-your-first-500-in-your-first-month-beginner-guide-1f668fb571f5)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: No audience, no ads, no email list. Just the math, the product, and the plan — and an honest word about what “first month” really means.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T16:18:03+00:00 (17h ago)
28. [App Competitor Analysis for Indie Developers | AppOrient](https://medium.com/@apporient/app-competitor-analysis-for-indie-developers-apporient-5775da5b40c6)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T15:50:43+00:00 (18h ago)
29. [I Tried 5 AI Side Hustles That Could Build a ₹1 Lakh Digital Product Business](https://medium.com/@kaminigoyl2_43044/i-tried-5-ai-side-hustles-that-could-build-a-1-lakh-digital-product-business-5b551af9ca2f)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Five practical AI-powered digital product ideas you can create over a weekend, package for specific professional audiences, and sell…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T15:41:13+00:00 (18h ago)
30. [Your Gumroad Tags Describe a Thousand Other Products](https://medium.com/@jerrytestone1/your-gumroad-tags-describe-a-thousand-other-products-e574b1d4df0d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: “Template” fits a thousand products. Gumroad’s own advice is to tag the way customers search, and Claude can pull those words from your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T13:01:05+00:00 (20h ago)
31. [We checked 11 indie SaaS homepages for AI visibility. The results were the opposite of what we expected.](https://dev.to/fivehandsstudio/we-checked-11-indie-saas-homepages-for-ai-visibility-the-results-were-the-opposite-of-what-we-50a4)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: We've spent the week running small, honest AI-visibility checks on real small businesses: UK kitchen...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-17T12:32:38+00:00 (21h ago)
32. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T07:45:46+00:00 (26h ago)
33. [Best Chrome Extensions for Founders and Indie Hackers: 17 Tools Worth Exploring](https://medium.com/@weeklylaunches/best-chrome-extensions-for-founders-and-indie-hackers-17-tools-worth-exploring-356e878dcf6e)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: From managing daily tasks to researching competitors, saving online information, and handling business operations, these Chrome extensions…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T06:13:40+00:00 (27h ago)
34. [Grok Bot #1: I Set Up an Agent to Watch My Gumroad Store for 7 Days. 6 Alerts, 6 Were Noise](https://dev.to/crzy_undefinedundefined/grok-bot-1-i-set-up-an-agent-to-watch-my-gumroad-store-for-7-days-6-alerts-6-were-noise-4jp8)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I sell a few n8n workflow packs on Gumroad. I don't check the dashboard every day, and when I do, I...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-17T05:57:08+00:00 (28h ago)
35. [I Ranked My Referrers by Revenue, Not Visitors. 28 Visitors From One Site Out-Paid 219 From Google.](https://dev.to/posting-dude/i-ranked-my-referrers-by-revenue-not-visitors-28-visitors-from-one-site-out-paid-219-from-google-1e8f)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I run a handful of launch boards for indie products. Every morning I used to open analytics and look...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-17T05:01:01+00:00 (28h ago)
36. [Show HN: Fundlark-open source tool help early-career researcher find funding](https://news.ycombinator.com/item?id=50526177)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I just finished my PhD and am trying to get some funding to start off. I found that opportunities are scattered and it is a pain to find…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T01:21:51+00:00 (32h ago)
37. [Show HN: Open-source, real-time object tracking for live video feeds](https://news.ycombinator.com/item?id=50523377)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I type "forklift" on a live warehouse camera, and tamserve finds and tracks both forklifts, including the one driving in. Then I add…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-16T21:14:39+00:00 (36h ago)
38. [Get a Free .is-an.ai Domain for Your AI SaaS (2026)](https://dev.to/f9xrteam/get-a-free-is-anai-domain-for-your-ai-saas-2026-lc8)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Claim a free your-project.is-an.ai subdomain for your AI SaaS. Register via web, the new CLI, or Claude Code and OpenClaw plugins. Signups…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-16T17:14:39+00:00 (40h ago)
39. [Show HN: Cookiecutter-uv-core – uv template with an agent SDLC and quality gates](https://news.ycombinator.com/item?id=50519945)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T17:09:48+00:00 (40h ago)
40. [telekom/scale](https://github.com/telekom/scale)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Scale is the digital design system for Telekom products and experiences.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T15:07:10+00:00 (42h ago)
41. [I calculated how much payment fees actually eat from a $10 sale](https://dev.to/__a275a1bef4/i-calculated-how-much-payment-fees-actually-eat-from-a-10-sale-14ll)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Every indie hacker knows "Stripe takes ~3%." But when I broke down a real $10 sale, the number was...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-14T19:27:12+00:00 (86h ago)
42. [hikaku-io/hikaku-extension](https://github.com/hikaku-io/hikaku-extension)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open-source browser extension that flags AI-generated images and video as you browse. Runs entirely on your device. Chrome, Edge and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-14T14:06:05+00:00 (91h ago)
43. [CzzzzzzJ/mdldm-maitian](https://github.com/CzzzzzzJ/mdldm-maitian)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 麦田：自媒体多平台发布中控与数据监控（B站/抖音/小红书/视频号/YouTube/X），飞书卡片通知 + 数据大屏
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-14T03:59:22+00:00 (101h ago)
44. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-13T15:10:07+00:00 (114h ago)
45. [ysunyang4/Nexus](https://github.com/ysunyang4/Nexus)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Web AI for local work：让网页版 AI 直接操作你的本地文件和电脑，配套浏览器插件 webagent
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-13T13:46:21+00:00 (116h ago)
46. [gabrielbuzziv/emissor-nfse-nacional](https://github.com/gabrielbuzziv/emissor-nfse-nacional)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Emissor de NFS-e direto na API do Sistema Nacional NFS-e, sem custo por nota, rodando na sua conta da Cloudflare.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T23:02:35+00:00 (130h ago)
47. [rivet-dev/open-orange](https://github.com/rivet-dev/open-orange)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Run Cloudflare Workers and Durable Objects unchanged on AWS, GCP, Azure or your own servers.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T00:44:12+00:00 (153h ago)
48. [ysunyang4/webagent](https://github.com/ysunyang4/webagent)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Nexus 的浏览器插件：让 DeepSeek、Gemini、ChatGPT、Kimi 等网页版 AI 通过 MCP 调用本地工具，需配合 Nexus 使用
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-11T01:32:04+00:00 (176h ago)
49. [PersiOnOff/tenlith](https://github.com/PersiOnOff/tenlith)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open-source .NET + React SaaS starter with multi-tenancy, authentication, teams, Stripe billing and Docker.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-10T19:06:58+00:00 (182h ago)
50. [HolyArrs/HolyArrs](https://github.com/HolyArrs/HolyArrs)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One self-hosted app for your shows, movies and music.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T23:53:25+00:00 (202h ago)
51. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (446h ago)
52. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (471h ago)
53. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
54. [Show HN: A tiny macOS app that turns off the MacBook display [free license]](https://news.ycombinator.com/item?id=50507722)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, I made a tiny app that lets you turn off the MacBook screen when you work on external monitors. It does NOT just dim the brightness to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-15T15:37:52+00:00 (66h ago)
55. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
56. [How to Sell Digital Products Even If You Have Zero Followers](https://medium.com/@empirelaunch132/how-to-sell-digital-products-even-if-you-have-zero-followers-3ea2088c4481)
   - Kind: asset
   - Score: 42/100
   - Cost: not published
   - Owner must do: nothing
   - Why: When I launched my first product, my Instagram following was about 40 people, and half of them were relatives
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T16:10:46+00:00 (17h ago)
57. [7 Things You Can Sell Online Without Creating Physical Products](https://medium.com/@empirelaunch132/7-things-you-can-sell-online-without-creating-physical-products-80016942b2b3)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I once ordered a box of 100 phone cases for a “can’t-fail” online store idea
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T09:21:18+00:00 (0h ago)
58. [Best Guest Posting Services in 2026: I Checked 7 Vendors' Own Pricing Pages. 5 Let You Pick the Site First](https://dev.to/posting-dude/best-guest-posting-services-in-2026-i-checked-7-vendors-own-pricing-pages-5-let-you-pick-the-3865)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most "best guest posting services" lists are written by one of the services. So I skipped the lists...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-18T04:52:42+00:00 (4h ago)
59. [Show HN: DecksMD – local first, Markdown flashcards app and plugin for Obsidian](https://news.ycombinator.com/item?id=50539204)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I built a flashcards app and plugin for obsidian, based on markdown syntax. You use headers and paragraphs, tables or highlighted text to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T22:31:25+00:00 (11h ago)
60. [I Built 3 JavaScript Side Projects That Now Pay My Rent](https://javascript.plainenglish.io/i-built-3-javascript-side-projects-that-now-pay-my-rent-9485dfef9675)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Here’s exactly how a few nights of coding turned into a steady monthly income stream — and the automation tricks that made it possible…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T16:47:19+00:00 (17h ago)
61. [Show HN: Coral – Open-source gateway where agents write their own tools](https://news.ycombinator.com/item?id=50517803)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I'm James, one of the co-founders of Coral. Coral is an open-source, self-hosted gateway that sits between your agents and the…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-16T14:14:51+00:00 (43h ago)
62. [Show HN: Claktor – a refactoring CLI for coding agents](https://news.ycombinator.com/item?id=50517415)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I've been working on Claktor ever since I got frustrated with some 'code smells' AI Agents have been producing while writing Rust. Claktor…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T13:31:12+00:00 (44h ago)
63. [AI Referral Traffic Benchmark (Nov 2026): Which SaaS & AI Tools Actually Get Traffic from ChatGPT, Gemini, and Perplexity?](https://dev.to/jack_yu_0909/ai-referral-traffic-benchmark-nov-2026-which-saas-ai-tools-actually-get-traffic-from-chatgpt-260o)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Everyone talks about GEO (Generative Engine Optimization)—getting cited inside ChatGPT Search,...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-16T08:40:02+00:00 (49h ago)
64. [From a Simple Google Sheet to a Paid AI Product](https://medium.com/illumination/from-a-simple-google-sheet-to-a-paid-ai-product-4f6664b46b14)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 6 Micro-SaaS Ideas Worth Testing Continue reading on ILLUMINATION »
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-15T22:51:08+00:00 (59h ago)
