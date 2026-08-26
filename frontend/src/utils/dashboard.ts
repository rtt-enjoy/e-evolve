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

export function buildOpportunityStats(opportunities: CodeTechOpportunity[]) {
	const values = opportunities.map((opportunity) => opportunity.estimated_value_usd || 0);
	return {
		total: opportunities.length,
		paidCount: values.filter((value) => value > 0).length,
		estimatedValue: values.reduce((sum, value) => sum + value, 0),
		topValue: values.reduce((top, value) => Math.max(top, value), 0),
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

export type LeadSort = 'value' | 'score';

export function sortLeads(opportunities: CodeTechOpportunity[], sort: LeadSort): CodeTechOpportunity[] {
	const copy = [...opportunities];
	if (sort === 'value') {
		copy.sort((a, b) => (b.estimated_value_usd || 0) - (a.estimated_value_usd || 0) || (b.score || 0) - (a.score || 0));
	} else {
		copy.sort((a, b) => (b.score || 0) - (a.score || 0) || (b.estimated_value_usd || 0) - (a.estimated_value_usd || 0));
	}
	return copy;
}

/** Stable id for deep-linking a lead: its index in the unsorted queue. */
export function leadId(opportunities: CodeTechOpportunity[], opportunity: CodeTechOpportunity): string {
	return String(opportunities.indexOf(opportunity));
}
