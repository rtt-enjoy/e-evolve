import type { Status } from '../types/status';

export function money(value = 0, digits = 2): string {
	return new Intl.NumberFormat('en-US', {
		style: 'currency',
		currency: 'USD',
		maximumFractionDigits: digits,
	}).format(value || 0);
}

/** Compact money for tiles: $960, $24.99, $1.2k */
export function compactMoney(value = 0): string {
	if (!value) return '$0';
	if (value >= 10_000) return `$${(value / 1000).toFixed(value >= 100_000 ? 0 : 1)}k`;
	if (value >= 100) return `$${Math.round(value)}`;
	return `$${value.toFixed(2).replace(/\.00$/, '')}`;
}

export function formatDate(value?: string): string {
	if (!value) return 'never';
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return value;
	return date.toLocaleString(undefined, {
		month: 'short',
		day: 'numeric',
		hour: '2-digit',
		minute: '2-digit',
	});
}

export function ageLabel(value?: string): { label: string; tone: 'good' | 'warn' | 'bad' } {
	if (!value) return { label: 'never', tone: 'bad' };
	const date = new Date(value);
	if (Number.isNaN(date.getTime())) return { label: value, tone: 'warn' };
	const minutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000));
	if (minutes < 75) return { label: `${minutes}m ago`, tone: 'good' };
	if (minutes < 180) return { label: `${Math.floor(minutes / 60)}h ${minutes % 60}m ago`, tone: 'warn' };
	return { label: `${Math.floor(minutes / 60)}h ago`, tone: 'bad' };
}

export function featureLabel(feature: string): string {
	return feature
		.replace(/^llm_/, '')
		.replace(/_/g, ' ')
		.replace(/\b\w/g, (char) => char.toUpperCase());
}

export function evolutionTone(status: Status): 'good' | 'warn' | 'bad' | 'info' {
	const evolution = status.last_evolution || {};
	if (evolution.error) return evolution.error_type === 'api' ? 'warn' : 'bad';
	if ((evolution.changes_applied || []).length) return 'good';
	if ((evolution.summary || '').toLowerCase().includes('skipped')) return 'warn';
	return 'info';
}

export function clampPercent(value: number): number {
	return Math.max(0, Math.min(100, Math.round(value)));
}

export function shortText(value = '', maxLength = 96): string {
	if (value.length <= maxLength) return value;
	return `${value.slice(0, maxLength - 1).trim()}...`;
}

export function scoreTone(score = 0): 'good' | 'warn' | 'bad' | 'info' {
	if (score >= 85) return 'good';
	if (score >= 60) return 'info';
	if (score >= 35) return 'warn';
	return 'bad';
}

/** `reddit:r/SideProject` -> `r/SideProject`; `github` -> `github` */
export function sourceLabel(source = ''): string {
	const [head, ...rest] = source.split(':');
	return rest.length ? rest.join(':') : head || 'unknown';
}

/** Strip emoji + issue/PR noise so lead titles read cleanly in a list. */
export function cleanTitle(value = ''): string {
	return value
		.replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, '')
		.replace(/\s+/g, ' ')
		.trim();
}
