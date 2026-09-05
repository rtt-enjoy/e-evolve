# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-09-05T23:01:12.681970+00:00

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

The only recurring-revenue angle that fits this exact stack is a paid newsletter whose entire funnel is an article on dev.to that converts readers into a paid Substack or Gumroad subscription. The bot can research, draft, and publish the article; the owner opens the subscription account and storefront by hand, since no automation in this stack can accept payment, accept signups via webhook, or run cold outreach. Realistic MRR depends entirely on how many readers the article reaches, and that number must be verified independently before any revenue claim is made. Narrow beats broad: pick one specific developer niche, write one specific article series, and price the subscription low enough that a single satisfied reader will pay for a year without a sales call.

## Ranked Ideas

### Paid newsletter on dev.to, billed via a paid Substack or Gumroad the owner opens by hand

- **Niche:** Solo developers and indie hackers debugging a specific recurring problem, for example "CI pipeline failures on GitHub Actions free tier" or "Postgres query plans for Rails developers."
- **Who pays:** An individual developer or indie hacker who has already read free dev.to content from the byline and wants the next installment delivered weekly without having to check the site.
- **Monthly price:** 5-10
- **Why this stack fits:** The whole deliverable is a written article the bot can publish to dev.to; the paid tier lives on a service the owner provisions once, and no webhook, form, or always-on server is required here.
- **First proof artifact:** One long-form dev.to article (verify length and style independently) that teaches the niche topic end-to-end and ends with a single sentence pointing to the paid Substack or Gumroad for the weekly follow-up.
- **Runway to first dollar:** 4-8 weeks of weekly publishing before any paid subscriber is realistic; expect 0 subscribers for the first 2-3 articles.
- **You must do by hand:** Create the Substack or Gumroad account, set the monthly price, write the landing-page copy, and paste the URL into the dev.to article by hand. The bot cannot create accounts, hold payment credentials, or accept a subscription signup.

### Notion or digital template library billed as a subscription the owner provisions by hand

- **Niche:** One specific template family, for example "Notion bug-tracking templates for solo SaaS founders" or "GitHub Actions workflow templates for Node CLIs."
- **Who pays:** A solo developer or small-team lead who has used one free template, wants the rest, and is willing to pay a small monthly fee for updates.
- **Monthly price:** 5-15
- **Why this stack fits:** The bot can draft the templates and the dev.to article that explains them; the recurring billing and gated download live on a Gumroad or Lemon Squeezy page the owner opens once.
- **First proof artifact:** Three real templates published on dev.to as code samples, each in its own article, so a reader can judge quality before paying for the full library.
- **Runway to first dollar:** 6-12 weeks; templates are easy to copy, so the paid angle only works if updates are visibly shipped each month.
- **You must do by hand:** Open the Gumroad or Lemon Squeezy subscription product, upload the actual template files, set the price, and link to it from the dev.to articles. No part of payment, file hosting, or access control can be automated inside this stack.


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API); needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API)

## How To Validate Without Outreach

- Publish a free dev.to article on the narrow niche that ends with one direct question, for example "What is the specific CI failure you keep hitting on GitHub Actions free tier?", then read every comment by hand and reply by hand to learn what real readers are stuck on.
- Search dev.to, the GitHub Actions docs, and public issue trackers by hand for recurring questions in the niche; compile a list of the 10 most common problems and confirm there are at least 10 people asking each one before assuming a market.
- Post one thread by hand in one community the owner already belongs to (for example a Discord or Slack the owner is already in) asking which of the 10 problems hurts most, and tally the responses by hand. Do not post to communities the owner is not already a member of.
- Cross-check on dev.to by hand how many existing articles already cover this niche and what they charge, if anything, so the price and angle are grounded in what is actually published, not assumed.

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

1. Pick one narrow niche from the two ideas above and write down the single sentence that names the specific buyer and the specific problem, so every later article is judged against it.
2. Open one Gumroad or Substack account by hand, set the monthly price in the 5-15 USD range, and save the public URL; this is the only paid surface the stack will ever link to.
3. Draft and publish the first long-form dev.to article on the niche, ending with the paid URL and one question for readers, and repeat weekly by hand until at least 6 issues are live before judging whether the model works.
4. Keep a hand-written spreadsheet of every dev.to comment, reply, and signup signal so the next article is chosen from evidence, not from guesswork.
5. After 8-12 weeks, count actual subscribers by hand and decide whether to continue, narrow further, or stop; do not scale spend or effort before this number exists.
