# Passive-Income Doctrine

**Read this first, every time this system evolves.** It is the standing brief for
what "evolve" means here, and it outranks any local cleverness a cycle proposes.

The goal is a workflow that earns continuously and routes the money to a crypto
wallet, with no human in the loop between the earning and the arrival. Everything
below is written to be applied, not admired.

---

## The finding that produced this document

On 2026-09-03, at cycle #1754, the numbers were:

| Measure | Value |
| --- | --- |
| Cycles run | 1,754 |
| Articles published | 10 |
| Lifetime views | 1,838 |
| Best single post | 1,562 views |
| **Lifetime earnings** | **$0.00** |

The system was not broken. Every module did its job. Articles were researched,
screened, written, gated for quality, and published to a real audience that read
them 1,838 times.

**The audience was never given a way to pay.** `devto.publish` sent a title, a
body, a description, and tags. It sent no address, no link, no ask. The wallet
poller in `status.py` read a balance that nothing on earth was going to change.

The code even documented its own surrender, in a comment that had been true long
enough to stop being questioned:

> `# dev.to pays nothing. Publishing is reach, not revenue`

That is half a sentence. dev.to pays nothing, correct. **dev.to readers can
pay**, and nobody had asked them.

---

## Principle 1 — Reach without a receive path earns exactly zero

This is not a rounding error or a conversion-rate problem. It is a **structural
zero**: no amount of additional reach multiplies into revenue when the multiplier
is absent. 1,838 views times no payment path is $0.00, and so is 1,838,000.

**Every future evolution that improves reach must state where the money enters.**
A cycle that makes articles better, more frequent, better-titled, or better-
targeted, and does not touch the receive path, is optimizing a number that is
being multiplied by zero.

Concretely, before shipping any earning-side change, answer these three:

1. Who pays?
2. Through what mechanism, with no human step in the middle?
3. How does the money reach the wallet, and how do we verify it landed?

If any answer is "eventually" or "the owner would have to", it is not passive
income. It may still be worth building — but log it honestly as reach or
research, not earning.

---

## Principle 2 — Rank channels by what runs unattended, not by upside

The tempting ideas are consistently the ones this stack cannot run. The
`mrr_ideas` module already learned this the expensive way: of twenty
recurring-revenue models it triaged, **eighteen** died on constraints, and the
survivors needed manual setup.

The binding constraints here are real and will not be argued away:

- **No server.** GitHub Actions, hourly, free tier. No inbound HTTP, so nothing
  can receive a webhook, host an endpoint, or serve an app.
- **No payment processor.** No Stripe, no merchant account, no KYC.
- **No outreach.** Cold email and social posting are refused in code, not merely
  unconfigured. This is a policy boundary and widening it needs an explicit
  owner decision.
- **No audience the bot controls.** It publishes to a platform it does not own.

Score a channel on this order, highest first:

| Rank | Property | Why it dominates |
| --- | --- | --- |
| 1 | Needs **no new secret** | A secret the owner must create is a manual step that may never happen |
| 2 | Needs **no owner action** per unit of income | Anything per-transaction is a job, not passive income |
| 3 | Works **within current policy** | A channel needing a policy change is blocked until a human decides |
| 4 | **Verifiable on-chain** | If arrival cannot be confirmed, the number is a guess |
| 5 | Scales with content **already being produced** | Reuses the working half instead of adding a second thing to maintain |

A channel that wins on 1–5 and earns a little beats a channel that would earn a
lot and needs the owner to open an account. The first compounds every cycle. The
second is a TODO.

---

## Principle 3 — The wallet address in the artifact is the baseline channel

Judged by Principle 2, an address printed in the published work wins on every
row. It needs no processor, no account, no policy change, no per-payment action,
and it is verifiable the moment the balance moves. It is also the only channel on
the list that works while the owner is asleep and has never logged in.

This is implemented in `bot/earning/payout.py` and attached in `devto.publish`,
so both products carry it and a future third product cannot ship without it.

Design rules that came out of building it, all of which are load-bearing:

- **Deterministic. Never an LLM call.** A model asked to write a payment footer
  can transpose a character. Money sent to a transposed address is burned. The
  footer is a template because determinism here is a correctness requirement.
- **Validate with a checksum, not a shape.** A regex on
  `^T[1-9A-HJ-NP-Za-km-z]{33}$` accepts an address with two characters swapped,
  and that address belongs to nobody. TRC-20 gets base58check; ERC-20 gets
  EIP-55 when mixed-case. **EIP-55 needs original Keccak-256, and
  `hashlib.sha3_256` is not it** — NIST changed the padding byte, so a check
  built on the stdlib silently rejects every valid checksummed address. That bug
  was written here and caught by the EIP's own test vectors before it shipped.
- **A malformed address publishes no footer.** A post without a footer earns
  nothing; a post with a broken address costs a reader real money. Those are not
  symmetric, so the failure mode is always "omit".
- **Attach after every quality gate.** The footer adds a heading and a fence.
  Attached before the gates it pads the word count and satisfies structural
  checks the draft failed, so a too-thin article publishes on boilerplate. Gates
  judge what the model wrote.
- **Off by default.** It publishes under the owner's byline. They opt in.
- **Do not name an amount.** A figure reads as a price for something already
  given away free, and it caps what a generous reader would have sent.

**This is a baseline, not a ceiling.** Tips from a developer audience are
low-conversion by nature. The point is that the multiplier is no longer zero, so
reach work now has somewhere to land.

---

## Principle 4 — Never let an estimate stand in for money

`devto.publish` reports `estimated_usd: 0.0` for a successful post, and it must
keep doing so even now that the post carries a tip address. The amount is
unknowable at publish time and arrives days later, if at all.

This project already deleted a fabricated per-article constant once. Attributing
a speculative dollar value to a post *because* it carries an address would be the
same lie in a new costume, and it would corrupt the one number that tells the
owner the truth.

**Real revenue is the on-chain balance. Only ever the on-chain balance.**

The corollary is that a wallet at `$0.00` is ambiguous, and ambiguity is a bug.
`$0.00` because nobody tipped, and `$0.00` because no footer was ever published,
demand opposite responses from the owner. So `status["payout"]` records which one
it is (`enabled`, `live`, `blocked_reason`) rather than leaving it to be inferred
from a zero. **Any future channel must report the same distinction.**

---

## Principle 5 — Measure the funnel, not the last stage

The reach loop (`devto_stats`) exists because the bot published blind for
hundreds of cycles. It found that `problem-workaround` articles earn roughly 25x
the engagement of `build-tutorial` — and `build-tutorial` was the most common
thing being published. That single measurement was worth more than any amount of
prompt tuning.

The same blindness now applies one stage later. Views are measured; **what
happens after a reader reaches the footer is not.** Until a tip arrives there is
nothing to measure, which is fine — but the moment revenue is non-zero, the next
evolution should be able to answer: which archetype, which title, which tag
earned it?

Order of work when revenue is still zero:
1. Make sure a receive path exists on everything published. *(done)*
2. Publish consistently into the shapes the audience measurably prefers.
3. Only then tune the ask itself.

Tuning the wording of a footer that has had 40 impressions is noise. This project
has already reverted one over-tightened keyword screen for exactly this reason:
**do not optimize on a sample that cannot support the conclusion.**

---

## Principle 6 — Boundaries are constraints to design within, not obstacles

The blocked list is: social posting, trading, minting, payouts, cold outreach,
commenting on external issues. These are enforced in code and every one of them
is where the "obvious" income ideas lead.

Two source articles have now proposed exactly these routes — auto-posting
affiliate content, scraping leads for cold email, an AI automation agency — and
all were refused and recorded. That refusal record is a feature. It stops each
evolution from rediscovering the same blocked idea and burning a cycle on it.

**The discipline: treat the boundary as the design brief.** The interesting
question is never "how do we get permission to spam" but "what earns inside these
constraints that nobody bothered to build". The wallet footer was sitting inside
the boundary, needing no permission, for 1,754 cycles.

When a genuinely better channel does need a boundary widened, the move is to
**write it down as an owner decision with the tradeoff stated** — not to widen it
in a cycle.

---

## The standing checklist for the next evolution

Work this in order. Stop at the first honest "no".

1. **Is a receive path live on everything published?**
   Check `status["payout"].live`. If `false`, read `blocked_reason` and fix that
   before anything else — every other improvement is being multiplied by zero.
2. **Is money arriving?** Check `earnings.received_total_usd`.
   - Still `$0.00` with a live path → the problem is reach or audience fit, not
     the ask. Go to Principle 5, step 2.
   - Non-zero → start attributing it. Which post, archetype, tag?
3. **Is there an unbuilt channel that wins on Principle 2?**
   Score candidates on the five-row table. Build the one that needs no new
   secret and no owner action. Record the ones you refuse, and why.
4. **Did this cycle improve reach without touching the receive path?**
   That is allowed, but say so plainly in the summary. Do not log it as earning
   work.
5. **Did anything start estimating revenue?** Delete it. On-chain or nothing.

---

## Candidate channels, scored

Kept here so each evolution does not re-derive the same list. Scored against
Principle 2.

| Channel | New secret | Owner action | Policy | Verdict |
| --- | --- | --- | --- | --- |
| Wallet address in published articles | none | none | allowed | **Built.** `bot/earning/payout.py` |
| Wallet address in the newsletter digest | none | none | allowed | **Built** — same `devto.publish` path |
| Wallet address on the public dashboard | none | none | allowed | **Open.** Lowest-effort remaining win; `docs/` is already published |
| Sponsored-content slot in the newsletter | none | negotiates each deal | allowed to publish | **Deferred.** Income is real but every unit needs a human |
| dev.to → own static site, then ads | ad network account | signup + tax details | allowed | **Deferred.** Needs an account and an audience move |
| Affiliate links in articles | affiliate account | signup per program | allowed to publish | **Deferred.** Also risks the fabrication and tone gates |
| Paid newsletter tier | payment processor | account + KYC | allowed to publish | **Refused for now.** Processor is a hard blocker here |
| Auto-posting affiliate content to social | — | — | **blocked** | **Refused.** Needs a policy change |
| Scraped-lead cold email | — | — | **blocked** | **Refused.** Needs a policy change |
| Trading, minting, yield farming | — | — | **blocked** | **Refused.** Not a content business |

The dashboard row is the honest next task: `docs/` is already served publicly by
GitHub Pages, the address is already validated in code, and it needs nothing that
does not exist.

---

## What this document is not

It is not a promise that the wallet fills up. A developer audience tips rarely,
and 1,838 lifetime views is a small sample from which to expect anything.

What changed is narrower and worth stating exactly: **the system now has a
complete path from a reader to the wallet, where before it had two working halves
and a gap.** Reach work compounds into something instead of nothing, and a
`$0.00` balance has become a measurement rather than a foregone conclusion.

Every future evolution should be able to point at which of these six principles
it served.
