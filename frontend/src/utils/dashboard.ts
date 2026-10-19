import { ageLabel } from './format';
import { atriaState } from './engine';
import type { CodeTechOpportunity, Status } from '../types/status';

export type Tone = 'good' | 'warn' | 'bad' | 'info' | 'neutral';

export type Issue = {
	tone: 'good' | 'warn' | 'bad' | 'info';
	label: string;
	title: string;
	detail: string;
	/** Where to go to act on this. */
	section?: string;
};

/** Human wording for `articles._reject` codes (status.article_rejects). */
export const REJECT_LABELS: Record<string, string> = {
	no_llm: 'no LLM available',
	no_source: 'no fresh source',
	llm_error: 'LLM call failed',
	empty_draft: 'model returned nothing',
	fabricated: 'invented figures',
	weak_title: 'title too weak',
	revision_fabricated: 'revision invented figures',
	duplicate: 'duplicate of a past post',
	too_similar: 'too close to the source',
};

export function rejectLabel(code?: string): string {
	return (code && REJECT_LABELS[code]) || (code || 'unknown').replace(/_/g, ' ');
}

/** A gate refusing a draft is the system working, not a module breaking. */
function isFailure(action: { success?: boolean; skipped?: boolean }): boolean {
	return action.success === false && !action.skipped;
}

export function buildIssues(status: Status): Issue[] {
	const issues: Issue[] = [];
	const fresh = ageLabel(status.last_run);
	if (fresh.tone !== 'good') {
		issues.push({
			tone: fresh.tone,
			label: fresh.tone === 'bad' ? 'urgent' : 'watch',
			title: 'Cycle is behind schedule',
			detail: `Latest run is ${fresh.label}. Check GitHub Actions if this is unexpected.`,
			section: 'health',
		});
	}
	if (status.payout && status.payout.live === false) {
		issues.push({
			tone: 'bad',
			label: 'zero',
			title: 'No way to pay is being published',
			detail: `${status.payout.blocked_reason || 'The receive path is off'}. Every view is multiplied by zero.`,
			section: 'reach',
		});
	}
	const gap = status.receipt_check?.known_without_footer ?? status.receipt_check?.without_footer ?? 0;
	if (gap > 0) {
		issues.push({
			tone: 'bad',
			label: 'gap',
			title: `${gap} published post${gap === 1 ? '' : 's'} show readers no way to pay`,
			detail: 'Observed by re-reading the live posts, not taken from the bot’s own report.',
			section: 'reach',
		});
	}
	if (status.last_evolution?.error) {
		issues.push({
			tone: 'bad',
			label: 'repair',
			title: 'Evolution failed',
			detail: status.last_evolution.error,
			section: 'engine',
		});
	}
	for (const error of status.errors || []) {
		issues.push({ tone: 'bad', label: 'error', title: 'Cycle error', detail: error, section: 'health' });
	}
	const atria = atriaState(status);
	if (atria.tone === 'warn') {
		issues.push({ tone: 'warn', label: 'engine', title: atria.label, detail: atria.detail, section: 'engine' });
	}
	const actions = status.last_earning?.actions || [];
	for (const action of actions.filter(isFailure).slice(0, 3)) {
		issues.push({
			tone: 'warn',
			label: 'module',
			title: `${action.platform || 'module'} action failed`,
			detail: action.error || action.title || 'Inspect module output.',
			section: 'engine',
		});
	}
	const held = actions.find((action) => action.skipped);
	if (held) {
		issues.push({
			tone: 'info',
			label: 'held',
			title: 'Latest draft was held back',
			detail: `${rejectLabel(held.reject_code)}: a quality gate refused it, so nothing weak was published.`,
			section: 'reach',
		});
	}
	if (status.evolution_pending_review && status.last_evolution_branch) {
		issues.push({
			tone: 'info',
			label: 'review',
			title: 'A code proposal is waiting for review',
			detail: `${status.last_evolution_branch}. Nothing reaches main until you merge it.`,
			section: 'engine',
		});
	}
	const readiness = buildReadiness(status);
	if (readiness.total && readiness.percent < 60) {
		issues.push({
			tone: 'warn',
			label: 'setup',
			title: 'Integration readiness is low',
			detail: `${readiness.ready} of ${readiness.total} integrations are fully configured.`,
			section: 'health',
		});
	}
	const stale = staleHours(status.code_tech_earning?.last_refresh_at, status.code_tech_earning?.refresh_hours);
	if (stale) {
		issues.push({
			tone: 'warn',
			label: 'research',
			title: 'Lead queue is stale',
			detail: `Last refresh was ${stale}h ago; the queue refreshes every ${status.code_tech_earning?.refresh_hours || 24}h.`,
			section: 'leads',
		});
	}
	if (!issues.some((issue) => issue.tone !== 'info')) {
		issues.unshift({
			tone: 'good',
			label: 'clear',
			title: 'Nothing is broken',
			detail: 'Cycle freshness, the receive path, and the latest actions all look healthy.',
		});
	}
	return issues.slice(0, 6);
}

export type PhaseResult = { name: string; tone: 'good' | 'warn' | 'bad' | 'info'; detail: string };

/** The five phases of the last cycle, shared by Overview and Health. */
export function buildPhases(status: Status): PhaseResult[] {
	const evolution = status.last_evolution || {};
	const actions = status.last_earning?.actions || [];
	const errors = status.errors || [];
	const failed = actions.filter(isFailure).length;
	const held = actions.filter((action) => action.skipped).length;

	let evolutionPhase: PhaseResult;
	if (evolution.error) evolutionPhase = { name: 'Evolution', tone: 'bad', detail: 'failed' };
	else if (status.evolution_pending_review) evolutionPhase = { name: 'Evolution', tone: 'good', detail: 'proposal in review' };
	else if ((evolution.summary || '').toLowerCase().includes('skip')) evolutionPhase = { name: 'Evolution', tone: 'info', detail: 'skipped' };
	else evolutionPhase = { name: 'Evolution', tone: 'info', detail: 'no proposal' };

	return [
		{ name: 'Status', tone: status.last_run ? 'good' : 'bad', detail: status.last_run ? 'loaded' : 'never ran' },
		{ name: 'Commands', tone: 'good', detail: 'queue read' },
		evolutionPhase,
		{
			name: 'Research',
			tone: failed ? 'warn' : held ? 'info' : 'good',
			detail: failed ? `${failed} failed` : held ? 'draft held back' : `${actions.length} action${actions.length === 1 ? '' : 's'}`,
		},
		{ name: 'Update', tone: errors.length ? 'bad' : 'good', detail: errors.length ? `${errors.length} errors` : 'saved' },
	];
}

/**
 * Reader -> ask -> wallet: the three stages of the only channel that earns.
 *
 * `$0.00` has to say why, because the two causes need opposite fixes: nobody
 * tipped (a conversion question) or no ask shipped (a structural zero).
 */
export function buildFunnel(status: Status) {
	const stats = status.article_stats || {};
	const check = status.receipt_check || {};
	const views = stats.total_views || 0;
	const posts = stats.count || check.published_total || 0;
	const published = check.published_total || posts;
	const gap = check.known_without_footer ?? check.without_footer ?? 0;
	const covered = check.covered || 0;
	const withAsk = Math.max(0, covered - gap);
	const received = status.wallet?.received_total_usd ?? status.earnings?.received_total_usd ?? 0;
	const live = status.payout?.live === true;
	const complete = check.coverage_complete === true;
	const unverified = check.unverified || 0;

	let verdict: { tone: 'good' | 'warn' | 'bad' | 'info'; text: string };
	if (received > 0) {
		verdict = { tone: 'good', text: 'Readers have paid. The on-chain balance is the only figure counted as earned.' };
	} else if (!live) {
		verdict = { tone: 'bad', text: 'No ask is being published, so every view is multiplied by zero.' };
	} else if (gap > 0) {
		verdict = { tone: 'warn', text: `${gap} post${gap === 1 ? '' : 's'} still show no ask. Those readers cannot pay.` };
	} else if (complete) {
		verdict = { tone: 'info', text: 'Every published post shows a way to pay, and nobody has tipped yet. The path works, so this is a conversion question rather than a broken pipe.' };
	} else {
		verdict = { tone: 'info', text: `The ask ships on new posts; ${unverified} older post${unverified === 1 ? '' : 's'} not yet re-read. Unverified is not the same as fine.` };
	}

	return { views, posts, published, withAsk, covered, gap, received, live, complete, verdict };
}

function staleHours(lastRefresh?: string, refreshHours = 24): number | null {
	if (!lastRefresh) return null;
	const date = new Date(lastRefresh);
	if (Number.isNaN(date.getTime())) return null;
	const hours = Math.floor((Date.now() - date.getTime()) / 3_600_000);
	return hours > refreshHours * 1.5 ? hours : null;
}

export function buildReadiness(status: Status) {
	const entries = Object.values(status.secret_readiness || {});
	if (!entries.length) return { ready: 0, total: 0, percent: 0 };
	const ready = entries.filter((info) => {
		const required = info.required_count || Math.max(1, info.present_count || 0);
		return (info.present_count || 0) >= required;
	}).length;
	return { ready, total: entries.length, percent: Math.round((ready / entries.length) * 100) };
}

/**
 * Lead counts for the KPI row.
 *
 * Deliberately returns no money aggregate. It used to sum
 * `estimated_value_usd` into an `estimatedValue` shown as "Pipeline value
 * $5.6k" beside the real on-chain balance of $0.00 -- and those inputs were
 * regex-scraped from unrelated text. Even with only genuine figures a sum
 * would be meaningless: the leads mix hourly, monthly and annual rates, so
 * they are not additive.
 */
export function buildOpportunityStats(opportunities: CodeTechOpportunity[]) {
	const fresh = opportunities.filter(
		(opportunity) => typeof opportunity.age_hours === 'number' && opportunity.age_hours <= 24,
	);
	// `demand`/`supply` are the pre-rename aliases; a committed snapshot from
	// before the rename still carries them, so both are counted as one thing.
	const channels = opportunities.filter(
		(opportunity) => opportunity.kind === 'channel' || opportunity.kind === 'demand',
	);
	// Free to list. `0` is a real value for a cost, so it is compared
	// explicitly rather than being caught by a falsy check.
	const free = opportunities.filter((opportunity) => opportunity.cost_usd === 0);
	// The honest cost of this page: a channel is not live until the owner has
	// done its one-time step, so the count is shown rather than implied.
	const needsSetup = opportunities.filter((opportunity) => {
		const setup = (opportunity.manual_setup || '').trim();
		return setup !== '' && !setup.toLowerCase().startsWith('none');
	});
	return {
		total: opportunities.length,
		freshCount: fresh.length,
		channelCount: channels.length,
		assetCount: opportunities.length - channels.length,
		freeCount: free.length,
		needsSetupCount: needsSetup.length,
		topScore: opportunities.reduce((top, opportunity) => Math.max(top, opportunity.score || 0), 0),
		pursued: opportunities.filter((opportunity) => opportunity.pursued).length,
	};
}

export function buildHealth(
	status: Status,
	issues: Array<{ tone: string }>,
	readinessPercent: number,
): { tone: 'good' | 'warn' | 'bad' | 'info'; label: string } {
	if (issues.some((issue) => issue.tone === 'bad')) return { tone: 'bad', label: 'attention required' };
	if (ageLabel(status.last_run).tone !== 'good') return { tone: 'warn', label: 'stale cycle' };
	if (readinessPercent < 60) return { tone: 'warn', label: 'setup incomplete' };
	if ((status.last_earning?.actions || []).some(isFailure)) {
		return { tone: 'warn', label: 'module warning' };
	}
	return { tone: 'good', label: 'operational' };
}

/** Distinct lead sources with counts, for the Leads filter bar. */
export function leadSources(opportunities: CodeTechOpportunity[]): Array<{ key: string; count: number }> {
	const counts = new Map<string, number>();
	for (const opportunity of opportunities) {
		const key = opportunity.source || 'unknown';
		counts.set(key, (counts.get(key) || 0) + 1);
	}
	return [...counts.entries()]
		.map(([key, count]) => ({ key, count }))
		.sort((a, b) => b.count - a.count);
}

export type LeadSort = 'newest' | 'score' | 'cost';

/** Older-is-larger, so an unknown age sorts as the oldest thing on the page. */
function ageOf(lead: CodeTechOpportunity): number {
	return typeof lead.age_hours === 'number' ? lead.age_hours : Number.POSITIVE_INFINITY;
}

export function sortLeads(opportunities: CodeTechOpportunity[], sort: LeadSort): CodeTechOpportunity[] {
	const copy = [...opportunities];
	if (sort === 'newest') {
		copy.sort((a, b) => ageOf(a) - ageOf(b) || (b.score || 0) - (a.score || 0));
	} else if (sort === 'cost') {
		// Cheapest first, because zero budget is the constraint. A lead with
		// no published cost sorts last rather than as free -- unknown is not
		// the same as $0, the same distinction `_cost` vs `_money` makes in
		// the Python.
		const costOf = (lead: CodeTechOpportunity) =>
			typeof lead.cost_usd === 'number' ? lead.cost_usd : Number.POSITIVE_INFINITY;
		copy.sort((a, b) => costOf(a) - costOf(b) || (b.score || 0) - (a.score || 0));
	} else {
		copy.sort((a, b) => (b.score || 0) - (a.score || 0) || ageOf(a) - ageOf(b));
	}
	return copy;
}
