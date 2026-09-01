# Free AI Earning Queue

Refreshed: 2026-09-01T14:55:28.470571+00:00
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

The fastest path to first dollar is offering focused, fixed-price AI micro-services where the buyer pays for the output, not the compute. Groq's free LLM API (no credit card, fast inference), AssemblyAI's free speech-to-text tier, Hugging Face's free inference API, ElevenLabs' free TTS tier, Cohere's free embedding tier, and LibreTranslate's open-source translation can each be packaged into deliverables with prices between $5-$50, starting same-day with no upfront spend.

## Free AI Services To Use

| Service | What it does | Free tier | Card? | How to earn | Price guide |
| --- | --- | --- | --- | --- | --- |
| Groq | Fast free LLM inference with Llama 3.1 70B | 14,400 tokens/min, no time limit | no | Resell as a document-cleaning, rewrite, or summarization API | $5-25 per document batch |
| AssemblyAI | Speech-to-text with speaker diarization | verify current limit (3 hours/month typical free tier) | verify (may require signup) | Sell transcribed podcast summaries or meeting notes | $10-30 per hour of audio |
| Hugging Face Inference API | Hosted image generation, OCR, and embedding models | Rate-limited free tier on Spaces and Endpoints | no for Spaces, verify for Endpoints | Bundle image gen or document extraction into a one-page tool | $5-20 per task |
| ElevenLabs | AI voice generation and text-to-speech | 10,000 characters/month free | no | Sell short voiceover clips for videos or audiobooks | $5-15 per 500-word clip |
| Cohere | LLM commands, embeddings, and reranking | Free tier for Command R+ and embeddings, no credit card | no | Build a document Q&A tool and charge per query | $0.05-0.10 per query to client, bundle at $10-30/month |
| LibreTranslate | Open-source machine translation API | Self-host free or use public instances free | no | Sell batch document translation at $0.01-0.05/page | $5-50 per document depending on length |

## Easy Earning Ideas

1. **Audio-to-meeting-notes pipeline**
   - Who pays: Freelancers, small agency owners, researchers
   - Deliverable: Upload MP3, receive cleaned, bullet-pointed notes with action items
   - Price: $15-25 per recording
   - Time to first dollar: same day (announce on LinkedIn, Upwork profile)
   - Free stack: AssemblyAI (transcription) + Groq (summarization)
2. **Resume rewrite service**
   - Who pays: Job seekers needing cover letters or resume rewrites
   - Deliverable: Upload resume + job posting, receive rewritten resume tailored to role
   - Price: $20-40 per resume
   - Time to first dollar: 2-3 days (create a simple landing page or Fiverr gig)
   - Free stack: Groq LLM (rewrite)
3. **YouTube video chapter generator**
   - Who pays: YouTube creators needing auto-generated timestamps and summaries
   - Deliverable: Upload video URL, receive chapter list and short description
   - Price: $5-15 per video
   - Time to first dollar: same day (offer in YouTube creator Facebook groups)
   - Free stack: AssemblyAI or Groq Whisper (transcription) + Groq (structuring)
4. **PDF text-extraction and summary tool**
   - Who pays: Lawyers, researchers, students needing document digestion
   - Deliverable: Upload PDF, receive extracted text and key-point summary
   - Price: $10-30 per document
   - Time to first dollar: 2-3 days (post on Reddit r/regulations, research communities)
   - Free stack: Hugging Face OCR + Groq summarization
5. **Small-business chatbot setup**
   - Who pays: Local shops, clinics, or service businesses wanting a Q&A bot
   - Deliverable: Configure a free-tier AI chatbot on their website with their FAQ data
   - Price: $50-150 one-time setup fee
   - Time to first dollar: 1-2 weeks (cold outreach to local businesses)
   - Free stack: Cohere embeddings + free vector DB (Qdrant) + simple frontend
6. **Batch image background removal**
   - Who pays: E-commerce sellers, photographers needing quick background removal
   - Deliverable: Upload ZIP of images, receive processed images back within 24h
   - Price: $20-50 per batch of 20-50 images
   - Time to first dollar: same day (post in Shopify seller groups)
   - Free stack: Hugging Face Spaces (RemBG or similar free models)

## Next Actions

- 1. Sign up for Groq and AssemblyAI today (no credit card) to test the transcription + summarization pipeline on one real audio file.
- 2. Create a simple single-page offer on Gumroad or a Google Form titled 'Audio to Meeting Notes - $20' and post the link in two relevant online communities.
- 3. Verify Cohere's exact free embedding limits and draft a one-page prompt library for document Q&A that you can sell as a template.
- 4. Pick one earning idea above and spend 2 hours building the minimum viable version: upload button, API call, output display.
- 5. Reach out to 5 potential buyers directly (no audience needed) with the specific deliverable and price before building anything else.

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

- Search online for currently-free AI services first, then have the LLM turn them into concrete earning offers.
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
3. [My domain renewals kept ambushing me in random months, so I built a tracker for everything my side projects cost](https://www.reddit.com/r/SideProject/comments/1w4c0cm/my_domain_renewals_kept_ambushing_me_in_random/)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Clean one messy sample export with the free LLM tier and quote a flat rate per file.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: My domain renewals kept ambushing me in random months, so I built a tracker for everything my side projects cost
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w4c0cm/my_domain_renewals_kept_ambushing_me_in_random/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Clean one messy sample export with the free LLM tier and quote a flat rate per file.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Like probably half this sub, I had a spreadsheet that was supposed to track what my side projects cost me. It was last updated in March. Meanwhile the actual numbers lived in six different tabs. Stripe for revenue, the hosting dashboard, Neon for the database, Cloudflare, GitHub, and a bank statement full of small charges I couldn&#39;t map to anything anymore. The one question I actually cared about, is this project making or losing money , had no single place where it got answered. So I did the cliché thing and built a tool for it. It&#39;s called StackMemo. What it does: You list each project&#39;s services with costs and renewal dates. The annual domain renewal that ambushes you every year now shows up in advance instead It connects to Stripe, GitHub, Neon, Cloudflare and Koyeb and pulls MRR, stars, traffic and so on every hour. Anything else with a JSON API works through a generic H
   - Owner-reviewed outreach draft:
     Hi, I found your request about "My domain renewals kept ambushing me in random months, so I built a tracker for everything my side projects cost" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w4c0cm/my_domain_renewals_kept_ambushing_me_in_random/
4. [Clypy is live on Product Hunt today after months of building across five platforms](https://www.reddit.com/r/SideProject/comments/1w44tju/clypy_is_live_on_product_hunt_today_after_months/)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Clypy is live on Product Hunt today after months of building across five platforms
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w44tju/clypy_is_live_on_product_hunt_today_after_months/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I previously shared Clypy here while it was still being built. Today it is officially live on Product Hunt. Clypy started with a simple problem: I would copy something on one device and need it on another. It has grown into one private, searchable clipboard across Mac, Windows, Linux, iOS, and Android. The finished product includes: • Unlimited local clipboard history • End-to-end encrypted device sync • Semantic search • On-device screenshot OCR • Collections and reusable snippets • Mobile keyboards and widgets • User-approved memory for AI agents through MCP Unlimited local history is free and requires no account. Pro adds the cross-device features through a one-time purchase. Thank you to everyone here who gave feedback during the build. I would now appreciate feedback on the finished product, launch page, and onboarding. Try Clypy: https://clypy.app Product Hunt: https://www.producth
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Clypy is live on Product Hunt today after months of building across five platforms" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w44tju/clypy_is_live_on_product_hunt_today_after_months/
5. [My friend wrote this note to explain my app so it wouldn't look like AI slop.](https://www.reddit.com/r/SideProject/comments/1w4dr6g/my_friend_wrote_this_note_to_explain_my_app_so_it/)
   - Score: 94/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: My friend wrote this note to explain my app so it wouldn't look like AI slop.
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w4dr6g/my_friend_wrote_this_note_to_explain_my_app_so_it/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I&#39;ve been building SpeakoFlow for the past few months. It&#39;s a local, open-source voice assistant that lets you talk to your computer instead of constantly reaching for your keyboard. I actually use it myself. Emails, Slack replies, asking AI questions, drafting things, and regular dictation all go through it. But there was one part I wasn&#39;t really happy with. The speech-to-text worked well, but the cleanup didn&#39;t. If I wanted the kind of dictation cleanup you get from paid cloud services, I either had to wait too long or send my text to a cloud provider. That kind of defeated the point. I wanted SpeakoFlow to be fast, local, and private. So I decided to fine-tune a really small open-weight language model specifically for dictation cleanup. The goal was simple: fix the mistakes and corrections I actually made while speaking, without rewriting everything else. I recently fi
   - Owner-reviewed outreach draft:
     Hi, I found your request about "My friend wrote this note to explain my app so it wouldn't look like AI slop." and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w4dr6g/my_friend_wrote_this_note_to_explain_my_app_so_it/
6. [I launched a one-time-payment alternative to subscription legal doc generators, then found out my paywall had been silently broken for 6 mon](https://www.reddit.com/r/SideProject/comments/1w4d7xx/i_launched_a_onetimepayment_alternative_to/)
   - Score: 90/100
   - Value signal: $24.99
   - Why: visible or inferred value around $24.99; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I launched a one-time-payment alternative to subscription legal doc generators, then found out my paywall had been silently broken for 6 mon
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w4d7xx/i_launched_a_onetimepayment_alternative_to/
     Why this is suitable: visible or inferred value around $24.99; runs on a free AI tier, so input cost is zero and margin is total
     First step: Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Six months ago I shipped PrivacyPage — a generator for privacy policies, terms of service, EULAs, cookie policies, and disclaimers. The angle: tools like Termly and iubenda charge a monthly subscription forever for a document that changes maybe twice a year. Mine is pay-once (₹849 / $9.99 per doc, $24.99 for all five), and your license key gets you free regenerations whenever laws change. Last week I sat down to audit all 6 of my side projects. PrivacyPage is the only one with a paywall. The paywall was broken. So was the AI generation behind it. It had been dead for months — every person who tried to pay me hit a wall, and I had no error reporting, so I never knew. I rebuilt the entire money path in one day: payment (Razorpay, geo-priced INR/USD), license key issuance, entitlement checks, generation. Then I added the monitoring I should have had from day one. Also shipped today: an open
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I launched a one-time-payment alternative to subscription legal doc generators, then found out my paywall had been silently broken for 6 mon" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $24.99 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w4d7xx/i_launched_a_onetimepayment_alternative_to/
7. [🤖 AI Agent 每周速递 — 2026-08-17](https://github.com/jojowadaxi/ai-agent-trending/issues/19)
   - Score: 86/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: 🤖 AI Agent 每周速递 — 2026-08-17
     Source: github
     URL: https://github.com/jojowadaxi/ai-agent-trending/issues/19
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: # 🤖 AI Agent Trending — 2026-08-17  每周自动抓取 GitHub 上与 AI Agent 相关的热门/新晋项目。  ## Topic: `ai-agent` (按 Stars 排序)  | # | 仓库 | Stars | 语言 | 最近更新 | 简介 | |---|------|-------|------|----------|------| | 1 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | ⭐ 231,554 | Python | 2026-08-17 | The agent that grows with you | | 2 | [shareAI-lab/learn-claude-code](https://github.com/shareAI-lab/learn-claude-code) | ⭐ 74,394 | Python | 2026-08-16 | Bash is all you need -  A nano claude code–like 「agent harness」, built from 0 to 1 | | 3 | [thedaviddias/Front-End-Checklist](https://github.com/thedaviddias/Front-End-Checklist) | ⭐ 73,540 | MDX | 2026-08-14 | 🗂 The essential checklist for modern web development, for humans and AI agents | | 4 | [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach) | ⭐ 72,325 | Python | 2026-08-12 | Give your AI agent eyes to see the
   - Owner-reviewed outreach draft:
     Hi, I found your request about "🤖 AI Agent 每周速递 — 2026-08-17" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://github.com/jojowadaxi/ai-agent-trending/issues/19
8. [API to extract data from tiktok, instagram and facebook posts (plus 50+ other platforms)](https://www.reddit.com/r/SideProject/comments/1w46ccl/api_to_extract_data_from_tiktok_instagram_and/)
   - Score: 86/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: API to extract data from tiktok, instagram and facebook posts (plus 50+ other platforms)
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w46ccl/api_to_extract_data_from_tiktok_instagram_and/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I&#39;m launching Post Reef, an API to extract data from tiktok/instagram/facebook/any website posts and videos. As of now, we extracted data from 51 different platforms. You POST a URL and out comes structured data (JSON). You can extract any sort of data from it, just create your own schema or use one of our own predefined ones. It uses AI to analyse video, transcript, comments, images and captions. I made this product because I use it on another product, cliprecipe, to extract recipes from social media videos. So yes, I&#39;m the first customer! And it works great. If you don&#39;t want to use the AI extraction, you can still just download the assets (images, videos and text elements) and it costs less credits (cheaper). I think this can be useful if: You are building a nutrition, meal planing or recipe app If you want to save automatically trip ideas from a bunch of tiktok videos If
   - Owner-reviewed outreach draft:
     Hi, I found your request about "API to extract data from tiktok, instagram and facebook posts (plus 50+ other platforms)" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w46ccl/api_to_extract_data_from_tiktok_instagram_and/
