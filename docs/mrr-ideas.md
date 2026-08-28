# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-08-28T18:49:24.174219+00:00

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

The only recurring-revenue path that fits a zero‑cost, research‑first stack that can only publish to dev.to is a paid, niche‑focused newsletter where each issue is a polished article the bot drafts and the owner manually distributes; a template‑store model would require a storefront and file delivery that the current stack cannot support without a payment processor or inbound HTTP.

## Ranked Ideas

### Paid newsletter

- **Niche:** Junior backend engineers who need weekly, code‑level guidance on optimizing PostgreSQL query performance in Kubernetes environments
- **Who pays:** Engineering leads at Series‑A SaaS companies who allocate a learning budget for their backend teams
- **Monthly price:** 10-15
- **Why this stack fits:** The bot can research, draft, and publish each issue as a dev.to article; the owner only needs to copy the article into an email and send it by hand.
- **First proof artifact:** A single, complete newsletter issue (≈1500 words) covering one concrete query‑tuning pattern with a runnable SQL snippet
- **Runway to first dollar:** 4-8 weeks
- **You must do by hand:** Open a payment/subscription account on a platform of their choice, collect subscriber emails manually (e.g., via dev.to comments), copy each drafted article into an email client, and send the newsletter each week

### Notion / digital template store

- **Niche:** DevOps engineers who need ready‑to‑apply Helm chart templates for zero‑downtime PostgreSQL upgrades on GKE
- **Who pays:** Platform teams at mid‑size fintech firms that run PostgreSQL on GKE and have a budget for internal tooling
- **Monthly price:** 20-30
- **Why this stack fits:** The bot can draft template documentation and usage guides as dev.to articles, but the store requires a storefront, file hosting, and recurring billing that the stack cannot provide.
- **First proof artifact:** One fully‑tested Helm chart template with a step‑by‑step migration guide published as a dev.to article
- **Runway to first dollar:** 8-12 weeks
- **You must do by hand:** Create a storefront on a payment/subscription platform of their choice, upload the chart files, manage subscription renewals, and deliver updates manually to each buyer


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner creates and maintains the storefront or channel by hand; needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner creates and maintains the storefront or channel by hand

## How To Validate Without Outreach

- Publish a dev.to article that explains the PostgreSQL‑on‑K8s pain point and ends with a single question: “Would you pay $10‑15/mo for a weekly 1500‑word deep‑dive on this topic?”
- Post the same question as a comment thread in the dev.to community you already follow (e.g., #kubernetes #postgresql) and monitor replies
- Join the existing “Kubernetes PostgreSQL Operators” Discord/Slack you already belong to and ask the same question in the #general channel, noting only inbound responses

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

1. Write and publish the validation article on dev.to (bot drafts, owner hits publish)
2. Manually create a payment/subscription account on a platform of your choice and set up a simple subscriber list (e.g., a spreadsheet)
3. Produce the first proof newsletter issue using the bot’s draft, copy it into your email client, and send it to the first 5‑10 addresses you collected from comments
4. Schedule a recurring weekly block (1‑2 hours) to research, let the bot draft, review, and manually send the next issue
5. Track open‑rate and reply‑rate in the spreadsheet; after 4 weeks decide whether to continue, adjust price, or pivot
