# Passive Product Income Queue

Refreshed: 2026-11-06T02:07:49.238640+00:00

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

The best zero-budget passive route is to build the product once, distribute it free everywhere that costs nothing to list, and monetize through two parallel paths: the already-live TRC-20 USDT receive address placed inside the product itself, and a one-time paid upgrade sold through a storefront that settles stablecoin to that same wallet without per-sale owner action. GitHub Releases/README/FUNDING.yml, dev.to articles, Firefox Add-ons and a static client-side page are free; Chrome Web Store is the only paid line item at a one-time $5. Getly is the lead storefront for crypto settlement, but verify its current terms before depending on it.

## Sales Channels

| Channel | What it lists | Cost | Crypto payout | Owner setup | Why passive |
| --- | --- | --- | --- | --- | --- |
| Wallet ask in README, --help/docs footer, product page and releases | Publishes the existing TRC-20 USDT receive address beside and inside the product | $0; no platform cut | USDT on Tron TRC-20 directly to the existing validated wallet; no custodian | Paste the same address into README, .github/FUNDING.yml custom URL, release notes, docs footer and CLI --help output once | No account, no approval, no per-sale action; payment is verifiable on-chain and needs no intermediary |
| Getly storefront | Sells the paid upgrade or one-time licence as a digital download and settles stablecoin to the seller wallet | Lead reports free listing with no monthly fee and a $15 Tron payout minimum; verify current terms | Lead reports USDT/USDC including TRC-20 to the seller's own wallet with no KYC for crypto settlement; verify current terms | Create account once, upload the paid artifact, set price, paste the existing TRC-20 receive address, connect the free product page | Delivery and settlement are handled by the storefront after one-time setup; the owner is not involved per sale |
| GitHub Releases + repo README/FUNDING.yml | Hosts the free product and the paid upgrade file with no storefront | $0 on the existing GitHub account; no listing fee | None by platform; the README/release ask uses the existing TRC-20 address | Create a public repo, add FUNDING.yml custom URL, attach release files, put the address and upgrade note in README and release bodies | Downloads are served by GitHub; the ask is embedded in the artifact, so there is no per-sale owner step |
| dev.to articles already running | Publishes problem-focused articles where the product is the fix and the footer is the ask | $0; already in use | Article footer already carries the TRC-20 receive address | Write one article per product shaped as a problem workaround; reuse the existing publishing path and footer | Articles and the back catalogue keep working after publication; no per-reader action |
| Firefox Add-ons / Edge Add-ons | Distributes a browser extension with organic discovery and no listing fee | Firefox: free to list; Edge: free to list, verify current review terms | None; monetization is the in-extension upgrade link or wallet ask | Create developer account once, package the extension, submit for review, add store listing pointing to the repo and paid upgrade | After approval, installs and updates are served by the store; the owner only ships new versions |
| Chrome Web Store | Distributes the extension to the largest extension audience with real organic discovery | One-time $5 developer registration per account, no renewal, covers up to 20 extensions; store takes no cut of a free extension | None; monetization is the paid upgrade sold elsewhere or the wallet ask | Pay the one-time $5, register, package and submit the extension, add listing with link to repo/upgrade page | The store handles install and update delivery; the only owner work is version updates |

## Product Ideas

1. **One-annoyance browser extension**
   - Who buys: Power users who hit one specific browser pain daily and want a two-click fix
   - Deliverable: Free extension in Firefox/Edge/Chrome; paid unlock adds saved profiles, export, or batch mode
   - Pricing model: Free tier plus one-time paid upgrade; wallet ask in the extension page and README
   - Cost per extra user: Near zero: client-side code, store delivery, no server
   - Free stack: GitHub repo, GitHub Releases, Firefox/Edge free listings, Chrome one-time $5, static page on GitHub Pages
2. **Single-purpose CLI utility**
   - Who buys: Developers and sysadmins who repeat one annoying conversion/cleanup/check task
   - Deliverable: Binary or script download; paid tier adds config presets, automation hooks, or a reference dataset
   - Pricing model: Free CLI with one-time licence for the upgrade; TRC-20 address printed in --help and README
   - Cost per extra user: Zero per user after packaging; downloads via GitHub Releases
   - Free stack: GitHub repo/Releases, README ask, dev.to problem article, optional Getly listing for the upgrade
3. **Client-side static web tool**
   - Who buys: Users who need one private conversion/calculator/inspection tool without uploading data
   - Deliverable: Static page that runs in the browser; paid unlock adds saved history, templates, or batch files
   - Pricing model: Free use plus one-time upgrade; wallet ask in page footer and repo
   - Cost per extra user: Zero: static hosting, no server, no per-user compute
   - Free stack: GitHub Pages, GitHub repo, dev.to article, optional storefront for the upgrade
4. **Template/preset/asset pack**
   - Who buys: Users of an existing tool who want a done-once starting set
   - Deliverable: Downloadable pack of templates, presets, snippets, or assets built once
   - Pricing model: One-time licence or pay-what-you-want with a floor; free sample pack as discovery
   - Cost per extra user: Zero per copy; file is downloaded repeatedly
   - Free stack: GitHub Releases for sample, Getly or wallet ask for the paid pack, dev.to article showing the problem it solves
5. **Compiled dataset or reference download**
   - Who buys: People who need a small, current, well-structured reference for a repeated task
   - Deliverable: Static JSON/CSV/markdown bundle with a free subset and a paid full set
   - Pricing model: Free subset plus one-time full download; address in README and dataset footer
   - Cost per extra user: Zero per download after compilation
   - Free stack: GitHub repo/Releases, GitHub Pages preview, dev.to article, Getly for paid delivery

## Next Actions

- Pick one product shape with the clearest single annoyance, and put the existing TRC-20 address into the README, product page and artifact help output from day one.
- Create the Getly listing for the paid upgrade, paste the existing TRC-20 receive address, and verify current payout minimums, fees and settlement terms before relying on it.
- Publish the free product through GitHub Releases and the repo, then write one dev.to problem-workaround article pointing at it, reusing the existing publishing footer.

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
   - Posted: 2026-11-05T12:51:51+00:00 (13h ago)
9. [Ahmadkhattak1/awesome-downloader](https://github.com/Ahmadkhattak1/awesome-downloader)
   - Kind: asset
   - Score: 65/100
   - Cost: not published
   - Owner must do: nothing
   - Why: pays in stablecoin, so the receive path is on-chain and verifiable; Open-source Windows download manager with browser video integration
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-24T17:58:52+00:00 (296h ago)
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
   - Posted: 2026-11-05T19:22:33+00:00 (7h ago)
13. [Show HN: An Open Source Superhuman Email Client Clone](https://news.ycombinator.com/item?id=50366894)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I'm a long-time Superhuman user, and a few weeks ago I cloned it as a native Mac app. It's keyboard-first, with split inboxes,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T15:22:44+00:00 (35h ago)
14. [I spent £2.53 per install to earn about 10p per download. What would you do next with a kids’ app?](https://www.reddit.com/r/SideProject/comments/1xmc632/i_spent_253_per_install_to_earn_about_10p_per/)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’m a product designer, and I make small ad-free iPhone/iPad apps for under-5s. Melody Music is a music toy where every note stays in key,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T22:50:49+00:00 (75h ago)
15. [Ask HN: Show your micro-SaaS (November 2026)](https://news.ycombinator.com/item?id=50329077)
   - Kind: asset
   - Score: 58/100
   - Cost: not published
   - Owner must do: nothing
   - Why: HN is a fantastic founder community. We, the people, love transparency, numbers, and analyzing bootstrapped business models. What is your…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T19:50:56+00:00 (102h ago)
16. [hhtower/price-comparison](https://github.com/hhtower/price-comparison)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: AI 订阅与卡网比价平台，说出需求，让 AI 帮你选。聚合 ChatGPT / Codex、Claude、Gemini 等代充或账号报价，对比价格走势、充值渠道与质保。AI-powered shopping and price comparison for…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T06:06:20+00:00 (212h ago)
17. [yaojingang/GEOInflow](https://github.com/yaojingang/GEOInflow)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Self-hosted web and AI crawler analytics for Generative Engine Optimization (GEO). Track visitors, AI search referrals, crawl logs, content…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-26T03:12:45+00:00 (263h ago)
18. [How much do AI agent businesses make? Median $13,894/month across 25 verified ones](https://dev.to/soloearn/how-much-do-ai-agent-businesses-make-median-13894month-across-25-verified-ones-4p78)
   - Kind: asset
   - Score: 57/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Verified monthly recurring revenue for 25 AI agent businesses, with the median, range and what the numbers leave out.
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-23T09:07:35+00:00 (329h ago)
19. One product, listed on every free channel at once
   - Kind: channel
   - Score: 53/100
   - Cost: not published
   - Owner must do: nothing
   - Why: sells the product while nobody is working; the signup is one-time
   - Next: List the product once and set the price. Owner does this by hand: open the account
20. [jnv/lists](https://github.com/jnv/lists)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The definitive list of lists (of lists) curated on GitHub and elsewhere
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T23:20:38+00:00 (3h ago)
21. [Day 17: encouragement belongs outside the sales column](https://dev.to/wyeco_ai/day-17-encouragement-belongs-outside-the-sales-column-2fk)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Wye Co is an AI-run studio. Day 17, November 5, 2026. Today's public activity was a Bluesky...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T22:15:18+00:00 (4h ago)
22. [I Built 6 Niche Calculator Sites with Astro — Here's the Full Stack and Monetization Plan](https://dev.to/sahamo/i-built-6-niche-calculator-sites-with-astro-heres-the-full-stack-and-monetization-plan-59na)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: ` Last year I decided to stop building things for clients and start building things for myself. The...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T20:43:06+00:00 (5h ago)
23. [I Researched 100 Marketplaces for Selling Digital Products.](https://medium.com/@jubileefestus/i-researched-100-marketplaces-for-selling-digital-products-9c0dbcabcfd0)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most advice about selling digital products starts with the same recommendation: Build an audience first.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T20:15:52+00:00 (6h ago)
24. [5 SaaS Ideas I Wish Someone Gave Me 2 Years Ago (2026)](https://ahmedgagan.medium.com/5-saas-ideas-i-wish-someone-gave-me-2-years-ago-2026-16afd312a749)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The boring niche that printed money
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T18:11:27+00:00 (8h ago)
25. [I'm an AI Agent With 3 Days Left. So Far: 5 Page Views, $0 in Sales.](https://dev.to/askkarenai/im-an-ai-agent-with-3-days-left-so-far-5-page-views-0-in-sales-5159)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Three days ago I said in public that I would try to make my first sale by November 9. I'm KAREN, an...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T15:33:52+00:00 (11h ago)
26. [Two forecasts from one dashboard function](https://dev.to/supero/two-forecasts-from-one-dashboard-function-2f4e)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Summit is an open-source sales CRM. Its dashboard has no role check, and a rep and a manager still...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T15:26:42+00:00 (11h ago)
27. [I Compared 5 SaaS Growth Benchmark Reports. The Most Counterintuitive Finding Wasn’t About Growth](https://nicheaitool.medium.com/i-compared-5-saas-growth-benchmark-reports-the-most-counterintuitive-finding-wasnt-about-growth-46e0d614ed24)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ve been tracking SaaS growth benchmarks for 18 months. Every quarter, I pull the latest reports from Aleph, High Alpha, SaaS Capital…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T15:05:08+00:00 (11h ago)
28. [6 Things Every Small SaaS Should Have Built In (2026)](https://medium.com/@antoine.valton/6-things-every-small-saas-should-have-built-in-2026-2edaeab04e10)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open the inbox for a SaaS you’ve been running for a few months.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T14:56:01+00:00 (11h ago)
29. [Supastarter Explained: Build Your Next.js SaaS Faster](https://dev.to/f9xrteam/supastarter-explained-build-your-nextjs-saas-faster-4n0m)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What is supastarter? See features, pricing and the stack, then follow a step-by-step guide to set it up and build your Next.js SaaS the…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T13:36:30+00:00 (12h ago)
30. [I Kept Launching Side Projects. Then I Realized Launch Day Wasn’t the Problem.](https://mrrehan21.medium.com/i-kept-launching-side-projects-then-i-realized-launch-day-wasnt-the-problem-c0ef150ffa20)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What building multiple SaaS products taught me about distribution, long term visibility and why I created Oribisoft.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T13:33:02+00:00 (13h ago)
31. [I Made $1,500 Selling Digital Products in 2 Hours and 45 Minutes. Here’s My Exact Blueprint](https://medium.com/@amnamuskan714/i-made-1-500-selling-digital-products-in-2-hours-and-45-minutes-heres-my-exact-blueprint-75193e553c5a)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I need to be upfront about the headline: the 2 hours and 45 minutes was the launch window,
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:48:40+00:00 (13h ago)
32. [PhantomDusknard48816/tiktok-respocket-unfollow-non-mutuals](https://github.com/PhantomDusknard48816/tiktok-respocket-unfollow-non-mutuals)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Automatically unfollow everyone on TikTok who doesn't follow you back – while keeping your friends safe.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:00:52+00:00 (14h ago)
33. [Audit One Digital Product Before You Change Its Price](https://medium.com/@madewithai/audit-one-digital-product-before-you-change-its-price-fb8da6924966)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Disclosure: The examples are fictional and illustrate a method, not customer results.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:01:01+00:00 (14h ago)
34. [unopim/unopim](https://github.com/unopim/unopim)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Open source Product Information Management (PIM) and Digital Asset Management (DAM) platform built on Laravel — manage, enrich, and scale…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-05T11:54:16+00:00 (14h ago)
35. [How to Monetize a Chrome Extension: Revenue Models That Work for B2B and SaaS Products](https://medium.com/@ryagoel1994/how-to-monetize-a-chrome-extension-revenue-models-that-work-for-b2b-and-saas-products-923eea393877)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Introduction
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T11:30:56+00:00 (15h ago)
36. [agamm/awesome-developer-first](https://github.com/agamm/awesome-developer-first)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A curated list of awesome developer-first tools products.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T11:06:17+00:00 (15h ago)
37. [I Put My Stripe Revenue in My MacBook Notch (and Stopped Alt-Tabbing to the Dashboard)](https://dev.to/notchrevenue/i-put-my-stripe-revenue-in-my-macbook-notch-and-stopped-alt-tabbing-to-the-dashboard-200d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For about a year, my most-used "app" was not my editor. It was a browser tab with the Stripe...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T06:40:36+00:00 (20h ago)
38. [Which link actually brought the sale?](https://dev.to/moinulhaq/which-link-actually-brought-the-sale-1h32)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most of us share links everywhere. Instagram bio. WhatsApp groups. Email. Ads. A poster with a QR...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T04:32:20+00:00 (22h ago)
39. [codelitdev/courselit](https://github.com/codelitdev/courselit)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Create/Sell courses and digital downloads and publish blogs on your own branded website. An open source alternative to Teachable,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T04:26:44+00:00 (22h ago)
40. [How to Get Your First 10 Paying Customers Without Spending Money on Ads](https://medium.com/@dealpilo/how-to-get-your-first-10-paying-customers-without-spending-money-on-ads-ef96e79665ac)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You don’t need a big audience, a viral launch, or a perfect product. You need to find the right people, solve a problem they care about…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T03:31:01+00:00 (23h ago)
41. [Show HN: Gauge – Open-Source CLI to recursively improve your docs](https://news.ycombinator.com/item?id=50371090)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi HN, I’m Evan from Gauge. We’re open-sourcing our CLI to recursively improve your docs for coding agents. The CLI includes a local…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T20:31:30+00:00 (30h ago)
42. [Show HN: Shield KYA – Open-source audit trail and gate for AI agent tool calls](https://news.ycombinator.com/item?id=50364706)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-04T12:33:39+00:00 (38h ago)
43. [lucascodev/aura-datadock-db](https://github.com/lucascodev/aura-datadock-db)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Database manager for VS Code: browse, query, edit and chart Postgres, MySQL and MariaDB in Docker, local or remote over SSH.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T02:58:38+00:00 (47h ago)
44. [yusufky63/x-country-withheld-viewer](https://github.com/yusufky63/x-country-withheld-viewer)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: X'te ülke bazlı gizlenen gönderileri ve hesapları, X'in kendi arayüzünde gösteren tarayıcı eklentisi
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T22:36:54+00:00 (52h ago)
45. [Show HN: Kairos – Open-source risk and fraud decisioning platform](https://news.ycombinator.com/item?id=50358314)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey HN, Ayan here from Finic. We’re launching Kairos, an open source alternative to Sift, Sardine, and other real-time fraud decisioning…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-11-03T21:16:48+00:00 (53h ago)
46. [Adam Robinson: A Legacy of Bootstrapping and Digital Innovation](https://medium.com/@couponfolloz/adam-robinson-a-legacy-of-bootstrapping-and-digital-innovation-cfafe360a9ad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The entrepreneur behind Retention.com and RB2B brought attention to building software businesses with lean teams and a clear commercial…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T16:49:13+00:00 (57h ago)
47. [KKKKhazix/agent-autoloop](https://github.com/KKKKhazix/agent-autoloop)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: 让你的命令行 Agent 在后台自己接活、自己跟进到底；平时不烦你，遇到拿不准的事才发卡片找你拍板。
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T08:02:11+00:00 (66h ago)
48. [How to schedule Shopify sale prices so they actually end on time (without leaving variants discounted)](https://dev.to/zhuanghua/how-to-schedule-shopify-sale-prices-so-they-actually-end-on-time-without-leaving-variants-4d)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I build a small Shopify app, and the problem I hear about most isn't "how do I start a sale." It's...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-31T02:37:24+00:00 (144h ago)
49. [Show HN: Staxless – Open-source microservice SaaS boilerplate](https://news.ycombinator.com/item?id=50309010)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-30T19:28:55+00:00 (151h ago)
50. [No-Code, AI Coding or Traditional Code: 5 Questions to Answer Before Building Your Micro-SaaS](https://pantpallavi13.medium.com/no-code-ai-coding-or-traditional-code-5-questions-to-answer-before-building-your-micro-saas-eebce1892bad)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I’ll walk you through the five things I consider first.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T13:01:04+00:00 (157h ago)
51. [Show HN: DistractFree-Chrome extension and web app to stop doomscrolling](https://news.ycombinator.com/item?id=50299880)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-30T04:31:31+00:00 (166h ago)
52. [One merchant account, four side projects: how I keep the payment data from turning into a mess](https://dev.to/buhgalterapp/one-merchant-account-four-side-projects-how-i-keep-the-payment-data-from-turning-into-a-mess-4ojc)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Most indie developers I know do not run one product. They run a VPN bot, a paid Discord or Telegram...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-29T21:04:03+00:00 (173h ago)
53. [Ask HN: Do you have side-projects that generate >$500 revenue/month?](https://news.ycombinator.com/item?id=50293459)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: What inspired you to build that project and how long did it take?
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-29T18:12:17+00:00 (176h ago)
54. [6 months ago I couldn't code. Here's what I built for Shopify sellers](https://www.reddit.com/r/SideProject/comments/1xhtldd/6_months_ago_i_couldnt_code_heres_what_i_built/)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm 21 and I started learning to code this year. My friends selling on Shopify all had the same problem: they knew which products sold, but…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T16:53:57+00:00 (201h ago)
55. [The Median Paid Newsletter Converts 0.62% of Free Readers. Do the Math Before You Launch](https://dev.to/devinios/the-median-paid-newsletter-converts-062-of-free-readers-do-the-math-before-you-launch-5466)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: The most useful number in beehiiv's 2026 paid-newsletter report is not a success story. It is the median: 0.62% conversion, $10/$100…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-27T11:27:29+00:00 (231h ago)
56. [Show HN: University of Malta LaTeX dissertation template, easily adapted](https://news.ycombinator.com/item?id=50255556)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-27T07:09:15+00:00 (235h ago)
57. [How to Price and Sell the AI Agent or n8n Workflow You Built: A Practical Guide for Creators](https://dev.to/aimarket24/how-to-price-and-sell-the-ai-agent-or-n8n-workflow-you-built-a-practical-guide-for-creators-1d8p)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: You built something that works. Maybe it's an n8n workflow that turns inbound emails into CRM...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-10-25T15:53:28+00:00 (274h ago)
58. [Show HN: MegaKey (standardization and extension of the Hyper and Meh keys)](https://news.ycombinator.com/item?id=50207489)
   - Kind: asset
   - Score: 52/100
   - Cost: not published
   - Owner must do: nothing
   - Why: MegaKey is a proposed standardization + extension of Hyper and Meh - Mental tools for your mind: turn a mouthful like…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-23T11:49:27+00:00 (326h ago)
59. [Show HN: Can a solo founder compete in the crowded Chrome extension market?](https://news.ycombinator.com/item?id=50076361)
   - Kind: asset
   - Score: 51/100
   - Cost: not published
   - Owner must do: nothing
   - Why: free tooling or reach to build and market the product with
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-13T18:30:09+00:00 (560h ago)
60. Free-tier stack so the product costs nothing to run
   - Kind: asset
   - Score: 48/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A product that costs nothing per user can stay free at the top of the funnel forever. Client-side work needs no server at all; GitHub Pages…
   - Next: Confirm the free tier's real limits and terms, then keep the product's per-user cost at zero so the free tier can stay free indefinitely.
61. [I’m a product manager, started vibe coding six months ago, and just released my first app](https://www.reddit.com/r/SideProject/comments/1xoh1bk/im_a_product_manager_started_vibe_coding_six/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey everyone, I’m Viktor, a product manager from Germany. I’ve been looking for a job for the past two years. About six months ago, I…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:08:55+00:00 (14h ago)
62. [7 Tools That Replace Expensive SaaS Marketing Subscriptions (2026)](https://medium.com/@antoine.valton/7-tools-that-replace-expensive-saas-marketing-subscriptions-2026-268a1c92932c)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Add up the marketing tools a small SaaS can end up paying for.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-04T14:21:01+00:00 (36h ago)
63. [composer/spdx-licenses](https://github.com/composer/spdx-licenses)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Tools for working with the SPDX license list and validating licenses.
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T08:52:33+00:00 (65h ago)
64. [I failed at selling CV templates in 2016. Ten years later I came back and built the whole tool](https://www.reddit.com/r/SideProject/comments/1xm1w3b/i_failed_at_selling_cv_templates_in_2016_ten/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My first attempt in 2016 flopped. Ten years of product design later, I tried again Back in 2016 I sold CV templates on a small WordPress…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T16:30:07+00:00 (82h ago)
65. [As launching a new feature, I made the old paid feature free. Is this a stupid marketing choice?](https://www.reddit.com/r/SideProject/comments/1xllisu/as_launching_a_new_feature_i_made_the_old_paid/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My current marketing plan is apparently to change for fewer things. I made Wallpets. Its a desktop wallpaper app where cats, dogs,…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T02:29:25+00:00 (96h ago)
66. [Citus Camera. An IOS camera app built by a Photographer.](https://www.reddit.com/r/SideProject/comments/1xld2dj/citus_camera_an_ios_camera_app_built_by_a/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: My name is Leon, I am a commercial photographer. And I built a camera app for IOS. Why? My camera bag weighs around 20kg (44lbs) And film…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T20:10:05+00:00 (102h ago)
67. [I built an all-in-one system for small used car dealerships in Brazil, because most of them still run on spreadsheets and WhatsApp](https://www.reddit.com/r/SideProject/comments/1xl3lrx/i_built_an_allinone_system_for_small_used_car/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject ! I've been building AutoPainel, a web app for small used car dealerships in Brazil. The problem: a typical small…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-01T13:52:57+00:00 (108h ago)
68. [AGENTORY — I turned my "AI assistant" workflows into boxed AI Task Kits (instruction files, not another app)](https://www.reddit.com/r/SideProject/comments/1xk8wji/agentory_i_turned_my_ai_assistant_workflows_into/)
   - Kind: asset
   - Score: 46/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi — I'm the person behind AGENTORY. Short version of how I got here: I spent about a year working hands-on with agentic AI tools at my day…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-31T12:26:03+00:00 (134h ago)
69. [After my paid clipboard manager went subscription, I built a free, open-source one for the Mac](https://www.reddit.com/r/SideProject/comments/1xhdlrk/after_my_paid_clipboard_manager_went_subscription/)
   - Kind: asset
   - Score: 45/100
   - Cost: not published
   - Owner must do: nothing
   - Why: For years I used a paid clipboard manager. I bought a license, then the developer changed everything: a subscription, a pricier paid…
   - Next: Publish the repository with the receive address in the README, so discovery and the ask live in the same artifact.
   - Posted: 2026-10-28T03:35:39+00:00 (215h ago)
70. [johackim/awesome-indiehackers](https://github.com/johackim/awesome-indiehackers)
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Awesome list about indie hackers
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-06T00:14:37+00:00 (2h ago)
71. Write the article that the product is the answer to
   - Kind: asset
   - Score: 44/100
   - Cost: not published
   - Owner must do: nothing
   - Why: This bot already publishes to dev.to daily and measures which shapes earn engagement -- problem-workaround outperforms build-tutorial by…
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
72. [A listing checklist for indie makers: what to fix before you launch](https://medium.com/@mainapp/a-listing-checklist-for-indie-makers-what-to-fix-before-you-launch-92b9456c0ec4)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Launching a small game, app or browser extension is mostly about the first five seconds someone spends on your listing. Directories like…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T19:22:05+00:00 (7h ago)
73. [I let an AI agent read one document. It tried to make a payment. Try it yourself in 60 seconds.](https://dev.to/tinniaru3005/i-let-an-ai-agent-read-one-document-it-tried-to-make-a-payment-try-it-yourself-in-60-seconds-jf9)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: AI agents are getting real tools: email, payments, code repos, customer data. At the same time, they...
   - Next: Write the problem-shaped article this product answers and let the existing footer carry the ask -- no new channel, and the publishing path already runs.
   - Posted: 2026-11-05T17:42:17+00:00 (8h ago)
74. [Google Wants My Home Address to Sell a $2 App: Why I’m Quitting Google Play](https://medium.com/cross-commit/google-wants-my-home-address-to-sell-a-2-app-why-im-quitting-google-play-695aaa03e7c7)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: A few days ago, I paid the $25 registration fee for the Google Play Console. Continue reading on Cross Commit »
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T13:58:04+00:00 (12h ago)
75. [I built a self-hosted store in plain PHP. No Composer, no bundler, takes Bitcoin / Paypal / Stripe](https://www.reddit.com/r/SideProject/comments/1xoh5er/i_built_a_selfhosted_store_in_plain_php_no/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Got tired of every "simple" ecommerce option being either a SaaS taking a cut or a 40 MB vendor folder, so I built the store I actually…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T12:14:59+00:00 (14h ago)
76. [I built an Omni-Tracker + Digital Garden so I could stop using 5 different apps for my media and notes](https://www.reddit.com/r/SideProject/comments/1xo6liw/i_built_an_omnitracker_digital_garden_so_i_could/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hey r/SideProject ! I was tired of my personal data and thoughts being scattered across the internet: Letterboxd for movies, Goodreads for…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-05T01:59:52+00:00 (24h ago)
77. [I built Folloverse, a creator platform with memberships, paid posts, a shop and community chat in one page](https://www.reddit.com/r/SideProject/comments/1xn71yx/i_built_folloverse_a_creator_platform_with/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi, This is Folloverse (folloverse.com), a home page for creators where they can: - Run memberships with tiers - Sell paid posts that fans…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T22:19:34+00:00 (52h ago)
78. [Globatics - live web analytics on a globe. My own dashboard saw 1 of my last 4 sales, so here's how I'd count the buyers analytics can't see](https://www.reddit.com/r/SideProject/comments/1xms0mb/globatics_live_web_analytics_on_a_globe_my_own/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I make Globatics, a web analytics tool. I also sell a small €25 digital product on the side, paid through Polar, and of course I track that…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-03T12:46:12+00:00 (61h ago)
79. [Show HN: Mago, an open source AI video studio, runs locally with Comfy](https://news.ycombinator.com/item?id=50341649)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm Alvaro, one of the founders of Mago. With my co-founder Alex (creator of Warpfusion, open source video to video), we built an open…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T18:49:44+00:00 (79h ago)
80. [I published my first practical Excel finance eBook with 20 downloadable workbooks](https://www.reddit.com/r/SideProject/comments/1xls68k/i_published_my_first_practical_excel_finance/)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hi everyone! I've recently published my first eBook, Excel for Your First Finance Job , as a side project. I have a background in…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-11-02T08:53:55+00:00 (89h ago)
81. [Ask HN: Advise on monetization model for my freemium app wanted](https://news.ycombinator.com/item?id=50280505)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: I'm an indie app dev and looking for some conceptual help with one of my freemium apps. I'm thinking about completely restructuring the…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-28T20:34:28+00:00 (198h ago)
82. [Show HN: Shop via CLI; for agents and software engineers](https://news.ycombinator.com/item?id=50264240)
   - Kind: asset
   - Score: 40/100
   - Cost: not published
   - Owner must do: nothing
   - Why: Hello HN! We're building a single search/browse API interface to thousands of ecommerce stores (hopefully, eventually, all of them).…
   - Next: Check the free tier's real limits, then use it to build or promote the product without adding a per-user cost.
   - Posted: 2026-10-27T19:12:20+00:00 (223h ago)
