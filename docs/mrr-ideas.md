# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-09-07T23:31:01.089940+00:00

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

The single best recurring-revenue angle is a paid newsletter targeting freelance writers who want to monetize their technical expertise, leveraging dev.to as the primary discovery channel and using a simple subscription platform to collect payments manually.

## Ranked Ideas

### Freelance Writer Monetization Newsletter

- **Niche:** Freelance writers seeking to build a secondary income stream from their technical writing skills
- **Who pays:** Freelance writers wanting additional income from their writing expertise
- **Monthly price:** 12-18
- **Why this stack fits:** A newsletter aligns naturally with the dev.to author platform and allows direct monetization through subscriptions without complex product development.
- **First proof artifact:** A 1000-word introductory issue published on dev.to with a clear CTA linking to a landing page offering $10/month or $15/month tiers
- **Runway to first dollar:** 4-8 weeks
- **You must do by hand:** Manually open a Gumroad or Substack subscription account, create the landing page with pricing tiers, and publish the first issue directly from dev.to


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API); needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API)

## How To Validate Without Outreach

- Write a long-form article on dev.to titled 'How Freelance Writers Can Build a Side Income Through Curated Content' ending with a question to spark discussion
- Share that article in relevant communities (r/writing, indie hacker forums, or dev.to comment threads) where you already have visibility, tracking engagement metrics
- Analyze the article's performance (views, comments, shares) for two weeks to identify natural interest signals before launching a paid offer

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

1. Create a simple landing page using a static site generator or structured Google Form to collect email addresses of potential subscribers
2. Draft the first three newsletter issues covering common freelance writer challenges (pricing, client acquisition, workflow optimization)
3. Set up a basic subscription system on Gumroad or Substack by hand, connecting it to your dev.to profile for seamless sharing
4. Publish the first issue within seven days of starting, then dedicate thirty minutes daily to engage with comments and answer questions to build trust
5. Track the conversion rate from reader to subscriber and refine the first deliverable based on feedback received
