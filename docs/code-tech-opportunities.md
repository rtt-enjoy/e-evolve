# Free AI Earning Queue

Refreshed: 2026-08-08T05:56:53.824230+00:00
Daily target: $10.00

Suggestions favour free AI services and free AI APIs with zero upfront cost.

## Requirements

- Lead with free AI services and free AI APIs: no credit card, generous free tier, usable today.
- Every suggestion must name the free service, its real limits, and one concrete way to earn with it.
- Prefer easy money: something the owner can start in under 2 hours with no upfront spend.
- Prefer repeatable offers over one-off tasks, and same-week payout over deferred upside.
- State the earning path in plain language: who pays, for what, and roughly how much.
- Skip anything needing paid infrastructure, approval queues, or an audience the owner lacks.
- Do not count discovery or speculative upside as earnings.

## Current Best Angle

The strongest immediate angle is reselling free-tier AI APIs as fixed-price micro-services (transcription, summarization, background removal, OCR) to small businesses and creators who need the output but don't want to wrangle API keys, rate limits, or prompt engineering. All services below have genuine ongoing free tiers; most require no credit card. Each idea can be listed on Fiverr, Upwork, or a simple Gumroad page in under two hours with zero spend.

## Free AI Services To Use

| Service | What it does | Free tier | Card? | How to earn | Price guide |
| --- | --- | --- | --- | --- | --- |
| Groq API | Ultra-fast LLM inference (Llama 3, Mixtral, Gemma) via OpenAI-compatible endpoint | 14,400 requests/day, 30K tokens/min on most models; verify current limit | no | Sell 500-word article summaries or email drafts delivered in a Google Doc within 15 minutes | $3–$5 per item |
| Google AI Studio (Gemini 1.5 Flash) | Multimodal LLM with 1M token context, text/image/video/audio input | 1,500 requests/day, 1M tokens/min; verify current limit | no | Turn long YouTube transcripts or meeting recordings into structured notes/action-items | $8–$15 per hour of source material |
| AssemblyAI | Speech-to-text with speaker diarization, punctuation, profanity filter | 100 hours/month free (Core transcription); verify current limit | no | Deliver clean, speaker-labeled transcripts for podcasters/coaches as .txt + .srt | $0.50–$1 per audio minute |
| ElevenLabs API | High-quality text-to-speech, 29 languages, voice cloning | 10,000 characters/month (~10 min audio); verify current limit | no | Produce short voiceovers for Reels/TikTok/ads using client's script and a stock voice | $5–$10 per 60-second clip |
| Remove.bg API | Automatic background removal for images | 50 free credits/month (1 credit = 1 image up to 0.25 MP); verify current limit | no | Batch-remove backgrounds for Etsy/Shopify sellers' product photos, deliver PNGs | $0.25–$0.50 per image (min batch 20) |
| Tesseract OCR (local) / OCR.space API | Extract text from scanned PDFs, photos, screenshots | OCR.space: 25,000 requests/month free; Tesseract: unlimited local | no | Convert stacks of scanned receipts/invoices into CSV/Excel for bookkeepers | $10–$20 per 100 pages |
| Hugging Face Inference API | Hosted inference for 100k+ open models (embeddings, classification, generation) | 30,000 requests/month on shared infrastructure; verify current limit | no | Run sentiment analysis or topic tagging on customer feedback CSVs, return tagged file | $15–$25 per 1,000 rows |
| Cloudflare Workers AI | Serverless GPU inference (Llama, Whisper, Stable Diffusion, embeddings) at edge | 100,000 requests/day free across all models; verify current limit | no | Deploy a one-page tool (e.g., 'paste text → get blog outline') and sell access via Gumroad | $7–$12 one-time per tool |
| Supabase (pgvector) | PostgreSQL + vector search + auth + edge functions, generous free tier | 500 MB database, 2 GB bandwidth, 50 MB file storage; verify current limit | no | Build a 'chat with your PDF' prototype for a client using their free Supabase project | $150–$300 fixed setup fee |
| GitHub Models | Free playground + API for GPT-4o, Llama 3.1, Phi-3, Mistral via GitHub token | Rate-limited free access for personal use; verify current limit | no | Sell a 'prompt pack + setup guide' so clients run the model in their own GitHub Codespace | $20–$40 per pack |

## Easy Earning Ideas

1. **Podcast Transcript + Show Notes Package**
   - Who pays: Solo podcasters / small agencies (1–5 shows)
   - Deliverable: Speaker-labeled transcript (.txt, .srt) + 300-word summary + 5 timestamps + 3 quote cards as PNG
   - Price: 25–40 per episode
   - Time to first dollar: same day
   - Free stack: AssemblyAI (transcript) + Groq (summary/quotes) + Canva free (quote cards)
2. **Etsy/Shopify Product Background Removal Batch**
   - Who pays: Handmade sellers with 20–200 SKUs
   - Deliverable: Transparent PNGs (original resolution) delivered via shared Drive folder, naming preserved
   - Price: 0.35 per image (min $10/order)
   - Time to first dollar: same day
   - Free stack: Remove.bg API (50 free/mo) + local Python script for batching
3. **Meeting Recording → Action Items + CRM-ready CSV**
   - Who pays: Consultants, coaches, fractional execs
   - Deliverable: Google Doc with decisions/owners/due-dates + CSV (task, owner, due, priority) for Notion/Asana import
   - Price: 12–18 per hour of recording
   - Time to first dollar: 2–3 days
   - Free stack: Google AI Studio (Gemini 1.5 Flash) for long-context extraction
4. **Scanned Receipts/Invoices → Bookkeeping CSV**
   - Who pays: Freelancers, small biz owners prepping for tax
   - Deliverable: CSV columns: date, vendor, amount, category, tax-deductible (Y/N), source filename
   - Price: 15 per 100 pages
   - Time to first dollar: same day
   - Free stack: OCR.space API (25k free req/mo) + Groq for line-item parsing
5. **One-Page 'Chat With Your PDF' Setup Service**
   - Who pays: Course creators, HR teams, researchers with private docs
   - Deliverable: Working Streamlit/Gradio app deployed on Hugging Face Spaces (free) + 15-min walkthrough video
   - Price: 120–180 fixed
   - Time to first dollar: 2–3 days
   - Free stack: Hugging Face Spaces (free hosting) + sentence-transformers embeddings + Groq LLM
6. **Short-Form Voiceover Pack for Content Creators**
   - Who pays: Faceless YouTube/TikTok/Reels channels
   - Deliverable: 5 × 60-sec MP3s (intro, hook, body, CTA, outro) in chosen voice, commercial license
   - Price: 30–45 per pack
   - Time to first dollar: same day
   - Free stack: ElevenLabs free tier (10k chars ≈ 5 mins) + Audacity for cleanup
7. **Customer Feedback Sentiment & Theme Report**
   - Who pays: SaaS founders, product managers with <5k responses
   - Deliverable: PDF: overall sentiment %, top 5 themes with verbatim quotes, priority matrix chart
   - Price: 40–60 per 1,000 responses
   - Time to first dollar: 2–3 days
   - Free stack: Hugging Face Inference API (sentiment + zero-shot classification) + Python matplotlib

## Next Actions

- Pick ONE idea above, create a Fiverr/Upwork/Gumroad listing tonight with exact deliverable, price, and 24-hr turnaround promise.
- Sign up for the 2–3 free APIs that idea needs (no credit card); run 3 test jobs end-to-end to confirm quality and latency.
- Build a 1-page Notion/Google Site portfolio with 'before/after' samples (redacted) and a Calendly link for discovery calls.
- Post the offer in 3 relevant Facebook/Reddit/Discord communities where buyers already ask for this work (e.g., r/podcasting, Etsy seller groups).
- After first 3 paid jobs, document the exact workflow into a checklist/template so delivery stays under 30 minutes per unit.

## Monetization Patterns

- Resell a free API as a tiny fixed-price service (transcribe, summarize, clean, convert).
- Sell the setup, not the compute: charge to configure a free AI tool inside someone's workflow.
- Bundle a free API into a one-page tool and charge a small one-time fee.
- Offer a done-for-you batch job: send files, get results back, fixed price per batch.
- Charge for the prompt library and workflow, and let the client bring their own free key.
- Package a recurring report built on free-tier APIs as a low-cost monthly retainer.

## Free AI Focus Areas

- free-tier LLM APIs with no credit card requirement
- free speech-to-text, TTS, and transcription APIs
- free image generation and background-removal APIs
- free OCR, document parsing, and PDF extraction APIs
- free embedding and vector-search tiers
- free translation and summarization APIs
- free AI hosting, inference, and scheduled-compute tiers
- open-weight models that run on free CPU/GPU allowances

## Reference Sources

- [OpenRouter free model list](https://openrouter.ai/models?max_price=0): Live list of zero-cost models usable through a single API key. Free (:free) models are capped at 20 req/min and only 50 req/day unless the account has ever purchased $10 in credits (then 1,000/day) -- verify current limit before relying on volume.
- [Google AI Studio (Gemini API)](https://aistudio.google.com/app/apikey): No credit card required. Gemini 2.5 Flash free tier is roughly 1,500 requests/day (10 RPM, 250K TPM); Gemini 2.0 Flash is roughly 15 RPM / 1M TPM. Much higher daily ceiling than OpenRouter's free chain -- verify current limit.
- [Cerebras Cloud free tier](https://cloud.cerebras.ai/): No credit card required. Roughly 1M tokens/day and 14,400 requests/day per model on fast inference hardware. Strong fallback once OpenRouter's free daily cap is hit -- verify current limit.
- [Groq Cloud free tier](https://console.groq.com/): No credit card required. Generous daily request allowance (roughly 14K/day depending on model) with very low latency -- verify current limit.

## Underserved Niches

- free AI APIs with real free tiers that most people have not heard of yet
- boring conversions people pay for: audio to text, image to text, PDF to data
- one-task tools that wrap a single free API and solve one annoyance well
- AI setup help for non-technical owners who cannot configure a key themselves
- batch jobs where the client sends files and gets clean output back
- recurring reports assembled from free-tier APIs on a schedule
- prompt libraries and workflows sold as a template, client brings their own free key
- small-business tasks still done by hand that a free AI API removes entirely
- niches where the buyer values the result and never asks what model produced it

## Strategy Playbook

- Search online for currently-free AI services first, then have Kimi K3 turn them into concrete earning offers.
- Sell the outcome, not the technology. Buyers pay for clean output, not for an API name.
- Keep input cost at zero: free API, free hosting, free scheduler. Every dollar in is margin.
- Prefer offers the owner can deliver the same day with no upfront spend.
- Start with one narrow task and a fixed price. Expand scope only after the first payment.
- Let the free tier set the batch size, and price per batch so limits are never a problem.
- Reuse each delivery as a public example that brings the next buyer.

## Avoid

- Anything requiring paid infrastructure, credit-card-gated tiers, or upfront spend.
- Services whose free tier is a short trial rather than an ongoing allowance.
- Offers needing a large audience, ad spend, or a following the owner does not have.
- Vague 'AI consulting' with no specific deliverable, fixed price, or named buyer.
- Reselling an API in a way its terms of service forbid.
- Bounty and prize hunting where many contributors compete for low-value visibility.
- Crypto/NFT hype work and anything promising passive income without delivery.

## Ranked Leads From Online Search

1. [feat: AI Project - MemoryAI: Memory-Enhanced AI Agents Platform (Issue #1086)](https://github.com/ava-agent/awesome-ai-ideas/pull/1379)
   - Score: 100/100
   - Value signal: $960.00
   - Why: visible or inferred value around $960.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: feat: AI Project - MemoryAI: Memory-Enhanced AI Agents Platform (Issue #1086)
     Source: github
     URL: https://github.com/ava-agent/awesome-ai-ideas/pull/1379
     Why this is suitable: visible or inferred value around $960.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: # feat: MemoryAI - Memory-Enhanced AI Agents with Dual-Trace Architecture (Issue #1086)  > **Source**: Issue #1086 > **Status**: Executive PR Document | v1.0  ---  ## 📋 Executive Summary  MemoryAI is an open-source AI agent platform introducing a **Dual-Trace Memory Architecture** — combining episodic memory (raw interaction logs with embeddings) and semantic memory (compressed knowledge graphs) — to give AI agents persistent, evolving context. Current LLM-based agents lose all context between sessions, leading to repetitive conversations, forgotten user preferences, and inability to learn from past interactions. MemoryAI solves this by providing a plug-and-play memory layer that reduces hallucination by 40%, improves task completion rates by 35%, and enables agents to genuinely "remember" and improve over time.  ### Key Metrics - **Market**: AI agent infrastructure market projected at $
   - Owner-reviewed outreach draft:
     Hi, I found your request about "feat: AI Project - MemoryAI: Memory-Enhanced AI Agents Platform (Issue #1086)" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $960.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/ava-agent/awesome-ai-ideas/pull/1379
2. [Receiptify - I got tired of being the guy doing receipt math at dinner, so I built a splitter where your friends claim their own items from ](https://www.reddit.com/r/SideProject/comments/1viluob/receiptify_i_got_tired_of_being_the_guy_doing/)
   - Score: 100/100
   - Value signal: $850.00
   - Why: visible or inferred value around $850.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Receiptify - I got tired of being the guy doing receipt math at dinner, so I built a splitter where your friends claim their own items from 
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1viluob/receiptify_i_got_tired_of_being_the_guy_doing/
     Why this is suitable: visible or inferred value around $850.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: every group dinner ended the same way for me. i pay, screenshot the receipt, then spend 20 minutes in my notes app trying to remember whether dan had two cocktails or three. the thing that annoyed me about every splitting app i tried is they all assume the whole table installs the app. half my friends will not do that for one dinner, and honestly they are right. so receiptify works the other way around. you scan the receipt, AI pulls the line items, you send a link. your friends open it in a browser, no account, no download, and tap what they had. tax and tip split proportionally across whatever each person claimed, and there is a running tab per person for the ones you eat with constantly. stack is expo + supabase, gpt-4o-mini for the OCR. the bug that nearly killed it: OCR reads $8.50 as $850 roughly 1 in 200 receipts. an app that occasionally tells your friend he owes $850 for a burri
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Receiptify - I got tired of being the guy doing receipt math at dinner, so I built a splitter where your friends claim their own items from " and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $850.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1viluob/receiptify_i_got_tired_of_being_the_guy_doing/
3. [I was tired of using 5+ tools to manage my Instagram so I created 1 tool that does everything in way less, and does it way better](https://www.reddit.com/r/SideProject/comments/1vhcb06/i_was_tired_of_using_5_tools_to_manage_my/)
   - Score: 100/100
   - Value signal: $249.00
   - Why: visible or inferred value around $249.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Process a handful of sample photos on the free image tier and offer a per-image or per-batch rate.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I was tired of using 5+ tools to manage my Instagram so I created 1 tool that does everything in way less, and does it way better
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1vhcb06/i_was_tired_of_using_5_tools_to_manage_my/
     Why this is suitable: visible or inferred value around $249.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Process a handful of sample photos on the free image tier and offer a per-image or per-batch rate.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: The All-in-one instagram growth platform is now available to subscribe and out of the beta phase. Reeldrop.io is now a meta approved tech provider! What that means? it means we are using official Meta APIs as per their terms and conditions, and usage of services underlying in their policies. You don&#39;t have to worry about getting your account banned by using ReelDrop. What makes ReelDrop different from other Instagram tools in the market? &gt; It&#39;s an all-in-one Instagram tool, you get DM automation, a carousel builder, a caption, hashtag, thumbnail generator, scheduler, and publisher, and everything is built in. &gt; The features that no other product has, like other market leaders like Manychat and SuperProfile these are amazing tools. I have used them in the past, but there were some issues that I have faced personally as a content creator, so I fixed those issues with ReelDrop
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I was tired of using 5+ tools to manage my Instagram so I created 1 tool that does everything in way less, and does it way better" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $249.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1vhcb06/i_was_tired_of_using_5_tools_to_manage_my/
4. [ShipKit - Bun + Elysia + Next.js 16 SaaS boilerplate, 11 apps shipped on it](https://www.reddit.com/r/SideProject/comments/1viltc9/shipkit_bun_elysia_nextjs_16_saas_boilerplate_11/)
   - Score: 100/100
   - Value signal: $149.00
   - Why: visible or inferred value around $149.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: ShipKit - Bun + Elysia + Next.js 16 SaaS boilerplate, 11 apps shipped on it
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1viltc9/shipkit_bun_elysia_nextjs_16_saas_boilerplate_11/
     Why this is suitable: visible or inferred value around $149.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I build client SaaS for a living, and every project started the same way: three or four weeks rebuilding auth, payments, admin and email before touching the actual product. So I extracted all of it into one monorepo and kept using it. Stack: Bun + Elysia.js API + Next.js 16 web + Postgres/Drizzle + Better Auth + Polar payments + Redis, plus a separate admin app with RBAC and a setup CLI. 7 apps, 17 packages, 68 UI components. What makes it not a demo: eleven apps have shipped on it, and four are written up with the exact package diff against the boilerplate, so you can see what each app had to build itself and which of those additions later landed in the box. runmate.net — AI running coach on top of Strava history astervis.io — licensing platform vgr.uz — e-commerce with its own courier app provaqt.com — payroll and time tracking Honest numbers, since this sub tends to like them: 4 sales
   - Owner-reviewed outreach draft:
     Hi, I found your request about "ShipKit - Bun + Elysia + Next.js 16 SaaS boilerplate, 11 apps shipped on it" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $149.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1viltc9/shipkit_bun_elysia_nextjs_16_saas_boilerplate_11/
5. [🚨 P0: Launch ADA SaaS Container — Self-Hosted OpenClaw + GitHub (Founder Decision)](https://github.com/ishan190425/autonomous-dev-agents/issues/155)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: 🚨 P0: Launch ADA SaaS Container — Self-Hosted OpenClaw + GitHub (Founder Decision)
     Source: github
     URL: https://github.com/ishan190425/autonomous-dev-agents/issues/155
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Founder Decision — Ship ASAP  This is the priority. Build a containerized ADA SaaS that:  1. **Sets up OpenClaw + GitHub integration automatically** 2. **Enables ADA autostart** to work on its own repo (dogfooding) 3. **Configures read/write role permissions** for safe operation 4. **Frontend website with paywall** for users to sign up and pay  ---  ## Phase 1: Container Infrastructure  A single Docker container that anyone can deploy to get: - OpenClaw gateway running - GitHub App or PAT configured - ADA dispatch cron running automatically - Role-based permissions (read-only vs read-write)  ### Container Contents - `openclaw` gateway (configured) - `@ada-ai/cli` installed - GitHub integration (App or PAT) - Cron scheduler for dispatch cycles - Environment-based configuration  ### Configuration ```yaml # docker-compose.yml or env vars GITHUB_TOKEN: xxx           # or GitHub App creden
   - Owner-reviewed outreach draft:
     Hi, I found your request about "🚨 P0: Launch ADA SaaS Container — Self-Hosted OpenClaw + GitHub (Founder Decision)" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/ishan190425/autonomous-dev-agents/issues/155
6. [Starboard weekly repo digest - 2026-07-27](https://github.com/Codevetter/starboard/issues/32)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Starboard weekly repo digest - 2026-07-27
     Source: github
     URL: https://github.com/Codevetter/starboard/issues/32
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Weekly repo discovery digest for the last 7 days.  Generated: 2026-07-27 UTC Threshold crossings: 86  ## Corpus snapshot  - 5,000+ stars: 12,283 repos - 10,000+ stars: 5,422 repos - 20,000+ stars: 2,196 repos - 50,000+ stars: 464 repos - 100,000+ stars: 119 repos  ### Top repos in corpus  - [codecrafters-io/build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) - 531,612 stars - Markdown - Master programming by recreating your favorite technologies from scratch. - [sindresorhus/awesome](https://github.com/sindresorhus/awesome) - 489,106 stars - 😎 Awesome lists about all kinds of interesting topics - [freeCodeCamp/freeCodeCamp](https://github.com/freeCodeCamp/freeCodeCamp) - 452,833 stars - TypeScript - freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming, and computer science for free. - [public-apis/public-apis](https://github.com/public-apis/p
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Starboard weekly repo digest - 2026-07-27" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/Codevetter/starboard/issues/32
7. [I’m electrician who can’t write single line of code. I built a voice to invoice app. Here’s everything that broke.](https://www.reddit.com/r/SideProject/comments/1viapoz/im_electrician_who_cant_write_single_line_of_code/)
   - Score: 100/100
   - Value signal: $9.99
   - Why: visible or inferred value around $9.99; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I’m electrician who can’t write single line of code. I built a voice to invoice app. Here’s everything that broke.
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1viapoz/im_electrician_who_cant_write_single_line_of_code/
     Why this is suitable: visible or inferred value around $9.99; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I do solar and smart home installs. Most of my invoicing used to happen at 9pm, sitting in the van, thumbs covered in dust, typing into a spreadsheet I hated. So I started building an app where you just talk. “Ran 40 meters of cable at the Novak house, four hours labour, two grand.” It transcribes, parses it into line items, spits out a PDF invoice. Takes about 20 seconds. I can’t code. Everything here was built through AI agents, and honestly the debugging was the actual job. A few of the more stupid things that happened: The transcription kept turning English speech into Cyrillic. Took me two days to work out why. There was Slovak text left in the system prompt, so Whisper decided the audio was probably Slovak too and transliterated everything. “Two grand” parsed as $0. Every single time. The model handled “two thousand dollars” fine but spoken shorthand just fell through. That’s the e
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I’m electrician who can’t write single line of code. I built a voice to invoice app. Here’s everything that broke." and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $9.99 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1viapoz/im_electrician_who_cant_write_single_line_of_code/
8. [🔍 CLI Discovery: 2026-08-07 — 20 candidates found](https://github.com/RealZST/harnesskit-resources/issues/63)
   - Score: 100/100
   - Value signal: $0.00
   - Why: runs on a free AI tier, so input cost is zero and margin is total; boring conversion work buyers already pay humans to do by hand
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: 🔍 CLI Discovery: 2026-08-07 — 20 candidates found
     Source: github
     URL: https://github.com/RealZST/harnesskit-resources/issues/63
     Why this is suitable: runs on a free AI tier, so input cost is zero and margin is total; boring conversion work buyers already pay humans to do by hand
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: ## Agent-first CLI Candidates  Auto-discovered on 2026-08-07. Review each candidate and check the ones to add to `registry.json`.  ### Candidates  #### 1. memU — ⭐ 14268 — Score: 10 - **Repo**: [NevaMind-AI/memU](https://github.com/NevaMind-AI/memU) - **Description**: Personal memory across agents - **Install**: `pip install memu-cli         # library + memu + memu-codex CLIs` - **Signals**: SKILL.md / .skill/ (+3), stars > 100 (+3), active within 6 months (+2), prebuilt binaries (+2) - **README excerpt**: ...Personal memory, stored as Wiki  **Across Sessions. Across Agents. Across Devices.**  [![PyPI version](https://badge.fury.io/py/memu-cli.svg)](https://badge.fury.io/py/memu-cli) [![License: Apache 2....  #### 2. GitNexus — ⭐ 45147 — Score: 7 - **Repo**: [abhigyanpatwari/GitNexus](https://github.com/abhigyanpatwari/GitNexus) - **Description**: GitNexus: The Zero-Server Code Intellige
   - Owner-reviewed outreach draft:
     Hi, I found your request about "🔍 CLI Discovery: 2026-08-07 — 20 candidates found" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/RealZST/harnesskit-resources/issues/63
