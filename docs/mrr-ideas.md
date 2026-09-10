# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-09-10T00:20:55.641183+00:00

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

The only recurring-revenue model that fits a zero‑cost, research‑first stack that can only publish to dev.to is a narrow‑focus paid newsletter: the bot writes and publishes deep‑dive articles, each ending with a call‑to‑action that drives interested readers to a manually created newsletter on a subscription platform; the owner handles the one‑time account setup and payment linkage, then the article stream becomes the sole acquisition funnel.

## Ranked Ideas

### Paid newsletter

- **Niche:** Mid‑level backend engineers at Series‑A SaaS startups who are designing resilient, observable microservice APIs in Go
- **Who pays:** Engineering leads or senior developers at early‑stage SaaS companies who own API architecture decisions
- **Monthly price:** 10-15
- **Why this stack fits:** The bot can research, draft, and publish long‑form technical articles to dev.to; each article can end with an inbound‑only prompt that funnels readers to a newsletter the owner controls, requiring no outbound outreach or payment automation.
- **First proof artifact:** A free 5‑part email mini‑course (one lesson per week) that walks through designing a production‑ready API gateway, delivered via the newsletter after the first dev.to article
- **Runway to first dollar:** 4-8 weeks
- **You must do by hand:** Open a subscription platform account (e.g., Substack) and connect a payment processor (e.g., Stripe) manually; create the newsletter, import the first subscriber list, and publish the welcome email


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API); needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API)

## How To Validate Without Outreach

- Publish a dev.to article titled "5 Hard Lessons Building Observable Go Microservices" that ends with the question: "Which of these pain points hits your team hardest? Reply in the comments."
- Manually post the same question in the "Go Microservices" Discord channel the owner already belongs to, inviting members to share their struggles.
- Collect the comment threads and Discord replies (inbound only) to confirm at least 10 distinct engineers describe the same API‑gateway design challenges.

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

1. Define the 5‑lesson mini‑course outline and write the first dev.to article with the inbound question.
2. Set up the newsletter on a subscription platform and link a payment processor by hand.
3. Publish the first article on dev.to, share the link in the owner’s existing Discord/Slack communities, and capture comment responses.
4. Deliver the first mini‑course lesson to anyone who subscribes via the newsletter sign‑up form.
5. Iterate: write and publish the next 4 articles, each referencing the previous lesson and ending with a new inbound question to grow the subscriber base.
