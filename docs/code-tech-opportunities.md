# Free AI Earning Queue

Refreshed: 2026-08-28T05:26:13.716987+00:00
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

The strongest free-AI earning angle right now is reselling small, fixed-price micro-services (transcription, summarization, translation, OCR cleanup, image background removal) to small-business owners, solo creators, and local service providers, using only free-tier APIs and a thin wrapper. You charge for the deliverable, not the compute, so the work scales to a few hundred dollars per month without paid infrastructure, an audience, or a credit card on file.

## Free AI Services To Use

| Service | What it does | Free tier | Card? | How to earn | Price guide |
| --- | --- | --- | --- | --- | --- |
| Google Gemini API (AI Studio) | Multimodal LLM for text generation, summarization, translation, vision, and structured JSON | Ongoing free tier with per-minute rate limits; verify current limit on the AI Studio page | no | Offer fixed-price 'clean up this transcript / summarize these notes / translate this page' jobs to small-business owners | $5 to $25 per job, $30 to $80/month per retainer client |
| OpenRouter (free models) | Unified API routing to multiple open-weight LLMs that are free to call | A rotating set of free models with daily or per-request caps; verify current limit per model | no | Sell a 'bring your own data, I build your prompt chain' setup that calls free models under the hood | $15 to $50 per prompt-chain setup, $20/month for maintenance |
| Groq Cloud Free Tier | Fast LLM inference API (Llama, Mixtral, Gemma) and Whisper speech-to-text | Ongoing free developer tier with per-minute token and audio limits; verify current limit | no | Resell transcription + clean summary as a one-page service for podcasters and YouTubers | $3 to $10 per hour of audio, $15/month per channel retainer |
| OpenAI Whisper (self-hosted via Whisper.cpp or faster-whisper) | Open-source speech-to-text model | Free to run on your own machine or free-tier compute; no API cost when self-hosted | no | Run batch transcription jobs for court reporters, journalists, or researchers on a free VM | $0.50 to $1.50 per audio minute billed to client, $50 per batch of 10 hours |
| Hugging Face Inference API (free tier) | Hosted inference for thousands of open models: TTS, translation, embeddings, vision, OCR | Ongoing free monthly inference credits; verify current limit on the account billing page | no | Batch-convert product photos: remove background, upscale, or generate alt text for ecommerce sellers | $0.20 to $0.50 per image, $20 per 100-image batch |
| Cohere Trial (Command + Embed) | LLM text generation, classification, and embeddings via API | Ongoing trial-tier keys with monthly request caps; verify current limit | no | Build a one-off FAQ or product-description rewriter that small Shopify stores pay a flat fee to use | $10 to $30 one-time setup, $10/month for ongoing rewrites |
| Mistral AI (La Plateforme free tier) | Hosted Mistral open-weight models for chat, JSON, and embeddings | Ongoing free experimentation tier with rate limits; verify current limit per model | no | Offer 'I will rewrite your 50 product listings for SEO' as a fixed-price job | $25 to $75 per 50 listings |
| remove.bg API alternative: @imgly/background-removal (open-source, on-device) | Open-source background removal model that runs locally or in a browser | Free forever (MIT) when self-hosted; no quota | no | Sell a '100 product photos, background removed, ready for Shopify' done-for-you batch | $0.10 to $0.30 per photo, $15 per 100-photo batch |
| Tesseract OCR (open-source) | Open-source OCR engine for scanned PDFs and images | Free forever, runs on your own machine | no | Extract text from scanned receipts, contracts, or old books as a fixed-price OCR job | $0.05 to $0.20 per page, $20 per 200-page batch |
| Surya OCR (open-source) | Modern open-source OCR with layout analysis, table extraction, and 90+ language support | Free forever when self-hosted; no API cost | no | Offer 'PDF to clean Excel/CSV' conversion for small accounting and real-estate offices | $5 to $15 per 20-page document, $50/month per office retainer |

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
3. [443 users, 4 paying, and people are making second accounts to farm my free tier. Should I be happy or worried?](https://www.reddit.com/r/SideProject/comments/1vzy5lc/443_users_4_paying_and_people_are_making_second/)
   - Score: 100/100
   - Value signal: $39.00
   - Why: visible or inferred value around $39.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Confirm the free tier limits and terms, build one small working demo, then attach a fixed price to a single narrow task.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: 443 users, 4 paying, and people are making second accounts to farm my free tier. Should I be happy or worried?
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1vzy5lc/443_users_4_paying_and_people_are_making_second/
     Why this is suitable: visible or inferred value around $39.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Confirm the free tier limits and terms, build one small working demo, then attach a fixed price to a single narrow task.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Day 15 of building in public. numbers first so nobody has to dig for them: 444 signups, 4 paying. some context on why the split is that ugly. My free tier is 5 comment-to-DM automations with no cap on how many people each one replies to, plus unlimited post and reel scheduling. no credit card. I made it that generous on purpose. Manychat&#39;s free plan is 25 active contacts a month and 4 automations. Essential is $14/mo for 250 contacts. The pro is $39/mo, or $29 if you prepay the year, and that covers 2,500 contacts before it starts charging $0.05 per contact on top. I wanted people to land on my free plan and feel like they&#39;d already gotten the thing they were about to pay for. That part worked. It worked so well that people finished their 5 automations, signed up again with a different email, and kept going. I can see it happening in the Posthog analytics. It&#39;s a compliment I
   - Owner-reviewed outreach draft:
     Hi, I found your request about "443 users, 4 paying, and people are making second accounts to farm my free tier. Should I be happy or worried?" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $39.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1vzy5lc/443_users_4_paying_and_people_are_making_second/
4. [I built an open-source dictation app so I could stop wrestling with Wispr Flow. Would love feedback.](https://www.reddit.com/r/SideProject/comments/1w0h2df/i_built_an_opensource_dictation_app_so_i_could/)
   - Score: 100/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I built an open-source dictation app so I could stop wrestling with Wispr Flow. Would love feedback.
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w0h2df/i_built_an_opensource_dictation_app_so_i_could/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Hey all — sharing a project I&#39;ve been working on for a while. What it is: SmoothFlow — a free, open-source, cross-platform voice-dictation app. Hold a hotkey, speak, release, and your words land cleaned up and typed into whatever app you&#39;re focused on. Email, chat, Word, terminal, browser — anywhere you can type. Why I built it: I wanted Wispr Flow&#39;s magic but without the subscription and the lock-in. So it&#39;s BYO-provider: you plug in your own API key (Groq has a free tier — ~2 minutes to set up, no credit card), and it works with any OpenAI-compatible transcription endpoint. Your key, your provider, no lock-in. Things that make it different: Clean text automatically — ending punctuation added, um/uh fillers stripped, self-corrections resolved ( I&#39;m going I&#39;m going to → I&#39;m going to ), and spoken emails/URLs converted ( user at gmail dot com → user@gmail.com )
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I built an open-source dictation app so I could stop wrestling with Wispr Flow. Would love feedback." and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w0h2df/i_built_an_opensource_dictation_app_so_i_could/
5. [I'm 21, still in school, and I built a prospecting tool because the "industry standard" ones are useless for half the people paying for them](https://www.reddit.com/r/SideProject/comments/1w048q2/im_21_still_in_school_and_i_built_a_prospecting/)
   - Score: 96/100
   - Value signal: $10.00
   - Why: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Clean one messy sample export with the free LLM tier and quote a flat rate per file.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I'm 21, still in school, and I built a prospecting tool because the "industry standard" ones are useless for half the people paying for them
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w048q2/im_21_still_in_school_and_i_built_a_prospecting/
     Why this is suitable: visible or inferred value around $10.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Clean one messy sample export with the free LLM tier and quote a flat rate per file.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Not a launch-hype post, just sharing the thing I built and the annoyance behind it, because I think a specific group of people will relate. I am a marketing student, and I was actually looking into getting into sales myself. So before building anything I just started asking SDRs and reps what their day actually looks like. Same complaint every time: the research before every cold email eats hours. Read the company, figure out the pain, find a real contact, write something that isn&#39;t a template. Then do it 50 more times. BUT the part that really got me was talking to people who sell to small businesses. HVAC companies, contractors, local trades, small agencies. These reps pay for the same expensive tools everyone recommends (Apollo, ZoomInfo, etc.), type in a local business, and get nothing. Empty. Because those tools run on giant databases that basically only have big companies in th
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I'm 21, still in school, and I built a prospecting tool because the "industry standard" ones are useless for half the people paying for them" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w048q2/im_21_still_in_school_and_i_built_a_prospecting/
6. [I built a bookmark app you can save to from WhatsApp, because my saved links were dying in 6 different apps](https://www.reddit.com/r/SideProject/comments/1vzy3ep/i_built_a_bookmark_app_you_can_save_to_from/)
   - Score: 88/100
   - Value signal: $4.00
   - Why: visible or inferred value around $4.00; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I built a bookmark app you can save to from WhatsApp, because my saved links were dying in 6 different apps
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1vzy3ep/i_built_a_bookmark_app_you_can_save_to_from/
     Why this is suitable: visible or inferred value around $4.00; runs on a free AI tier, so input cost is zero and margin is total
     First step: Sign up for the free speech-to-text tier, transcribe one sample file end to end, and publish a fixed price per hour of audio.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: Saved stuff was scattered across Instagram saves, WhatsApp messages to myself, browser bookmarks and three note apps. None of it searchable together, and I never opened any of it again. So I built Dissect. You forward a link, reel, PDF or voice note to it (browser extension, share sheet, or literally a WhatsApp message), it transcribes video and audio, OCRs images and PDFs, and then you ask your own library a question in plain language and get an answer with the source attached. The part that took longest was making retrieval not depend on a model call. An upstream model stalled for 129 seconds once and took search down with it, so now search works even when the AI layer is completely down. Free tier is 10 saves a month, paid is $4. Happy to answer anything about how it&#39;s built. Also genuinely want to know what makes you bounce off tools like this, since I know the category is crowde
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I built a bookmark app you can save to from WhatsApp, because my saved links were dying in 6 different apps" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $4.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1vzy3ep/i_built_a_bookmark_app_you_can_save_to_from/
7. [I built an AI CFO for small businesses, where tapping any number opens the math behind it. Three App Store submissions later, it's live!](https://www.reddit.com/r/SideProject/comments/1w05rj7/i_built_an_ai_cfo_for_small_businesses_where/)
   - Score: 88/100
   - Value signal: $0.00
   - Why: runs on a free AI tier, so input cost is zero and margin is total; startable today without new skills or tools
   - Next: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: I built an AI CFO for small businesses, where tapping any number opens the math behind it. Three App Store submissions later, it's live!
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w05rj7/i_built_an_ai_cfo_for_small_businesses_where/
     Why this is suitable: runs on a free AI tier, so input cost is zero and margin is total; startable today without new skills or tools
     First step: Run one scanned sample through the free OCR tier, produce a clean spreadsheet, and price per batch of pages.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: My app went live on the App Store this morning after three submissions and I&#39;m still a little wired, so here&#39;s the story while it&#39;s fresh. For the last while I&#39;ve been maintaining an open source stats engine called Aurora. Its whole thing is that it measures its own false positive rate and refuses to report findings it can&#39;t defend. Very satisfying to build. Used by approximately nobody outside of data people. At some point it hit me that the people who could actually use math like this aren&#39;t data scientists, they&#39;re small business owners. The coffee shop, the landscaping crew, the Etsy shop. They&#39;re sitting on years of their own Square and QuickBooks and bank data and getting basically zero decisions out of it, and every AI tool that offers to help will confidently make things up, which is worse than nothing when it&#39;s your rent on the line. So I spen
   - Owner-reviewed outreach draft:
     Hi, I found your request about "I built an AI CFO for small businesses, where tapping any number opens the math behind it. Three App Store submissions later, it's live!" and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $10.00 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w05rj7/i_built_an_ai_cfo_for_small_businesses_where/
8. [While building my apps, I figured out about a third of what I paid for Claude Code bought me nothing. So our next app went after the waste.](https://www.reddit.com/r/SideProject/comments/1w0ec22/while_building_my_apps_i_figured_out_about_a/)
   - Score: 87/100
   - Value signal: $19.99
   - Why: visible or inferred value around $19.99; runs on a free AI tier, so input cost is zero and margin is total
   - Next: Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer.
   - Codex request:
     Implement a small, verifiable solution for this public request.
     
     Lead: While building my apps, I figured out about a third of what I paid for Claude Code bought me nothing. So our next app went after the waste.
     Source: reddit:r/SideProject
     URL: https://www.reddit.com/r/SideProject/comments/1w0ec22/while_building_my_apps_i_figured_out_about_a/
     Why this is suitable: visible or inferred value around $19.99; runs on a free AI tier, so input cost is zero and margin is total
     First step: Build the recurring report once on free scheduled compute, then sell it as a low monthly retainer.
     
     Constraints:
     - Keep the first change narrowly scoped.
     - Use free APIs or offline code paths when possible.
     - Add or update a specific file that demonstrates the result.
     - Include exact verification commands and output notes.
     - Do not post externally or request payment automatically.
     
     Request excerpt: I build apps for a living. A couple on the Mac, others in the digital forensics space. Like a lot of people here, Claude Code has become a bigger and bigger part of how we build since it came out, and the bill lands every month. A while back I started analyzing my own usage, and about a third of what I was paying for bought me nothing. Not lower quality work. Nothing. The same files read over and over. Old chats re-read at full price inside every new chat. And the whole time, the Mac doing the building sat there with a perfectly good AI chip in it, mostly idle. There are three people behind this company and as developers we were all running into the same issue. So that became the next app. It&#39;s called Peddra ( peddra.com ). Phase 1 is live and it&#39;s simple: your Mac uses Apple Intelligence to read your chats as they grow, even overnight, without spending a single token, and when a
   - Owner-reviewed outreach draft:
     Hi, I found your request about "While building my apps, I figured out about a third of what I paid for Claude Code bought me nothing. So our next app went after the waste." and can make a small working version.
     
     I will keep it simple: one focused file/change, a short usage note, and proof that it runs. If the result solves the request, the fixed price is $19.99 via crypto.
     
     Payment address (USDT_WALLET_ADDRESS): TFTNsfyomKrnUutRjBTGVULp19ByW29KbY
     
     Reference: https://www.reddit.com/r/SideProject/comments/1w0ec22/while_building_my_apps_i_figured_out_about_a/
