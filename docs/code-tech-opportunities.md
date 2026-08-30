# Free AI Earning Queue

Refreshed: 2026-08-30T12:56:23.107318+00:00
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

The strongest current angle is becoming a 'done-for-you AI batch processor' for local small businesses, solopreneurs, and creators: you bundle free-tier APIs (e.g., OpenRouter's no-card models, Groq's free LLM API, and HF Inference) into fixed-price batch jobs like transcription cleanup, PDF-to-structured-data extraction, and background removal for product photos. Buyers pay per batch, you pay nothing upfront, and you can deliver within hours because the heavy lifting runs on someone else's free compute.

## Free AI Services To Use

| Service | What it does | Free tier | Card? | How to earn | Price guide |
| --- | --- | --- | --- | --- | --- |
| Groq Cloud (Free Tier) | Very fast LLM inference (Llama, Mixtral, Gemma) and Whisper speech-to-text | Ongoing free API keys with daily token/minute limits; verify current limit on console.groq.com | no | Offer fast transcript cleanup and meeting-summary batches for $10-25 per hour of audio | $15-30 per deliverable (per hour of audio or per 50-page document) |
| OpenRouter (Free Models) | Unified API to multiple free open-weight LLMs | Several models free with rate limits; verify current model list and daily allowance | no | Resell as a structured-data extractor: turn messy listings/CSV/HTML into clean JSON for $20 per batch | $15-40 per batch job |
| Hugging Face Inference API (Free Tier) | Hosted models for summarization, translation, embeddings, image gen, OCR | Ongoing free monthly credits for inference providers; verify current limit per model | no | Run multilingual summarization or translation batches for e-commerce sellers at $10 per 5,000 words | $10-30 per batch |
| Google Cloud Speech-to-Text (Free Tier) | Audio transcription via API | Free minutes per month for standard models; verify current monthly allowance | no | Transcribe podcasts/interview audio for creators at $1-2 per minute, billed in 30-min chunks | $15-60 per hour of audio |
| remove.bg API (Free Tier) | Background removal from product photos | Ongoing free images per month with API key; verify current monthly cap | no | Batch-clean product photos for Etsy/eBay sellers at $0.50-1 per photo with a $20 minimum order | $20-100 per 50-100 photos |
| OCR.space Free OCR API | Extract text from images and PDFs | Ongoing free monthly requests; verify current monthly cap | no | Convert scanned receipts/invoices/contracts to Excel/CSV for bookkeepers at $5 per 50 pages | $15-40 per job |
| Cohere Trial Free Tier | Embeddings, text generation, rerank API | Free trial keys (verify whether currently ongoing or time-limited in your region) | no | Build a small FAQ/menu search improvement service for Shopify owners, charged per store | $25-75 per store setup |
| Chroma / Qdrant Cloud Free Tier | Hosted vector database for semantic search | Free tier with small storage; verify current GB limit | no | Charge a one-time fee to ingest a small business's docs and configure semantic search | $50-150 per setup |
| Google Translate API (Free Tier via Cloudflare Workers AI or similar) | Machine translation | Workers AI free daily neurons; verify current daily allowance | no | Translate product listings or short documents for sellers at $5 per 1,000 words | $10-30 per batch |
| Replicate (Free Trial / Free CPU) | On-demand inference for many open models (image, audio, LLM) | Free trial credit; CPU endpoints are cheap; verify ongoing free credits | no | Offer custom image generation or upscaling as one-off paid batches | $10-50 per batch |

## Easy Earning Ideas

1. **Batch audio transcription + cleanup**
   - Who pays: Podcasters, journalists, course creators, therapists with recorded sessions
   - Deliverable: Clean transcript (TXT/DOCX) plus a short summary and key-points list per recording
   - Price: 20-60 per hour of audio (bundled in 30-min chunks)
   - Time to first dollar: same day, after posting on Fiverr/Upwork/local Facebook groups
   - Free stack: Groq Whisper + Groq Llama for cleanup
2. **PDF / scanned doc to structured spreadsheet**
   - Who pays: Small bookkeepers, property managers, e-commerce sellers with supplier invoices
   - Deliverable: Excel/CSV file with extracted fields (vendor, date, totals, line items) and a master sheet
   - Price: 15-40 per 50 pages; $5 minimum
   - Time to first dollar: 1-3 days (post in r/slavelabour, Upwork, local biz groups)
   - Free stack: OCR.space + Hugging Face table extraction + Groq for field normalization
3. **Product photo background removal batches**
   - Who pays: Etsy / eBay / Shopify sellers who don't want to learn Photoshop
   - Deliverable: PNG files with transparent backgrounds, resized to their spec (e.g., 2000x2000)
   - Price: 0.50-1 per photo, $20 minimum order
   - Time to first dollar: same day (list in Fiverr gig, post in seller Facebook groups)
   - Free stack: remove.bg free tier + Pillow for resizing
4. **Translate + localize product listings**
   - Who pays: E-commerce sellers expanding to EU/AS markets
   - Deliverable: Translated titles, bullet points, and descriptions for a set of listings, in a CSV ready to upload
   - Price: 10-30 per 100 listings or per 5,000 words
   - Time to first dollar: 2-3 days (post in Amazon seller forums, Fiverr)
   - Free stack: OpenRouter free models + HF translation models + manual spot-check
5. **Meeting notes and action-item pack**
   - Who pays: Small agencies, coaches, remote teams, real estate agents
   - Deliverable: Per meeting: transcript, summary, decisions, action items with owners, sent as a formatted doc
   - Price: 10-25 per meeting; monthly retainer $80-150 for up to 10 meetings
   - Time to first dollar: 1-2 days (pitch to local business networks, Slack/Discord communities)
   - Free stack: Groq Whisper + Groq Llama for structured summary
6. **Setup of a free internal AI assistant (BYO key)**
   - Who pays: Freelancers, copywriters, small agencies who want ChatGPT-like help but with templates
   - Deliverable: Configured open-source chat UI + 20+ prompt templates + SOPs, installed on their machine or a free HF Space
   - Price: 75-200 per setup, plus optional $30/mo maintenance
   - Time to first dollar: 2-5 days (sell via direct outreach in indie/Slack communities)
   - Free stack: Open WebUI on a free HF Space + Ollama or OpenRouter free models
7. **Resume / cover-letter rewrite batches**
   - Who pays: Job seekers, career changers, recent grads
   - Deliverable: Rewritten resume tailored to a specific job ad + matching cover letter, 24h turnaround
   - Price: 25-60 per resume bundle
   - Time to first dollar: same day (Fiverr gig, university Facebook groups)
   - Free stack: OpenRouter free LLM + your own prompt templates
8. **Real-estate listing description packs**
   - Who pays: Independent realtors / property managers
   - Deliverable: Per property: MLS-style description, social captions, 5 image captions, email blast
   - Price: 15-30 per property; $100 monthly retainer for up to 8 listings
   - Time to first dollar: 2-3 days (direct outreach to local realtors)
   - Free stack: OpenRouter free LLM + HF image captioning model

## Next Actions

- Sign up today (no card) for Groq, OpenRouter, Hugging Face, remove.bg, and OCR.space, and save API keys in a single .env file so you can switch providers when one is rate-limited.
- Pick ONE of the eight ideas above, build a tiny demo deliverable (one real example), and post a fixed-price gig on Fiverr or Upwork today — do not build a full site before you have one paid order.
- Write a one-page 'menu' (PDF or Notion page) listing your 3-5 batch services with prices, turnaround, and 'send me files, get results back' wording; share it in 3 relevant Facebook groups, Slack/Discords, and subreddits where your buyers already hang out.
- Create a reusable prompt-and-script kit per service (transcription cleanup, PDF extraction, listing translation) so each new order takes under 60 minutes to deliver, leaving room for margin even at $15 per job.
- Track every order, cost-equivalent (which free API did it use), and turnaround time in a simple spreadsheet; once one service hits 10 orders, raise the price by $5-10 or convert it into a $80-150 monthly retainer for repeat buyers.

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
2. [A licence granting this source away, a check that failed its own rule, and each product against its own competitors](https://github.com/famouslytrill-boop/sonara-os/pull/202)
   - Score: 100/100
   - Value signal: $79.00
   - Why: visible or inferred value around $79.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: A licence granting this source away, a check that failed its own rule, and each product against its own competitors
     Source: github
     URL: https://github.com/famouslytrill-boop/sonara-os/pull/202
     Why this is suitable: visible or inferred value around $79.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: `pnpm run verify:launch` green across **27 commands**. **3,478 tests** passing — 3,101 in the repository across 236 files, plus 221 (serverless CLI), 69 (agentkit), 44 (songsmith) and 43 (AWS emulator) in `tools/`. `server.js` is **3,845 lines** across 117 `lib/` modules and 39 `routes/` modules. 101 migrations, 145 canonical tables, 165 reviewed external repositories.  > **This description is kept current deliberately.** Refreshed again on 26 August 2026, and this time the refresh found the branch's own defect sitting in its own description: the table below said this application **cannot upload a file**, which stopped being true earlier the same day. A claim that quietly stopped holding is exactly what every check on this branch exists to catch, and prose in a pull request has nothing watching it. Earlier narratives are preserved in the commit history and in `docs/SPRINT_LOG.md`, which
   - Owner-reviewed outreach draft:
     Hi, I found your request about "A licence granting this source away, a check that failed its own rule, and each product against its own competitors" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $79.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/famouslytrill-boop/sonara-os/pull/202
3. [Technical Specification: AI Agent Bot with Token System & Admin CRM](https://github.com/labtgbot/telegram-ai-agent/issues/1)
   - Score: 84/100
   - Value signal: $13.00
   - Why: visible or inferred value around $13.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Technical Specification: AI Agent Bot with Token System & Admin CRM
     Source: github
     URL: https://github.com/labtgbot/telegram-ai-agent/issues/1
     Why this is suitable: visible or inferred value around $13.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: > **Issue Type**: `feature` | **Priority**: `critical` | **Epic**: `telegram-ai-agent-v1`   > **Assignee**: `hive-mind` | **Labels**: `bot`, `tokens`, `crm`, `monetization`, `admin-panel`  ---  ## 🎯 Project Overview  Создание конкурентного продукта на основе **Mira** с внутренней токеновой экономикой, ценообразованием на **50% дешевле** аналогов и профессиональной **CRM-системой** для администрирования.  ### 📊 Competitive Analysis (Mira Pricing)  | Пакет Mira | Stars | Наши цены (-50%) | Экономия | |------------|-------|------------------|----------| | 500 токенов | 500 ⭐ | **250 ⭐** | 250 ⭐ | | 1,200 токенов (-17%) | 1,000 ⭐ | **500 ⭐** | 500 ⭐ | | 2,000 токенов (-25%) | 1,500 ⭐ | **750 ⭐** | 750 ⭐ | | Mira Pro (месяц) | 999 ⭐ (~$13) | **500 ⭐ (~$6.50)** | 499 ⭐ |  ---  ## 🏗️ System Architecture  ```mermaid graph TB     A[Telegram User] --> B[Telegram Bot API]     A --> C[Mini App Inter
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Technical Specification: AI Agent Bot with Token System & Admin CRM" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $13.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/labtgbot/telegram-ai-agent/issues/1
4. [📈 AI Open Source Trends 2026-08-17](https://github.com/xavier9802/agents-radar/issues/361)
   - Score: 76/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: 📈 AI Open Source Trends 2026-08-17
     Source: github
     URL: https://github.com/xavier9802/agents-radar/issues/361
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: # AI Open Source Trends 2026-08-17  > Sources: GitHub Trending + GitHub Search API | Generated: 2026-08-17 01:42 UTC  ---    # AI Open Source Trends Report — August 17, 2026  ---  ## 1. Today's Highlights  The most striking development today is the rapid maturation of **local-first agent infrastructures**: Unsloth, Ollama, and Needle collectively signal that running LLMs on personal hardware is shifting from niche experiment to baseline workflow. The trending list also highlights **Cactus Compute's Needle** — a mere 14 MB foundation model targeting phones, wearables, and robots — which marks a dramatic compression of capability into edge-deployable packages. Meanwhile, the agent ecosystem continues its explosive growth, with tools like Agent-Reach and Claude-Mem demonstrating that the next competitive frontier is **context persistence and web-scale information access**, not just model si
   - Owner-reviewed outreach draft:
     Hi, I found your request about "📈 AI Open Source Trends 2026-08-17" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/xavier9802/agents-radar/issues/361
5. [🔥 GitHub Trending AI 早报 · 2026-07-09 · Top 7 项目](https://github.com/happydog-intj/ai-xiaohongshu-daily/issues/272)
   - Score: 70/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: 🔥 GitHub Trending AI 早报 · 2026-07-09 · Top 7 项目
     Source: github
     URL: https://github.com/happydog-intj/ai-xiaohongshu-daily/issues/272
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: # 🔥 GitHub Trending AI 早报 · 2026.07.09  > 由 GitHub Actions 自动生成 · 数据来源：GitHub Trending（每日榜）  ---  ## 📊 今日 AI 热榜总览  ![trending-summary](https://raw.githubusercontent.com/happydog-intj/ai-xiaohongshu-daily/master/assets/2026-07-09/trending/summary.png)  1. **[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)** · JavaScript · ⭐ 73,993 · 🔺 1,297 stars today    _Production-grade engineering skills for AI coding agents._  2. **[TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)** · TypeScript · ⭐ 7,615 · 🔺 318 stars today    _TencentDB Agent Memory delivers fully local long-term memory for AI Agents via a 4-tier progressive pipeline, with zero external API dependencies._  3. **[mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)** · Python · ⭐ 50,727 · 🔺 352 stars today    _AI agent skill that researches any topi
   - Owner-reviewed outreach draft:
     Hi, I found your request about "🔥 GitHub Trending AI 早报 · 2026-07-09 · Top 7 项目" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/happydog-intj/ai-xiaohongshu-daily/issues/272
