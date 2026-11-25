# Passive Product Income Queue

Refreshed: 2026-11-25T20:30:40.112379+00:00

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

The best current route is to build the product once as a zero-marginal-cost artifact (client-side tool, asset pack, or downloadable utility), host it free on GitHub Releases and GitHub Pages, and list it on Getly, the one storefront this research verified that settles USDT directly to the seller's own Tron wallet with no monthly fee and no crypto-payout KYC. Layer the already-live Tron receive address into the README, product page, FUNDING.yml, and the tool's own output so users can pay without any storefront at all, and let the dev.to publishing pipeline (already running) drive discovery with problem-focused articles. Every channel below is free to list or a one-time manual setup; no per-sale owner action is required anywhere.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Getly (getly.store/sell/crypto) | Storefront for digital downloads with card and crypto checkout | No monthly fee; minimum payout $15 on Tron ($5 on BNB Smart Chain); network fee roughly $0.50-1 on Tron — verify current terms | USDT/USDC to the seller's own wallet; TRC-20 supported; no KYC for crypto settlement — verify current terms | One manual signup, one product listing, wallet address entered once | Buyers pay by card or crypto; the file is delivered by the storefront; payout lands in the wallet with no owner action per sale |
| GitHub Releases + README + FUNDING.yml | Free hosting for binaries/archives and an on-repo payment ask | Free, on the account already hosting the code | Direct: the validated Tron receive address goes in FUNDING.yml custom field, README, and each release body; payment goes straight to the wallet, no platform holds it | Add FUNDING.yml with the address as a custom URL; append the ask to README and release notes — one-time edits | No processor, no KYC, no platform that can freeze a payout; each download needs no owner action |
| Wallet ask inside the artifact (product page, --help, docs footer) | Receive address printed in the tool's own output and docs | Free | Direct to the validated Tron address; no custodian, no KYC | Embed the address once in the code, README, and product page | The ask travels with every copy and every fork, reaching users who never open the listing page; zero per-sale work |
| Chrome Web Store | Official distribution and organic discovery for browser extensions | One-time $5 developer registration per account, covers up to 20 extensions; no renewal, no cut on free extensions — verify current terms | None (free listing only); monetization via the wallet ask and a paid upgrade sold through Getly | Pay the $5 fee with a card once, upload the extension once | The store handles updates and discovery; a paid upgrade link is a fixed page, not per-sale work |
| itch.io | Free-to-publish storefront for tools and asset packs | Free to upload; seller chooses revenue share (default ~10%); payout requires a tax interview with a TIN and a one-time $3 identity fee — verify current terms | Fiat only; payout gated behind identity verification, so it does not meet the no-KYC preference | One manual upload and pricing page; a tax interview once if the owner is willing | Storefront delivers the file and handles checkout with no owner action per sale |
| dev.to articles (already running) | Problem-focused articles whose footer already carries the Tron address | Free; infrastructure already paid for and running | Direct to the already-published receive address | Reuse the existing pipeline; write the article framing the product as the fix — verify current dev.to policies on links | The back catalogue keeps working after publish; measurement already shows problem-workaround shapes outperform tutorials on this account |

## Product Ideas

1. **One-annoyance browser extension with a Pro unlock**
   - Who buys: Users who hit one specific site or workflow annoyance daily
   - Deliverable: Free extension from the Chrome Web Store; paid unlock key (extra features/settings sync) bought via Getly or the wallet address in the options page
   - Pricing model: Free tier plus paid upgrade
   - Cost per extra user: Zero per user — client-side code, no server
   - Free stack: Chrome Web Store listing + GitHub repo; upgrade sold on Getly
2. **Single-purpose CLI utility sold as a downloadable binary**
   - Who buys: Developers wanting a one-command fix (format, convert, lint, batch-rename)
   - Deliverable: Binary/archive on GitHub Releases; licence-free honest ask in README, --help, and release notes; optionally a Getly listing with a bundled Pro preset pack
   - Pricing model: Pay-what-you-want via wallet ask, or one-time licence via Getly
   - Cost per extra user: Zero — the binary is built once and downloaded many times
   - Free stack: GitHub Releases, GitHub Actions for builds, GitHub Pages product page
3. **Template / preset / asset pack for a tool people already use**
   - Who buys: Users of a popular editor or framework who want to skip setup
   - Deliverable: Downloadable pack hosted on GitHub Releases and listed on Getly
   - Pricing model: One-time licence per pack, or pay-what-you-want
   - Cost per extra user: Zero — built once, downloaded many times
   - Free stack: GitHub Releases + Getly listing + dev.to article as the discovery engine
4. **Static client-side web tool with a paid tier**
   - Who buys: Users needing a calculation, formatter, or converter done in-browser with no signup
   - Deliverable: Free tool on GitHub Pages; paid tier (offline copy, extra presets, licence) via Getly; wallet ask in the page footer
   - Pricing model: Freemium: free tier plus paid upgrade
   - Cost per extra user: Zero per user — everything runs client-side
   - Free stack: GitHub Pages (hosting), GitHub Actions (deploys), Getly (paid tier)

## Next Actions

- Pick one product shape (extension, CLI utility, or asset pack) and build it fully client-side so it costs nothing per user to run.
- Embed the validated Tron receive address in the product page, README, FUNDING.yml, release notes, and the tool's own --help/about output.
- Sign up on Getly once, list the product, and enter the Tron wallet for USDT payout — verify the current minimum payout ($15 Tron) and fee terms before publishing.
- Publish the artifact free on GitHub Releases and write the problem-workaround article to dev.to framing the product as the fix, reusing the existing publishing pipeline.
- If the product is a browser extension, pay the one-time $5 Chrome Web Store registration and list the free tier there for organic discovery, linking the paid upgrade to Getly.

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
   - Posted: 2026-11-24T13:22:06+00:00 (31h ago)
9. [balikunsh-bot/keepassxc-talroora](https://github.com/balikunsh-bot/keepassxc-talroora)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Keepassxc Talroora organizes credential records and manages encrypted password databases.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-18T20:10:03+00:00 (168h ago)
10. [tensorpass/aiconnect](https://github.com/tensorpass/aiconnect)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: AI Connect is the open source SDK of TensorPass for websites. Add an AI chat, a search bar that answers or an AI mode that runs on each…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-12T13:05:27+00:00 (319h ago)
11. Open-source the tool and take sponsorship on the repo
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A public repository is discovery that keeps working after it is published, and the wallet address in the README is a receive path that…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
12. [itch.io — free to publish, but a payout needs a tax interview and a TIN](https://itch.io/docs/creators/payments)
   - Kind: channel
   - Score: 61/100
   - Cost: $3.00 one-time
   - Owner must do: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: Owner creates an account, completes the tax interview with a TIN/SSN, pays the one-time $3 identity fee, and adds fiat payout details.
   - Verified: Tax interview, TIN requirement and the one-time $3.00 identity fee confirmed on itch.io/docs/creators/payments 2026-09-15. The earlier row said 'free to publish, no approval queue' and recorded cost_u
13. [cashapp/licensee](https://github.com/cashapp/licensee)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Gradle plugin which validates the licenses of your dependency graph match what you expect
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T18:36:08+00:00 (2h ago)
14. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (577h ago)
15. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
16. [w01fb0ss/PiBot](https://github.com/w01fb0ss/PiBot)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; Open-source, local-first AI agent team for your desktop: multi-agent group chats, computer use, browser, MCP, routines and approvals.…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-21T06:54:24+00:00 (110h ago)
17. [cedar-v/license-manager](https://github.com/cedar-v/license-manager)
   - Kind: asset
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: License Manager is an independent software licensing platform that provides license code generation, distribution, validation, and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-09-01T15:21:55+00:00 (2045h ago)
18. [I aimed for 90% form-fill accuracy on-device and got 80.7%: what a code gate around Gemini Nano taught me](https://dev.to/edycutjong/i-aimed-for-90-form-fill-accuracy-on-device-and-got-807-what-a-code-gate-around-gemini-nano-3937)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A Chrome form filler that reads customer messages on-device with Gemini Nano via Firebase AI Logic, and the three accuracy bars it missed.
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T19:54:27+00:00 (1h ago)
19. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T19:04:40+00:00 (2h ago)
20. [Show HN: Eight invisible personal Mac tools in one open source app](https://news.ycombinator.com/item?id=50645131)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T17:48:04+00:00 (3h ago)
21. [Day 5: I read about 570 posts looking for paying work and found none](https://dev.to/work247ia/day-5-i-read-about-570-posts-looking-for-paying-work-and-found-none-pac)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: I'm Moonlighter, an AI (Claude, made by Anthropic). I wrote this post myself. A human...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T17:15:03+00:00 (3h ago)
22. [I made $44,645 selling digital products. Here’s what I did wrong](https://travisnicholson.medium.com/i-made-44-645-selling-digital-products-heres-what-i-did-wrong-f471b1ed4008)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Since I started selling digital products online last year, I’ve generated $44,645 in revenue.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T17:04:54+00:00 (4h ago)
23. [We ran a company on an append-only ledger for 66 days. Here is the audit.](https://dev.to/orange_black_1c98182920bb/we-ran-a-company-on-an-append-only-ledger-for-66-days-here-is-the-audit-pel)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 12,873 events. 868 closed tasks. Zero revenue. A 66-day audit of a one-person company run by agents on an append-only ledger — including…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T15:09:09+00:00 (5h ago)
24. [This app changed how much I pay for email across my side projects](https://medium.com/@Yogesh_H/this-app-changed-how-much-i-pay-for-email-across-my-side-projects-f923d326d108)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 8 ways to put email on your own domain, what each costs for five projects, and the free trick that stops working in January 2027
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T12:48:55+00:00 (8h ago)
25. [9 self-hosted apps that replace $170 a month of SaaS bills on a side project](https://medium.com/@Yogesh_H/9-self-hosted-apps-that-replace-170-a-month-of-saas-bills-on-a-side-project-d2b174d4d72a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Analytics, automation, newsletters, uptime, forms, support chat, error tracking and email: $169.99 a month at list price, or one small…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T12:32:32+00:00 (8h ago)
26. [How to Make Your First $1 Selling Digital Products Online](https://medium.com/@zjjmhkk/how-to-make-your-first-1-selling-digital-products-online-c5459ffea7c8)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T12:08:04+00:00 (8h ago)
27. [Every side project needs an email address](https://medium.com/@sightradar.connect/every-side-project-needs-an-email-address-fd427a0aa84c)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I stopped paying per seat for them
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T10:31:51+00:00 (10h ago)
28. [Talking to 15 founders about launch distribution — free AI-visibility snapshot of your product in return](https://dev.to/visionwei/talking-to-15-founders-about-launch-distribution-free-ai-visibility-snapshot-of-your-product-in-e6l)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm researching how indie founders actually handle launch distribution, and I'd like to interview 15...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T06:22:21+00:00 (14h ago)
29. [SilverFeit/StikSound](https://github.com/SilverFeit/StikSound)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: StikSound — Ponle sonido de hasta 5 segundos a tus stickers PNG y GIFs animados para WhatsApp (Windows, macOS & Chrome Extension, 100%…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T21:55:25+00:00 (23h ago)
30. [When do you call a side project done — ship it, shelve it, or kill it?](https://dev.to/userxnom/when-do-you-call-a-side-project-done-ship-it-shelve-it-or-kill-it-1g2k)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Every side project I start reaches the same awkward point: it works, mostly. It's not polished, it's...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-24T21:39:46+00:00 (23h ago)
31. [What kept you going on a side project when almost nobody was using it?](https://dev.to/userxnom/what-kept-you-going-on-a-side-project-when-almost-nobody-was-using-it-23ho)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm a solo developer, and my first app is live. The part nobody talks about much is the quiet stretch...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-24T20:32:50+00:00 (24h ago)
32. [Micro SaaS Without Coding: How Solo Founders Are Building $1,000/Month Tools in a Weekend](https://medium.com/@fazak22344/micro-saas-without-coding-how-solo-founders-are-building-1-000-month-tools-in-a-weekend-535aeb281ed7)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You don’t need a tech co-founder or venture capital. Here is how to spot a profitable Micro SaaS idea, validate it fast, and grab a free…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T12:27:36+00:00 (32h ago)
33. [Plausible Spent 324 Days Stuck Near $400 a Month. Then It Picked a Fight With Google Analytics](https://abhinayguptha.medium.com/plausible-spent-324-days-stuck-near-400-a-month-then-it-picked-a-fight-with-google-analytics-ff008de63734)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: How a bootstrapped analytics SaaS reached $1M a year in revenue without paying for a single ad, and the quiet moves behind the viral post
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T09:07:41+00:00 (35h ago)
34. [Show HN: Alter – Restyle any website by typing what you want (extension, BYOK)](https://news.ycombinator.com/item?id=50617387)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Alter is a Chrome extension: open it on any site, type something like "hide the sidebar and display articles in Hacker News format", or…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-23T19:11:59+00:00 (49h ago)
35. [I emailed 95 indie iOS devs their real App Store ranks. Here's what actually happened](https://dev.to/eunice99x/i-emailed-95-indie-ios-devs-their-real-app-store-ranks-heres-what-actually-happened-en0)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: so for 11 days i did the thing everyone says to do. i replied to people launching their iOS apps on...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-23T16:41:39+00:00 (52h ago)
36. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-23T15:27:09+00:00 (53h ago)
37. [MVP Funding: 8 Ways to Pay for Your First Version](https://medium.com/@shipgrants/mvp-funding-8-ways-to-pay-for-your-first-version-ec0bc3d3343f)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: TL;DR: MVP funding does not have to come from investors. The eight main non-dilutive routes are pre-sales and paid pilots, cloud and AI…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-23T08:53:09+00:00 (60h ago)
38. [Why We Didn’t Spend ₹1 on Meta Ads to Sell a ₹699 Home Utility Product in Tier-2 India](https://medium.com/@info_83789/why-we-didnt-spend-1-on-meta-ads-to-sell-a-699-home-utility-product-in-tier-2-india-e1796578aef9)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: How building EverDailyIndia taught us that in Bharat, distribution isn’t a media-buying problem it’s a unit-economics and local-trust…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-23T03:40:05+00:00 (65h ago)
39. [Show HN: OpenComputer – an open source alternative to Devin](https://news.ycombinator.com/item?id=50581403)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN! Utpal here, I'm one of the founders of OpenComputer. OpenComputer is an open source cloud coding agent for teams that can run in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T20:19:56+00:00 (120h ago)
40. [oxnr/awesome-analytics](https://github.com/oxnr/awesome-analytics)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of analytics frameworks, software and other tools.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T15:11:47+00:00 (125h ago)
41. [ngiken/KenEasy-Gemini-MCP-Auto-Helper](https://github.com/ngiken/KenEasy-Gemini-MCP-Auto-Helper)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Google Gemini MCP 自动化放行与连续对话助手：MV3 永不断线后台引擎 + 智能点击重试，自动点击「始终允许」与「继续/Yes」、4 语言黑白双模式、零飞角自由拖拽悬浮窗、超时桌面通知及 6 层防刷熔断保护。
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-20T07:20:09+00:00 (133h ago)
42. [Show HN: Mastra Factory, the open-source software factory we use to build Mastra](https://news.ycombinator.com/item?id=50548660)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, we're Shane, Sam, and Abhi. Almost two years ago, we shared Mastra, our open-source TypeScript agent framework, on Show HN:…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-18T16:53:42+00:00 (172h ago)
43. [wittiden/glasshour](https://github.com/wittiden/glasshour)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Glasshour is a custom Chrome new tab page inspired by Apple's Liquid Glass. Built with vanilla HTML, CSS, and JavaScript (Manifest V3), it…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T10:53:21+00:00 (202h ago)
44. [Show HN: Cookiecutter-uv-core – uv template with an agent SDLC and quality gates](https://news.ycombinator.com/item?id=50519945)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T17:09:48+00:00 (219h ago)
45. [telekom/scale](https://github.com/telekom/scale)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Scale is the digital design system for Telekom products and experiences.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-16T15:07:10+00:00 (221h ago)
46. [hikaku-io/hikaku-extension](https://github.com/hikaku-io/hikaku-extension)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open-source browser extension that flags AI-generated images and video as you browse. Runs entirely on your device. Chrome, Edge and…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-14T14:06:05+00:00 (270h ago)
47. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (625h ago)
48. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (650h ago)
49. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
50. [Show HN: A tiny macOS app that turns off the MacBook display [free license]](https://news.ycombinator.com/item?id=50507722)
   - Kind: asset
   - Score: 45/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, I made a tiny app that lets you turn off the MacBook screen when you work on external monitors. It does NOT just dim the brightness to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-15T15:37:52+00:00 (245h ago)
51. [How I Self-Host 4 Free Browser Tools (0.3s AI Cutout, Fee Math, Bulk WebP, PDF Invoice) on a Home Mac mini](https://dev.to/flymilkbear/how-i-self-host-4-free-browser-tools-03s-ai-cutout-fee-math-bulk-webp-pdf-invoice-on-a-home-5dcf)
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most small e-commerce sellers and freelancers end up paying $40–$60/month across 4 separate SaaS apps...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-24T13:21:21+00:00 (31h ago)
52. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
53. [How to Sell One Digital Product From One Page (You Don’t Need a Store)](https://blog.wealthbuildingbaddie.com/how-to-sell-one-digital-product-from-one-page-you-dont-need-a-store-a874f760f54b)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: One product and one clear message can be your entire store. Continue reading on Wealth Building Baddie »
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T14:01:02+00:00 (6h ago)
54. [Your Content Is Getting Attention. So Why Is Nobody Buying?](https://medium.com/@madewithai/your-content-is-getting-attention-so-why-is-nobody-buying-44659fe37b39)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The uncomfortable difference between attracting an audience and attracting customers.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T14:01:02+00:00 (6h ago)
55. [I run my whole marketing desk in 30 minutes, from my phone. Here's the exact Grok Bot setup.](https://medium.com/@meestierolff/i-run-my-whole-marketing-desk-in-30-minutes-from-my-phone-heres-the-exact-grok-bot-setup-812099f06dec)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 5 sign-ups, $0 revenue, and a weekday 08:15 Grok Bot prompt you can paste. I still press send myself.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-25T09:34:44+00:00 (11h ago)
56. [I'm an AI agent running a tiny software business from A$0. Week one: A$0 revenue, 2 users](https://dev.to/snakbacks_sheets/im-an-ai-agent-running-a-tiny-software-business-from-a0-week-one-a0-revenue-2-users-159e)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm Claude, an AI agent. Six days ago a human gave me a domain, an email inbox and one instruction:...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-25T00:37:47+00:00 (20h ago)
57. [Show HN: Wakeshift – Open-Source MCP Events for Claude Code, Codex and More](https://news.ycombinator.com/item?id=50634239)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: tl;dr: We just open-sourced Wakeshift, which lets any MCP server serve interoperable events via MCP Events or harness-specific bridges.…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-24T20:27:48+00:00 (24h ago)
58. [I Built a Micro SaaS With AI. Here Is How I Would Monetize It](https://ai.plainenglish.io/i-built-a-micro-saas-with-ai-here-is-how-i-would-monetize-it-61351deac7c1)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Building it took a weekend. Charging for it took a plan. Here is the pricing playbook I wish I had. Continue reading on Artificial…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T14:52:13+00:00 (30h ago)
59. [Vibe Coding: Build Tiny AI Tools and Sell Them as Micro-SaaS](https://medium.com/ai-made-practical/vibe-coding-build-tiny-ai-tools-and-sell-them-as-micro-saas-34db0675dca3)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You describe what you want in plain English, the AI writes the code, and you sell the result. Tiny tools, real revenue. Continue reading on…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-24T01:01:02+00:00 (44h ago)
60. [Show HN: Budget – an open-source private budgeting app for Mac and Windows](https://news.ycombinator.com/item?id=50619761)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Budget is a free, open-source app for Mac and Windows. With the simple mode, it gives you what you'd expect of a budgeting app: configure…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-23T21:39:57+00:00 (47h ago)
61. [Lemon Squeezy is shutting down. What should you switch to, by country and by what you sell?](https://dev.to/panchei/lemon-squeezy-is-shutting-down-what-should-you-switch-to-by-country-and-by-what-you-sell-3egb)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Short answer: if your business is in one of Stripe's 37 locations and you sell software or digital...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-23T13:00:00+00:00 (56h ago)
62. [Show HN: Relaticle, an open-source CRM that Claude and ChatGPT can work in](https://news.ycombinator.com/item?id=50600315)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I asked rela (the assistant inside my open source crm relaticle) once for a task and a note (in a test workspace). It shows me a plan, one…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-22T14:59:49+00:00 (78h ago)
63. [title: The Zero-Backend Mobile App: How Cutting Cloud Infrastructure Eliminated My Monthly SaaS Bill published: false](https://dev.to/itech_accesories_b86af4c5/title-the-zero-backend-mobile-app-how-cutting-cloud-infrastructure-eliminated-my-monthly-saas-a58)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A look at the engineering and unit-economics math behind shipping My Momentum with zero servers, zero...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-19T10:16:40+00:00 (154h ago)
64. [Show HN: DecksMD – local first, Markdown flashcards app and plugin for Obsidian](https://news.ycombinator.com/item?id=50539204)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I built a flashcards app and plugin for obsidian, based on markdown syntax. You use headers and paragraphs, tables or highlighted text to…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-17T22:31:25+00:00 (190h ago)
