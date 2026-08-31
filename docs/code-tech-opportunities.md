# Free AI Earning Queue

Refreshed: 2026-08-31T13:55:14.253880+00:00
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

The cleanest current angle is selling tiny done-for-you services (transcription cleanup, meeting notes, PDF data extraction, background removal, translation passes) built on top of free-tier APIs like Groq, Google Gemini, Mistral, OpenRouter, and Hugging Face Inference. Each job is a fixed-price deliverable with a named buyer (local small businesses, freelancers, real-estate agents, Etsy sellers, podcasters), so no audience, ad spend, or paid infrastructure is required, and start-up cost is essentially zero.

## Free AI Services To Use

| Service | What it does | Free tier | Card? | How to earn | Price guide |
| --- | --- | --- | --- | --- | --- |
| Groq Cloud (LLM API) | Very fast LLM inference for Llama, Mixtral, Gemma, Whisper | Free dev tier with rate-limited requests; verify current limit | no | Offer a '1-hour meeting -> clean notes + action items' done-for-you service. | $7-$15 per meeting |
| Google AI Studio / Gemini API | Gemini LLM API with generous free quota | Free tier with RPM/RPD limits; verify current limit | no | Sell a 'messy notes -> structured doc' or email/draft rewrite service. | $5 per rewrite, $10 per structured doc |
| OpenRouter (free model router) | Single API key to call multiple free LLMs (DeepSeek, Qwen, Mistral, Llama) | Several models marked ':free' with daily request caps; verify current limit | no | Build a prompt-routing setup for clients and charge for the configuration + prompts. | $25-$75 setup fee per client |
| Mistral AI (La Plateforme) | Mistral / Mixtral LLM API | Free experimentation tier with limited requests; verify current limit | verify | Run batch summarization of articles or PDFs as a fixed-price job. | $0.10-$0.30 per article, $5 per 20-page PDF |
| Hugging Face Inference API | Hosted models for summarization, translation, embeddings, ASR, TTS, image tasks | Free tier with monthly credit allowance; verify current limit | no | Resell speech-to-text transcription or translation as a fixed-price service. | $0.05-$0.15 per audio minute, $1 per 1k words translated |
| Cohere Trial API | LLM, summarization, embeddings, classification | Trial keys with monthly request allowance; verify current limit | verify | Sell bulk classification/tagging of product reviews or support tickets. | $10 per 1,000 items |
| Google Cloud Speech-to-Text (free tier) | Audio transcription API | Free monthly usage up to a cap; verify current limit | yes | Transcribe podcasts or YouTube audio and sell cleaned transcripts. | $1 per 10 minutes of audio |
| Deepgram (free tier) | Speech-to-text API with diarization | Free monthly credits on signup; verify current limit | yes | Offer 'interview audio -> transcript + summary' to journalists and researchers. | $5 per interview |
| edge-tts (open-source) | Free Microsoft Edge TTS, runs on your machine | Free, no key | no | Generate voiceovers for short videos or IVR prompts as a service. | $3-$8 per finished minute of audio |
| Piper TTS (open-source) | Local neural TTS, runs on CPU | Free, runs locally | no | Produce audiobook-style narration samples for indie authors. | $5 per 1,000 words narrated |

## Easy Earning Ideas

1. **Meeting Notes Cleanup Service**
   - Who pays: Freelancers, consultants, small agency owners, real-estate agents
   - Deliverable: Clean structured notes + action items from a recorded meeting (audio or rough transcript)
   - Price: $7-$15 per meeting
   - Time to first dollar: same day
   - Free stack: Groq Whisper for transcription + Groq LLM or Gemini for structuring
2. **PDF-to-Spreadsheet Extraction**
   - Who pays: Bookkeepers, accountants, property managers, small e-commerce sellers
   - Deliverable: Clean Excel/CSV file extracted from messy PDF invoices, statements, or rent rolls
   - Price: $10-$25 per document batch
   - Time to first dollar: 2-3 days
   - Free stack: Marker/PyMuPDF + Tesseract for parsing, Gemini for structuring, Supabase or local scripts for assembly
3. **Background Removal for Resellers**
   - Who pays: Etsy, eBay, Poshmark, Depop sellers
   - Deliverable: Cleaned product photos with backgrounds removed and optional white background
   - Price: $10 per 50 images
   - Time to first dollar: same day
   - Free stack: rembg running locally, bundled via a small free-hosted tool or simple email intake
4. **Podcast Episode Transcription + Summary**
   - Who pays: Indie podcasters, YouTubers, coaches, course creators
   - Deliverable: Timestamped transcript plus a 5-bullet summary and 3 suggested titles
   - Price: $8-$15 per 30-min episode
   - Time to first dollar: 2-3 days
   - Free stack: OpenAI Whisper via Groq or Hugging Face for ASR, Gemini for summary/titles
5. **Bulk Product Review Tagging**
   - Who pays: Small DTC brands, Amazon FBA sellers, Shopify store owners
   - Deliverable: CSV of customer reviews labeled with topic tags (shipping, quality, fit, etc.) and sentiment
   - Price: $10 per 1,000 reviews
   - Time to first dollar: 3-5 days
   - Free stack: Cohere or OpenRouter free models for classification, Python scripts for batching
6. **Translation Pass for Short Content**
   - Who pays: Indie authors, bloggers, course creators, app developers
   - Deliverable: Clean translation of articles, app store listings, or short marketing copy into EN/ES/FR/DE/JA
   - Price: $1 per 1,000 words
   - Time to first dollar: same day
   - Free stack: Hugging Face translation models or OpenRouter free LLMs, human-style post-editing pass
7. **Resume / Cover Letter Rewrite**
   - Who pays: Job seekers in tech, marketing, and ops
   - Deliverable: Rewritten, ATS-friendly resume tailored to a specific job posting
   - Price: $15-$30 per resume
   - Time to first dollar: 1-3 days
   - Free stack: Gemini or OpenRouter free models with a prompt template you sell as part of the deliverable
8. **Bulk Headshot / Product Stylization**
   - Who pays: Etsy sellers, small Shopify stores, indie game devs
   - Deliverable: 5-10 stylized product or character images in a chosen style
   - Price: $5 per 5-image pack
   - Time to first dollar: same day
   - Free stack: Pollinations.ai or local Stable Diffusion via ComfyUI on Colab free GPU

## Next Actions

- Pick one easy idea (start with meeting notes cleanup or background removal) and post a concrete offer on a local freelancer marketplace or community board today.
- Build a 1-page intake form using a free Google Form or Tally linked to a free-hosted AI tool on Vercel or HF Spaces.
- Test the full pipeline end-to-end with 2-3 sample jobs before publishing, so pricing and turnaround time are realistic.
- Create a fixed-scope, fixed-price listing or DM template that names a specific buyer, a specific deliverable, and a specific price.
- Collect before/after samples (anonymized) into a one-page portfolio so buyers can see the output quality.

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
2. [Two weeks ago I asked for feedback on Scinta, our screenshots-to-actions Mac app. We just launched](https://www.reddit.com/r/SideProject/comments/1w2si2i/two_weeks_ago_i_asked_for_feedback_on_scinta_our/)
   - Score: 100/100
   - Value signal: $80.00
   - Why: visible or inferred value around $80.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Two weeks ago I asked for feedback on Scinta, our screenshots-to-actions Mac app. We just launched
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w2si2i/two_weeks_ago_i_asked_for_feedback_on_scinta_our/
     Why this is suitable: visible or inferred value around $80.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Hey everybody! My wife and I are building Scinta - a macOS app that turns screenshots into actions: an error becomes a ticket, dinner Saturday at 7 becomes a calendar event, an email signature becomes a contact. Two weeks ago I showed it here and got some really useful feedback. What came out of it: feature ideas from the comments went to the roadmap - a sharing action, highlighting which part of the screenshot produced each extracted field, accessibility checklist from a UI screenshot - several new features are already on the finish line and will be in one of upcoming releases soon the most common question from different threads and communities - why not just paste the screenshot into ChatGPT? - became our main pitch. There you switch apps, upload, write a prompt, copy the result back and still create the event yourself. Scinta does it in one click. I have my own AI setup and still do n
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Two weeks ago I asked for feedback on Scinta, our screenshots-to-actions Mac app. We just launched" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $80.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w2si2i/two_weeks_ago_i_asked_for_feedback_on_scinta_our/
3. [A licence granting this source away, a check that failed its own rule, and each product against its own competitors](https://github.com/famouslytrill-boop/sonara-os/pull/202)
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
4. [I built an open-source PDF editor that keeps your files on your computer](https://www.reddit.com/r/SideProject/comments/1w39bei/i_built_an_opensource_pdf_editor_that_keeps_your/)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I built an open-source PDF editor that keeps your files on your computer
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w39bei/i_built_an_opensource_pdf_editor_that_keeps_your/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I got tired of PDF tools that ask you to upload your documents somewhere before you can do anything with them. So I built PDF Editor Offline, a free and open-source PDF editor designed around one simple rule: your documents stay on your machine. No account. No file uploads. No recurring subscription. It can handle most of the PDF tasks I regularly need: Edit and annotate PDFs Add text, images, drawings, highlights and comments Fill and sign forms Merge, split, reorder, rotate and crop pages Compress PDFs Convert PDF ↔ Word, PowerPoint, Excel, images, Markdown, EPUB, etc. Run OCR locally Permanently redact sensitive information Remove metadata and hidden/private data Protect and unlock PDFs Search documents There’s also a CLI and Python API for automation, plus Docker support for self-hosting. The desktop app is built with Tauri, the editor uses React, and the backend/tooling is primarily
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I built an open-source PDF editor that keeps your files on your computer" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w39bei/i_built_an_opensource_pdf_editor_that_keeps_your/
5. [I built a project management tool that turns unstructured notes into tasks and documentation](https://www.reddit.com/r/SideProject/comments/1w390c0/i_built_a_project_management_tool_that_turns/)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Confirm the free tier limits and terms, build one small working demo, then attach a fixed price to a single narrow task.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I built a project management tool that turns unstructured notes into tasks and documentation
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w390c0/i_built_a_project_management_tool_that_turns/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Confirm the free tier limits and terms, build one small working demo, then attach a fixed price to a single narrow task.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Sooo, why even make yet another tool like this, you might ask? To put it simply, like many devs do, I wasn&#39;t happy with the mainstream options and made my own. Now, some more detail! I&#39;ve been a dev for about 10 years and, for the past 2, I&#39;ve been managing a team. When I was just getting tasks assigned, mostly on Jira/Asana, it wasn&#39;t so bad. The problem is that now I have to run meetings, take notes and plan work for others it&#39;s not so simple anymore. It takes ages and with AI accelerating development it&#39;s already hard to keep up. And the big players having such complex flows and UIs is not helping. To be fair, in bigger/more structured companies it makes sense. Also, why is it that on most project management tools it&#39;s so hard to track what others are doing!? Anyway, tools are either too simple or have grown into beasts that are too complex. So I&#39;ve tri
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I built a project management tool that turns unstructured notes into tasks and documentation" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w390c0/i_built_a_project_management_tool_that_turns/
6. [gave away 100k free credits at launch and now I can't tell if that was smart or stupid](https://www.reddit.com/r/SideProject/comments/1w3cqrg/gave_away_100k_free_credits_at_launch_and_now_i/)
   - Score: 92/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: gave away 100k free credits at launch and now I can't tell if that was smart or stupid
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w3cqrg/gave_away_100k_free_credits_at_launch_and_now_i/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Document the exact free-tier setup steps once, then charge a flat fee to perform it inside a client's workflow.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Shipped a chrome extension on august 10th, 148 weekly users now. It builds google forms with ai. Free tier is 100k credits, no card, works out to something like 5 forms before you hit the wall. The idea was obvious, remove every reason not to try it. And people do try it. What I did not expect is that a big chunk of people who install never send a single message. Not sent one and bounced . Zero. They install, the panel opens, they close it. So I don&#39;t think my problem is the free tier at all. I think I have an activation problem and I spent weeks tuning credits instead of looking at that. I only found it because I finally sat down with the session replays and watched people just... not type anything. The empty state has suggestion chips you can click and I still watched people close the panel. Kind of annoyed at myself because I had the analytics wired up in the first week and didn&#
   - Owner-reviewed outreach draft:
     Hi, I found your request about "gave away 100k free credits at launch and now I can't tell if that was smart or stupid" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w3cqrg/gave_away_100k_free_credits_at_launch_and_now_i/
7. [Real Estate Scraper A token-efficient scraper with llm formatting](https://www.reddit.com/r/SideProject/comments/1w3apwz/real_estate_scraper_a_tokenefficient_scraper_with/)
   - Score: 92/100
   - Value signal: $0.00
   - Why: runs on a free AI tier, so input cost is zero and margin is total; boring conversion work buyers already pay humans to do by hand
   - Next: Clean one messy sample export with the free LLM tier and quote a flat rate per file.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: Real Estate Scraper A token-efficient scraper with llm formatting
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w3apwz/real_estate_scraper_a_tokenefficient_scraper_with/
     Why this is suitable: runs on a free AI tier, so input cost is zero and margin is total; boring conversion work buyers already pay humans to do by hand
     First step: Clean one messy sample export with the free LLM tier and quote a flat rate per file.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Hey everyone! I built an open-source tool designed to discover, crawl, and extract structured real estate data across any city or country using LLM structured outputs Why this was built: Traditional scrapers break whenever property portals change their layout. LLM-based scrapers solve this, but usually consume huge amounts of tokens. How token efficiency was achieved: DOM Condensation (~75% reduction) : Cleans noise, scripts, and banners prior to LLM processing. Micro-Batch Slicing : Prevents TPM/RPM rate limits, allowing full extraction on free-tier APIs (Google Gemini, Groq, OpenRouter). Index-Matched Curation : AI selects distinct deep portal URLs without hallucinations. Streamlit Dashboard : Client-side filtering, price sorting, and one-click CSV/JSON export. I recommend Start with 1 Curated Site and 1 Page to test your location and conserve token quota. GitHub Repo: https://github.c
   - Owner-reviewed outreach draft:
     Hi, I found your request about "Real Estate Scraper A token-efficient scraper with llm formatting" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w3apwz/real_estate_scraper_a_tokenefficient_scraper_with/
8. [I got tired of paying for subscriptions for voice dictation, so I built a 100% local, open-source alternative (OpenDictate)](https://www.reddit.com/r/SideProject/comments/1w2q4ke/i_got_tired_of_paying_for_subscriptions_for_voice/)
   - Score: 90/100
   - Value signal: $20.00
   - Why: visible or inferred value around $20.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I got tired of paying for subscriptions for voice dictation, so I built a 100% local, open-source alternative (OpenDictate)
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w2q4ke/i_got_tired_of_paying_for_subscriptions_for_voice/
     Why this is suitable: visible or inferred value around $20.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Hey r/SideProject ! Like many developers and writers, I love using voice dictation to write at 150+ WPM. But existing tools like Wispr Flow or Superwhisper either require monthly cloud subscriptions ($12–$20/mo), lock you into macOS, or stream your raw microphone audio to remote servers. I spent the last few weeks building OpenDictate , a completely free, local-first, open-source AI voice dictation app for your desktop. What it does: Global Hotkey, Anywhere : Press Ctrl+Alt+Space (or ⌘+Shift+Space on Mac), speak naturally, and your words are instantly typed into whatever app has focus (VS Code, Notion, Slack, Obsidian, terminal, etc.). 100% Offline Private : Speech recognition runs entirely on your device via ONNX Runtime (FastConformer, Parakeet TDT, Whisper Large v3 Turbo). Zero cloud, zero telemetry. Hands-Free Wake Word : Say Hey Dictate to start dictating without touching your keybo
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I got tired of paying for subscriptions for voice dictation, so I built a 100% local, open-source alternative (OpenDictate)" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $20.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w2q4ke/i_got_tired_of_paying_for_subscriptions_for_voice/
