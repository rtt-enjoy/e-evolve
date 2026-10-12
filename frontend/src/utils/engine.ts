import type { Tone } from '../components/ui';
import type { Status } from '../types/status';

const MAIN_MODEL = 'Atria-Dawn-Preview';

const REASONS: Record<string, string> = {
	key_missing: 'ATRIA_API_KEY is not set',
	auth_failed: 'Atria rejected the key (401/403)',
	quota_spent: 'Atria free quota spent this cycle',
	model_not_found: 'Atria model withdrawn (404)',
};

export type AtriaState = {
	model: string;
	/** null = this snapshot cannot tell (written before Atria was wired in). */
	keySet: boolean | null;
	live: boolean | null;
	serving: string;
	reason: string | null;
	calls: Record<string, number>;
	label: string;
	tone: Tone;
	detail: string;
};

/**
 * Atria's real state, read from what the cycle observed (status.llm_engine)
 * rather than from the routing preference. An older snapshot without that
 * field reads as "not reported", never as some other engine being main.
 */
export function atriaState(status: Status): AtriaState {
	const engine = status.llm_engine;
	const model = engine?.main_model || MAIN_MODEL;
	const calls = engine?.calls || {};

	let keySet: boolean | null = null;
	if (typeof engine?.key_set === 'boolean') keySet = engine.key_set;
	else if ((status.active_features || []).includes('llm_atria') || (status.configured_github_secrets || []).includes('ATRIA_API_KEY')) keySet = true;
	else if ((status.inactive_features || []).includes('llm_atria')) keySet = false;

	const live = typeof engine?.live === 'boolean' ? engine.live : keySet === false ? false : null;
	const reasonCode = engine?.disabled_reason || (keySet === false ? 'key_missing' : null);
	const reason = reasonCode ? REASONS[reasonCode] || reasonCode : null;
	const serving = engine?.serving || (keySet === false ? 'openrouter' : status.llm_provider || 'unknown');
	const atriaCalls = calls.atria || 0;
	const totalCalls = Object.values(calls).reduce((sum, n) => sum + n, 0);

	if (live === true) {
		return { model, keySet, live, serving, reason, calls, label: 'Atria live', tone: 'good', detail: `key set · answered ${atriaCalls} of ${totalCalls} calls last cycle` };
	}
	if (live === false) {
		return { model, keySet, live, serving, reason, calls, label: 'Atria fallback', tone: 'warn', detail: `${reason || 'not serving'} — roles ran on ${serving}` };
	}
	return {
		model, keySet, live, serving, reason, calls,
		label: 'Atria not reported',
		tone: 'neutral',
		detail: keySet ? 'ATRIA_API_KEY set — usage appears after the next cycle' : 'snapshot predates Atria — next cycle will report it',
	};
}
