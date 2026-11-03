import { ArrowLeft, ExternalLink, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { CopyButton } from '../components/CopyButton';
import { Bullets, Card, Disclosure, Empty, KeyValue, Pill, Progress, SectionHead, Subhead, Tile } from '../components/ui';
import { buildOpportunityStats, leadSources, sortLeads, type LeadSort } from '../utils/dashboard';
import { cleanTitle, formatDate, leadAge, scoreTone, sourceLabel } from '../utils/format';
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
		() => (codeTech.opportunities || []).filter((lead) => !isProhibited(lead)),
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

function LeadList({ codeTech, opportunities }: { codeTech: CodeTechEarning; opportunities: CodeTechOpportunity[] }) {
	const [query, setQuery] = useState('');
	const [source, setSource] = useState('all');
	const [kind, setKind] = useState<LeadKind | 'all'>('all');
	const [quick, setQuick] = useState<Set<QuickFilter>>(new Set());
	// Newest first by default: the complaint that started this rebuild was
	// that the page showed stale leads.
	const [sort, setSort] = useState<LeadSort>('newest');

	const stats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
	const sources = useMemo(() => leadSources(opportunities), [opportunities]);
	const newCount = opportunities.filter((lead) => lead.is_new).length;

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
			if (source !== 'all' && (lead.source || 'unknown') !== source) return false;
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

	return (
		<>
			<SectionHead
				title="Leads"
				blurb={
					`Routes to passive income from a digital product on a zero budget: where it gets paid, and what builds and markets it. Freelance postings are deliberately absent — income per hour of your time is a job, not passive income. Refreshed every ${codeTech.refresh_hours || 6}h — last ${formatDate(codeTech.last_refresh_at)}.` +
					// Say so when the queue ranked more than this page carries,
					// rather than letting the count quietly under-report.
					(codeTech.ranked_total && codeTech.ranked_total > opportunities.length
						? ` ${codeTech.ranked_total} ranked this cycle; the top ${opportunities.length} are kept here.`
						: '')
				}
			/>

			{/* No money aggregate here on purpose. See buildOpportunityStats. */}
			<div className="tile-row">
				<Tile
					label="Routes tracked"
					value={String(stats.total)}
					detail={`${stats.channelCount} channels · ${stats.assetCount} assets`}
					tone="info"
				/>
				<Tile
					label="Free to start"
					value={String(stats.freeCount)}
					detail="no listing fee, cost published by the platform"
					tone={stats.freeCount ? 'good' : 'neutral'}
				/>
				<Tile
					label="Needs a one-time setup"
					value={String(stats.needsSetupCount)}
					detail="owner opens the account before it can earn"
					tone={stats.needsSetupCount ? 'warn' : 'good'}
				/>
				<Tile
					label="New this refresh"
					value={String(newCount)}
					detail="not on the page at the previous refresh"
					tone={newCount ? 'info' : 'neutral'}
				/>
			</div>

			<Card>
				<div className="filters">
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
					<div className="segmented" role="group" aria-label="Filter by lead kind">
						<button type="button" className={kind === 'all' ? 'active' : ''} onClick={() => setKind('all')}>
							all <em>{opportunities.length}</em>
						</button>
						<button type="button" className={kind === 'channel' ? 'active' : ''} onClick={() => setKind('channel')}>
							gets paid <em>{stats.channelCount}</em>
						</button>
						<button type="button" className={kind === 'asset' ? 'active' : ''} onClick={() => setKind('asset')}>
							build &amp; market <em>{stats.assetCount}</em>
						</button>
					</div>
					<div className="segmented" role="group" aria-label="Sort leads">
						<button type="button" className={sort === 'newest' ? 'active' : ''} onClick={() => setSort('newest')}>newest</button>
						<button type="button" className={sort === 'score' ? 'active' : ''} onClick={() => setSort('score')}>score</button>
						<button type="button" className={sort === 'cost' ? 'active' : ''} onClick={() => setSort('cost')}>cheapest</button>
					</div>
				</div>

				<div className="filters">
					{/* Toggles that stack: each narrows the list further. */}
					<div className="segmented" role="group" aria-label="Quick filters">
						<button type="button" aria-pressed={quick.has('free')} className={quick.has('free') ? 'active' : ''} onClick={() => toggleQuick('free')}>
							free to start <em>{stats.freeCount}</em>
						</button>
						<button type="button" aria-pressed={quick.has('nosetup')} className={quick.has('nosetup') ? 'active' : ''} onClick={() => toggleQuick('nosetup')}>
							no setup <em>{stats.total - stats.needsSetupCount}</em>
						</button>
						<button type="button" aria-pressed={quick.has('new')} className={quick.has('new') ? 'active' : ''} onClick={() => toggleQuick('new')}>
							new <em>{newCount}</em>
						</button>
					</div>
					<div className="segmented" role="group" aria-label="Filter by source">
						<button type="button" className={source === 'all' ? 'active' : ''} onClick={() => setSource('all')}>
							every source
						</button>
						{sources.map((entry) => (
							<button
								key={entry.key}
								type="button"
								className={source === entry.key ? 'active' : ''}
								onClick={() => setSource(entry.key)}
							>
								{sourceLabel(entry.key)} <em>{entry.count}</em>
							</button>
						))}
					</div>
				</div>

				{visible.length !== opportunities.length ? (
					<p className="muted">Showing {visible.length} of {opportunities.length}.</p>
				) : null}

				{visible.length ? (
					<div className="lead-table">
						{visible.map((lead) => {
							const index = opportunities.indexOf(lead);
							const isChannel = normalizeKind(lead.kind) === 'channel';
							const age = leadAge(lead.age_hours);
							return (
								// A div, not an <a>: the row holds two links (detail and
								// source), and links cannot nest.
								<div className="lead-row" key={`${lead.url}-${index}`}>
									<a className="lead-row-link" href={`#/leads/${index}`}>
										{/* Score leads the row: it ranks by how passive the income is. */}
										<span className={`score-chip ${scoreTone(lead.score)}`} title="passive score, out of 100">{lead.score || 0}</span>
										<span className="lead-row-body">
											<strong>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
											<p>{lead.reason || 'No reason recorded.'}</p>
										</span>
										<span className="lead-row-meta">
											{lead.is_new ? <Pill tone="info">new</Pill> : null}
											{/* "Free" only when the platform published $0. An unknown
											    cost renders nothing rather than implying free. */}
											{lead.cost_usd === 0 ? <Pill tone="good">free</Pill> : null}
											{typeof lead.cost_usd === 'number' && lead.cost_usd > 0 ? (
												<Pill tone="warn">{formatCost(lead.cost_usd)}</Pill>
											) : null}
											<Pill tone={isChannel ? 'info' : 'neutral'}>
												{isChannel ? 'gets paid' : 'build & market'}
											</Pill>
											<Pill tone="neutral">{sourceLabel(lead.source)}</Pill>
											{/* Only fetched rows have a posting time; curated rows show none. */}
											{lead.posted_at ? <Pill tone={age.tone}>{age.label} ago</Pill> : null}
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
									) : null}
								</div>
							);
						})}
					</div>
				) : (
					<Empty text={opportunities.length ? 'No leads match this filter.' : 'No research leads in the queue yet.'} />
				)}
			</Card>

			<div className="grid-2">
				{/* Fetched vs ranked vs shown, so a source that silently returns
				    nothing is visible as one. The HN fetcher returned 0 for its
				    whole life before this existed. */}
				<Card title="Where leads come from" hint="Rows fetched this refresh, how many cleared the score bar, and how many are on this page.">
					{sourceStats.length ? (
						<KeyValue
							rows={sourceStats.map((row) => [
								sourceLabel(row.source),
								row.fetched
									? `${row.fetched} fetched · ${row.ranked ?? 0} ranked · ${row.shown ?? 0} shown`
									: row.source === 'reddit'
										? '0 fetched — Reddit rate-limits most cycles'
										: '0 fetched this refresh',
							])}
						/>
					) : (
						<Empty text="Source counts arrive with the next refresh." />
					)}
				</Card>

				<Card title="Refused routes" hint="Checked and rejected, so they cannot return to this page.">
					{refused.length ? (
						<div className="stack">
							{refused.map((row, index) => (
								<article className="suggestion" key={`${row.name}-${index}`}>
									<div className="suggestion-head">
										<strong>{row.name || 'Unnamed route'}</strong>
										<Pill tone="warn">refused</Pill>
									</div>
									<p className="prose">{row.why || 'No reason recorded.'}</p>
								</article>
							))}
						</div>
					) : (
						<Empty text="No refused routes recorded." />
					)}
				</Card>
			</div>

			{playbook.length ? (
				<>
					<Subhead>Product playbook</Subhead>
					<div className="stack">
						{playbook.map((block, index) => (
							<Disclosure key={block.title} title={block.title} hint={block.hint} count={block.items.length} defaultOpen={index === 0}>
								<Bullets items={block.items} />
							</Disclosure>
						))}
					</div>
				</>
			) : null}
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

			<div className="tile-row">
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

			<div className="split">
				<div className="stack">
					<Card title="First step" hint="The concrete move that turns this lead into money.">
						<p className="prose">{lead.next_step || 'No next step recorded.'}</p>
					</Card>

					{known.length ? (
						<Card
							title="Why it scores this"
							hint={`Points per component, out of its weight.${penalty ? ` ${penalty} taken off by penalties.` : ''}`}
						>
							<div className="stack">
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

					{lead.codex_prompt ? (
						<Card
							title="Codex prompt"
							hint="Paste into Codex to build a scoped, verifiable solution."
							action={<CopyButton text={lead.codex_prompt} label="copy prompt" />}
						>
							<pre className="code-block">{lead.codex_prompt}</pre>
						</Card>
					) : (
						<Card title="Codex prompt">
							<Empty text="Prompts are generated for the highest-scoring leads only." />
						</Card>
					)}
				</div>

				<div className="stack">
					<Card title="Lead facts">
						{/* Cost and its provenance always travel together, so a
						    figure on this page can always be traced to who published it. */}
						<KeyValue
							rows={[
								['Cost to start', formatCost(lead.cost_usd)],
								['Owner must do', setup || 'nothing'],
								['Score', `${lead.score || 0}/100`],
								['Source', sourceLabel(lead.source)],
								['Verified', lead.verified_note || 'not recorded'],
								['Posted', lead.posted_at ? `${formatDate(lead.posted_at)} (${leadAge(lead.age_hours).label} ago)` : 'not applicable'],
								['First seen by bot', lead.discovered_at ? formatDate(lead.discovered_at) : '—'],
								['New this refresh', lead.is_new ? 'yes' : 'no'],
								['Link', lead.url ? <a href={lead.url} target="_blank" rel="noreferrer">open ↗</a> : '—'],
							]}
						/>
					</Card>

					{related.length ? (
						<Card title={isChannel ? 'Other places to get paid' : 'Other build & market routes'} hint="Same kind, best score first.">
							<div className="stack">
								{related.map(({ other, otherIndex }) => (
									<a className="reference" key={`${other.url}-${otherIndex}`} href={`#/leads/${otherIndex}`}>
										<span className="min-w-0">
											<strong>{cleanTitle(other.title) || 'Untitled lead'}</strong>
											<p>{other.score || 0}/100 · {formatCost(other.cost_usd)} · {sourceLabel(other.source)}</p>
										</span>
									</a>
								))}
							</div>
						</Card>
					) : null}
				</div>
			</div>

			<Subhead>Navigate</Subhead>
			<div className="pager">
				{index > 0 ? <a className="btn" href={`#/leads/${index - 1}`}><ArrowLeft size={15} /> previous lead</a> : <span />}
				{index < total - 1 ? <a className="btn" href={`#/leads/${index + 1}`}>next lead →</a> : <span />}
			</div>
		</>
	);
}
