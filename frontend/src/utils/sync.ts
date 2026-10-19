import { useCallback, useEffect, useRef, useState } from 'react';
import { fetchStatus, type StatusSource } from '../services/status';
import type { Status } from '../types/status';
import { money } from './format';

const POLL_MS = 60_000;
/** The cycle is scheduled hourly; GitHub's cron often starts it late. */
const CYCLE_MS = 60 * 60_000;

/** What a newly landed cycle changed, for the "cycle landed" notice. */
export type CycleNotice = { run: number; changes: string[] };

export type StatusSync = {
	status: Status;
	source: StatusSource | null;
	lastPoll: Date | null;
	error: string;
	loading: boolean;
	refreshing: boolean;
	notice: CycleNotice | null;
	dismiss: () => void;
	refresh: () => void;
};

const EMPTY: Status = {
	active_features: [],
	inactive_features: [],
	earnings: {},
	last_evolution: {},
	last_earning: { actions: [] },
	suggestions: [],
	errors: [],
};

function plural(n: number, word: string): string {
	return `${n.toLocaleString()} ${word}${n === 1 ? '' : 's'}`;
}

/** The handful of deltas worth announcing, in the order an owner cares about. */
export function diffCycle(prev: Status, next: Status): string[] {
	const changes: string[] = [];
	const received = (next.wallet?.received_total_usd || 0) - (prev.wallet?.received_total_usd || 0);
	if (received > 0) changes.push(`+${money(received)} received on-chain`);
	const posts = (next.article_stats?.count || 0) - (prev.article_stats?.count || 0);
	if (posts > 0) changes.push(`${plural(posts, 'new post')} published`);
	const views = (next.article_stats?.total_views || 0) - (prev.article_stats?.total_views || 0);
	if (views > 0) changes.push(`+${plural(views, 'view')}`);
	const rejects = (next.article_rejects?.total || 0) - (prev.article_rejects?.total || 0);
	if (rejects > 0) changes.push(`${plural(rejects, 'draft')} held back by the gates`);
	const branch = next.last_evolution_branch;
	if (branch && branch !== prev.last_evolution_branch) changes.push(`proposal on ${branch}`);
	const errors = (next.errors || []).length;
	if (errors) changes.push(`${plural(errors, 'error')} this cycle`);
	return changes;
}

/**
 * Keeps the snapshot current without a reload.
 *
 * Polls while the tab is visible, pauses while hidden (a background tab polling
 * hourly data every minute is pure waste), and refetches the moment the tab
 * comes back so a returning owner never reads a stale page.
 */
export function useStatusSync(): StatusSync {
	const [status, setStatus] = useState<Status>(EMPTY);
	const [source, setSource] = useState<StatusSource | null>(null);
	const [lastPoll, setLastPoll] = useState<Date | null>(null);
	const [error, setError] = useState('');
	const [loading, setLoading] = useState(true);
	const [refreshing, setRefreshing] = useState(false);
	const [notice, setNotice] = useState<CycleNotice | null>(null);
	const current = useRef<Status | null>(null);
	const inFlight = useRef(false);

	const load = useCallback(async () => {
		if (inFlight.current) return;
		inFlight.current = true;
		setRefreshing(true);
		try {
			const result = await fetchStatus(current.current?.github_repo);
			const prev = current.current;
			const next = result.status;
			// Only a strictly newer cycle replaces what is on screen: the two
			// copies can briefly disagree, and stepping back would undo a
			// "cycle landed" notice the owner just read.
			if (prev && (next.total_runs || 0) < (prev.total_runs || 0)) return;
			if (prev && (next.total_runs || 0) > (prev.total_runs || 0)) {
				setNotice({ run: next.total_runs || 0, changes: diffCycle(prev, next) });
			}
			current.current = next;
			setStatus(next);
			setSource(result.source);
			setLastPoll(new Date());
			setError('');
		} catch (caught) {
			setError(caught instanceof Error ? caught.message : String(caught));
		} finally {
			inFlight.current = false;
			setRefreshing(false);
			setLoading(false);
		}
	}, []);

	useEffect(() => {
		load();
		const timer = window.setInterval(() => {
			if (document.visibilityState === 'visible') load();
		}, POLL_MS);
		const onVisible = () => {
			if (document.visibilityState === 'visible') load();
		};
		document.addEventListener('visibilitychange', onVisible);
		window.addEventListener('online', load);
		return () => {
			window.clearInterval(timer);
			document.removeEventListener('visibilitychange', onVisible);
			window.removeEventListener('online', load);
		};
	}, [load]);

	// A notice is a moment, not a state: let it go on its own.
	useEffect(() => {
		if (!notice) return;
		const timer = window.setTimeout(() => setNotice(null), 15_000);
		return () => window.clearTimeout(timer);
	}, [notice]);

	return { status, source, lastPoll, error, loading, refreshing, notice, dismiss: () => setNotice(null), refresh: load };
}

/** Re-renders on an interval so relative times ("12s ago") stay true. */
export function useNow(intervalMs = 15_000): number {
	const [now, setNow] = useState(() => Date.now());
	useEffect(() => {
		const timer = window.setInterval(() => setNow(Date.now()), intervalMs);
		return () => window.clearInterval(timer);
	}, [intervalMs]);
	return now;
}

export function sinceLabel(date: Date | null, now: number): string {
	if (!date) return 'syncing';
	const seconds = Math.max(0, Math.round((now - date.getTime()) / 1000));
	if (seconds < 10) return 'just now';
	if (seconds < 60) return `${seconds}s ago`;
	return `${Math.floor(seconds / 60)}m ago`;
}

/**
 * When the next cycle should start, relative to now.
 *
 * `last_run` is the start of the previous cycle, so the next is due an hour
 * after it; its data lands a few minutes later, once the cycle commits.
 */
export function nextCycle(lastRun: string | undefined, now: number): { label: string; overdue: boolean } {
	const start = lastRun ? new Date(lastRun).getTime() : Number.NaN;
	if (Number.isNaN(start)) return { label: 'next cycle unknown', overdue: false };
	const minutes = Math.round((start + CYCLE_MS - now) / 60_000);
	if (minutes > 1) return { label: `next cycle in ~${minutes}m`, overdue: false };
	if (minutes >= -15) return { label: 'next cycle due now', overdue: false };
	return { label: `next cycle ${-minutes}m late`, overdue: true };
}
