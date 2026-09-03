# Recurring Revenue (MRR) Idea Triage

Refreshed: 2026-09-03T21:49:58.478685+00:00

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

For a stack that can only research, write, and publish to dev.to, the most honest recurring-revenue angle is a paid newsletter on a single narrow technical topic where the audience already gathers on dev.to itself. The bot can publish free articles to build a byline and a niche audience; the owner has to do everything else by hand, including opening a payment account, putting a paid tier behind a link, and convincing readers to subscribe. This works only if the owner already has readers in that niche or joins a dev.to tag and posts there by hand; it cannot conjure subscribers from nothing.

## Ranked Ideas

### Paid newsletter

- **Niche:** Weekly debugging notes for engineers stuck on flaky Playwright CI runs on GitHub Actions free tier.
- **Who pays:** A backend or QA engineer at a seed-to-Series-B startup who runs Playwright in CI and keeps losing hours to flake on the free GitHub Actions tier.
- **Monthly price:** 10
- **Why this stack fits:** The dev.to publish surface is literally where developer newsletters get discovered; the bot can draft each issue, but payment and subscription mechanics are entirely the owner's manual job.
- **First proof artifact:** Three free public dev.to articles in that exact niche, each ending with one question for readers, published on a fixed weekday so a habit forms.
- **Runway to first dollar:** 4-8 weeks, gated entirely by how fast the owner can build a tagged following on dev.to by hand
- **You must do by hand:** Open a paid subscription product on a platform the owner picks (Gumroad, Substack, or Stripe + a landing page the owner builds by hand), paste the subscribe link into each free article by hand, manually reply to anyone who comments, and manually promote the tag the articles live under; the bot will 

### Notion / digital template store

- **Niche:** Notion incident-response runbooks for SRE on-call rotations at startups without a dedicated incident tool.
- **Who pays:** An SRE or tech lead at a 20-100 person startup whose on-call rotation still lives in a shared Google Doc.
- **Monthly price:** 9
- **Why this stack fits:** The bot can draft template content and supporting articles, but selling any template library requires a storefront and a payment account that the owner has to set up by hand, and templates are commodity goods with thin differentiation unless the niche is razor-sharp.
- **First proof artifact:** One free Notion template exported as a public read-only link, plus one dev.to article walking through how to fork it for a specific stack (e.g. a Node + Postgres service).
- **Runway to first dollar:** 6-12 weeks, because the owner must build the storefront and prove the template's value before any subscription makes sense
- **You must do by hand:** Open a Gumroad or Lemon Squeezy subscription product by hand, upload the template files by hand, write the sales page by hand, and add the link to the dev.to article by hand; the bot cannot take payment, cannot deliver files, and cannot follow up with prospects.


## Set Up By Hand First

None of these is a blocker — but no money moves until you do them.

- **Paid newsletter:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API); needs an existing audience; the dev.to byline is the only one this stack builds
- **Notion / digital template store:** owner opens a payment/subscription account by hand (Gumroad, Substack, Stripe); owner opens the storefront or channel by hand (Gumroad products can then be created/updated via its API)

## How To Validate Without Outreach

- Publish a free dev.to article in the exact niche and end it with one concrete question (e.g. 'What does your flaky-test triage checklist look like?') so readers reply on dev.to itself, which is inbound and does not require cold outreach.
- Post one short comment thread by hand on three older high-traffic dev.to articles in the same tag, leaving a useful reply and the author's new article link in the bio, not as spam, so the tag community notices the byline.
- Watch the dev.to tag's RSS feed for the niche and note which post titles consistently get comments; these are the topics the next free issues should cover, and they also reveal the actual reader vocabulary to use.
- Join a relevant open Slack or Discord the owner already belongs to and read for two weeks without posting a pitch; the recurring complaints observed there are the validation signal, and any reply is still inbound.

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

1. Pick one niche from above and commit to one free dev.to article per week for eight weeks, all in the same tag, before thinking about charging anyone.
2. After three articles are live, open a Gumroad account by hand, create one $10/mo subscription product titled exactly like the newsletter, and copy the link into each article's author bio by hand.
3. Reply by hand, within 24 hours, to every comment on every article; this is the only audience-building motion the stack actually allows.
4. Set up a UptimeRobot or cron-free GitHub Action ping that emails the owner if a scheduled publish job fails, because losing a weekly slot breaks the habit the model depends on.
5. Track in a plain text file: article URL, publish date, comment count, and any inbound email; use this to decide after eight weeks whether the niche has real demand before paying for any tooling.
