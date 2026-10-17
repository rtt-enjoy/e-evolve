# Passive Income Doctrine

This document is the single source of truth for the earning principles referenced throughout the E-Evolve codebase. It is cited by `bot/earning/attribution.py` (Principle 5) and `bot/earning/backfill.py` (Principle 2).

## Principle 1: Passive income is a product, not a service

Income that requires the owner to perform work per unit is a job, not passive income. Freelance postings, contract work, retainers, consulting, and agency work are explicitly refused. A product that delivers value while nobody is working is the only valid path.

## Principle 2: Rank by owner action per unit of income

Channels are ranked by how little owner action each unit of income needs, not by headline upside. A $5 listing fee paid once beats a $0 channel that demands per-sale owner action. Every cost and every manual setup step is stated out loud; zero budget is the binding constraint.

## Principle 3: Money lands on-chain, in the owner's wallet

Revenue is the on-chain balance only. Listings, views, pipeline, and speculative upside are not revenue. The published Tron (TRC-20) USDT receive address is the canonical receive path. A channel that cannot settle to that address is not a channel this project can use.

## Principle 3f: One address, one meter

A second wallet address is a second meter. Channels that settle only to a different network or asset (e.g. Ethereum ERC-20 only) require a second address and a second meter to earn a cent, and are refused on infrastructure, not on merit.

## Principle 4: State every cost and every manual step

No cost is hidden. No manual setup step is implied. If a figure matters, it is published by the platform or it is not stated. Invented figures are fabrication and are refused in code.

## Principle 5: Measure the funnel, not the last stage

Views are measured, but what happens after a reader reaches the footer is not directly attributable. A TRC-20 transfer carries no memo tying it to an article. Attribution records the publishing context at receipt time (which posts were live, which archetype and tags they carried) and labels it as `correlated`, never as proven. `count` is reported alongside every total so a single receipt is not mistaken for a trend.

## Principle 6: Stay inside policy

No social posting, no trading, no minting, no cold outreach, no yield farming or staking. The bot may research, analyse, draft, and publish articles to dev.to. That is the whole surface.

## Principle 7: Reuse output already produced

The wallet ask is already appended to every published article. The same address belongs on the product page, in the README, and in release notes. Reuse of existing output is preferred over new work.

## Refused patterns

- Selling the owner's hours: freelance, contract, retainers, consulting.
- Anything requiring paid infrastructure, a monthly fee, or a credit-card-gated tier.
- Custodial payment processors that hold the money before the owner does.
- Platforms that are dead, seized, or unverifiable (Sellix, Coinbase Commerce, CoinPayments, kofi.network).
- Anything requiring a large audience, ad spend, or a following the owner does not have.
- Anything promising passive income without a product that delivers something.