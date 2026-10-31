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
	/**
	 * Why `model` is not the chain's lead, when it is not: the key was refused
	 * on the lead model, or the snapshot was written by code that led with a
	 * different one. null when the lead model is the one serving.
	 */
	modelNote: string | null;
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
	const preferred = engine?.preferred_model || null;
	let modelNote: string | null = null;
	if (preferred && model !== preferred) {
		const refusal = (engine?.refused || []).find((row) => row.model === preferred);
		modelNote = refusal
			? `${preferred} refused by this key (code ${refusal.code || '?'}${refusal.message ? `: ${refusal.message}` : ''}) — running on ${model}`
			: `${preferred} is first in the chain — running on ${model}`;
	} else if (engine && !preferred && model !== meta.model) {
		// Written before the bot reported its preferred model, i.e. before
		// meta.model led the chain: the next cycle replaces this value.
		modelNote = `Snapshot predates the ${meta.model} lead — the next cycle reports it`;
	}
	const base = { provider, name, secret, model, modelNote, endpoint: engine?.endpoint || null, keySet, live, reason, calls, fallback };

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

export type ChainStep = {
	name: string;
	model: string;
	/** Short state word shown beside the step. */
	state: string;
	tone: Tone;
	calls: number;
};

/**
 * The order every role tries engines in, each with what it did last cycle:
 * GLM, then Atria, then OpenRouter's free router.
 */
export function engineChain(status: Status, engine: EngineState): ChainStep[] {
	const calls = engine.calls;
	const totalCalls = Object.values(calls).reduce((sum, n) => sum + n, 0);
	const mainCalls = calls[engine.provider] || 0;
	const main: ChainStep = {
		name: engine.name,
		model: engine.model,
		calls: mainCalls,
		...(engine.keySet === false
			? { state: 'key not set', tone: 'bad' as Tone }
			: engine.live === false
				? { state: 'off this cycle', tone: 'warn' as Tone }
				: engine.live === true && totalCalls > 0 && mainCalls === 0
					? { state: 'not answering', tone: 'warn' as Tone }
					: engine.live === true
						? { state: mainCalls ? 'serving' : 'ready', tone: 'good' as Tone }
						: { state: 'not reported', tone: 'neutral' as Tone }),
	};
	const steps = [main];

	const fb = engine.fallback;
	if (fb) {
		const fbProvider = status.llm_engine?.fallback?.provider || 'atria';
		const n = calls[fbProvider] || 0;
		steps.push({
			name: fb.name,
			model: fb.model,
			calls: n,
			...(fb.keySet === false
				? { state: 'key not set', tone: 'neutral' as Tone }
				: fb.live === false
					? { state: 'off this cycle', tone: 'warn' as Tone }
					: n
						? { state: 'served', tone: 'info' as Tone }
						: { state: 'standby', tone: 'neutral' as Tone }),
		});
	}

	const flow = Object.values(status.llm_workflows || {})[0];
	const lastModel = flow?.last_resort_model || 'openrouter/free';
	const n = calls.openrouter || 0;
	steps.push({ name: 'OpenRouter', model: lastModel, calls: n, state: n ? 'served' : 'standby', tone: n ? 'info' : 'neutral' });
	return steps;
}
