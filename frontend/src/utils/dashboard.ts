import { ageLabel } from './format';
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
	const failed = (status.last_earning?.actions || []).filter((action) => action.success === false);
	for (const action of failed.slice(0, 3)) {
		issues.push({
			tone: 'warn',
			label: 'module',
			title: `${action.platform || 'module'} action failed`,
			detail: action.error || action.title || 'Inspect module output.',
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
	if (!issues.length) {
		issues.push({
			tone: 'good',
			label: 'clear',
			title: 'Nothing needs attention',
			detail: 'Cycle freshness, integrations, and the latest actions all look healthy.',
		});
	}
	return issues.slice(0, 6);
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
	if ((status.last_earning?.actions || []).some((action) => action.success === false)) {
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
