import type { Tone } from '../components/ui';
import type { Status } from '../types/status';

/** Names and secrets for engines that can lead (`llm_engine.main_provider`). */
const ENGINES: Record<string, { name: string; secret: string; model: string }> = {
	glm: { name: 'GLM', secret: 'GLM_API_KEY', model: 'glm-5.3-flash' },
	atria: { name: 'Atria', secret: 'ATRIA_API_KEY', model: 'Atria-Dawn' },
};

function reasonText(code: string, name: string, secret: string): string {
	const reasons: Record<string, string> = {
		key_missing: `${secret} is not set`,
		auth_failed: `${name} rejected the key (401/403)`,
		quota_spent: `${name} quota or balance spent this cycle`,
		model_not_found: `${name} model unavailable to this key`,
		timeout: `${name} timed out twice this cycle`,
		unreachable: `${name} unreachable twice this cycle`,
	};
	return reasons[code] || code;
}

export type EngineState = {
	/** Provider id of the main engine (glm; atria on snapshots before GLM). */
	provider: string;
	name: string;
	secret: string;
	model: string;
	/** Resolved GLM host, e.g. https://api.z.ai/api/paas/v4; null until probed. */
	endpoint: string | null;
	/** null = this snapshot cannot tell. */
	keySet: boolean | null;
	live: boolean | null;
	serving: string;
	reason: string | null;
	calls: Record<string, number>;
	label: string;
	tone: Tone;
	detail: string;
	/** The engine that serves when the main one cannot (Atria behind GLM). */
	fallback: { name: string; model: string; keySet: boolean | null; live: boolean | null; reason: string | null } | null;
};

/**
 * The main engine's real state, read from what the cycle observed
 * (status.llm_engine) rather than from the routing preference. A snapshot
 * written before GLM led reports main_provider "atria" and renders as Atria.
 */
export function engineState(status: Status): EngineState {
	const engine = status.llm_engine;
	const provider = engine?.main_provider || 'glm';
	const meta = ENGINES[provider] || { name: provider, secret: `${provider.toUpperCase()}_API_KEY`, model: provider };
	const { name, secret } = meta;
	const model = engine?.main_model || meta.model;
	const calls = engine?.calls || {};

	let keySet: boolean | null = null;
	if (typeof engine?.key_set === 'boolean') keySet = engine.key_set;
	else if ((status.active_features || []).includes(`llm_${provider}`) || (status.configured_github_secrets || []).includes(secret)) keySet = true;
	else if ((status.inactive_features || []).includes(`llm_${provider}`)) keySet = false;

	const live = typeof engine?.live === 'boolean' ? engine.live : keySet === false ? false : null;
	const reasonCode = engine?.disabled_reason || (keySet === false ? 'key_missing' : null);
	const reason = reasonCode ? reasonText(reasonCode, name, secret) : null;
	const serving = engine?.serving || status.llm_provider || 'unknown';
	const mainCalls = calls[provider] || 0;
	const totalCalls = Object.values(calls).reduce((sum, n) => sum + n, 0);

	const fb = engine?.fallback;
	const fbMeta = fb?.provider ? ENGINES[fb.provider] : undefined;
	const fallback = fb
		? {
				name: fbMeta?.name || fb.provider || 'fallback',
				model: fb.model || fbMeta?.model || '',
				keySet: typeof fb.key_set === 'boolean' ? fb.key_set : null,
				live: typeof fb.live === 'boolean' ? fb.live : null,
				reason: fb.disabled_reason ? reasonText(fb.disabled_reason, fbMeta?.name || 'fallback', fbMeta?.secret || 'key') : null,
			}
		: null;
	const base = { provider, name, secret, model, endpoint: engine?.endpoint || null, keySet, live, reason, calls, fallback };

	// `live` only means the engine was not latched off. A call that times out
	// or comes back empty falls through without latching, so a cycle can end
	// "live" with the main engine having answered nothing -- cycle #2004 did,
	// 0 of 2. Built is not live; neither is configured.
	if (live === true && totalCalls > 0 && mainCalls === 0) {
		const busiest = Object.entries(calls).sort((a, b) => b[1] - a[1])[0]?.[0];
		return { ...base, serving: busiest || serving, label: `${name} not answering`, tone: 'warn', detail: `key set, but answered 0 of ${totalCalls} calls — the fallback served all of them` };
	}
	if (live === true) {
		return { ...base, serving, label: `${name} live`, tone: 'good', detail: totalCalls ? `answered ${mainCalls} of ${totalCalls} calls last cycle` : 'key set · no LLM calls last cycle' };
	}
	if (live === false) {
		return { ...base, serving, label: `${name} fallback`, tone: 'warn', detail: `${reason || 'not serving'} — roles ran on ${serving}` };
	}
	return {
		...base,
		serving,
		label: `${name} not reported`,
		tone: 'neutral',
		detail: keySet ? `${secret} set — usage appears after the next cycle` : `snapshot predates ${name} — next cycle will report it`,
	};
}
