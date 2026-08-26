# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-08-26T10:33:27.947490+00:00

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

The only recurring-revenue model that fits a zero‑cost, research‑first stack that can only publish to dev.to is a paid newsletter: the bot writes and publishes articles, the owner manually turns those articles into a weekly email issue, and the owner sets up a simple subscription page (e.g., Substack or Gumroad) by hand to collect $10/mo from individual developers who want curated, niche‑specific technical insights.

## Ranked Ideas

### Paid newsletter

- **Niche:** Go performance optimization for cloud‑native microservices
- **Who pays:** Individual backend engineers (2‑5 years experience) who write Go services on Kubernetes and want a weekly curated tip sheet
- **Monthly price:** 10
- **Why this stack fits:** The bot can produce the exact long‑form content the newsletter needs, and dev.to publishing builds the inbound audience without any outreach or paid ads.
- **First proof artifact:** A 5‑issue sample newsletter published as five dev.to articles, each ending with a subscription call‑to‑action
- **Runway to first dollar:** 6‑10 weeks
- **You must do by hand:** Create and maintain a Substack/Gumroad account, set up the subscription landing page, manually import each dev.to article into the newsletter, manage the subscriber list, and send each weekly issue

### Notion / digital template store

- **Niche:** Ready‑to‑use OpenAPI spec templates for Go gRPC services with CI/CD pipelines
- **Who pays:** Solo Go developers or small teams building new gRPC services who need a compliant OpenAPI contract from day one
- **Monthly price:** 15
- **Why this stack fits:** The bot can draft detailed Notion templates and accompanying documentation, which the owner can then package and sell.
- **First proof artifact:** One complete Notion template (spec file, folder structure, GitHub Actions workflow) published as a dev.to article with a download link
- **Runway to first dollar:** 8‑12 weeks
- **You must do by hand:** Open a Gumroad/Stripe account, create the product listing, upload the Notion template files, handle order fulfillment (manual email with download link), and maintain the storefront


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner creates and maintains the storefront or channel by hand; needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner creates and maintains the storefront or channel by hand

## How To Validate Without Outreach

- Publish a dev.to article titled "5 Go performance traps in Kubernetes" that ends with the question: "Which of these traps hits your service the most? Comment below."
- Monitor the comments for 2 weeks; collect the usernames of developers who describe the same pain points.
- Join the "Go Performance" Discord server you already belong to; post a short summary of the article and ask members if they would pay for a weekly tip sheet.
- Create a simple Google Form (shared only in the article and Discord) asking for email and willingness to pay $10/mo; count responses after 1 week.
- If at least 10 distinct developers express willingness, proceed to set up the subscription page.

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

1. Write and publish the first 5 dev.to articles covering the top Go performance traps, each with a clear subscription CTA.
2. Manually create a Substack newsletter, import the 5 articles as the inaugural issues, and configure the $10/mo paid tier.
3. Add a subscription link to the bottom of every existing and future dev.to article.
4. Each week, manually copy the latest dev.to article into Substack, format it, and send to subscribers.
5. After 4 weeks, review subscriber count and feedback; decide whether to continue, adjust price, or pivot.
