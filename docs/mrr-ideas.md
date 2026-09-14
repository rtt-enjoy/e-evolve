# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-09-14T01:16:28.541222+00:00

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

The only recurring-revenue path that fits a zero‑cost, research‑first, publish‑to‑dev.to stack is a paid newsletter that monetises a tightly defined technical niche; the owner writes deep‑dive articles on dev.to, uses them as proof of expertise, and then manually sets up a subscription page (e.g., Gumroad or Substack) to collect $10‑20 per month from solo developers who need curated, actionable guidance on that niche.

## Ranked Ideas

### Paid newsletter

- **Niche:** Solo developers who maintain CI/CD pipelines with GitHub Actions and need weekly, copy‑paste‑ready workflow patterns for Node.js, Python, and Docker projects
- **Who pays:** Individual solo developers or freelance engineers who ship code to production at least weekly and spend >5 hours/week debugging CI
- **Monthly price:** 10-20
- **Why this stack fits:** Articles on dev.to serve as free samples that demonstrate authority; the owner can hand‑craft a subscription landing page without any inbound HTTP or automation.
- **First proof artifact:** A 12‑article series on dev.to titled "GitHub Actions Patterns for Solo Devs" each ending with a one‑question poll about the reader's biggest pipeline pain point
- **Runway to first dollar:** 4-8 weeks
- **You must do by hand:** Create a Gumroad/Substack account, configure a $10‑20 monthly subscription product, and manually copy the subscription link into each dev.to article and the newsletter sign‑up page

### Notion / digital template store

- **Niche:** Freelance frontend developers who need ready‑to‑use Notion project‑tracking dashboards tailored to React/Next.js client work
- **Who pays:** Freelance frontend developers billing $75‑150/hr who manage 3+ concurrent client projects and want a reusable tracking system
- **Monthly price:** 15-30
- **Why this stack fits:** Dev.to articles can showcase template walkthroughs; the owner can later list a Notion template pack on Gumroad, but the storefront and payment must be set up manually.
- **First proof artifact:** A single dev.to article that publishes a complete Notion dashboard template (exported as a public duplicate link) with a step‑by‑step setup guide
- **Runway to first dollar:** 6-10 weeks
- **You must do by hand:** Open a Gumroad account, create a product for the Notion template pack, set a monthly subscription price, and manually embed the purchase link in the dev.to article and any follow‑up posts


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API); needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API)

## How To Validate Without Outreach

- Publish the first proof article on dev.to and end it with a specific question (e.g., "What GitHub Actions pattern wastes the most of your time?")
- Reply to every comment on that article by hand, asking commenters if they would pay for a weekly curated pattern email
- Join the existing dev.to community tags "github-actions" and "ci-cd" and monitor discussions for recurring pain points
- Post a short follow‑up article summarising the top 5 pain points you observed and ask readers to vote on which they’d pay to solve
- Track the number of unique commenters who express willingness to pay; aim for at least 10 distinct voices before building the paid product

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

1. Write and publish the 12‑article "GitHub Actions Patterns for Solo Devs" series on dev.to, each ending with the same targeted question
2. Manually create a Gumroad (or Substack) account and a $15/month subscription product for the newsletter
3. Add the subscription link to the bio and to the bottom of every article in the series
4. Respond to every comment on the series by hand, noting names of developers who signal purchase intent
5. After 4 weeks, compile the top‑voted pain points into a one‑page PDF and send it manually (via email address collected in Gumroad) to the first 10 interested commenters as a free preview
