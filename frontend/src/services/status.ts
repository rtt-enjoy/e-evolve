import type { Status } from '../types/status';

/** Where the snapshot on screen came from. */
export type StatusSource = 'pages' | 'repo';

export type StatusFetch = { status: Status; source: StatusSource };

const REPO_PATTERN = /^[\w.-]+\/[\w.-]+$/;

async function fetchJson(url: string): Promise<Status> {
	const response = await fetch(url, { cache: 'no-store' });
	if (!response.ok) {
		throw new Error(`status.json returned ${response.status}`);
	}
	return response.json();
}

function runTime(status: Status): number {
	const time = status.last_run ? new Date(status.last_run).getTime() : Number.NaN;
	return Number.isNaN(time) ? 0 : time;
}

/**
 * The newest snapshot available, from either copy of the same file.
 *
 * Each cycle commits `docs/status.json` to `main`, but the Pages copy only
 * changes when the frontend workflow redeploys (a push made with the Actions
 * token does not trigger it, so it falls back to its hourly cron) and is then
 * cached for 10 minutes. The raw file on `main` is cached for 5. Reading both
 * and keeping the newer `last_run` puts a cycle on screen minutes after it
 * commits rather than up to an hour later. Pages stays the primary: if the raw
 * read fails, or the repo is private, nothing changes.
 */
export async function fetchStatus(repo?: string): Promise<StatusFetch> {
	const stamp = Date.now();
	const readRaw = (name?: string) => (name && REPO_PATTERN.test(name)
		? fetchJson(`https://raw.githubusercontent.com/${name}/main/docs/status.json?ts=${stamp}`)
		: Promise.reject(new Error('no repo')));
	const pages = fetchJson(`status.json?ts=${stamp}`);
	// The repo name lives in the snapshot itself, so the very first load reads
	// it from the Pages copy; later polls already know it and go in parallel.
	const raw = repo ? readRaw(repo) : pages.then((snapshot) => readRaw(snapshot.github_repo));
	const [local, remote] = await Promise.allSettled([pages, raw]);

	if (local.status === 'fulfilled' && remote.status === 'fulfilled') {
		// Ties go to Pages: same cycle, and it is the copy this page shipped with.
		return runTime(remote.value) > runTime(local.value)
			? { status: remote.value, source: 'repo' }
			: { status: local.value, source: 'pages' };
	}
	if (local.status === 'fulfilled') return { status: local.value, source: 'pages' };
	if (remote.status === 'fulfilled') return { status: remote.value, source: 'repo' };
	throw local.reason instanceof Error ? local.reason : new Error(String(local.reason));
}
