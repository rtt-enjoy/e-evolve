# Passive Income Doctrine

This document records the operating principles for E-Evolve's earning layer.
Every module in ``bot/earning/`` is designed to satisfy them. If a proposal
contradicts a principle here, it is refused rather than patched.

## Principle 1 — Measure the funnel, not the last stage

Views are measured. What happens after a reader reaches the footer is not
per-post attributable, because a TRC-20 transfer carries no memo. Attribution
records the publishing context at receipt time (which posts were live, which
archetype was leading) and labels it ``confidence: "correlated"``. A single
receipt is a single receipt; ``count`` is reported alongside every total so no
one receipt is mistaken for a trend.

## Principle 2 — Income must not need the owner per unit

A channel earns while the owner sleeps. The signup is one-time; the sale is
automatic or on-chain. Selling the owner's hours (freelance, contract,
retainer, consulting) is income per unit of work and is a job, not passive
income. It is refused in code.

Six rows test every lead:

1. **owner_action** — does income need the owner, per unit?
2. **receive_path** — can money actually arrive, in the asset already published?
3. **identity_cost** — does earning here require handing over government ID?
4. **zero_budget** — is there a published cost, and is it zero?
5. **setup_burden** — how much owner work before the first dollar?
6. **recency** — is the lead fresh enough to act on?

## Principle 3 — The receive path travels with the artifact

The wallet ask belongs on the product page, in the README, in ``--help``
output, and in the article footer — not only beside the product on a
storefront. A footer attached at publish time missed 85% of readers who were
on the back catalogue; backfill closes that gap for old posts. The same gap
exists for a product: an address printed in ``--help`` travels with every copy.

## Principle 4 — State every cost and every manual setup step out loud

Zero budget is the constraint. A cost of ``0.00`` is real and useful; a missing
cost is ``None`` and forces the UI to admit it does not know. Never estimate
revenue or invent a price. Revenue is the on-chain balance only; listings,
views, and pipeline are not revenue.

## Principle 5 — Measure the funnel, not the last stage

(See Principle 1. This principle is named separately in attribution code.)

## Principle 6 — Refuse what the stack cannot do

No inbound HTTP. No payment processing. No outreach. No social posting. No
trading, minting, yield farming, staking, or airdrops. No custodial payment
processor that holds money before the owner does. No platform that demands KYC
to receive. No dead or seized platform (Sellix, Coinbase Commerce,
CoinPayments). These are refused in code, not negotiated with a model.

## Principle 7 — Build once, distribute forever

Build the product once, then spend every later cycle on distribution rather
than on more product. Keep marginal cost per user at zero: client-side code,
free hosting, free scheduler. Every dollar in is margin. List on the free
channels first; pay a listing fee only where discovery is worth it, and say
what it cost.

## Principle 8 — Price once and leave it

A price that needs renegotiating per buyer is a service in disguise. One-time
licence for a digital download, delivered by the storefront with no owner
action, is the model.

## Source

These principles are applied in ``bot/earning/attribution.py``,
``bot/earning/backfill.py``, ``bot/earning/code_techs.py``, and
``bot/earning/mrr_ideas.py``.