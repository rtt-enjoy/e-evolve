# No-ID Free Path

Use this path when you cannot use Binance identity verification, phone-gated
social APIs, Claude premium features, paid LLM accounts, or funded wallets.

## Recommended Order

1. Enable code-tech leads. This is already on by default and needs no external
   account secret.
2. Add `GROQ_API_KEY` or `GEMINI_API_KEY` for free LLM capacity.
3. Add `DEV_TO_API_KEY` when you want the bot to publish articles.
4. Add optional GitHub Actions variables `EARN_CTA_URL` and `EARN_CTA_LABEL`
   for a sponsor, tip, newsletter, affiliate, portfolio, or product link.
5. Use OpenRouter free models only if Groq or Gemini limits are not enough.

## Avoid By Default

| Area | Why to avoid |
|------|--------------|
| Binance trading and payout | Exchange identity verification, address whitelisting, and funded balances are required in practice. |
| Claude/Anthropic premium path | Useful quality, but it is not the no-cost path and can depend on paid access. |
| Twitter/X API posting | Developer/API access can be phone-gated or paid, so do not make it a required earning path. |
| Ethereum NFT minting | Requires wallet funding, deployed contracts, and chain fees. |
| Any suggestion marked paid | The dashboard now filters these out of the main recommendation list. |

## Notes Checked On 2026-05-16

- Google lists a Gemini API free tier with free input/output tokens on eligible
  models and published rate limits.
- OpenRouter documents free model routing and a free-tier quota, but availability
  depends on the selected free model/provider.
- Forem/dev.to documents user-generated API keys for article publishing.
- Provider anti-abuse checks can change. This path avoids services whose core
  use is known to require exchange KYC, premium subscription, phone-gated social
  API setup, or funded wallets; it cannot promise that every account signup will
  skip every regional challenge forever.

## Sources

- Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Gemini API rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- OpenRouter FAQ: https://openrouter.ai/docs/faq
- OpenRouter rate limits: https://openrouter.zendesk.com/hc/en-us/articles/39501163636379-OpenRouter-Rate-Limits-What-You-Need-to-Know
- Forem/dev.to API: https://developers.forem.com/api/
