import { ArrowLeft, ExternalLink, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { CopyButton } from '../components/CopyButton';
import { Bullets, Card, Disclosure, Empty, Fold, KeyValue, Pill, Progress, SectionHead, Subhead, Tile } from '../components/ui';
import { buildOpportunityStats, sortLeads, type LeadSort } from '../utils/dashboard';
import { cleanTitle, formatDate, hoursSince, leadAge, scoreTone, sourceFamily, sourceName } from '../utils/format';
import { useRoute } from '../utils/route';
import type { CodeTechEarning, CodeTechOpportunity, LeadKind, Status } from '../types/status';

/**
 * Fold the pre-rename `demand`/`supply` names onto `channel`/`asset`.
 *
 * `status.json` is committed, so a snapshot written before the rename is still
 * what the page loads after a deploy. Without this the kind filter silently
 * matches nothing for one cycle.
 */
function normalizeKind(kind: string | undefined): 'channel' | 'asset' {
	return kind === 'asset' || kind === 'supply' ? 'asset' : 'channel';
}

/**
 * Cost of a route, where `0` is real and means free to list.
 *
 * Deliberately not `formatLeadValue`, which renders an em dash for a missing
 * *price*. A missing cost and a zero cost are different claims, and collapsing
 * them would let an unverified platform look free.
 */
function formatCost(cost: number | null | undefined): string {
	if (typeof cost !== 'number') return '—';
	if (cost === 0) return 'Free';
	return `$${cost.toFixed(2)}`;
}

function needsSetup(lead: CodeTechOpportunity): boolean {
	const setup = (lead.manual_setup || '').trim();
	return setup !== '' && !setup.toLowerCase().startsWith('none');
}

/**
 * The score components, in the order and with the weights `_score` uses in
 * bot/earning/code_techs.py. Points = weight x part, before penalties.
 * Keep in step with the Python if the weights change.
 */
const SCORE_PARTS: Array<{ key: string; label: string; weight: number; help: string }> = [
	{ key: 'owner_action', label: 'Runs without you', weight: 28, help: 'income per sale needs no owner action' },
	{ key: 'receive_path', label: 'Money can arrive', weight: 22, help: 'pays to a wallet or a working payout' },
	{ key: 'identity_cost', label: 'No identity check', weight: 20, help: 'earning does not need a government ID' },
	{ key: 'zero_budget', label: 'Free to run', weight: 13, help: 'no fee, subscription or paid tier' },
	{ key: 'setup_burden', label: 'Light setup', weight: 10, help: 'little one-time work before it earns' },
	{ key: 'recency', label: 'Fresh', weight: 7, help: 'fetched rows only; curated rows are dated by hand' },
];

type QuickFilter = 'free' | 'nosetup' | 'new';

/**
 * A free route already at 100 is fully live: nothing is left for the owner to
 * do, so listing it again only pushes open work down the page. Free means a
 * published $0 -- an unknown cost is not free.
 */
function isFreeAndDone(lead: CodeTechOpportunity): boolean {
	return lead.cost_usd === 0 && (lead.score || 0) >= 100;
}

/**
 * Owner rule, top priority: never adult or piracy content on this page.
 *
 * The real screen is `_PROHIBITED_PATTERNS` in bot/earning/code_techs.py,
 * which keeps such rows out of status.json. This is a backstop for a snapshot
 * written before that screen existed, so it holds only the core terms.
 */
const PROHIBITED_RE =
	/porn|xxx|nsfw|hentai|onlyfans|\bsex(ual|y)?\b|\bnude|erotic|\bwarez\b|\bkeygens?\b|\bcrack(ed|s|ing)?\b|\bnulled\b|\bpirat(e|ed|es|ing|cy)\b|\btorrents?\b|\bcasinos?\b|gambl(e|ing)/i;

function isProhibited(lead: CodeTechOpportunity): boolean {
	return PROHIBITED_RE.test([lead.title, lead.reason, lead.url].join(' '));
}

export default function LeadsSection({ status }: { status: Status }) {
	const route = useRoute();
	const codeTech = status.code_tech_earning || {};
	// Filtered before indexing, so lead links and the detail page agree.
	const opportunities = useMemo(
		() => (codeTech.opportunities || []).filter((lead) => !isProhibited(lead) && !isFreeAndDone(lead)),
		[codeTech.opportunities],
	);

	const detailIndex = route.detail === null ? null : Number(route.detail);
	// A lead id is its index in the unsorted queue, and the queue is rebuilt
	// every refresh -- so an old link can point past the end. Fall back to the
	// list rather than rendering a blank page.
	const detail =
		detailIndex !== null && Number.isInteger(detailIndex) ? opportunities[detailIndex] : undefined;

	if (detail) {
		return <LeadDetail lead={detail} index={detailIndex as number} opportunities={opportunities} />;
	}

	return <LeadList codeTech={codeTech} opportunities={opportunities} />;
}

/* --------------------------------------------------------------------- list */

/** Rows a group shows before "show more", so 60+ leads do not become a 5,000px page. */
const GROUP_PAGE = 20;

const KIND_GROUPS: Array<{ kind: 'channel' | 'asset'; title: string; hint: string }> = [
	{ kind: 'channel', title: 'Gets paid', hint: 'where a product is listed and money arrives' },
	{ kind: 'asset', title: 'Build & market', hint: 'tooling, launches and what makers report earning' },
];

function LeadRow({ lead, index }: { lead: CodeTechOpportunity; index: number }) {
	// Two different times, never merged: when the bot put the row on this page
	// (exact, and the thing that says "is this new to me"), and when the source
	// published it (a repo can be listed today and be ten days old).
	const listedHours = hoursSince(lead.discovered_at);
	const listed = leadAge(listedHours);
	const postedHours = lead.posted_at ? hoursSince(lead.posted_at) ?? lead.age_hours ?? null : null;
	const posted = leadAge(postedHours);
	return (
		// A div, not an <a>: the row holds two links (detail and source), and
		// links cannot nest.
		<div className="lead-row">
			<a className="lead-row-link" href={`#/leads/${index}`}>
				{/* Score leads the row: it ranks by how passive the income is. */}
				<span className={`score-chip ${scoreTone(lead.score)}`} title="passive score, out of 100">{lead.score || 0}</span>
				<span className="lead-row-body">
					<strong title={cleanTitle(lead.title)}>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
					<p title={lead.reason}>{lead.reason || 'No reason recorded.'}</p>
				</span>
				<span className="lead-row-meta">
					{lead.is_new ? <Pill tone="info">new</Pill> : null}
					{/* "Free" only when the platform published $0. An unknown
					    cost renders nothing rather than implying free. */}
					{lead.cost_usd === 0 ? <Pill tone="good">free</Pill> : null}
					{typeof lead.cost_usd === 'number' && lead.cost_usd > 0 ? <Pill tone="warn">{formatCost(lead.cost_usd)}</Pill> : null}
					<span className="lead-row-time">
						{/* The listed time is the row's freshness. A snapshot from before
						    the stamp existed says so instead of implying a time. */}
						<b
							className={listed.tone}
							title={lead.discovered_at ? `Listed on this page ${formatDate(lead.discovered_at)}` : undefined}
						>
							{lead.discovered_at
								? `Listed ${formatDate(lead.discovered_at)} · ${listed.label} ago`
								: 'Listed time not recorded'}
						</b>
						{/* Only fetched rows have a posting time; curated rows show the feed alone. */}
						<span title={lead.posted_at ? `Posted at the source ${formatDate(lead.posted_at)}` : undefined}>
							{sourceName(lead.source)}
							{lead.posted_at ? ` · posted ${posted.label} ago` : ' · curated'}
						</span>
					</span>
				</span>
			</a>
			{/* Playbook rows have no URL, so no button rather than a dead one. */}
			{lead.url ? (
				<a
					className="icon-btn lead-row-source"
					href={lead.url}
					target="_blank"
					rel="noreferrer"
					title="Open source"
					aria-label={`Open source: ${cleanTitle(lead.title) || 'lead'}`}
				>
					<ExternalLink size={15} />
				</a>
			) : (
				// Same footprint, so the time column lines up across rows.
				<span className="lead-row-source" aria-hidden="true" />
			)}
		</div>
	);
}

function LeadList({ codeTech, opportunities }: { codeTech: CodeTechEarning; opportunities: CodeTechOpportunity[] }) {
	const [query, setQuery] = useState('');
	const [source, setSource] = useState('all');
	const [kind, setKind] = useState<LeadKind | 'all'>('all');
	const [quick, setQuick] = useState<Set<QuickFilter>>(new Set());
	// Newest first by default: the complaint that started this rebuild was
	// that the page showed stale leads.
	const [sort, setSort] = useState<LeadSort>('newest');
	const [limit, setLimit] = useState<Record<string, number>>({});

	const stats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
	// One chip per feed, not per subreddit: a chip for every `reddit:r/...` and
	// every new feed would make the filter row taller than the list it filters.
	const families = useMemo(() => {
		const counts = new Map<string, number>();
		for (const lead of opportunities) {
			const key = sourceFamily(lead.source);
			counts.set(key, (counts.get(key) || 0) + 1);
		}
		return [...counts.entries()].map(([key, count]) => ({ key, count })).sort((a, b) => b.count - a.count);
	}, [opportunities]);
	const newCount = opportunities.filter((lead) => lead.is_new).length;
	const dayCount = opportunities.filter((lead) => {
		const hours = hoursSince(lead.posted_at) ?? lead.age_hours;
		return typeof hours === 'number' && hours <= 24;
	}).length;

	const toggleQuick = (key: QuickFilter) =>
		setQuick((current) => {
			const next = new Set(current);
			if (next.has(key)) next.delete(key);
			else next.add(key);
			return next;
		});

	const visible = useMemo(() => {
		const needle = query.trim().toLowerCase();
		const filtered = opportunities.filter((lead) => {
			if (kind !== 'all' && normalizeKind(lead.kind) !== kind) return false;
			if (source !== 'all' && sourceFamily(lead.source) !== source) return false;
			// Free means a published $0. An unknown cost is not free.
			if (quick.has('free') && lead.cost_usd !== 0) return false;
			if (quick.has('nosetup') && needsSetup(lead)) return false;
			if (quick.has('new') && !lead.is_new) return false;
			if (!needle) return true;
			return [lead.title, lead.reason, lead.next_step, lead.source, lead.manual_setup, lead.verified_note]
				.some((field) => (field || '').toLowerCase().includes(needle));
		});
		return sortLeads(filtered, sort);
	}, [opportunities, query, source, kind, quick, sort]);

	const sourceStats = codeTech.source_stats || [];
	const refused = codeTech.refused_channels || [];
	const playbook: Array<{ title: string; hint: string; items: string[] }> = [
		{ title: 'Product shapes', hint: 'What a solo dev can build once and sell', items: codeTech.product_shapes || [] },
		{ title: 'Monetization patterns', hint: 'Ways a product earns unattended', items: codeTech.monetization_patterns || [] },
		{ title: 'Strategy playbook', hint: 'Build once, then spend cycles on distribution', items: codeTech.strategy_playbook || [] },
		{ title: 'Avoid patterns', hint: 'Disqualifies a lead immediately', items: codeTech.avoid_patterns || [] },
	].filter((block) => block.items.length);

	const chip = (active: boolean, onClick: () => void, label: string, count?: number, pressed?: boolean) => (
		<button type="button" className={`leads-chip ${active ? 'active' : ''}`} aria-pressed={pressed} onClick={onClick}>
			{label}
			{typeof count === 'number' ? <em>{count}</em> : null}
		</button>
	);

	return (
		<>
			<SectionHead
				title="Leads"
				blurb={
					`Where a digital product gets paid, and the tooling and market evidence to build and sell it. Refreshed every ${codeTech.refresh_hours || 6}h, last ${formatDate(codeTech.last_refresh_at)}.` +
					// Say so when the queue ranked more than this page carries,
					// rather than letting the count quietly under-report.
					(codeTech.ranked_total && codeTech.ranked_total > opportunities.length
						? ` ${codeTech.ranked_total} ranked; the top ${opportunities.length} are kept.`
						: '')
				}
			/>

			{/* No money aggregate here on purpose. See buildOpportunityStats. */}
			<div className="leads-stats" aria-label="Lead counts">
				<div><span>Routes</span><strong>{stats.total}</strong></div>
				<div><span>Posted in 24h</span><strong>{dayCount}</strong></div>
				<div><span>New this refresh</span><strong>{newCount}</strong></div>
				<div><span>Free to start</span><strong>{stats.freeCount}</strong></div>
				<div><span>Needs setup</span><strong>{stats.needsSetupCount}</strong></div>
			</div>

			<Card className="card-compact">
				<div className="leads-toolbar">
					<label className="search">
						<Search size={16} />
						<input
							type="search"
							placeholder="Search leads…"
							value={query}
							onChange={(event) => setQuery(event.target.value)}
							aria-label="Search leads"
						/>
					</label>
					<div className="leads-chips" role="group" aria-label="Sort leads">
						{chip(sort === 'newest', () => setSort('newest'), 'newest')}
						{chip(sort === 'score', () => setSort('score'), 'score')}
						{chip(sort === 'cost', () => setSort('cost'), 'cheapest')}
					</div>
				</div>

				<div className="leads-chips" role="group" aria-label="Filter leads">
					{chip(kind === 'all', () => setKind('all'), 'all', opportunities.length)}
					{chip(kind === 'channel', () => setKind('channel'), 'gets paid', stats.channelCount)}
					{chip(kind === 'asset', () => setKind('asset'), 'build & market', stats.assetCount)}
					<span className="leads-sep" aria-hidden="true" />
					{chip(quick.has('free'), () => toggleQuick('free'), 'free', stats.freeCount, quick.has('free'))}
					{chip(quick.has('nosetup'), () => toggleQuick('nosetup'), 'no setup', stats.total - stats.needsSetupCount, quick.has('nosetup'))}
					{chip(quick.has('new'), () => toggleQuick('new'), 'new', newCount, quick.has('new'))}
					<span className="leads-sep" aria-hidden="true" />
					{chip(source === 'all', () => setSource('all'), 'every source')}
					{families.map((entry) => chip(source === entry.key, () => setSource(entry.key), sourceName(entry.key), entry.count))}
				</div>

				{visible.length ? (
					KIND_GROUPS.map((group) => {
						const rows = visible.filter((lead) => normalizeKind(lead.kind) === group.kind);
						if (!rows.length) return null;
						const cap = limit[group.kind] || GROUP_PAGE;
						return (
							<section className="lead-group" key={group.kind}>
								<header className="lead-group-head">
									<strong>{group.title}</strong>
									<span>{rows.length}</span>
									<em>{group.hint}</em>
								</header>
								<div className="lead-table">
									{rows.slice(0, cap).map((lead) => (
										<LeadRow key={`${lead.url}-${opportunities.indexOf(lead)}`} lead={lead} index={opportunities.indexOf(lead)} />
									))}
								</div>
								{rows.length > cap ? (
									<button
										type="button"
										className="btn lead-more"
										onClick={() => setLimit((current) => ({ ...current, [group.kind]: cap + GROUP_PAGE }))}
									>
										Show {Math.min(GROUP_PAGE, rows.length - cap)} more · {rows.length - cap} left
									</button>
								) : null}
							</section>
						);
					})
				) : (
					<Empty text={opportunities.length ? 'No leads match this filter.' : 'No research leads in the queue yet.'} />
				)}
			</Card>

			{/* Everything below is reference, so it starts closed: the summary line
			    is visible and the detail is one click away. */}
			<Subhead>Reference</Subhead>
			<div className="stack tight">
				{/* Fetched vs ranked vs shown, so a source that silently returns
				    nothing is visible as one. The HN fetcher returned 0 for its
				    whole life before this existed. */}
				{sourceStats.length ? (
					<Disclosure title="Where leads come from" hint="fetched, ranked and shown per source" count={sourceStats.length}>
						<KeyValue
							compact
							rows={sourceStats.map((row) => [
								sourceName(row.source),
								row.fetched
									? `${row.fetched} fetched · ${row.ranked ?? 0} ranked · ${row.shown ?? 0} shown`
									: row.source === 'reddit'
										? '0 fetched — Reddit rate-limits most cycles'
										: '0 fetched this refresh',
							])}
						/>
					</Disclosure>
				) : null}
				{refused.length ? (
					<Disclosure title="Refused routes" hint="checked and rejected, so they cannot return" count={refused.length}>
						<div className="stack tight">
							{refused.map((row, index) => (
								<Fold key={`${row.name}-${index}`} title={row.name || 'Unnamed route'} meta={<Pill tone="warn">refused</Pill>}>
									<p className="prose">{row.why || 'No reason recorded.'}</p>
								</Fold>
							))}
						</div>
					</Disclosure>
				) : null}
				{playbook.map((block) => (
					<Disclosure key={block.title} title={block.title} hint={block.hint} count={block.items.length}>
						<Bullets items={block.items} />
					</Disclosure>
				))}
			</div>
		</>
	);
}

/* ------------------------------------------------------------------- detail */

function LeadDetail({ lead, index, opportunities }: { lead: CodeTechOpportunity; index: number; opportunities: CodeTechOpportunity[] }) {
	const total = opportunities.length;
	const isChannel = normalizeKind(lead.kind) === 'channel';
	const setup = (lead.manual_setup || '').trim();
	const setupNeeded = needsSetup(lead);
	const parts = lead.score_parts || {};
	const known = SCORE_PARTS.filter((part) => typeof parts[part.key] === 'number');
	// Components the page does not know yet still render, unweighted.
	const unknown = Object.entries(parts).filter(
		([key]) => key !== 'penalty' && !SCORE_PARTS.some((part) => part.key === key),
	);
	// `_score` records penalties as a negative `penalty` part.
	const penalty = Math.abs(parts.penalty || 0);

	// Same kind, best score first: the alternatives to this route.
	const related = opportunities
		.map((other, otherIndex) => ({ other, otherIndex }))
		.filter(({ other, otherIndex }) => otherIndex !== index && normalizeKind(other.kind) === normalizeKind(lead.kind))
		.sort((a, b) => (b.other.score || 0) - (a.other.score || 0))
		.slice(0, 4);

	return (
		<>
			<SectionHead
				title={cleanTitle(lead.title) || 'Untitled lead'}
				blurb={lead.reason || 'No reason recorded for this lead.'}
				action={lead.url ? <a className="btn primary" href={lead.url} target="_blank" rel="noreferrer"><ExternalLink size={15} /> open source</a> : undefined}
			/>

			<div className="tile-row compact">
				{/* Never toned 'good' when the cost is unknown -- green beside an
				    em dash reads as a confirmed free, which is a claim. */}
				<Tile
					label="Cost to start"
					value={formatCost(lead.cost_usd)}
					detail={
						lead.cost_usd === 0
							? 'free to list'
							: typeof lead.cost_usd === 'number'
								? 'one-time, published by the platform'
								: 'no cost published'
					}
					tone={lead.cost_usd === 0 ? 'good' : typeof lead.cost_usd === 'number' ? 'warn' : 'neutral'}
				/>
				<Tile label="Passive score" value={String(lead.score || 0)} detail="out of 100" tone={scoreTone(lead.score)} />
				<Tile
					label="Owner setup"
					value={setupNeeded ? 'one-time' : 'none'}
					detail={setupNeeded ? 'before it can earn anything' : 'nothing to do'}
					tone={setupNeeded ? 'warn' : 'good'}
				/>
				<Tile
					label="Kind"
					value={isChannel ? 'gets paid' : 'build & market'}
					detail={isChannel ? 'where money arrives' : 'what makes or promotes it'}
					tone={isChannel ? 'info' : 'neutral'}
				/>
			</div>

			<div className="split even">
				<div className="stack tight">
					<Card className="card-compact" title="First step" hint="The concrete move that turns this lead into money.">
						<p className="prose">{lead.next_step || 'No next step recorded.'}</p>
					</Card>

					{known.length ? (
						<Card
							className="card-compact"
							title="Why it scores this"
							hint={`Points per component, out of its weight.${penalty ? ` ${penalty} taken off by penalties.` : ''}`}
						>
							<div className="stack tight">
								{known.map((part) => {
									const value = parts[part.key] || 0;
									return (
										<div key={part.key} title={part.help}>
											<Progress
												value={value * 100}
												label={`${part.label} — ${Math.round(part.weight * value)}/${part.weight}`}
											/>
										</div>
									);
								})}
								{unknown.length ? (
									<KeyValue rows={unknown.map(([name, value]) => [name.replace(/_/g, ' '), value.toFixed(2)])} />
								) : null}
							</div>
						</Card>
					) : null}

					{/* A ~1.3 KB prompt is detail, not summary: one line until opened. */}
					{lead.codex_prompt ? (
						<Fold
							title="Codex prompt"
							meta="paste into Codex to build it"
							action={<CopyButton text={lead.codex_prompt} label="copy prompt" />}
						>
							<pre className="code-block">{lead.codex_prompt}</pre>
						</Fold>
					) : null}
				</div>

				<div className="stack tight">
					<Card className="card-compact" title="Lead facts">
						{/* Cost, score, setup and kind are the tiles above and are not
						    repeated. Provenance stays beside them, so a figure on this
						    page can always be traced to who published it. */}
						<KeyValue
							compact
							rows={[
								['Owner must do', setup || 'nothing'],
								['Source', sourceName(lead.source)],
								['Verified', lead.verified_note || 'not recorded'],
								['Listed on this page', lead.discovered_at ? `${formatDate(lead.discovered_at)} (${leadAge(hoursSince(lead.discovered_at)).label} ago)` : 'not recorded'],
								['Posted at the source', lead.posted_at ? `${formatDate(lead.posted_at)} (${leadAge(hoursSince(lead.posted_at) ?? lead.age_hours).label} ago)` : 'not applicable (curated)'],
								['Link', lead.url ? <a href={lead.url} target="_blank" rel="noreferrer">open ↗</a> : '—'],
							]}
						/>
					</Card>

					{related.length ? (
						<Card className="card-compact" title={isChannel ? 'Other places to get paid' : 'Other build & market routes'} hint="Same kind, best score first.">
							<div className="stack tight">
								{related.map(({ other, otherIndex }) => (
									<a className="reference" key={`${other.url}-${otherIndex}`} href={`#/leads/${otherIndex}`}>
										<span className="min-w-0">
											{/* .reference truncates to one line, and on an inline <strong>
											    that only forces nowrap -- long lead titles ran off the card. */}
											<strong className="block whitespace-normal break-words">{cleanTitle(other.title) || 'Untitled lead'}</strong>
											<p>{other.score || 0}/100 · {formatCost(other.cost_usd)} · {sourceName(other.source)}</p>
										</span>
									</a>
								))}
							</div>
						</Card>
					) : null}
				</div>
			</div>

			<div className="pager">
				{index > 0 ? <a className="btn" href={`#/leads/${index - 1}`}><ArrowLeft size={15} /> previous lead</a> : <span />}
				{index < total - 1 ? <a className="btn" href={`#/leads/${index + 1}`}>next lead →</a> : <span />}
			</div>
		</>
	);
}
