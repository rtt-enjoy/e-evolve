# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-09-08T09:43:11.053731+00:00

Research and suggestions only. This bot does not contact anyone, collect
payment, or host a service. Every figure quoted from the source article
is unverified — check it yourself before acting on it.

## What This Stack Can Actually Support

- Runs on GitHub Actions free tier: hourly, outbound-only, no always-on server.
- No inbound HTTP. Nothing can accept a request, a form, or a webhook.
- No payment processing. Nothing can charge a card or bill a subscription.
- No outreach. Cold email, DMs, and social posting are refused in code.
- Can research, analyse, draft, and publish articles to dev.to. That is the whole surface.

## Best Current Angle

The only recurring-revenue model that fits a zero-cost, research-first, publish-to-dev.to stack with no payment processor, no inbound HTTP, and no outreach is the wallet ask on published work: embed a stablecoin address in each article and invite voluntary recurring tips from readers who value the niche technical content.

## Surviving Models (no LLM brief this refresh)

| Model | MRR model | Bot can | Score |
|---|---|---|---|
| Wallet ask on published work | voluntary stablecoin tips, no platform and no fee | publish | 80 |
| Developer library or plugin with sponsorship | recurring sponsorship on a public repository | draft | 65 |
| Notion / digital template store | $500-5K/mo, library subscription | draft | 60 |
| Freemium browser extension with a paid upgrade | one-time or subscription upgrade; free tier drives discovery | draft | 60 |
| Paid desktop or CLI utility, sold as a download | one-time licence, or a paid major version | draft | 60 |
| Paid newsletter | $10-20/mo per subscriber | publish | 50 |

## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

**On the payout account:** to be paid in stablecoin, pick a storefront
that settles to your own wallet — the Leads page lists the verified
ones. Gumroad, Substack and Stripe are fiat-only and pay out in USD,
so they do not reach the Tron address this project already publishes.

- **Developer library or plugin with sponsorship:** owner opens the storefront or channel by hand, once
- **Notion / digital template store:** owner opens a payout account by hand, once; owner opens the storefront or channel by hand, once
- **Freemium browser extension with a paid upgrade:** owner opens a payout account by hand, once; owner opens the storefront or channel by hand, once
- **Paid desktop or CLI utility, sold as a download:** owner opens a payout account by hand, once; owner opens the storefront or channel by hand, once
- **Paid newsletter:** owner opens a payout account by hand, once; owner opens the storefront or channel by hand, once; needs an existing audience; the dev.to byline is the only one this stack builds

## Refused, And Why

These are not oversights. Each one needs an action this project refuses in
code, or infrastructure that does not exist here and is not free.

| Model | MRR model | Why not |
|---|---|---|
| Micro SaaS | $15-99/mo subscription | needs a server accepting requests; GitHub Actions is outbound-only |
| Local business AI automation agency | $300-800/mo retainer per client | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); client acquisition needs cold email/DM — blocked in code; requires a paid third-party platform |
| Online course membership | $49/mo; ~204 members = $10K MRR | fit score 30 is below the 50 threshold for this stack |
| Bookkeeping as a service | $200-600/mo retainer | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); requires a professional credential the owner does not hold; requires a human performing the service per client; client acquisition needs cold email/DM — blocked in code |
| Social media management retainer | $500-1.5K/mo per client | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); delivery requires posting to social platforms — blocked in code; client acquisition needs cold email/DM — blocked in code |
| SEO retainer | $400-3K/mo per client | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); client acquisition needs cold email/DM — blocked in code; requires a human performing the service per client |
| Podcast production service | $500-2K/mo retainer | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); requires a human performing the service per client; client acquisition needs cold email/DM — blocked in code |
| White-label SaaS reselling | platform markup, $1-6K/mo | requires a paid third-party platform; client acquisition needs cold email/DM — blocked in code |
| Email marketing management retainer | $400-1.2K/mo per client | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); client acquisition needs cold email/DM — blocked in code; requires a human performing the service per client |
| Paid Discord / Slack community | $15-50/mo per member | delivery requires posting to social platforms — blocked in code |
| No-code app dev for one industry | hosting + maintenance retainer | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); client acquisition needs cold email/DM — blocked in code; requires a paid third-party platform |
| YouTube automation channel | AdSense + affiliate + memberships | delivery requires posting to social platforms — blocked in code |
| Freelance writing retainer | 4-8 articles/mo, $1.5-8K | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); client acquisition needs cold email/DM — blocked in code |
| Online tutoring / coaching subscription | $150-500/mo per client | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); requires a human performing the service per client |
| API or data feed for a niche | recurring API access fee | needs a server accepting requests; GitHub Actions is outbound-only |
| Virtual assistant agency | $500-2K/mo per client | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); requires a human performing the service per client; client acquisition needs cold email/DM — blocked in code |
| Niche job board / marketplace | $99-499 per posting, recruiter memberships | needs a server accepting requests; GitHub Actions is outbound-only |
| Content repurposing service | $500-1.5K/mo retainer | revenue is a fee for the owner's hours — a job, not passive income (Principle 2 row 2); delivery requires posting to social platforms — blocked in code; client acquisition needs cold email/DM — blocked in code |
