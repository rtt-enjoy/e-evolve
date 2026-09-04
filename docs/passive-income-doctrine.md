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

**Built is not the same as live, and that cost another five cycles.** The footer
shipped complete and tested on 2026-09-03 with `payout.enabled: false`, which was
the right default — it publishes under the owner's byline. But the doctrine's own
checklist then read `payout.live: false` for cycles #1755–#1759, and every article
published in that window still carried no ask. The structural zero had been
*fixed in code and left switched off*, which looks identical in the earnings
figures to never having built it.

The lesson generalises past this feature: **an opt-in earning path is not an
earning path until someone opts in.** `blocked_reason` existed precisely to make
that visible, and it said so plainly the whole time. Enabled on 2026-09-04, by
owner decision.

- **Check `payout.live`, not whether the module exists.** Checklist step 1 is
  worded that way on purpose.

**This is a baseline, not a ceiling.** Tips from a developer audience are
low-conversion by nature. The point is that the multiplier is no longer zero, so
reach work now has somewhere to land.

---

## Principle 3b — A masked address on a tip surface is still a structural zero

The dashboard row of the channel table was built on 2026-09-04. `docs/` is
already served publicly by GitHub Pages, the address is already checksum-
validated, and the page is regenerated every cycle — so it needed no new secret,
no owner action, and no policy change, exactly like the article footer.

One decision in it is worth recording, because the obvious implementation is
wrong in a way that fails silently.

`status["payout"]` deliberately carries **only the masked address**
(`TFTNsf…9KbY`), because `status.json` is committed and public and a receive
address has no business appearing in a log line or a research note. The tempting
move is to reuse that field for the dashboard tip box. **A reader cannot pay a
masked address.** A tip box built on it renders complete, looks finished, and
takes nothing — the same structural zero as 1,838 views with no footer, rebuilt
inside the fix for it.

So there are now two fields, and the split is the point:

- `status["payout"]` — the **diagnostic**. Masked. Answers "is the path live,
  and if not why". For the owner.
- `status["payout_public"]` — the **ask**. Full address. Exists only when
  `payout.public_snapshot()` confirms the footer is already publishing that same
  address to dev.to readers, so it never widens exposure beyond what every
  published article already carries. For the reader.

`TestPayoutPublicSnapshot.test_agrees_with_footer_on_whether_path_is_live` pins
the invariant that the two surfaces can never disagree about whether the path is
live.

**The trap that nearly shipped:** `status._secret_names()` treats any env var
whose name contains `WALLET` as a secret, which correctly catches
`USDT_WALLET_ADDRESS` — and would have redacted the tip address to
`[redacted]` on its way into `docs/status.json`. The page would have rendered a
polished tip box containing the word "redacted". `_restore_public_payout`
exempts exactly one field, and `TestPublicAddressSurvivesRedaction` pins that
the exemption stays that narrow: the address is still redacted in `errors`, in
`suggestions`, and everywhere else, and API keys are untouched.

Generalising: **when a field's whole purpose is to be published, redaction is a
bug, not a safeguard — and a redaction bug on a payment surface is invisible,
because the page still looks right.**

---

## Principle 3c — A receive path that only runs on new work skips the audience you already have

Built 2026-09-04, `bot/earning/backfill.py`.

The footer was attached inside `devto.publish`, which is a `POST`. It therefore
ran on new articles and on nothing else. Everything already published — the
posts that had spent months accumulating search traffic — kept exactly the ask
it was published with, which was none.

The numbers made this most of the problem, not an edge case:

| Measure | Value |
| --- | --- |
| Published posts carrying no ask | 11 |
| Views on them | 1,949 |
| Share on a single evergreen post | 1,652 (**85%**) |
| Views a new post adds | ~177 |

So **85% of every reader this project has ever had** was looking at a page with
no way to pay, and daily publishing would need eleven perfect consecutive days
just to match reach that already exists and keeps growing on its own. The
back catalogue is not a historical record; it is the traffic.

Scored on Principle 2 it wins every row — `PUT /api/articles/{id}` takes the
same `DEV_TO_API_KEY` that already publishes and already reads stats, no owner
action, editing our own article is the allowed action, on-chain like every other
tip, and it reuses writing that already exists. It needed no new capability at
all. **It was missed because the fix was filed under "publishing" and the
back catalogue is not published, it *was* published.** When a channel is added,
ask what it covers as well as what it does.

Four rules, each of which is the difference between this being safe to run
unattended and it being a liability:

- **It never edits prose.** The only mutation is appending the same
  deterministic footer `payout` already renders. No LLM call, for a sharper
  version of the reason `payout` has none: the quality gates run on drafts, so
  nothing downstream would catch a model quietly degrading a live post that
  earns real traffic.
- **A body it cannot safely reproduce is skipped.** A dev.to body opening with
  YAML front matter has its title and tags re-read from that block on save, and
  Forem's tag handling *clears the list first*. Nothing this bot publishes uses
  front matter, but "probably not" is not a basis for rewriting the account's
  best post, so those are detected and left alone. Only `body_markdown` is
  sent, so nothing else can be re-asserted from data this bot re-derived.
- **Idempotent, because it runs every hour forever.** `has_footer` is asked
  about the *live* body, not local history, so a hand-edited post is read as it
  actually is. This is also why `has_footer` now matches the configured heading
  and the address, not just the hardcoded default string: `footer()` renders
  `cfg["heading"]` while the check tested only the stock wording, so changing
  `payout.heading` would have made it blind to its own footers — a nuisance on
  the publish path, and on this path a loop appending a second footer to every
  post, every cycle, under the owner's byline.
- **Highest-traffic first**, because the distribution is top-heavy enough that
  the order is most of the value.

**Editing does not re-surface a post.** Forem preserves `published_at` on
update, so this adds an ask to what people already read rather than pushing old
posts back into the feed — it does not game distribution and does not
counterfeit the follow-up path, which deliberately publishes a *new* post.

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

The same blindness applied one stage later. Views were measured; **what happened
after a reader reached the footer was not.** That was acceptable only while no
footer had ever shipped. Once one did, the first tip became the first evidence
this project has ever had about what readers actually pay for — and an
unattributed dollar teaches nothing.

`bot/earning/attribution.py` closes that gap, and the honest limit of it is
worth stating up front: **a TRC-20 transfer carries no memo.** Nobody tips
through a tracked link; they read a post, copy an address, and send from a
wallet this bot cannot see. So per-post attribution is not available, and
building something that claimed it would be Principle 4's fabrication in a new
costume.

What *is* available is the publishing context at the moment money arrived — which
posts were live, which was performing, which archetype and tags they carried.
That is correlation, and it is labelled as such: `confidence` is never better
than `"correlated"`, and `count` rides along with every total so an n=1 receipt
reads as one receipt. Across enough receipts the pattern is real evidence; the
first one is a data point.

The module follows the same rules as the rest of the earning layer:

- **Triggered by the wallet, never by a publish.** A record is written only when
  `wallet.last_received_usd > 0` — i.e. the chain confirmed money moved. Nothing
  in it can invent revenue, because nothing in it decides revenue happened.
- **Deterministic. No LLM call.** A model asked which post earned a tip would
  answer confidently with nothing behind it.
- **Never raises.** It is bookkeeping; losing a cycle over it would trade the
  working system for a note about the working system.

Order of work when revenue is still zero:
1. Make sure a receive path exists on everything published. *(done)*
2. **Confirm it is actually switched on** — `payout.live`, not "the code exists".
   *(done 2026-09-04; it sat built-and-disabled for five cycles)*
3. Publish consistently into the shapes the audience measurably prefers.
4. Only then tune the ask itself.

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
   *Live since 2026-09-04. It read `false` for five cycles after the code
   shipped, because the config flag was still off — so read the flag, not the
   filesystem.*
   **"Everything published" includes what was published before the path
   existed.** Check `status["backfill"].remaining` — while it is non-zero, posts
   that already have readers are still showing them no way to pay. Note that
   `status.json` is written at the *end* of a cycle, so a field can lag a config
   change by one run; the config flag is the truth, the snapshot is the report.
2. **Is money arriving?** Check `earnings.received_total_usd`.
   Once it is non-zero, `status["attribution"]` holds what was live when it
   landed — ranked by archetype and tag, with sample sizes. Read `count` before
   believing any ordering in it.
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
| Wallet address on the public dashboard | none | none | allowed | **Built** 2026-09-04. `status["payout_public"]` + Overview tip card |
| Wallet address on the **back catalogue** | none | none | allowed | **Built** 2026-09-04. `bot/earning/backfill.py` |
| Sponsored-content slot in the newsletter | none | negotiates each deal | allowed to publish | **Deferred.** Income is real but every unit needs a human |
| dev.to → own static site, then ads | ad network account | signup + tax details | allowed | **Deferred.** Needs an account and an audience move |
| Affiliate links in articles | affiliate account | signup per program | allowed to publish | **Deferred.** Also risks the fabrication and tone gates |
| Paid newsletter tier | payment processor | account + KYC | allowed to publish | **Refused for now.** Processor is a hard blocker here |
| Auto-posting affiliate content to social | — | — | **blocked** | **Refused.** Needs a policy change |
| Scraped-lead cold email | — | — | **blocked** | **Refused.** Needs a policy change |
| Trading, minting, yield farming | — | — | **blocked** | **Refused.** Not a content business |

Every row that needs no new secret and no owner action is now built. What remains
on the list needs either an account the owner must open (ad network, affiliate
program, payment processor) or a policy the owner must widen (social posting,
cold email). Those are owner decisions with the tradeoff already stated here,
not work a cycle may take on itself.

**This table said exactly that once before and was wrong.** On 2026-09-04 it
claimed completeness while 85% of the audience — the back catalogue — still had
no ask on it, because the channel had been scored as "wallet address in
published articles" and nobody asked whether that covered posts published
before the code existed. The row was ticked on the mechanism, not the coverage.
Before trusting the sentence above, check `status["backfill"].remaining` and
`status["payout"].live` against reality rather than against this table.

So the next honest task is no longer a channel — it is **reach into a live
receive path**, per Principle 5, step 2: publish consistently into the shapes
the audience measurably prefers, and let `status["attribution"]` accumulate
enough receipts to say which of them earned.

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
