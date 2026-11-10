# Passive Product Income Queue

Refreshed: 2026-11-10T01:32:00.323795+00:00

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

The best zero-budget route is a freemium digital product whose free tier is distributed where discovery already exists, monetized by a paid upgrade or download sold through a storefront that settles stablecoin directly to the owner's wallet, backed by the already-live Tron receive address placed in the README, FUNDING.yml, release notes, and the tool's own output. The wallet ask costs nothing, needs no account or KYC, and cannot be seized; Getly is the storefront candidate for buyers who want a checkout flow, and the Chrome Web Store's one-time $5 is the only unavoidable cost if the product is a browser extension. Income is passive because every channel delivers the artifact or collects payment without the owner touching a sale.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Direct TRC-20 wallet address (already live) | Users pay USDT straight to the owner's validated Tron address from README, FUNDING.yml, release notes, --help, and dev.to articles | Zero; only Tron network fees, paid by the sender | USDT on Tron (TRC-20), direct to own wallet, no custodian, no KYC | Paste the existing validated address into README, .github/FUNDING.yml custom field, release bodies, and the tool's about output — one-time, no new account | The address is static text in artifacts already shipped; payment and delivery need no owner action ever |
| Getly | Digital-goods storefront with card and crypto checkout and direct stablecoin payout | Verify current terms (no monthly fee per lead excerpt; confirm any per-sale cut) | USDT on Tron (TRC-20) and USDC, to the seller's own wallet; ~$15 minimum payout on Tron (verify current terms) | One-time manual signup, product listing, and entering the existing TRC-20 payout address | Storefront handles checkout, license delivery, and payout automatically; owner never touches a sale |
| GitHub Releases + FUNDING.yml | Free hosting of binaries/archives and a rendered sponsor button, on the account that already hosts the code | Zero | Whatever address the owner puts in FUNDING.yml custom field and release notes — the existing TRC-20 address | Add .github/FUNDING.yml with custom: URL and attach the product file to a release — both one-time manual steps | Hosting and payment are static; downloads and payments flow without the owner |
| Chrome Web Store | Official distribution and organic discovery for browser extensions | One-time $5 developer registration; no renewal, no store cut on free extensions | None — it only distributes; payment happens via the wallet address in the extension's about page and the linked product page | Pay the $5 fee and upload the extension once; updates are manual but infrequent | Store handles hosting, updates, and discovery; monetization rides on the embedded wallet ask and storefront link |
| itch.io | Free storefront for tools and asset packs, pay-what-you-want supported | Free to publish; default ~10% revenue share (adjustable); payout requires a tax interview (TIN) and a one-time $3 identity fee | None — fiat only, so it fails the crypto-settlement preference and requires KYC | Manual account creation, upload, tax interview | Storefront delivers downloads automatically; note it is a secondary/reach channel since payout is custodial fiat with identity checks — verify current terms before relying on it |
| dev.to article funnel (already running) | Daily published articles whose footers carry the receive address; a problem-focused article drives product discovery | Zero; infrastructure already exists and runs | The same validated TRC-20 address, direct to own wallet | Write one article framing the problem the product solves, with the product link and address in the footer | Publication and address insertion are already automated; the article keeps working after publish |

## Product Ideas

1. **One-annoyance browser extension with pro unlock**
   - Who buys: Power users of one specific site or workflow annoyed by a single recurring friction (e.g. a missing keyboard shortcut, a cluttered UI, an auto-formatting nuisance)
   - Deliverable: Free extension on the Chrome Web Store; paid code/key unlocking the pro features, delivered by the storefront
   - Pricing model: Free tier plus paid one-time upgrade sold via Getly, with the TRC-20 address in the extension's about page
   - Cost per extra user: Zero — the extension runs client-side on the user's browser
   - Free stack: Chrome Web Store for distribution, Getly for the paid unlock, GitHub repo + FUNDING.yml for the wallet ask
2. **Single-purpose CLI utility or self-hostable script**
   - Who buys: Developers and homelab users who want a fix for one specific chore and will pay to skip building it
   - Deliverable: Binary/source in a GitHub Release; pro version (extra flags, output formats, batch mode) behind the paid download
   - Pricing model: Free core plus paid pro build, or pay-what-you-want with the TRC-20 address in README and --help
   - Cost per extra user: Zero — the buyer runs it on their own machine
   - Free stack: GitHub Releases hosting, GitHub repo, FUNDING.yml, Getly listing for card buyers
3. **Preset/template/asset pack for a tool people already use**
   - Who buys: Users of a popular tool (editor configs, Obsidian templates, design presets) who want a done-for-you setup
   - Deliverable: A zip archive of files, delivered as a download
   - Pricing model: Pay-what-you-want with a suggested price; wallet address in the listing, README, and a docs file inside the pack
   - Cost per extra user: Zero — files are built once and copied
   - Free stack: GitHub Releases + itch.io listing + dev.to article about the problem the pack solves
4. **Static client-side web tool with paid data/feature tier**
   - Who buys: People who need a one-shot conversion/lookup/formatting task solved in-browser with no signup
   - Deliverable: Free page on GitHub Pages; paid tier is a downloadable data set or offline/extended version
   - Pricing model: Free tier plus paid download of the extended version via Getly; TRC-20 address on the page footer
   - Cost per extra user: Zero — static hosting, no server
   - Free stack: GitHub Pages, GitHub Releases, Getly, existing dev.to funnel

## Next Actions

- Paste the validated TRC-20 address into the product README, .github/FUNDING.yml (custom: field), release notes, and the tool's --help/about output
- Build the freemium split: pick one product, ship the free core, define exactly what the paid upgrade adds
- Create a Getly account, list the paid tier, and enter the existing TRC-20 payout address; verify current fees and minimum payout before launch
- If the product is an extension, pay the one-time $5 Chrome Web Store registration and publish the free tier for organic discovery
- Write one dev.to problem-workaround article where the product is the fix, relying on the existing automated publish + address pipeline

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
10. [I made an Excel pricing kit for small T-shirt and hoodie sellers demo](https://www.reddit.com/r/SideProject/comments/1xq609w/i_made_an_excel_pricing_kit_for_small_tshirt_and/)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I run FireGuyUSA LLC and built this small digital product with AI assistance: a Windows desktop Excel kit for apparel sellers using DTF…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-07T13:10:11+00:00 (60h ago)
11. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T19:02:15+00:00 (78h ago)
12. [I spent £2.53 per install to earn about 10p per download. What would you do next with a kids’ app?](https://www.reddit.com/r/SideProject/comments/1xmc632/i_spent_253_per_install_to_earn_about_10p_per/)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’m a product designer, and I make small ad-free iPhone/iPad apps for under-5s. Melody Music is a music toy where every note stays in key,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T22:50:49+00:00 (171h ago)
13. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (198h ago)
14. [hhtower/price-comparison](https://github.com/hhtower/price-comparison)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: AI 订阅与卡网比价平台，说出需求，让 AI 帮你选。聚合 ChatGPT / Codex、Claude、Gemini 等代充或账号报价，对比价格走势、充值渠道与质保。AI-powered shopping and price comparison for…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T06:06:20+00:00 (307h ago)
15. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 54/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (1666h ago)
16. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
17. [I Made $400/Week Selling eBooks](https://medium.com/@gloriawrites21/i-made-400-week-selling-ebooks-6d1133106719)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I sold nearly 1,000 digital products in six months.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T23:06:58+00:00 (2h ago)
18. [The $5 Side Hustle That Started With 47 Abandoned Journals](https://medium.com/@gloriawrites1_74813/the-5-side-hustle-that-started-with-47-abandoned-journals-450941fb5bd1)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I found a way to sell them.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T22:43:15+00:00 (3h ago)
19. [I Turned a Reddit Complaint Into a Digital Product in 21 Minutes](https://medium.com/@gloriawrites1_74813/i-turned-a-reddit-complaint-into-a-digital-product-in-21-minutes-4ad083255123)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I used ChatGPT to turn a real problem into a simple PDF — and what I learned about finding customers.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T22:41:34+00:00 (3h ago)
20. [AgriciDaniel/obsidian-herdr](https://github.com/AgriciDaniel/obsidian-herdr)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Run Claude Code, Codex, Antigravity and OpenCode in persistent Herdr terminals inside Obsidian, with Mission Control and a safe, undoable…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T18:37:49+00:00 (7h ago)
21. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T17:53:38+00:00 (8h ago)
22. [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of awesome developer-first tools products.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T17:05:35+00:00 (8h ago)
23. [Show HN: DBDelve – Open-Source DB Client Made with Rust and GPUI](https://news.ycombinator.com/item?id=50427934)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I’m Shayan and a few months ago I started building a DB Client DBDelve with a focus on performance and just making something that…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-09T16:36:38+00:00 (9h ago)
24. [Building WUUUH: The First Phone Calls Are a Triage Problem — What Worked, What Broke](https://dev.to/onelifevibe/building-wuuuh-the-first-phone-calls-are-a-triage-problem-what-worked-what-broke-5c0i)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: When income stops, the loudest problem is rarely the most urgent one. In the early builds of a peer...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T12:50:33+00:00 (13h ago)
25. [I Finally Made Money From Something I Built ($0 to $152)](https://dev.to/dsspec/i-finally-made-money-from-something-i-built-0-to-152-17gb)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I've been building side projects on weekends next to my job for years. Until this week every single...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T10:31:49+00:00 (15h ago)
26. [How to Get Your First 100 SaaS Users Without Paid Ads: A 7-Step Beginner Playbook](https://davishaal.medium.com/how-to-get-your-first-100-saas-users-without-paid-ads-a-7-step-beginner-playbook-61c5543495a4)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You built the thing. You launched it. Then you refreshed the dashboard and saw zero.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T06:49:12+00:00 (19h ago)
27. [Text Blaze Alternative: TypeCrux vs Text Blaze Compared](https://rahakit.medium.com/text-blaze-alternative-typecrux-vs-text-blaze-compared-3c4108407dd3)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Compare TypeCrux and Text Blaze. Explore local-first privacy vs. cloud sync, free tier limits, dynamic templates, pricing, and lifetime…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T04:00:25+00:00 (22h ago)
28. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-09T00:36:30+00:00 (25h ago)
29. [Show HN: Notekpr – An open-source, E2EE alternative to Notion and Obsidian](https://news.ycombinator.com/item?id=50415581)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-08T18:10:29+00:00 (31h ago)
30. [Victor-Go/VictorLoad](https://github.com/Victor-Go/VictorLoad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Chrome/Edge extension to download videos and images from YouTube, X and Bilibili in a side panel
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-07T20:44:57+00:00 (53h ago)
31. [How to Spot Outdated Udemy Courses Before You Buy One](https://medium.com/@opportunityportalb/how-to-spot-outdated-udemy-courses-before-you-buy-one-f7c254ccf350)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A few years ago I bought a Python course on a Udemy sale for about the price of a sandwich.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-07T20:09:42+00:00 (53h ago)
32. [Sell software through your own Paddle or Lemon Squeezy account—with licensing connected](https://dev.to/permitcore/sell-software-through-your-own-paddle-or-lemon-squeezy-account-with-licensing-connected-1jbn)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You want to sell your app, not spend every release maintaining a second product made of checkout...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-07T19:31:56+00:00 (54h ago)
33. [What “scheduled” means on IndieNeed before a product goes live](https://dev.to/indieneed/what-scheduled-means-on-indieneed-before-a-product-goes-live-heh)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: IndieNeed is a small launch site for indie makers. A launch is tied to a specific day: the product is...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-07T15:12:48+00:00 (58h ago)
34. [How to protect your plugin or app from piracy, step by step](https://dev.to/ka0/how-to-protect-your-plugin-or-app-from-piracy-step-by-step-fk3)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A practical anti-piracy plan for indie developers selling plugins, scripts, bots and apps, layer by layer, without punishing the people who…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-06T20:31:29+00:00 (77h ago)
35. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T15:11:13+00:00 (82h ago)
36. [My first digital product:)](https://www.reddit.com/r/SideProject/comments/1xpepxk/my_first_digital_product/)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I created a $1 guide for restaurant owners. Would love some honest feedback. I recently made a 13-page digital guide called "Who Answers at…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T14:52:32+00:00 (83h ago)
37. [Best Stripe revenue apps for the Mac notch and menu bar (2026)](https://dev.to/notchrevenue/best-stripe-revenue-apps-for-the-mac-notch-and-menu-bar-2026-40ec)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Checked on each vendor's own page on 2026-11-06. This is an honest comparison of eight Mac apps that...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-06T06:35:26+00:00 (91h ago)
38. [jnv/lists](https://github.com/jnv/lists)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The definitive list of lists (of lists) curated on GitHub and elsewhere
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T23:20:38+00:00 (98h ago)
39. [jammaru/sakutto](https://github.com/jammaru/sakutto)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A browser extension for easy on-device translation with a local LLM (PLaMo). Private, free, no server needed.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T19:00:10+00:00 (103h ago)
40. [I Compared 5 SaaS Growth Benchmark Reports. The Most Counterintuitive Finding Wasn’t About Growth](https://nicheaitool.medium.com/i-compared-5-saas-growth-benchmark-reports-the-most-counterintuitive-finding-wasnt-about-growth-46e0d614ed24)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ve been tracking SaaS growth benchmarks for 18 months. Every quarter, I pull the latest reports from Aleph, High Alpha, SaaS Capital…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T15:05:08+00:00 (106h ago)
41. [6 Things Every Small SaaS Should Have Built In (2026)](https://medium.com/@antoine.valton/6-things-every-small-saas-should-have-built-in-2026-2edaeab04e10)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open the inbox for a SaaS you’ve been running for a few months.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T14:56:01+00:00 (107h ago)
42. [Supastarter Explained: Build Your Next.js SaaS Faster](https://dev.to/f9xrteam/supastarter-explained-build-your-nextjs-saas-faster-4n0m)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What is supastarter? See features, pricing and the stack, then follow a step-by-step guide to set it up and build your Next.js SaaS the…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T13:36:30+00:00 (108h ago)
43. [onlyreadai/onlyread](https://github.com/onlyreadai/onlyread)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Make AI browser agents read-only: a Chrome extension that refuses writes (send, post, edit, delete) before they leave the browser.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T11:32:23+00:00 (110h ago)
44. [inlevel9-com/BrowserControl](https://github.com/inlevel9-com/BrowserControl)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Chrome, Edge, Whale, Brave, Arc, Dia etc. Chromium Browser optimized BrowserControl Skill, Extension, Tool.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T08:01:46+00:00 (114h ago)
45. [I Put My Stripe Revenue in My MacBook Notch (and Stopped Alt-Tabbing to the Dashboard)](https://dev.to/notchrevenue/i-put-my-stripe-revenue-in-my-macbook-notch-and-stopped-alt-tabbing-to-the-dashboard-200d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For about a year, my most-used "app" was not my editor. It was a browser tab with the Stripe...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T06:40:36+00:00 (115h ago)
46. [Show HN: Gauge – Open-Source CLI to recursively improve your docs](https://news.ycombinator.com/item?id=50371090)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I’m Evan from Gauge. We’re open-sourcing our CLI to recursively improve your docs for coding agents. The CLI includes a local…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T20:31:30+00:00 (125h ago)
47. [Show HN: Shield KYA – Open-source audit trail and gate for AI agent tool calls](https://news.ycombinator.com/item?id=50364706)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T12:33:39+00:00 (133h ago)
48. [Show HN: Kairos – Open-source risk and fraud decisioning platform](https://news.ycombinator.com/item?id=50358314)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey HN, Ayan here from Finic. We’re launching Kairos, an open source alternative to Sift, Sardine, and other real-time fraud decisioning…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-03T21:16:48+00:00 (148h ago)
49. [Adam Robinson: A Legacy of Bootstrapping and Digital Innovation](https://medium.com/@couponfolloz/adam-robinson-a-legacy-of-bootstrapping-and-digital-innovation-cfafe360a9ad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The entrepreneur behind Retention.com and RB2B brought attention to building software businesses with lean teams and a clear commercial…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T16:49:13+00:00 (153h ago)
50. [How to schedule Shopify sale prices so they actually end on time (without leaving variants discounted)](https://dev.to/zhuanghua/how-to-schedule-shopify-sale-prices-so-they-actually-end-on-time-without-leaving-variants-4d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I build a small Shopify app, and the problem I hear about most isn't "how do I start a sale." It's...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-31T02:37:24+00:00 (239h ago)
51. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (246h ago)
52. [How I Built a $1.2M ARR SaaS Business Without Raising Funding](https://medium.com/@SteveBaltodano/how-i-built-a-1-2m-arr-saas-business-without-raising-funding-0fc560f4d1e6)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building a million-dollar SaaS business doesn’t always require venture capital, a large team, or millions in the bank. Sometimes, it…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T05:29:19+00:00 (260h ago)
53. [Show HN: DistractFree-Chrome extension and web app to stop doomscrolling](https://news.ycombinator.com/item?id=50299880)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T04:31:31+00:00 (261h ago)
54. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (271h ago)
55. [Show HN: MegaKey (standardization and extension of the Hyper and Meh keys)](https://news.ycombinator.com/item?id=50207489)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: MegaKey is a proposed standardization + extension of Hyper and Meh - Mental tools for your mind: turn a mouthful like…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-23T11:49:27+00:00 (422h ago)
56. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
57. [I’m a product manager, started vibe coding six months ago, and just released my first app](https://www.reddit.com/r/SideProject/comments/1xoh1bk/im_a_product_manager_started_vibe_coding_six/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey everyone, I’m Viktor, a product manager from Germany. I’ve been looking for a job for the past two years. About six months ago, I…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:08:55+00:00 (109h ago)
58. [I failed at selling CV templates in 2016. Ten years later I came back and built the whole tool](https://www.reddit.com/r/SideProject/comments/1xm1w3b/i_failed_at_selling_cv_templates_in_2016_ten/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My first attempt in 2016 flopped. Ten years of product design later, I tried again Back in 2016 I sold CV templates on a small WordPress…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T16:30:07+00:00 (177h ago)
59. [johackim/awesome-indiehackers](https://github.com/johackim/awesome-indiehackers)
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Awesome list about indie hackers
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T16:36:17+00:00 (9h ago)
60. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
61. [How I Turned –$37 Into $105 in One Day — With a JANKY $3.99 PDF](https://medium.com/@gloriawrites21/how-i-turned-37-into-105-in-one-day-with-a-janky-3-99-pdf-423eb9609a2d)
   - Kind: asset
   - Score: 42/100
   - Cost: not published
   - Owner must do: nothing
   - Why: No followers, no ads, no soul-selling.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T23:12:19+00:00 (2h ago)
62. [Why Small Digital Products Can Outsell Bigger, More Complicated Ideas](https://medium.com/@gloriawrites1_74813/why-small-digital-products-can-outsell-bigger-more-complicated-ideas-31c198b06a4b)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I made money selling tiny eBooks. The surprising lesson was how little commitment buyers wanted before making a purchase.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T22:42:22+00:00 (3h ago)
63. [Your Etsy Digital Planner Isn’t Selling Because You Launched It in the Wrong Order](https://medium.com/@Jamesdoy11/your-etsy-digital-planner-isnt-selling-because-you-launched-it-in-the-wrong-order-effafe895792)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Three sequencing mistakes that bury most planner listings — and the order that fixes them.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T18:53:04+00:00 (7h ago)
64. [I Let AI Fill My Side Project With Content. Google Took It Away Overnight.](https://levelup.gitconnected.com/i-let-ai-fill-my-side-project-with-content-google-took-it-away-overnight-1c30e97a7c5a)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 130 deep dives, a six-week SEO plan shipped in one day, a cliff on October 3, and the numbers I would normally leave out. Continue reading…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T16:50:35+00:00 (9h ago)
65. [I’m building a marketplace where AI agents can discover, purchase, physical products use online services](https://www.reddit.com/r/SideProject/comments/1xrvcrp/im_building_a_marketplace_where_ai_agents_can/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: We’re building a marketplace where AI agents can discover, pay for, and access online services, APIs, and even physical products, all…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T15:56:38+00:00 (10h ago)
66. [Unpopular opinion: a niche directory should charge before it has traffic](https://dev.to/wbcomdesigns/unpopular-opinion-a-niche-directory-should-charge-before-it-has-traffic-1a24)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One camp says charge listings or sponsors from day one so you learn what's worth paying for. The other says nobody pays to appear on an…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T15:45:01+00:00 (10h ago)
67. [SaaS Role Permission Testing: Share a Matrix Before Asking Peers to Try Your Demo](https://dev.to/urielbitton/saas-role-permission-testing-share-a-matrix-before-asking-peers-to-try-your-demo-oc)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For SaaS role permission testing, define the expected action for each account and resource before...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-09T14:55:16+00:00 (11h ago)
68. [Show HN: TimeScroll – an open-source, local replacement for Rewind on Mac](https://news.ycombinator.com/item?id=50424070)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I've been building TimeScroll since September 2025. It's a Mac app that records your screen in the background, so you can scroll…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-09T11:19:39+00:00 (14h ago)
69. [I built a Telugu-language news website and Android app - looking for honest feedback](https://www.reddit.com/r/SideProject/comments/1xrioxm/i_built_a_telugulanguage_news_website_and_android/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi everyone, A few months ago I started Telugu Vaadi TV, a news project for Telugu-speaking readers (Andhra Pradesh and Telangana, India).…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-09T04:49:02+00:00 (21h ago)
70. [We don't need more shovel shops. We need people to test the shovels.](https://www.reddit.com/r/SideProject/comments/1xr1eul/we_dont_need_more_shovel_shops_we_need_people_to/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: AI coding tools made shipping an app easy and cheap, but users stayed exactly as scarce as before, which is why a lot of us, me included,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-08T15:46:51+00:00 (34h ago)
71. [I set up a design-forward digital goods shop to learn the process](https://www.reddit.com/r/SideProject/comments/1xr0nvu/i_set_up_a_designforward_digital_goods_shop_to/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’m a brand designer in London. I’ve wanted to go through the process of setting up a digital goods shop for a while, and recently found…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-08T15:13:16+00:00 (34h ago)
72. [Why "AI" ends up as the biggest category on a launch board](https://dev.to/indieneed/why-ai-ends-up-as-the-biggest-category-on-a-launch-board-2cfh)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: IndieNeed is a small launch site for indie makers, and listings carry a primary category. Its public...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-08T08:09:43+00:00 (41h ago)
73. [need honest feedback - will give the entire reason and current progress of the build but in return would love to have your honest thoughts a](https://www.reddit.com/r/SideProject/comments/1xqltk9/need_honest_feedback_will_give_the_entire_reason/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: During the user-acquisition phase of my previous start-up - I realized what stood out most was how we are pitching/selling the idea decided…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-08T00:57:24+00:00 (49h ago)
74. [My side project for the past year: my own programming language. Today it runs a Minecraft clone.](https://www.reddit.com/r/SideProject/comments/1xqd056/my_side_project_for_the_past_year_my_own/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: GitHub: https://github.com/ahmadodeh9000/Lunar Hey everyone! I'm a 19 year old computer engineering student, and this is Lunar, a…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-07T18:16:41+00:00 (55h ago)
75. [I built an Android app that scans and tracks Pokémon TCG cards for collectors. Looking for honest feedback](https://www.reddit.com/r/SideProject/comments/1xqa7wp/i_built_an_android_app_that_scans_and_tracks/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm the solo developer behind PokeStash, and I'd really like some honest feedback from other makers. I built it because I keep a binder and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-07T16:19:42+00:00 (57h ago)
76. [The launch-readiness checks behind IndieNeed's review process](https://dev.to/indieneed/a-launch-readiness-checklist-for-show-hn-and-developer-communities-1eai)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: IndieNeed is a small launch site for indie makers. Free listings are reviewed by a person before they...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-07T06:10:23+00:00 (67h ago)
77. [I built another side project. But this time, I wanted honest feedback instead of "Looks good."](https://dev.to/dineshbista/i-built-another-side-project-but-this-time-i-wanted-honest-feedback-instead-of-looks-good-4h90)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building a side project is exciting. You spend nights coding, fixing bugs, improving the UI, and...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-07T03:29:21+00:00 (70h ago)
78. [I built a ChatGPT toolkit for adults over 40 — would love your honest feedback](https://www.reddit.com/r/SideProject/comments/1xpja5g/i_built_a_chatgpt_toolkit_for_adults_over_40/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ve been working on a small side project called Roland AI Life Reset. I created a 24-page digital toolkit with 40 practical ChatGPT…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T17:51:00+00:00 (80h ago)
79. [I created an 89-page AI guide for non-technical professionals — looking for honest feedback on my first digital product!](https://www.reddit.com/r/SideProject/comments/1xp8ixh/i_created_an_89page_ai_guide_for_nontechnical/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey everyone! I'm starting my journey into building digital products, and this is one of my first projects. I've been exploring the AI…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T09:22:23+00:00 (88h ago)
80. [Ask HN: Advise on monetization model for my freemium app wanted](https://news.ycombinator.com/item?id=50280505)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm an indie app dev and looking for some conceptual help with one of my freemium apps. I'm thinking about completely restructuring the…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T20:34:28+00:00 (293h ago)
81. [Show HN: Shop via CLI; for agents and software engineers](https://news.ycombinator.com/item?id=50264240)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hello HN! We're building a single search/browse API interface to thousands of ecommerce stores (hopefully, eventually, all of them).…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-27T19:12:20+00:00 (318h ago)
82. [Show HN: Nodecode, open-source living agent in Lisp that rewrites itself for you](https://news.ycombinator.com/item?id=50238751)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, we're Mike and Thom. Agents of the future should only have one tool (the interpreter, ideally a LISP eval), nothing more or less; to…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-26T03:30:18+00:00 (358h ago)
