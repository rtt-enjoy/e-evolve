import type { CtfEvent, ResearchFeedRow, Status } from '../types/status';
import { hoursSince } from './format';

/**
 * Research rows: CTFs (`ctf_bounty`) and every other prize feed
 * (`research_feed`) folded into one shape, so the page can search, filter and
 * sort them together. Research, never earnings: a prize is the organiser's
 * claim, so nothing here is summed or valued.
 */
export type ResearchCategory = 'ctf' | ResearchFeedRow['category'];

export type ResearchRow = {
	id: string;
	category: ResearchCategory;
	source: string;
	title: string;
	url: string;
	prize: string;
	detail: string;
	pays: boolean;
	crypto: boolean;
	kyc: string;
	beginner: boolean;
	/** When the bot first listed it. The one clock that answers "is this new to me". */
	discovered_at?: string;
	/** The source's own clocks. */
	deadline?: string | null;
	starts_at?: string | null;
	posted_at?: string | null;
	score: number;
};

/** Display order of the groups, and what each one is. */
export const CATEGORIES: Array<{ key: ResearchCategory; title: string; hint: string }> = [
	{ key: 'ctf', title: 'CTF', hint: 'capture-the-flag events on CTFtime' },
	{ key: 'hackathon', title: 'Hackathons', hint: 'online, open to anyone, cash prize' },
	{ key: 'crypto-bounty', title: 'Crypto bounties', hint: 'paid in a stablecoin on Superteam Earn' },
	{ key: 'bug-bounty', title: 'Bug bounties', hint: 'web3 programs that do not ask for KYC' },
	{ key: 'challenge', title: 'Dev challenges', hint: 'announced by the DEV team' },
];

const SOURCE_NAMES: Record<string, string> = {
	ctftime: 'CTFtime',
	devpost: 'Devpost',
	superteam: 'Superteam',
	immunefi: 'Immunefi',
	devto: 'DEV',
};

export function researchSourceName(source = ''): string {
	return SOURCE_NAMES[source] || source || 'unknown';
}

function fromCtf(event: CtfEvent): ResearchRow {
	return {
		id: `ctftime:${event.id ?? event.url ?? event.title}`,
		category: 'ctf',
		source: 'ctftime',
		title: event.title || 'Untitled CTF',
		url: event.url || event.ctftime_url || '',
		prize: event.pays && event.prizes ? event.prizes : '',
		detail: event.format || '',
		pays: !!event.pays,
		crypto: !!event.crypto,
		kyc: event.kyc || 'not published',
		beginner: !!event.beginner,
		discovered_at: event.discovered_at,
		deadline: event.finish,
		starts_at: event.start,
		score: event.score || 0,
	};
}

function fromFeed(row: ResearchFeedRow): ResearchRow {
	return {
		id: row.id,
		category: row.category,
		source: row.source,
		title: row.title || 'Untitled',
		url: row.url || '',
		prize: row.prize || '',
		detail: row.detail || '',
		pays: !!row.pays,
		crypto: !!row.crypto,
		kyc: row.kyc || 'not published',
		beginner: !!row.beginner,
		discovered_at: row.discovered_at,
		deadline: row.deadline,
		starts_at: row.starts_at,
		posted_at: row.posted_at,
		score: row.score || 0,
	};
}

/**
 * Every research row in the snapshot. A snapshot written before `research_feed`
 * existed has CTFs only, and the page still renders.
 */
export function buildResearchRows(status: Status): ResearchRow[] {
	return [
		...(status.ctf_bounty?.events || []).map(fromCtf),
		...(status.research_feed?.items || []).map(fromFeed),
	];
}

function ms(value?: string | null): number | null {
	if (!value) return null;
	const time = new Date(value).getTime();
	return Number.isNaN(time) ? null : time;
}

/** Days until a timestamp against the viewer's clock; negative once it has passed. */
export function daysUntil(value?: string | null): number | null {
	const time = ms(value);
	return time === null ? null : (time - Date.now()) / 86_400_000;
}

function span(days: number): string {
	const abs = Math.abs(days);
	if (abs < 1 / 24) return '<1h';
	if (abs < 1) return `${Math.round(abs * 24)}h`;
	if (abs < 60) return `${Math.round(abs)}d`;
	return `${Math.round(abs / 30)}mo`;
}

/**
 * The source's own timing, always against the viewer's clock (the snapshot's
 * `days_until_start` is frozen at the refresh that wrote it).
 */
export function timing(row: ResearchRow): string {
	const toDeadline = daysUntil(row.deadline);
	const toStart = daysUntil(row.starts_at);
	if (toDeadline !== null && toDeadline < 0) return 'closed';
	if (toStart !== null && toStart > 0) return `starts in ${span(toStart)}`;
	if (toDeadline !== null) {
		return row.category === 'ctf' && toStart !== null ? `live · ends in ${span(toDeadline)}` : `closes in ${span(toDeadline)}`;
	}
	const posted = ms(row.posted_at);
	if (posted !== null) {
		const age = (Date.now() - posted) / 86_400_000;
		return row.category === 'bug-bounty' ? `live since ${new Date(posted).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}` : `announced ${span(age)} ago`;
	}
	return 'no date published';
}

/** Rows the bot listed within a day: the answer to "what is new since I last looked". */
export function isFresh(row: ResearchRow): boolean {
	const hours = hoursSince(row.discovered_at);
	return hours !== null && hours <= 24;
}

/** Closing within a week and not yet over. */
export function closesSoon(row: ResearchRow): boolean {
	const days = daysUntil(row.deadline);
	return days !== null && days >= 0 && days <= 7;
}

export type ResearchSort = 'newest' | 'ending' | 'score';

export function sortResearch(rows: ResearchRow[], sort: ResearchSort): ResearchRow[] {
	const listed = (row: ResearchRow) => ms(row.discovered_at) ?? 0;
	return [...rows].sort((a, b) => {
		if (sort === 'ending') {
			// Closing soonest first; rows with no deadline sink to the end.
			const da = ms(a.deadline) ?? Number.POSITIVE_INFINITY;
			const db = ms(b.deadline) ?? Number.POSITIVE_INFINITY;
			return da - db || b.score - a.score;
		}
		if (sort === 'score') return b.score - a.score || listed(b) - listed(a);
		return listed(b) - listed(a) || b.score - a.score;
	});
}
