from __future__ import annotations

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

_GROQ_MAX_PROMPT_TOKENS = 8_000
_CHARS_PER_TOKEN = 3.5

_GROQ_MODELS = [
	"llama-3.3-70b-versatile",
	"llama-3.1-70b-versatile",
	"llama3-70b-8192",
	"llama3-8b-8192",
]
# Cerebras free tier: 1M tokens/day + 14,400 req/day per model, no credit card.
# Far higher daily ceiling than OpenRouter's free 50 req/day, so it is a strong
# fallback once OpenRouter's free chain is exhausted for the day.
_CEREBRAS_MODELS = [
	"llama-3.3-70b",
	"llama3.1-8b",
]
_ANTHROPIC_MODELS = [
	"claude-sonnet-4-6",
	"claude-3-5-sonnet-20241022",
	"claude-3-haiku-20240307",
]
_GEMINI_MODELS = [
	"gemini-2.5-pro",
	"gemini-2.5-flash",
	"gemini-2.5-flash-lite",
]
# OpenRouter: every chain is zero-cost. Kimi K3 was the main engine but is PAID
# and fails outright without credits, so the whole chain is free-tier models,
# ordered by capability so a rate limit degrades quality instead of breaking a
# cycle.
#
# minimax/minimax-m3:free leads every chain. It is $0 in/$0 out with a 1M
# context window and is the only free model that advertises BOTH native
# response_format and tools, which is what keeps JSON drafts from coming back
# wrapped in prose. It was picked by probing the live OpenRouter catalogue:
# it returned valid, compiling, spec-complete code on every trial and was the
# fastest candidate (2-3s vs 5-42s).
#
# It replaced stealth/ox-alpha, which has been withdrawn from OpenRouter --
# exactly the stealth-release risk noted below. That is why no chain here ever
# has a single entry.
#
# Rejected during that probe, so they are deliberately absent:
#   thinkingmachines/inkling{,-small}:free -- best on paper (975B MoE, 1M ctx)
#     but returns HTTP 403 "only available on agentic harnesses". It is
#     allowlisted to approved apps, so this bot can never call it.
#   dots-studio/dots-3-note-preview:free   -- 512K ctx but failed to emit
#     parseable JSON on repeated trials.
#   nvidia/nemotron-3.5-lightning:free     -- slow (42s) and failed JSON.
_MAIN = "minimax/minimax-m3:free"

# Default chain: general-purpose fallback order, strongest first.
_OPENROUTER_MODELS = [
	_MAIN,                                      # 1M ctx, response_format + tools
	"nvidia/nemotron-3-ultra-550b-a55b:free",   # 1M ctx, strongest open-weight reasoning
	"google/gemma-4-26b-a4b-it:free",           # 262K ctx, native function calling
	"z-ai/glm-5.2:free",                        # 256K ctx, response_format
	"minimax/minimax-m2.7:free",                # verified fallback, response_format
	"openrouter/free",                          # auto-router: always resolves to *some* free model
]

# Code / repair suggestions ("upgrade"): lead with the models that are actually
# trained for software engineering, then fall back to general reasoners. This
# role previously had no chain of its own and silently used the default.
_OPENROUTER_MODELS_UPGRADE = [
	_MAIN,                                      # verified: compiling code + strict JSON
	"poolside/laguna-s-2.1:free",               # code-specialised, 262K ctx
	"cohere/north-mini-code:free",              # code-specialised
	"nvidia/nemotron-3-ultra-550b-a55b:free",
	"minimax/minimax-m2.7:free",                # verified fallback
	"openrouter/free",
]

# Research/long-context work: research prompts are long, so rank by context
# window and reasoning strength.
_OPENROUTER_MODELS_RESEARCH = [
	_MAIN,                                      # 1M ctx
	"nvidia/nemotron-3-ultra-550b-a55b:free",   # 1M ctx
	"nvidia/nemotron-3-super-120b-a12b:free",   # 262K ctx, response_format
	"google/gemma-4-26b-a4b-it:free",
	"minimax/minimax-m2.7:free",                # verified fallback
	"openrouter/free",
]

# Article writing (long-form structured JSON): every model here must support
# response_format natively, so drafts don't come back as prose-wrapped JSON.
_OPENROUTER_MODELS_POST = [
	_MAIN,
	"google/gemma-4-26b-a4b-it:free",
	"z-ai/glm-5.2:free",
	"nvidia/nemotron-3-super-120b-a12b:free",
	"minimax/minimax-m2.7:free",                # verified sibling fallback
	"openrouter/free",
]

_OPENROUTER_MODELS_BY_ROLE: dict[str, list[str]] = {
	"upgrade":  _OPENROUTER_MODELS_UPGRADE,
	"research": _OPENROUTER_MODELS_RESEARCH,
	"post":     _OPENROUTER_MODELS_POST,
}

# Role → preferred provider mapping. Free OpenRouter models are the main
# engine for every role; gemini/groq remain as provider-level fallbacks.
ROLE_PROVIDER: dict[str, str] = {
	"upgrade":    "openrouter",
	"research":   "openrouter",
	"post":       "openrouter",
	"think":      "openrouter",
	"fast":       "openrouter",
	"experiment": "openrouter",
}


@dataclass
class LLMResponse:
	text: str
	provider: str
	model: str
	latency_s: float


class LLMClient:
	"""Unified LLM client. Raises RuntimeError at init if no key is available."""

	def __init__(self) -> None:
		self._anthropic_key  = os.getenv("ANTHROPIC_API_KEY",  "").strip()
		self._gemini_key     = os.getenv("GEMINI_API_KEY",     "").strip()
		self._openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
		self._groq_key       = os.getenv("GROQ_API_KEY",       "").strip()
		self._cerebras_key   = os.getenv("CEREBRAS_API_KEY",   "").strip()
		self.provider        = self._pick_provider()
		self._current_role: str | None = None
		self.model           = self._pick_model()
		self.info            = {"provider": self.provider, "model": self.model}
		log.info("LLM ready -- provider=%s model=%s", self.provider, self.model)

	# -- Public API ------------------------------------------------------------

	def complete(
		self,
		prompt: str,
		system: str = "",
		max_tokens: int = 4096,
		temperature: float = 0.7,
	) -> LLMResponse:
		"""Send a prompt, return LLMResponse. Retries 3x then falls back to next provider."""
		providers_to_try = self._provider_chain()
		last_exc: Exception | None = None

		for provider in providers_to_try:
			p_prompt  = self._truncate_for_groq(prompt, system, max_tokens) if provider == "groq" else prompt
			p_model   = self._model_for_provider(provider)
			exhausted = False

			# `attempt` counts real retries of the *same* model. Stepping down
			# the model chain must not consume that budget, otherwise a long
			# free-model chain is abandoned after only 2-3 entries.
			attempt = 0
			while attempt < 3:
				attempt += 1
				try:
					if provider == "anthropic":
						return self._call_anthropic(p_prompt, system, max_tokens, temperature, p_model)
					if provider == "gemini":
						return self._call_gemini(p_prompt, system, max_tokens, temperature, p_model)
					if provider == "openrouter":
						return self._call_openrouter(p_prompt, system, max_tokens, temperature, p_model)
					if provider == "cerebras":
						return self._call_cerebras(p_prompt, system, max_tokens, temperature, p_model)
					if provider == "claude-cli":
						return self._call_claude_cli(p_prompt, system, max_tokens)
					return self._call_groq(p_prompt, system, max_tokens, temperature, p_model)
				except Exception as exc:
					last_exc = exc
					exc_str  = str(exc)

					# Auth errors: no point retrying same provider
					if any(code in exc_str for code in ("401", "403", "authentication_error", "invalid x-api-key", "invalid_api_key", "API_KEY_INVALID")):
						log.warning("LLM auth error on provider=%s -- skipping to fallback: %s", provider, exc)
						exhausted = True
						break

					# Out of credits / rate limited on a PAID OpenRouter model:
					# step down to the next model in the chain (which is free)
					# rather than abandoning OpenRouter entirely.
					if provider == "openrouter" and any(
						code in exc_str for code in ("402", "429", "insufficient", "rate_limit", "quota", "Too Many Requests")
					):
						model_list = self._model_list_for(provider)
						if p_model in model_list and model_list.index(p_model) < len(model_list) - 1:
							p_model = model_list[model_list.index(p_model) + 1]
							log.warning("openrouter model unavailable (%s) -- stepping down to %s", exc_str[:80], p_model)
							attempt = 0  # new model gets a fresh retry budget
							continue
						log.warning("openrouter model chain exhausted -- skipping to fallback: %s", exc)
						exhausted = True
						break

					# Rate limit / quota exhausted: skip provider immediately
					if any(code in exc_str for code in ("429", "rate_limit_exceeded", "RESOURCE_EXHAUSTED", "quota_exceeded", "RateLimitError", "insufficient_quota", "Too Many Requests")):
						log.warning("LLM rate limit on provider=%s -- skipping to fallback: %s", provider, exc)
						exhausted = True
						break

					# 413: truncate and retry (Groq only)
					if "413" in exc_str and provider == "groq" and attempt < 3:
						cutoff   = int(len(p_prompt) * 0.6)
						nl       = p_prompt.rfind("\n", 0, cutoff)
						p_prompt = p_prompt[: nl if nl > 0 else cutoff]
						log.warning("LLM 413 attempt %d -- truncated to %d chars", attempt, len(p_prompt))
						continue

					# Model deprecated: advance to next in chain
					# Model deprecated/withdrawn (stealth previews can vanish
					# without notice): advance to the next entry in the chain.
					if "model_not_found" in exc_str or "model not found" in exc_str.lower():
						model_list = self._model_list_for(provider)
						if p_model in model_list:
							idx = model_list.index(p_model)
							if idx < len(model_list) - 1:
								p_model = model_list[idx + 1]
								log.warning("%s model %s unavailable -- advancing to %s",
											provider, model_list[idx], p_model)
								attempt = 0  # new model gets a fresh retry budget
								continue
						log.warning("%s model chain exhausted -- skipping to fallback", provider)
						exhausted = True
						break

					log.warning("LLM attempt %d/3 provider=%s failed: %s", attempt, provider, exc)
					if attempt < 3:
						time.sleep(2 ** attempt)
					else:
						exhausted = True

			if exhausted and providers_to_try.index(provider) < len(providers_to_try) - 1:
				log.warning("LLM provider=%s exhausted -- trying fallback", provider)

		raise RuntimeError(f"LLM failed on all providers: {last_exc}") from last_exc

	def complete_for_role(
		self,
		role: str,
		prompt: str,
		system: str = "",
		max_tokens: int = 4096,
		temperature: float = 0.7,
	) -> LLMResponse:
		"""Route to role-appropriate provider (upgrade→gemini, research→openrouter, post→groq).
        Falls back to complete() with default provider if role provider unavailable."""
		preferred = ROLE_PROVIDER.get(role)
		if preferred:
			key_map = {
				"gemini":     self._gemini_key,
				"groq":       self._groq_key,
				"openrouter": self._openrouter_key,
				"anthropic":  self._anthropic_key,
			}
			if key_map.get(preferred):
				log.info("Role=%s → provider=%s", role, preferred)
				old_provider = self.provider
				old_role     = self._current_role
				self.provider     = preferred
				self._current_role = role
				try:
					return self.complete(prompt, system=system, max_tokens=max_tokens,
										temperature=temperature)
				finally:
					self.provider     = old_provider
					self._current_role = old_role
		return self.complete(prompt, system=system, max_tokens=max_tokens,
							 temperature=temperature)

	def complete_json(
		self,
		prompt: str,
		system: str = "",
		max_tokens: int = 4096,
	) -> dict[str, Any]:
		"""
        Like complete() but parses the response as JSON.
        Appends a JSON-only instruction to the system prompt.
        Raises ValueError if JSON cannot be extracted after retries.
        """
		json_system = (
			(system + "\n\n" if system else "")
			+ "IMPORTANT: Respond with ONLY a single valid JSON object. "
			"No markdown, no code fences, no explanation before or after."
		)
		last_exc: Exception | None = None
		for attempt in range(1, 4):
			try:
				resp = self.complete(
					prompt, system=json_system,
					max_tokens=max_tokens, temperature=0.2,
				)
				return parse_json(resp.text)
			except (ValueError, RuntimeError) as exc:
				last_exc = exc
				log.warning("JSON attempt %d/3 failed: %s", attempt, exc)
				if attempt < 3:
					time.sleep(1)
		raise ValueError(f"Could not get valid JSON from LLM: {last_exc}") from last_exc

	def complete_json_for_role(
		self,
		role: str,
		prompt: str,
		system: str = "",
		max_tokens: int = 4096,
	) -> dict[str, Any]:
		"""Like complete_json() but routes to role-appropriate provider."""
		json_system = (
			(system + "\n\n" if system else "")
			+ "IMPORTANT: Respond with ONLY a single valid JSON object. "
			"No markdown, no code fences, no explanation before or after."
		)
		last_exc: Exception | None = None
		for attempt in range(1, 4):
			try:
				resp = self.complete_for_role(
					role, prompt, system=json_system,
					max_tokens=max_tokens, temperature=0.2,
				)
				return parse_json(resp.text)
			except (ValueError, RuntimeError) as exc:
				last_exc = exc
				log.warning("JSON[role=%s] attempt %d/3 failed: %s", role, attempt, exc)
				if attempt < 3:
					time.sleep(1)
		raise ValueError(f"Could not get valid JSON from LLM (role={role}): {last_exc}") from last_exc

	# -- Groq ------------------------------------------------------------------

	def _truncate_for_groq(self, prompt: str, system: str, max_tokens: int) -> str:
		system_tokens    = len(system) / _CHARS_PER_TOKEN
		response_budget  = max_tokens
		available_chars  = int(
			(_GROQ_MAX_PROMPT_TOKENS - system_tokens - response_budget) * _CHARS_PER_TOKEN
		)
		if len(prompt) > available_chars > 0:
			log.info(
				"Groq prompt pre-truncated from %d to %d chars (token budget)",
				len(prompt), available_chars,
			)
			return prompt[:available_chars] + "\n... [truncated for token limit]"
		return prompt

	def _call_groq(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		from groq import Groq  # lazy import
		client   = Groq(api_key=self._groq_key)
		messages: list[dict] = []
		if system:
			messages.append({"role": "system", "content": system})
		messages.append({"role": "user", "content": prompt})
		t0  = time.monotonic()
		rsp = client.chat.completions.create(
			model=model,
			messages=messages,
			max_tokens=max_tokens,
			temperature=temperature,
		)
		return LLMResponse(
			text      = rsp.choices[0].message.content or "",
			provider  = "groq",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Anthropic -------------------------------------------------------------

	def _call_anthropic(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		import anthropic  # lazy import
		client = anthropic.Anthropic(api_key=self._anthropic_key)
		kwargs: dict[str, Any] = {
			"model":       model,
			"max_tokens":  max_tokens,
			"temperature": temperature,
			"messages":    [{"role": "user", "content": prompt}],
		}
		if system:
			kwargs["system"] = system
		t0  = time.monotonic()
		msg = client.messages.create(**kwargs)
		return LLMResponse(
			text      = msg.content[0].text if msg.content else "",
			provider  = "anthropic",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Gemini ----------------------------------------------------------------

	def _call_gemini(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		import google.generativeai as genai  # lazy import
		genai.configure(api_key=self._gemini_key)
		gen_config = genai.GenerationConfig(
			max_output_tokens=max_tokens,
			temperature=temperature,
		)
		# system_instruction supported on gemini-1.5+ and gemini-2.0+
		kwargs: dict[str, Any] = {"generation_config": gen_config}
		if system:
			kwargs["system_instruction"] = system
		t0     = time.monotonic()
		client = genai.GenerativeModel(model, **kwargs)
		rsp    = client.generate_content(prompt)
		return LLMResponse(
			text      = rsp.text or "",
			provider  = "gemini",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- OpenRouter ------------------------------------------------------------

	def _call_openrouter(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		import requests  # already in requirements
		messages: list[dict] = []
		if system:
			messages.append({"role": "system", "content": system})
		messages.append({"role": "user", "content": prompt})
		t0  = time.monotonic()
		rsp = requests.post(
			"https://openrouter.ai/api/v1/chat/completions",
			headers={
				"Authorization":  f"Bearer {self._openrouter_key}",
				"HTTP-Referer":   "https://github.com/rtt-enjoy/e-evolve",
				"X-Title":        "e-evolve",
				"Content-Type":   "application/json",
			},
			json={
				"model":       model,
				"messages":    messages,
				"max_tokens":  max_tokens,
				"temperature": temperature,
			},
			timeout=90,
		)
		if rsp.status_code in (401, 403):
			raise RuntimeError(f"401 authentication_error from openrouter: {rsp.text[:200]}")
		if rsp.status_code == 402:
			raise RuntimeError(f"402 insufficient credits on openrouter model {model}: {rsp.text[:200]}")
		if rsp.status_code == 429:
			raise RuntimeError(f"429 rate_limit_exceeded from openrouter: {rsp.text[:200]}")
		if rsp.status_code == 404:
			raise RuntimeError(f"model_not_found on openrouter: {model}: {rsp.text[:200]}")
		rsp.raise_for_status()
		data = rsp.json()
		if "error" in data:
			raise RuntimeError(f"OpenRouter error: {data['error']}")
		if not data.get("choices"):
			raise RuntimeError(f"OpenRouter returned no choices for {model}: {str(data)[:200]}")
		text = data["choices"][0]["message"]["content"] or ""
		return LLMResponse(
			text      = text,
			provider  = "openrouter",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Cerebras ----------------------------------------------------------------

	def _call_cerebras(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		import requests  # already in requirements
		messages: list[dict] = []
		if system:
			messages.append({"role": "system", "content": system})
		messages.append({"role": "user", "content": prompt})
		t0  = time.monotonic()
		rsp = requests.post(
			"https://api.cerebras.ai/v1/chat/completions",
			headers={
				"Authorization": f"Bearer {self._cerebras_key}",
				"Content-Type":  "application/json",
			},
			json={
				"model":       model,
				"messages":    messages,
				"max_tokens":  max_tokens,
				"temperature": temperature,
			},
			timeout=90,
		)
		if rsp.status_code in (401, 403):
			raise RuntimeError(f"401 authentication_error from cerebras: {rsp.text[:200]}")
		if rsp.status_code == 429:
			raise RuntimeError(f"429 rate_limit_exceeded from cerebras: {rsp.text[:200]}")
		if rsp.status_code == 404:
			raise RuntimeError(f"model_not_found on cerebras: {model}: {rsp.text[:200]}")
		rsp.raise_for_status()
		data = rsp.json()
		if "error" in data:
			raise RuntimeError(f"Cerebras error: {data['error']}")
		if not data.get("choices"):
			raise RuntimeError(f"Cerebras returned no choices for {model}: {str(data)[:200]}")
		text = data["choices"][0]["message"]["content"] or ""
		return LLMResponse(
			text      = text,
			provider  = "cerebras",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Claude CLI (Pro subscription, no API key) -----------------------------

	def _call_claude_cli(
		self, prompt: str, system: str, max_tokens: int
	) -> LLMResponse:
		full_prompt = f"{system}\n\n{prompt}" if system else prompt
		t0 = time.monotonic()
		result = subprocess.run(
			["claude", "-p", full_prompt],
			capture_output=True,
			text=True,
			timeout=120,
		)
		if result.returncode != 0:
			stderr = result.stderr[:400]
			if "401" in stderr or "authentication" in stderr.lower() or "api key" in stderr.lower():
				raise RuntimeError(f"401 authentication_error from claude CLI: {stderr}")
			raise RuntimeError(f"claude CLI exited {result.returncode}: {stderr}")
		text = result.stdout.strip()
		if not text:
			raise RuntimeError("claude CLI returned empty response")
		return LLMResponse(
			text      = text,
			provider  = "claude-cli",
			model     = self.model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Helpers ---------------------------------------------------------------

	def _pick_provider(self) -> str:
		if os.getenv("CLAUDE_CLI_MODE", "").strip() == "1":
			return "claude-cli"
		# OpenRouter first: it hosts the free-tier model chain, the main engine.
		if self._openrouter_key:
			return "openrouter"
		if self._anthropic_key:
			return "anthropic"
		if self._gemini_key:
			return "gemini"
		if self._groq_key:
			return "groq"
		if self._cerebras_key:
			return "cerebras"
		raise RuntimeError(
			"No LLM API key found.\n"
			"Add one of: ANTHROPIC_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, GROQ_API_KEY, CEREBRAS_API_KEY\n"
			"to GitHub -> Settings -> Secrets and variables -> Actions.\n"
			"For local dev with Claude Pro: set CLAUDE_CLI_MODE=1 in .env"
		)

	def _pick_model(self) -> str:
		return self._model_for_provider(self.provider)

	def _model_for_provider(self, provider: str) -> str:
		if provider == "anthropic":
			return _ANTHROPIC_MODELS[0]
		if provider == "gemini":
			return _GEMINI_MODELS[0]
		if provider == "openrouter":
			return self._model_list_for(provider)[0]
		if provider == "cerebras":
			return _CEREBRAS_MODELS[0]
		if provider == "claude-cli":
			return "claude-sonnet-4-6"
		return _GROQ_MODELS[0]

	def _model_list_for(self, provider: str) -> list[str]:
		"""Model fallback chain for a provider, role-aware for openrouter."""
		if provider == "openrouter":
			return _OPENROUTER_MODELS_BY_ROLE.get(self._current_role, _OPENROUTER_MODELS)
		return _model_list_for(provider)

	def _provider_chain(self) -> list[str]:
		"""Ordered fallback chain starting from primary provider."""
		all_providers = [
			("claude-cli",   os.getenv("CLAUDE_CLI_MODE", "").strip() == "1"),
			("openrouter",   bool(self._openrouter_key)),
			("anthropic",    bool(self._anthropic_key)),
			("gemini",       bool(self._gemini_key)),
			("cerebras",     bool(self._cerebras_key)),
			("groq",         bool(self._groq_key)),
		]
		available = [p for p, has_key in all_providers if has_key]
		# Ensure primary is first
		if self.provider in available:
			available.remove(self.provider)
			available.insert(0, self.provider)
		return available


def _model_list_for(provider: str) -> list[str]:
	return {
		"groq":        _GROQ_MODELS,
		"anthropic":   _ANTHROPIC_MODELS,
		"gemini":      _GEMINI_MODELS,
		"openrouter":  _OPENROUTER_MODELS,
		"cerebras":    _CEREBRAS_MODELS,
	}.get(provider, [])


# -- JSON parser (module-level so tests can import directly) ------------------

def parse_json(text: str) -> dict[str, Any]:
	"""
    Parse JSON from an LLM response string.
    Handles markdown fences, leading/trailing prose.
    Raises ValueError if no valid JSON object found.
    """
	text = text.strip()
	text = re.sub(r'^```(?:json)?\s*\n?', '', text, flags=re.MULTILINE)
	text = re.sub(r'\n?```\s*$',          '', text, flags=re.MULTILINE)
	text = text.strip()

	try:
		return json.loads(text)
	except json.JSONDecodeError:
		pass

	start = text.find("{")
	if start != -1:
		decoder = json.JSONDecoder()
		try:
			obj, _ = decoder.raw_decode(text, start)
			return obj
		except json.JSONDecodeError:
			pass

	raise ValueError(f"No valid JSON object found in LLM response. First 200 chars: {text[:200]!r}")
