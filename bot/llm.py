from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

# GLM (Z.ai / Zhipu): main engine when GLM_API_KEY is set. Atria is the first
# fallback, then Anthropic and Gemini when their keys are set.
#
# Z.ai issues separate, non-interchangeable keys for its general API and its
# Coding Plan, and bigmodel.cn (mainland) issues its own, so the key alone does
# not say which host to call. The first GLM call of a run probes these in order
# with a tiny request and keeps the first endpoint + model that accepts the key.
# Coding Plan hosts go first: a flat subscription, not metered per token.
_GLM_ENDPOINTS = [
	"https://api.z.ai/api/coding/paas/v4",
	"https://api.z.ai/api/paas/v4",
	"https://open.bigmodel.cn/api/coding/paas/v4",
	"https://open.bigmodel.cn/api/paas/v4",
]
# glm-5.3-flash leads (owner directive 2026-10-31): $0.15/$0.50 per 1M tokens on
# the general API, against $1.40/$4.40 for glm-5.2. The rest run strongest
# first. The two Flash models at the end are free on the general API, so a key
# with no balance (code 1113) still lands on a model that answers.
_GLM_MODELS = [
	"glm-5.3-flash",
	"glm-5.2",
	"glm-5.1",
	"glm-5",
	"glm-4.7",
	"glm-4.7-flash",
	"glm-4.5-flash",
]
# Z.ai business codes (docs.z.ai/api-reference/api-code), grouped by what the
# caller should do next.
_GLM_NEXT_MODEL_CODES = {"1113", "1211", "1212", "1221", "1311"}   # this model is not usable on this key
_GLM_WRONG_HOST_CODES = {"1000", "1001", "1003", "1005", "1220", "1309", "1315"}  # key belongs elsewhere
_GLM_TRANSIENT_CODES  = {"1302", "1305"}                           # rate limit / overloaded: this call only
# GLM-5.3 models cannot switch thinking off: thinking.type accepts only
# "enabled", and "disabled" is refused (docs.z.ai/guides/llm/glm-5.3). Their
# documented equivalent of "off" is reasoning_effort "low". Reasoning may count
# against max_tokens, so a 5.3 call gets extra room for it on top of what the
# caller sized for the answer; max_tokens is a ceiling, not a charge.
_GLM_ALWAYS_THINKS = ("glm-5.3",)
_GLM_REASONING_HEADROOM = 8192
_GLM_TIMEOUT = (15, 240)
_GLM_MAX_FAILURES = 2
_GLM_SKIP_MARKER = "glm_skip"
# Atria: first fallback when ATRIA_API_KEY is set (~1B free tokens). Called through
# the OpenAI-style endpoint of the intern-ai discovery API; the same host also
# serves an Anthropic-style API at its root, which this client does not use.
# Single model, case-sensitive ID ("Atria-Dawn" since the Preview was upgraded).
# Quota exhaustion latches the provider off for the rest of the run and the chain
# falls through to the next provider.
_ATRIA_BASE_URL = "https://discovery-api.intern-ai.org.cn/v1"
_ATRIA_MODELS = [
	"Atria-Dawn",
]
# Atria is slow to answer, so it gets far more patience than a 90s call:
# (connect, read) seconds. A timeout after that wait falls through to the next
# provider for that call -- it is not retried, since three 5-minute waits on one prompt
# would eat most of the 55-minute job cap. After _ATRIA_MAX_TIMEOUTS in one run
# Atria is latched off, so a stalled Atria costs at most ~10 minutes a cycle.
_ATRIA_TIMEOUT = (15, 300)
_ATRIA_MAX_TIMEOUTS = 2
_ATRIA_TIMEOUT_MARKER = "atria_timeout"
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
# Role → preferred provider mapping. GLM leads every role; when it is absent or
# latched off, Atria serves, then anthropic/gemini as provider-level fallbacks.
ROLE_PROVIDER: dict[str, str] = {
	"upgrade":    "glm",
	"research":   "glm",
	"post":       "glm",
	"think":      "glm",
	"fast":       "glm",
	"experiment": "glm",
}


@dataclass
class LLMResponse:
	text: str
	provider: str
	model: str
	latency_s: float


_EMPTY_RESPONSE_MARKER = "empty_response"
_ALL_PROVIDERS_FAILED = "LLM failed on all providers"
# A model that has been retired or closed to this key. Providers word it
# differently, so match the shapes seen so far; anything this misses is still
# caught by the generic retry path in complete(), which also walks the chain.
_MODEL_GONE_RE = re.compile(
	r"\b404\b|not_found_error|no longer available|is not found|not found for api version",
	re.IGNORECASE,
)
# Parse attempts per provider in complete_json*. Two, not three: Atria can take
# five minutes an answer and the whole job is capped at 55.
_JSON_ATTEMPTS_PER_PROVIDER = 2


def _require_text(text: str | None, provider: str, model: str) -> str:
	"""
    Reject a completion that arrived with no content.

    An HTTP 200 carrying an empty body is a *failed* call, not a valid empty
    answer -- no caller here has a use for "". Every provider used to coerce it
    to `""` and return successfully, which broke two things at once: `complete()`
    returned on the first model and never stepped down its chain, and
    `complete_json*` then re-sent the same prompt to the same dead model three
    times before failing the cycle with `First 200 chars: ''`. Raising instead
    puts an empty response on the same footing as a 404 -- advance to the next
    model.    """
	if text and text.strip():
		return text
	raise RuntimeError(
		f"{_EMPTY_RESPONSE_MARKER}: {provider} model {model} returned no content"
	)


class LLMClient:
	"""Unified LLM client. Raises RuntimeError at init if no key is available."""

	def __init__(self) -> None:
		self._anthropic_key  = os.getenv("ANTHROPIC_API_KEY",  "").strip()
		self._gemini_key     = os.getenv("GEMINI_API_KEY",     "").strip()
		self._atria_key      = os.getenv("ATRIA_API_KEY",      "").strip()
		self._glm_key        = os.getenv("GLM_API_KEY",        "").strip()
		# GLM state for this run: the endpoint + model the probe settled on
		# (None until the first GLM call), and why it was latched off, if it was.
		self._glm_endpoint: str | None = None
		self._glm_model: str | None = None
		self._glm_disabled = False
		self._glm_disabled_reason: str | None = None
		self._glm_failures = 0
		# Models this key was refused on, so a run that settles below
		# _GLM_MODELS[0] can say why instead of quietly naming another model.
		self._glm_refused: list[dict[str, str]] = []
		# Set when Atria answers 401 or its free quota is spent. Per-process: the
		# next hourly cycle starts with Atria enabled again.
		self._atria_disabled = False
		# Why Atria was latched off this run (auth_failed / quota_spent /
		# model_not_found), and which provider actually answered each call.
		# Both feed engine_report(): a preference is not a live engine.
		self._atria_disabled_reason: str | None = None
		self._atria_timeouts = 0
		self._served: dict[str, int] = {}
		self.provider        = self._pick_provider()
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
		exclude: frozenset[str] = frozenset(),
	) -> LLMResponse:
		"""Send a prompt, return LLMResponse.

		A failure never ends the call while a candidate is left: the model chain
		of the failing provider is walked first, then the next provider's. Only
		when every candidate has failed does it raise. `exclude` names providers
		to skip -- `complete_json*` uses it to hand a prompt to the next provider
		after one answered with unparseable output.
		"""
		providers_to_try = [p for p in self._provider_chain() if p not in exclude]
		last_exc: Exception | None = None
		if not providers_to_try:
			raise RuntimeError(f"{_ALL_PROVIDERS_FAILED}: no provider left to try")

		for provider in providers_to_try:
			p_prompt  = prompt
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
						resp = self._call_anthropic(p_prompt, system, max_tokens, temperature, p_model)
					elif provider == "gemini":
						resp = self._call_gemini(p_prompt, system, max_tokens, temperature, p_model)
					elif provider == "glm":
						resp = self._call_glm(p_prompt, system, max_tokens, temperature, p_model)
					else:
						resp = self._call_atria(p_prompt, system, max_tokens, temperature, p_model)
					self._served[resp.provider] = self._served.get(resp.provider, 0) + 1
					return resp
				except Exception as exc:
					last_exc = exc
					exc_str  = str(exc)

					# Auth errors: no point retrying same provider
					if any(code in exc_str for code in ("401", "403", "authentication_error", "invalid x-api-key", "invalid_api_key", "API_KEY_INVALID")):
						log.warning("LLM auth error on provider=%s -- skipping to fallback: %s", provider, exc)
						exhausted = True
						break

					# Atria already had its full patience window; another wait
					# on the same prompt is not worth the cycle time.
					if _ATRIA_TIMEOUT_MARKER in exc_str:
						log.warning("atria gave no answer in time -- using fallback for this call: %s", exc)
						exhausted = True
						break

					# GLM timed out, was unreachable, or refused this one
					# request (too long, flagged): retrying the same prompt
					# would fail the same way, so the next provider takes it.
					if _GLM_SKIP_MARKER in exc_str:
						log.warning("glm could not serve this call -- using fallback: %s", exc)
						exhausted = True
						break

					# Rate limit / quota exhausted: skip provider immediately
					if any(code in exc_str for code in ("429", "rate_limit_exceeded", "RESOURCE_EXHAUSTED", "quota_exceeded", "RateLimitError", "insufficient_quota", "Too Many Requests")):
						log.warning("LLM rate limit on provider=%s -- skipping to fallback: %s", provider, exc)
						exhausted = True
						break

					# Model deprecated/withdrawn (stealth previews can vanish
					# without notice), or answering 200 with an empty body:
					# advance to the next entry in the chain. An empty response
					# belongs here and not with the generic retry below --
					# re-asking a model that just returned nothing almost always
					# returns nothing again, and each wasted call spends quota.
					if (
						"model_not_found" in exc_str
						or "model not found" in exc_str.lower()
						or _MODEL_GONE_RE.search(exc_str)
						or _EMPTY_RESPONSE_MARKER in exc_str
					):
						nxt = _next_model(provider, p_model)
						if nxt:
							log.warning("%s model %s unusable (%s) -- advancing to %s",
										provider, p_model, exc_str[:80], nxt)
							p_model = nxt
							attempt = 0  # new model gets a fresh retry budget
							continue
						log.warning("%s model chain exhausted -- skipping to fallback", provider)
						exhausted = True
						break

					log.warning("LLM attempt %d/3 provider=%s failed: %s", attempt, provider, exc)
					if attempt < 3:
						time.sleep(2 ** attempt)
						continue
					# The retry budget on this model is spent. Before giving up on the
					# provider, try the rest of its chain -- one attempt per model,
					# since an unclassified error says nothing about the others, and
					# phrasing differs per provider (Gemini's "no longer available"
					# once ended the run with flash and flash-lite never asked).
					nxt = _next_model(provider, p_model)
					if nxt:
						log.warning("%s model %s kept failing -- trying %s", provider, p_model, nxt)
						p_model = nxt
						attempt = 2  # exactly one attempt on each later model
						continue
					exhausted = True

			if exhausted and providers_to_try.index(provider) < len(providers_to_try) - 1:
				log.warning("LLM provider=%s exhausted -- trying fallback", provider)

		raise RuntimeError(f"{_ALL_PROVIDERS_FAILED}: {last_exc}") from last_exc

	def complete_for_role(
		self,
		role: str,
		prompt: str,
		system: str = "",
		max_tokens: int = 4096,
		temperature: float = 0.7,
		exclude: frozenset[str] = frozenset(),
	) -> LLMResponse:
		"""Route to the role's provider (GLM for every role, then Atria, then
        Anthropic/Gemini once those are absent or spent). Falls back to complete()
        with the default provider if the role's provider has no key."""
		preferred = self.provider_for_role(role)
		if preferred:
			log.info("Role=%s → provider=%s", role, preferred)
			old_provider = self.provider
			self.provider     = preferred
			try:
				return self.complete(prompt, system=system, max_tokens=max_tokens,
									temperature=temperature, exclude=exclude)
			finally:
				self.provider     = old_provider
		return self.complete(prompt, system=system, max_tokens=max_tokens,
							 temperature=temperature, exclude=exclude)

	def provider_for_role(self, role: str) -> str | None:
		"""
        The provider that will actually serve `role` right now, or None.

        ROLE_PROVIDER names GLM for every role, but that is the *preference*.
        Without GLM_API_KEY, or once GLM is latched off, the role is served by
        Atria, and without that by Anthropic or Gemini when their keys are set --
        and the dashboard must say so rather than advertise an engine that is not
        running.
        """
		preferred = ROLE_PROVIDER.get(role)
		if not preferred:
			return None
		key_map = {
			"glm":        "" if self._glm_disabled else self._glm_key,
			"atria":      "" if self._atria_disabled else self._atria_key,
			"gemini":     self._gemini_key,
			"anthropic":  self._anthropic_key,
		}
		if preferred == "glm" and not key_map["glm"]:
			preferred = "atria"
		if preferred == "atria" and not key_map["atria"]:
			# Atria absent or spent: whichever of anthropic/gemini has a key serves.
			preferred = next((p for p in ("anthropic", "gemini") if key_map[p]), "")
		return preferred if key_map.get(preferred) else None

	def _parse_json_walk(self, ask, label: str) -> dict[str, Any]:
		"""
		Ask until the answer parses, handing the prompt to the next provider
		when one keeps returning something unparseable.

		`ask(exclude)` returns an LLMResponse. Re-asking the same provider
		usually returns the same truncated or malformed text, and because that
		provider "succeeds" at the HTTP level, complete() would never reach the
		next one -- so after _JSON_ATTEMPTS_PER_PROVIDER bad answers it is
		excluded. complete() raises when no candidate is left, and that, not a
		counter, is what ends the walk.
		"""
		parse_exc: Exception | None = None
		bad: dict[str, int] = {}
		excluded: set[str] = set()
		while True:
			try:
				resp = ask(frozenset(excluded))
			except RuntimeError as exc:
				# Every remaining provider failed (or none is left). Keep the parse
				# error visible: it is why the earlier providers were dropped.
				detail = f"{parse_exc}; then {exc}" if parse_exc else str(exc)
				raise ValueError(f"Could not get valid JSON from LLM{label}: {detail}") from exc
			try:
				return parse_json(resp.text)
			except ValueError as exc:
				parse_exc = exc
				bad[resp.provider] = bad.get(resp.provider, 0) + 1
				log.warning("JSON%s: %s answered unparseable text (%d/%d): %s",
							label, resp.provider, bad[resp.provider], _JSON_ATTEMPTS_PER_PROVIDER, exc)
				if bad[resp.provider] >= _JSON_ATTEMPTS_PER_PROVIDER:
					excluded.add(resp.provider)
				time.sleep(1)

	def complete_json(
		self,
		prompt: str,
		system: str = "",
		max_tokens: int = 4096,
	) -> dict[str, Any]:
		"""
        Like complete() but parses the response as JSON.
        Appends a JSON-only instruction to the system prompt.
        Raises ValueError if no provider produces parseable JSON.
        """
		json_system = (
			(system + "\n\n" if system else "")
			+ "IMPORTANT: Respond with ONLY a single valid JSON object. "
			"No markdown, no code fences, no explanation before or after."
		)
		return self._parse_json_walk(
			lambda exclude: self.complete(
				prompt, system=json_system, max_tokens=max_tokens,
				temperature=0.2, exclude=exclude,
			),
			"",
		)

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
		return self._parse_json_walk(
			lambda exclude: self.complete_for_role(
				role, prompt, system=json_system, max_tokens=max_tokens,
				temperature=0.2, exclude=exclude,
			),
			f" (role={role})",
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
			text      = _require_text(
				msg.content[0].text if msg.content else "", "anthropic", model
			),
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
			text      = _require_text(rsp.text, "gemini", model),
			provider  = "gemini",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Atria -----------------------------------------------------------------

	def _latch_atria_off(self, reason: str) -> None:
		self._atria_disabled = True
		self._atria_disabled_reason = self._atria_disabled_reason or reason

	def engine_report(self) -> dict[str, Any]:
		"""
        What the main engine actually did this run, for status["llm_engine"].

        `key_set` answers "is GLM_API_KEY configured", `calls` answers "was it
        used" (responses each provider actually returned), and
        `disabled_reason` says why the run fell back when it did. `fallback`
        reports Atria the same way, since it serves whenever GLM does not.
        Read after the cycle's LLM work, so a quota spent mid-run is reported.
        """
		glm_set = bool(self._glm_key)
		glm_live = glm_set and not self._glm_disabled
		atria_set = bool(self._atria_key)
		atria_live = atria_set and not self._atria_disabled
		# First provider still usable, in fallback order -- never a latched one.
		chain = self._provider_chain()
		serving = chain[0] if chain else "none"
		return {
			"main_provider":   "glm",
			# The model the probe settled on, so a key that fell to the free
			# Flash tier says so instead of naming the model it was meant to use.
			"main_model":      self._glm_model or _GLM_MODELS[0],
			"preferred_model": _GLM_MODELS[0],
			"refused":         self._glm_refused[:8],
			"endpoint":        self._glm_endpoint,
			"key_set":         glm_set,
			"live":            glm_live,
			"serving":         serving,
			"disabled_reason": self._glm_disabled_reason if glm_set else "key_missing",
			"calls":           dict(self._served),
			"fallback": {
				"provider":        "atria",
				"model":           _ATRIA_MODELS[0],
				"key_set":         atria_set,
				"live":            atria_live,
				"disabled_reason": self._atria_disabled_reason if atria_set else "key_missing",
			},
		}

	# -- GLM -------------------------------------------------------------------

	def _latch_glm_off(self, reason: str) -> None:
		self._glm_disabled = True
		self._glm_disabled_reason = self._glm_disabled_reason or reason

	def _glm_post(self, endpoint: str, body: dict[str, Any]):
		import requests  # already in requirements
		return requests.post(
			f"{endpoint}/chat/completions",
			headers={
				"Authorization": f"Bearer {self._glm_key}",
				"Content-Type":  "application/json",
			},
			json=body,
			timeout=_GLM_TIMEOUT,
		)

	@staticmethod
	def _glm_error(rsp) -> tuple[str, str]:
		"""(business code, message) from a Z.ai error body, or ("", "")."""
		try:
			err = rsp.json().get("error") or {}
		except Exception:
			return "", ""
		if not isinstance(err, dict):
			return "", str(err)[:120]
		return str(err.get("code") or ""), str(err.get("message") or "")[:120]

	@staticmethod
	def _glm_thinking(model: str) -> dict:
		"""The lightest reasoning setting the model accepts."""
		if model.startswith(_GLM_ALWAYS_THINKS):
			return {"thinking": {"type": "enabled"}, "reasoning_effort": "low"}
		# Reasoning tokens count against max_tokens, which callers size for
		# the answer; with thinking on, long JSON plans came back cut.
		return {"thinking": {"type": "disabled"}}

	def _note_glm_refusal(self, endpoint: str, model: str, code: str, msg: str) -> None:
		self._glm_refused.append({"model": model, "endpoint": endpoint, "code": code, "message": msg})

	def _glm_failed_to_reach(self, why: str) -> RuntimeError:
		"""A timeout or outage. Two in one run latch GLM off for the rest of it."""
		self._glm_failures += 1
		if self._glm_failures >= _GLM_MAX_FAILURES:
			self._latch_glm_off("timeout" if "timed out" in why else "unreachable")
			log.warning("glm failed %d times -- routing the rest of this run to the fallback",
						self._glm_failures)
		return RuntimeError(f"{_GLM_SKIP_MARKER}: {why}")

	def _resolve_glm(self) -> None:
		"""
        Find the endpoint + model this key works on, once per run.

        Each probe is a one-word request capped at a few tokens, and an error
        answer is not billed, so the walk costs next to nothing. A 401 means the
        key belongs to another host; a 1113/1211/1311 means this model is not on
        the key's plan or balance, so the next (cheaper, then free) model is
        tried. Raises when nothing accepts the key, after latching GLM off.
        """
		import requests
		probe = {
			"messages":   [{"role": "user", "content": "ping"}],
			"max_tokens": 8,
		}
		host_accepted_key = False
		no_balance = False
		quota_hit = False
		for endpoint in _GLM_ENDPOINTS:
			for model in _GLM_MODELS:
				try:
					rsp = self._glm_post(endpoint, {**probe, **self._glm_thinking(model), "model": model})
				except requests.RequestException as exc:
					raise self._glm_failed_to_reach(f"probe of {endpoint} failed: {type(exc).__name__}") from exc
				code, msg = self._glm_error(rsp) if rsp.status_code != 200 else ("", "")
				if rsp.status_code == 200 or code in _GLM_TRANSIENT_CODES:
					# A rate limit still proves the key and model are valid here.
					self._glm_endpoint, self._glm_model = endpoint, model
					log.info("glm resolved -- endpoint=%s model=%s", endpoint, model)
					return
				if rsp.status_code in (401, 403) or code in _GLM_WRONG_HOST_CODES:
					break  # key belongs to another host; its models are moot
				host_accepted_key = True
				if rsp.status_code >= 500:
					raise self._glm_failed_to_reach(f"probe of {endpoint} answered {rsp.status_code}")
				if code in _GLM_NEXT_MODEL_CODES or rsp.status_code == 400:
					no_balance = no_balance or code == "1113"
					self._note_glm_refusal(endpoint, model, code or str(rsp.status_code), msg)
					continue
				# Any other 429: a usage or plan limit on this model. It is not a
				# verdict on the key -- the cheaper and free models further down
				# may sit outside that limit -- so record it and keep walking.
				# Latching on the first answer left 27 of 28 candidates unasked.
				quota_hit = True
				self._note_glm_refusal(endpoint, model, code or str(rsp.status_code), msg)
				continue
		if not host_accepted_key:
			self._latch_glm_off("auth_failed")
			raise RuntimeError("401 authentication_error from glm: no endpoint accepted the key")
		self._latch_glm_off("quota_spent" if (no_balance or quota_hit) else "model_not_found")
		raise RuntimeError(f"{_GLM_SKIP_MARKER}: no model in the chain is available to this key")

	def _call_glm(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		import requests
		if self._glm_disabled:
			# Latched mid-call (e.g. the last model ran out): stop stepping.
			raise RuntimeError(f"{_GLM_SKIP_MARKER}: off for this run ({self._glm_disabled_reason})")
		if self._glm_endpoint is None:
			self._resolve_glm()
		# Never go back up the chain past the model the key actually reaches.
		if model not in _GLM_MODELS or _GLM_MODELS.index(model) < _GLM_MODELS.index(self._glm_model):
			model = self._glm_model
		messages: list[dict] = []
		if system:
			messages.append({"role": "system", "content": system})
		messages.append({"role": "user", "content": prompt})
		if model.startswith(_GLM_ALWAYS_THINKS):
			max_tokens += _GLM_REASONING_HEADROOM
		t0 = time.monotonic()
		try:
			rsp = self._glm_post(self._glm_endpoint, {
				"model":       model,
				"messages":    messages,
				"max_tokens":  max_tokens,
				"temperature": temperature,
				**self._glm_thinking(model),
			})
		except requests.Timeout as exc:
			raise self._glm_failed_to_reach(f"timed out after {_GLM_TIMEOUT[1]}s") from exc
		except requests.RequestException as exc:
			raise self._glm_failed_to_reach(f"request failed: {type(exc).__name__}") from exc

		if rsp.status_code != 200:
			code, msg = self._glm_error(rsp)
			if rsp.status_code in (401, 403) or code in _GLM_WRONG_HOST_CODES:
				self._latch_glm_off("auth_failed")
				raise RuntimeError(f"401 authentication_error from glm: code {code} {msg}")
			if code in _GLM_TRANSIENT_CODES:
				raise RuntimeError(f"429 rate_limit_exceeded from glm: code {code}")
			spent = rsp.status_code == 429 and code not in _GLM_NEXT_MODEL_CODES
			if code in _GLM_NEXT_MODEL_CODES or spent:
				# Balance, plan or usage limit no longer covers this model: step
				# down for the rest of the run, so later calls do not re-hit the
				# same wall. A spent limit steps down too -- the free models at the
				# end of the chain may still answer -- and only the last model
				# running out turns GLM off. The message avoids "429" on purpose:
				# complete() reads that as "skip the provider", and this is the
				# case where the next model is still worth a call.
				self._note_glm_refusal(self._glm_endpoint, model, code or "429", msg)
				idx = _GLM_MODELS.index(model)
				if idx == len(_GLM_MODELS) - 1:
					self._latch_glm_off("quota_spent" if spent else "model_not_found")
				else:
					self._glm_model = _GLM_MODELS[idx + 1]
				raise RuntimeError(
					f"model_not_found on glm: {model} (code {code or 'none'}"
					f"{', usage spent' if spent else ''})"
				)
			if rsp.status_code == 400:
				# Prompt too long, content flagged, bad parameter: this request
				# fails identically on retry, but another provider may take it.
				raise RuntimeError(f"{_GLM_SKIP_MARKER}: glm refused the request (code {code}: {msg})")
			raise RuntimeError(f"GLM HTTP {rsp.status_code} (code {code})")

		data = rsp.json()
		if not data.get("choices"):
			raise RuntimeError(f"GLM returned no choices for {model}: {str(data)[:200]}")
		choice  = data["choices"][0]
		message = choice.get("message") or {}
		content = message.get("content")
		if not (content and content.strip()):
			log.warning(
				"glm returned no content: finish_reason=%s message_fields=%s usage=%s",
				choice.get("finish_reason"),
				{k: len(v) if isinstance(v, str) else type(v).__name__ for k, v in message.items()},
				data.get("usage"),
			)
		return LLMResponse(
			text      = _require_text(content, "glm", model),
			provider  = "glm",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	def _call_atria(
		self, prompt: str, system: str, max_tokens: int, temperature: float, model: str
	) -> LLMResponse:
		import requests  # already in requirements
		messages: list[dict] = []
		if system:
			messages.append({"role": "system", "content": system})
		messages.append({"role": "user", "content": prompt})
		t0  = time.monotonic()
		try:
			rsp = requests.post(
				f"{_ATRIA_BASE_URL}/chat/completions",
				headers={
					"Authorization": f"Bearer {self._atria_key}",
					"Content-Type":  "application/json",
				},
				json={
					"model":       model,
					"messages":    messages,
					"max_tokens":  max_tokens,
					"temperature": temperature,
				},
				timeout=_ATRIA_TIMEOUT,
			)
		except requests.Timeout as exc:
			self._atria_timeouts += 1
			if self._atria_timeouts >= _ATRIA_MAX_TIMEOUTS:
				self._latch_atria_off("timeout")
				log.warning("atria timed out %d times -- routing the rest of this run to the next provider",
							self._atria_timeouts)
			raise RuntimeError(
				f"{_ATRIA_TIMEOUT_MARKER}: no answer from atria within {_ATRIA_TIMEOUT[1]}s"
			) from exc
		if rsp.status_code in (401, 403):
			self._latch_atria_off("auth_failed")
			raise RuntimeError(f"401 authentication_error from atria: {rsp.text[:200]}")
		if rsp.status_code == 429:
			# A per-minute limit sends Retry-After and recovers within the cycle.
			# Without it, or with a body naming a quota, the free allowance is
			# spent: stop asking for the rest of this run and use the next provider.
			body = rsp.text[:200]
			if "Retry-After" not in rsp.headers or re.search(r"quota|balance|insufficient", body, re.I):
				self._latch_atria_off("quota_spent")
				log.warning("atria quota appears spent -- routing the rest of this run to the next provider")
				raise RuntimeError(f"429 quota_exceeded from atria: {body}")
			raise RuntimeError(f"429 rate_limit_exceeded from atria: {body}")
		if rsp.status_code == 404:
			# Atria serves one model; if it is gone, every later call would 404 too.
			self._latch_atria_off("model_not_found")
			raise RuntimeError(f"model_not_found on atria: {model}: {rsp.text[:200]}")
		rsp.raise_for_status()
		data = rsp.json()
		if "error" in data:
			raise RuntimeError(f"Atria error: {data['error']}")
		if not data.get("choices"):
			raise RuntimeError(f"Atria returned no choices for {model}: {str(data)[:200]}")
		choice  = data["choices"][0]
		message = choice.get("message") or {}
		content = message.get("content")
		if not (content and content.strip()):
			# The chain has one model, so complete() logs only "chain exhausted";
			# record why the answer was empty. Field names and sizes, never text.
			log.warning(
				"atria returned no content: finish_reason=%s message_fields=%s usage=%s",
				choice.get("finish_reason"),
				{k: len(v) if isinstance(v, str) else type(v).__name__ for k, v in message.items()},
				data.get("usage"),
			)
		text = _require_text(content, "atria", model)
		return LLMResponse(
			text      = text,
			provider  = "atria",
			model     = model,
			latency_s = round(time.monotonic() - t0, 2),
		)

	# -- Helpers ---------------------------------------------------------------

	def _pick_provider(self) -> str:
		# GLM first, then Atria (~1B free tokens), then Anthropic, then Gemini.
		if self._glm_key:
			return "glm"
		if self._atria_key:
			return "atria"
		if self._anthropic_key:
			return "anthropic"
		if self._gemini_key:
			return "gemini"
		raise RuntimeError(
			"No LLM API key found.\n"
			"Add one of: GLM_API_KEY, ATRIA_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY\n"
			"to GitHub -> Settings -> Secrets and variables -> Actions."
		)

	def _pick_model(self) -> str:
		return self._model_for_provider(self.provider)

	def _model_for_provider(self, provider: str) -> str:
		if provider == "glm":
			return self._glm_model or _GLM_MODELS[0]
		if provider == "atria":
			return _ATRIA_MODELS[0]
		if provider == "anthropic":
			return _ANTHROPIC_MODELS[0]
		if provider == "gemini":
			return _GEMINI_MODELS[0]
		raise ValueError(f"unknown LLM provider: {provider!r}")

	def _provider_chain(self) -> list[str]:
		"""Ordered fallback chain starting from primary provider."""
		all_providers = [
			("glm",          bool(self._glm_key) and not self._glm_disabled),
			("atria",       bool(self._atria_key) and not self._atria_disabled),
			("anthropic",    bool(self._anthropic_key)),
			("gemini",       bool(self._gemini_key)),
		]
		available = [p for p, has_key in all_providers if has_key]
		# Ensure primary is first
		if self.provider in available:
			available.remove(self.provider)
			available.insert(0, self.provider)
		return available


def _next_model(provider: str, model: str) -> str | None:
	"""The model after `model` in the provider's chain, or None at the end."""
	chain = _model_list_for(provider)
	if model in chain and chain.index(model) < len(chain) - 1:
		return chain[chain.index(model) + 1]
	return None


def _model_list_for(provider: str) -> list[str]:
	return {
		"glm":         _GLM_MODELS,
		"atria":       _ATRIA_MODELS,
		"anthropic":   _ANTHROPIC_MODELS,
		"gemini":      _GEMINI_MODELS,
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
		obj = json.loads(text)
		# A bare list parses fine but every caller does plan.get(...), so
		# returning it swaps a handled ValueError for an AttributeError crash.
		if isinstance(obj, dict):
			return obj
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

		recovered = _recover_truncated(text[start:])
		if recovered is not None:
			log.warning(
				"Recovered truncated JSON (%d chars, kept keys: %s)",
				len(text), sorted(recovered),
			)
			return recovered

	# Distinguish the two failure modes: a response that opens as a JSON object
	# but never closes was cut off by max_tokens, and the fix is a bigger output
	# budget or a smaller ask -- not a better prompt. Saying "no valid JSON"
	# for both sent the last diagnosis down the wrong path.
	if start != -1 and text.rstrip().endswith("}") is False:
		raise ValueError(
			f"Truncated JSON in LLM response ({len(text)} chars, unterminated) "
			f"-- response likely hit max_tokens. First 200 chars: {text[:200]!r}"
		)
	raise ValueError(f"No valid JSON object found in LLM response. First 200 chars: {text[:200]!r}")


def _recover_truncated(text: str) -> dict[str, Any] | None:
	"""
    Salvage a JSON object that was cut off by the model hitting max_tokens.

    The response is well-formed up to the cut, so walk the string, remember the
    last position where the object was closable at depth 1 (a completed
    top-level value), and re-parse the prefix with the closing braces added.
    Half-written values are dropped rather than guessed at.

    Returns None when nothing complete survives.
    """
	depth       = 0
	in_string   = False
	escaped     = False
	# Position just after the last complete top-level key/value pair.
	last_good   = -1
	# Stack of container chars so a cut inside a list closes as a list.
	stack: list[str] = []

	for i, ch in enumerate(text):
		if in_string:
			if escaped:
				escaped = False
			elif ch == "\\":
				escaped = True
			elif ch == '"':
				in_string = False
			continue

		if ch == '"':
			in_string = True
		elif ch in "{[":
			stack.append(ch)
			depth += 1
		elif ch in "}]":
			if not stack:
				break
			stack.pop()
			depth -= 1
			if depth in (1, 2):
				# depth 1: a completed top-level value.
				# depth 2: a completed element of a top-level array -- keeping
				# these is the point, since a cut inside changes[1] must not
				# throw away the complete changes[0].
				last_good = i + 1
			elif depth == 0:
				# A complete object -- raw_decode already handles this case.
				last_good = i + 1
				break
		elif ch == "," and depth in (1, 2):
			last_good = i

	if last_good <= 0:
		return None

	prefix = text[:last_good].rstrip().rstrip(",")
	# Close whatever containers were still open at the cut, innermost first.
	depth_at_cut = 0
	in_string    = False
	escaped      = False
	closers: list[str] = []
	for ch in prefix:
		if in_string:
			if escaped:
				escaped = False
			elif ch == "\\":
				escaped = True
			elif ch == '"':
				in_string = False
			continue
		if ch == '"':
			in_string = True
		elif ch == "{":
			closers.append("}")
		elif ch == "[":
			closers.append("]")
		elif ch in "}]":
			if closers:
				closers.pop()

	candidate = prefix + "".join(reversed(closers))
	try:
		obj = json.loads(candidate)
	except json.JSONDecodeError:
		return None
	return obj if isinstance(obj, dict) else None
