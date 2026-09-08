import { ArrowLeft, ExternalLink, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { CopyButton } from '../components/CopyButton';
import { Card, Disclosure, Empty, KeyValue, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { buildOpportunityStats, leadSources, sortLeads, type LeadSort } from '../utils/dashboard';
import { cleanTitle, formatDate, formatLeadValue, leadAge, scoreTone, sourceLabel, valueBasisLabel } from '../utils/format';
import { useRoute } from '../utils/route';
import type { CodeTechOpportunity, LeadKind, Status } from '../types/status';

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
			if (kind !== 'all' && (lead.kind || 'demand') !== kind) return false;
			if (source !== 'all' && (lead.source || 'unknown') !== source) return false;
			if (!needle) return true;
			return [lead.title, lead.reason, lead.next_step, lead.source, lead.buyer, lead.value_note]
				.some((field) => (field || '').toLowerCase().includes(needle));
		});
		return sortLeads(filtered, sort);
	}, [opportunities, query, source, kind, sort]);

	return (
		<>
			<SectionHead
				title="Leads"
				blurb={
					`Live market signals and the free tooling to serve them. Refreshed every ${codeTech.refresh_hours || 6}h — last ${formatDate(codeTech.last_refresh_at)}.` +
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
					label="Leads tracked"
					value={String(stats.total)}
					detail={`${stats.demandCount} demand · ${stats.supplyCount} tooling`}
					tone="info"
				/>
				<Tile
					label="Posted today"
					value={String(stats.freshCount)}
					detail="within the last 24h"
					tone={stats.freshCount ? 'good' : 'warn'}
				/>
				<Tile
					label="With a stated price"
					value={String(stats.withValue)}
					detail="published by the source, not inferred"
					tone={stats.withValue ? 'good' : 'neutral'}
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
						<button type="button" className={kind === 'demand' ? 'active' : ''} onClick={() => setKind('demand')}>
							demand <em>{stats.demandCount}</em>
						</button>
						<button type="button" className={kind === 'supply' ? 'active' : ''} onClick={() => setKind('supply')}>
							tooling <em>{stats.supplyCount}</em>
						</button>
					</div>
					<div className="segmented" role="group" aria-label="Sort leads">
						<button type="button" className={sort === 'newest' ? 'active' : ''} onClick={() => setSort('newest')}>newest</button>
						<button type="button" className={sort === 'score' ? 'active' : ''} onClick={() => setSort('score')}>score</button>
						<button type="button" className={sort === 'value' ? 'active' : ''} onClick={() => setSort('value')}>price</button>
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
							const age = leadAge(lead.age_hours);
							const price = formatLeadValue(lead);
							return (
								<a className="lead-row" href={`#/leads/${index}`} key={`${lead.url}-${index}`}>
									{/* Age leads the row, because freshness is what was broken. */}
									<span className={`lead-row-age tone-${age.tone}`}>{age.label}</span>
									<span className="lead-row-body">
										<strong>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
										<p>{lead.reason || 'No reason recorded.'}</p>
									</span>
									<span className="lead-row-meta">
										{/* A price Pill only when one exists: an em dash is honest, "$0" is not. */}
										{price !== '—' ? <Pill tone="good">{price}</Pill> : null}
										<Pill tone={(lead.kind || 'demand') === 'demand' ? 'info' : 'neutral'}>
											{(lead.kind || 'demand') === 'demand' ? 'demand' : 'tooling'}
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
	const price = formatLeadValue(lead);
	const isDemand = (lead.kind || 'demand') === 'demand';
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
				{/* Never toned 'good' when unpriced -- green next to an em dash
				    reads as a confirmed zero. */}
				<Tile
					label="Stated price"
					value={price}
					detail={valueBasisLabel(lead.value_basis)}
					tone={price === '—' ? 'neutral' : 'good'}
				/>
				<Tile label="Fit score" value={String(lead.score || 0)} detail="out of 100" tone={scoreTone(lead.score)} />
				<Tile label="Posted" value={age.label} detail={isDemand ? 'buyer may still be looking' : 'last repo activity'} tone={age.tone} />
				<Tile
					label="Kind"
					value={isDemand ? 'demand' : 'tooling'}
					detail={isDemand ? 'somebody is paying' : 'what you deliver with'}
					tone={isDemand ? 'info' : 'neutral'}
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
						{/* Price and provenance always travel together. */}
						<KeyValue
							rows={[
								['Buyer', lead.buyer || 'not named'],
								['Price', price],
								['Price basis', valueBasisLabel(lead.value_basis)],
								['Score', `${lead.score || 0}/100`],
								['Source', sourceLabel(lead.source)],
								['Posted', lead.posted_at ? formatDate(lead.posted_at) : 'unknown'],
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
