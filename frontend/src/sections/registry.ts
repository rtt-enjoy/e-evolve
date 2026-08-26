/**
 * Section registry.
 *
 * Each section declares which status.json paths it consumes. Two things follow
 * from that declaration:
 *
 *   1. A section with no data in the current snapshot is hidden from the nav,
 *      so the shell only ever shows routes that lead somewhere.
 *   2. Every top-level key claimed by some section is "known". Keys the bot
 *      starts emitting later are unclaimed, and the Data section renders them
 *      generically — new backend fields appear without a frontend change.
 */
import type { ComponentType } from 'react';
import type { Status } from '../types/status';

export type SectionId =
	| 'overview'
	| 'leads'
	| 'research'
	| 'engine'
	| 'health'
	| 'data';

export type SectionDef = {
	id: SectionId;
	label: string;
	/** Sub-caption shown at the top of the section page. */
	blurb: string;
	/** Dotted status.json paths this section reads. First segment claims the key. */
	keys: string[];
	/** Small count shown next to the nav label; null hides the badge. */
	badge?: (status: Status) => number | null;
	/** Sections that always render, even with an empty snapshot. */
	always?: boolean;
	load: () => Promise<{ default: ComponentType<{ status: Status }> }>;
};

export const SECTIONS: SectionDef[] = [
	{
		id: 'overview',
		label: 'Overview',
		blurb: 'The five things worth knowing right now.',
		keys: [
			'earnings',
			'total_runs',
			'last_run',
			'last_cycle_seconds',
			'version',
			'operation_mode',
			'external_action_policy',
			'last_earning',
		],
		always: true,
		load: () => import('./OverviewSection'),
	},
	{
		id: 'leads',
		label: 'Leads',
		blurb: 'Ranked earning opportunities the research cycle found.',
		keys: ['code_tech_earning'],
		badge: (status) => status.code_tech_earning?.opportunities?.length || null,
		load: () => import('./LeadsSection'),
	},
	{
		id: 'research',
		label: 'Research',
		blurb: 'Free-tier AI services, earning playbooks, MRR idea triage, and the strategy guardrails.',
		keys: ['suggestions', 'mrr_ideas'],
		badge: (status) => {
			const brief = status.code_tech_earning?.online_ai_brief;
			const services = brief?.free_ai_services?.length || 0;
			const ideas = brief?.easy_earning_ideas?.length || 0;
			const mrr = status.mrr_ideas?.viable?.length || 0;
			return services + ideas + mrr || null;
		},
		load: () => import('./ResearchSection'),
	},
	{
		id: 'engine',
		label: 'Engine',
		blurb: 'Which model handles which role, and what the last cycle changed.',
		keys: ['llm_provider', 'llm_roles', 'llm_workflows', 'last_evolution', 'article_daily'],
		badge: (status) => Object.keys(status.llm_workflows || {}).length || null,
		load: () => import('./EngineSection'),
	},
	{
		id: 'health',
		label: 'Health',
		blurb: 'Freshness, integration readiness, and anything currently broken.',
		keys: [
			'secret_readiness',
			'configured_github_secrets',
			'active_features',
			'inactive_features',
			'errors',
			// Receive wallet: the real earnings source, rendered in full here.
			'wallet',
			'usdt_balance',
		],
		always: true,
		badge: (status) => (status.errors || []).length || null,
		load: () => import('./HealthSection'),
	},
	{
		id: 'data',
		label: 'Data',
		blurb: 'Every field in the snapshot, including keys no section claims yet.',
		keys: [],
		always: true,
		load: () => import('./DataSection'),
	},
];

/** Top-level status.json keys that at least one section renders explicitly. */
export const CLAIMED_KEYS: ReadonlySet<string> = new Set(
	SECTIONS.flatMap((section) => section.keys.map((key) => key.split('.')[0])),
);

/**
 * Keys present in the snapshot that no section claims — i.e. fields the bot
 * added after this frontend was built.
 */
export function unclaimedKeys(status: Status): string[] {
	return Object.keys(status)
		.filter((key) => !key.startsWith('_'))
		.filter((key) => !CLAIMED_KEYS.has(key))
		.filter((key) => !NEVER_UNCLAIMED.has(key))
		.sort();
}

/** Plumbing keys that are not interesting as "new bot data". */
const NEVER_UNCLAIMED: ReadonlySet<string> = new Set(['github_repo']);

function valueAt(status: Status, path: string): unknown {
	return path.split('.').reduce<unknown>((node, part) => {
		if (node && typeof node === 'object') return (node as Record<string, unknown>)[part];
		return undefined;
	}, status);
}

function hasContent(value: unknown): boolean {
	if (value === null || value === undefined || value === '') return false;
	if (Array.isArray(value)) return value.length > 0;
	if (typeof value === 'object') return Object.keys(value as object).length > 0;
	return true;
}

/** A section is available when it is pinned, or any declared path has content. */
export function isAvailable(section: SectionDef, status: Status): boolean {
	if (section.always) return true;
	return section.keys.some((key) => hasContent(valueAt(status, key)));
}

export function availableSections(status: Status): SectionDef[] {
	return SECTIONS.filter((section) => isAvailable(section, status));
}

export function sectionById(id: string): SectionDef | undefined {
	return SECTIONS.find((section) => section.id === id);
}
