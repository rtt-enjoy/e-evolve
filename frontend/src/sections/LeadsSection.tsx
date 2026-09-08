import { ArrowLeft, ExternalLink, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { CopyButton } from '../components/CopyButton';
import { Card, Disclosure, Empty, KeyValue, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { buildOpportunityStats, leadSources, sortLeads, type LeadSort } from '../utils/dashboard';
import { cleanTitle, formatDate, leadAge, scoreTone, sourceLabel } from '../utils/format';
import { useRoute } from '../utils/route';
import type { CodeTechOpportunity, LeadKind, Status } from '../types/status';

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

export default function LeadsSection({ status }: { status: Status }) {
	const route = useRoute();
	const codeTech = status.code_tech_earning || {};
	const opportunities = codeTech.opportunities || [];

	const detailIndex = route.detail === null ? null : Number(route.detail);
	// A lead id is its index in the unsorted queue, and the queue is rebuilt
	// every refresh -- so an old link can point past the end. Fall back to the
	// list rather than rendering a blank page.
	const detail =
		detailIndex !== null && Number.isInteger(detailIndex) ? opportunities[detailIndex] : undefined;

	if (detail) return <LeadDetail lead={detail} index={detailIndex as number} total={opportunities.length} />;

	return <LeadList status={status} opportunities={opportunities} />;
}

/* --------------------------------------------------------------------- list */

function LeadList({ status, opportunities }: { status: Status; opportunities: CodeTechOpportunity[] }) {
	const codeTech = status.code_tech_earning || {};
	const [query, setQuery] = useState('');
	const [source, setSource] = useState('all');
	const [kind, setKind] = useState<LeadKind | 'all'>('all');
	// Newest first by default: the complaint that started this rebuild was
	// that the page showed stale leads.
	const [sort, setSort] = useState<LeadSort>('newest');

	const stats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
	const sources = useMemo(() => leadSources(opportunities), [opportunities]);

	const visible = useMemo(() => {
		const needle = query.trim().toLowerCase();
		const filtered = opportunities.filter((lead) => {
			if (kind !== 'all' && normalizeKind(lead.kind) !== kind) return false;
			if (source !== 'all' && (lead.source || 'unknown') !== source) return false;
			if (!needle) return true;
			return [lead.title, lead.reason, lead.next_step, lead.source, lead.manual_setup, lead.verified_note]
				.some((field) => (field || '').toLowerCase().includes(needle));
		});
		return sortLeads(filtered, sort);
	}, [opportunities, query, source, kind, sort]);

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
				<Tile label="Top score" value={String(stats.topScore)} detail="out of 100" tone={scoreTone(stats.topScore)} />
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

				{visible.length ? (
					<div className="lead-table">
						{visible.map((lead) => {
							const index = opportunities.indexOf(lead);
							const isChannel = normalizeKind(lead.kind) === 'channel';
							return (
								<a className="lead-row" href={`#/leads/${index}`} key={`${lead.url}-${index}`}>
									{/* Score leads the row: it ranks by how passive the income is. */}
									<span className={`lead-row-age tone-${scoreTone(lead.score)}`}>{lead.score || 0}</span>
									<span className="lead-row-body">
										<strong>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
										<p>{lead.reason || 'No reason recorded.'}</p>
									</span>
									<span className="lead-row-meta">
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
										<Pill tone={scoreTone(lead.score)}>{lead.score || 0}</Pill>
									</span>
								</a>
							);
						})}
					</div>
				) : (
					<Empty text={opportunities.length ? 'No leads match this filter.' : 'No research leads in the queue yet.'} />
				)}
			</Card>
		</>
	);
}

/* ------------------------------------------------------------------- detail */

function LeadDetail({ lead, index, total }: { lead: CodeTechOpportunity; index: number; total: number }) {
	const age = leadAge(lead.age_hours);
	const isChannel = normalizeKind(lead.kind) === 'channel';
	const setup = (lead.manual_setup || '').trim();
	const needsSetup = setup !== '' && !setup.toLowerCase().startsWith('none');
	const parts = Object.entries(lead.score_parts || {});

	return (
		<>
			<a className="btn back" href="#/leads"><ArrowLeft size={15} /> all leads</a>

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
					value={needsSetup ? 'one-time' : 'none'}
					detail={needsSetup ? 'before it can earn anything' : 'nothing to do'}
					tone={needsSetup ? 'warn' : 'good'}
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
								['Posted', lead.posted_at ? formatDate(lead.posted_at) : 'not applicable'],
								['Seen by bot', lead.discovered_at ? formatDate(lead.discovered_at) : '—'],
								['Link', lead.url ? <a href={lead.url} target="_blank" rel="noreferrer">open ↗</a> : '—'],
							]}
						/>
					</Card>

					{parts.length ? (
						<Disclosure title="Why it ranks here" hint="Each component of the score, 0 to 1." count={parts.length}>
							<KeyValue rows={parts.map(([name, value]) => [name.replace(/_/g, ' '), value.toFixed(2)])} />
						</Disclosure>
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
