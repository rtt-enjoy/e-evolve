# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-08-30T21:08:07.532543+00:00

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

The only honest recurring-revenue fit for a stack that can only research, draft, and publish to dev.to is a tightly-narrowed paid newsletter whose subscription is sold and collected entirely by hand off-platform. The dev.to byline is an audience-building tool, not a revenue tool; the owner funnels readers toward a newsletter signup the bot cannot manage, and payment, list hygiene, and renewals all happen outside the stack. This is a content business with a manual backend, not automation, and revenue depends on a niche narrow enough that a single writer can out-research and out-write the alternatives.

## Ranked Ideas

### Paid newsletter, niche developer audience

- **Niche:** Solo developers or indie hackers building internal tooling in Go or Rust who need a monthly digest of obscure RFC changes, CVEs, and migration pitfalls they can read in 10 minutes.
- **Who pays:** Independent developers or one-person SaaS founders who already pay for one or two newsletters and use Go or Rust in production.
- **Monthly price:** 10-15
- **Why this stack fits:** Publishing articles to dev.to is a real channel; subscriptions and storefronts are owned and run by hand, so no payment or outreach code is required and no constraints are violated.
- **First proof artifact:** One free 1,000-word sample issue published as a dev.to article, plus a hand-built landing page describing the paid cadence, scope, and price.
- **Runway to first dollar:** 6-10 weeks to build a small reading list on dev.to, then a hand-collected first subscriber
- **You must do by hand:** Open the payment or subscription account, maintain the subscriber list by hand, collect renewals by hand, and personally write each issue — no automation here can do any of this.

### Notion or digital template library, very narrow niche

- **Niche:** Incident-postmortem and runbook templates for solo SREs or on-call engineers at small startups running on-call for the first time.
- **Who pays:** Solo SREs, on-call engineers, or DevOps generalists at seed- to Series-A startups who have just inherited on-call duties.
- **Monthly price:** 8-15 per subscriber for a library subscription, paid manually through a storefront the owner runs
- **Why this stack fits:** The bot can draft and structure templates; selling and delivering them happens on a storefront the owner runs by hand, so the stack stays within its limits and no client-acquisition or payment processing is automated.
- **First proof artifact:** Three free runbook and postmortem templates published as a single dev.to article or downloadable PDF, formatted from drafts the bot produces.
- **Runway to first dollar:** 8-14 weeks to validate demand through dev.to readership before charging
- **You must do by hand:** Open and run the template storefront or subscription page, price the library, manage subscribers and access by hand, and curate every template — none of this can be automated inside the stack.


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner creates and maintains the storefront or channel by hand; needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner creates and maintains the storefront or channel by hand

## How To Validate Without Outreach

- Publish a dev.to article that ends with one concrete question and reply to every comment by hand to find who is wrestling with the problem.
- Start or join one existing community the owner already belongs to (a Slack, a Discord, a long-running comment thread on dev.to) and read what people ask about repeatedly without posting or cold-messaging anyone.
- Track which free sample or template gets downloaded or shared the most by hand, using only the analytics dev.to surfaces, to estimate whether a paid audience exists at all.

## Refused, And Why

These are not oversights. Each one needs an action this project refuses in
code, or infrastructure that does not exist here and is not free.

| Model | MRR model | Why not |
|---|---|---|
| Micro SaaS | $15-99/mo subscription | needs a server accepting requests; GitHub Actions is outbound-only |
| Local business AI automation agency | $300-800/mo retainer per client | client acquisition needs cold email/DM — blocked in code; requires a paid third-party platform |
| Online course membership | $49/mo; ~204 members = $10K MRR | fit score 45 is below the 50 threshold for this stack |
| Bookkeeping as a service | $200-600/mo retainer | requires a professional credential the owner does not hold; requires a human performing the service per client; client acquisition needs cold email/DM — blocked in code |
| Social media management retainer | $500-1.5K/mo per client | delivery requires posting to social platforms — blocked in code; client acquisition needs cold email/DM — blocked in code |
| SEO retainer | $400-3K/mo per client | client acquisition needs cold email/DM — blocked in code; requires a human performing the service per client |
| Podcast production service | $500-2K/mo retainer | requires a human performing the service per client; client acquisition needs cold email/DM — blocked in code |
| White-label SaaS reselling | platform markup, $1-6K/mo | requires a paid third-party platform; client acquisition needs cold email/DM — blocked in code |
| Email marketing management retainer | $400-1.2K/mo per client | client acquisition needs cold email/DM — blocked in code; requires a human performing the service per client |
| Paid Discord / Slack community | $15-50/mo per member | delivery requires posting to social platforms — blocked in code |
| No-code app dev for one industry | hosting + maintenance retainer | client acquisition needs cold email/DM — blocked in code; requires a paid third-party platform |
| YouTube automation channel | AdSense + affiliate + memberships | delivery requires posting to social platforms — blocked in code |
| Freelance writing retainer | 4-8 articles/mo, $1.5-8K | client acquisition needs cold email/DM — blocked in code |
| Online tutoring / coaching subscription | $150-500/mo per client | requires a human performing the service per client |
| API or data feed for a niche | recurring API access fee | needs a server accepting requests; GitHub Actions is outbound-only |
| Virtual assistant agency | $500-2K/mo per client | requires a human performing the service per client; client acquisition needs cold email/DM — blocked in code |
| Niche job board / marketplace | $99-499 per posting, recruiter memberships | needs a server accepting requests; GitHub Actions is outbound-only |
| Content repurposing service | $500-1.5K/mo retainer | delivery requires posting to social platforms — blocked in code; client acquisition needs cold email/DM — blocked in code |

## Next Actions

1. Pick the single narrowest niche from the two ideas above and commit to it for 90 days, writing one dev.to article per week by hand.
2. Open the payment or subscription account the owner will use and build the landing page by hand, even before the audience is large.
3. Publish the first proof artifact (sample newsletter issue or free templates) on dev.to and note every reader signal by hand.
4. Reply personally to every comment on every dev.to article to build a small, named reading list without any automation.
5. Re-evaluate after 8-10 weeks whether the hand-collected interest justifies continuing, and stop if it does not.
