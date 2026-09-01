import { ArrowLeft, ExternalLink, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { CopyButton } from '../components/CopyButton';
import { Card, Disclosure, Empty, KeyValue, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { buildOpportunityStats, leadSources, sortLeads, type LeadSort } from '../utils/dashboard';
import { cleanTitle, compactMoney, formatDate, scoreTone, sourceLabel } from '../utils/format';
import { useRoute } from '../utils/route';
import type { CodeTechOpportunity, Status } from '../types/status';

export default function LeadsSection({ status }: { status: Status }) {
	const route = useRoute();
	const codeTech = status.code_tech_earning || {};
	const opportunities = codeTech.opportunities || [];

	const detailIndex = route.detail === null ? null : Number(route.detail);
	const detail = detailIndex !== null && Number.isInteger(detailIndex) ? opportunities[detailIndex] : undefined;

	if (detail) return <LeadDetail lead={detail} index={detailIndex as number} total={opportunities.length} />;

	return <LeadList status={status} opportunities={opportunities} />;
}

/* --------------------------------------------------------------------- list */

function LeadList({ status, opportunities }: { status: Status; opportunities: CodeTechOpportunity[] }) {
	const codeTech = status.code_tech_earning || {};
	const [query, setQuery] = useState('');
	const [source, setSource] = useState('all');
	const [sort, setSort] = useState<LeadSort>('value');

	const stats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
	const sources = useMemo(() => leadSources(opportunities), [opportunities]);

	const visible = useMemo(() => {
		const needle = query.trim().toLowerCase();
		const filtered = opportunities.filter((lead) => {
			if (source !== 'all' && (lead.source || 'unknown') !== source) return false;
			if (!needle) return true;
			return [lead.title, lead.reason, lead.next_step, lead.source]
				.some((field) => (field || '').toLowerCase().includes(needle));
		});
		return sortLeads(filtered, sort);
	}, [opportunities, query, source, sort]);

	return (
		<>
			<SectionHead
				title="Leads"
				blurb={`Ranked earning opportunities from the research cycle. Refreshed every ${codeTech.refresh_hours || 24}h — last ${formatDate(codeTech.last_refresh_at)}.`}
			/>

			<div className="tile-row">
				<Tile label="Leads tracked" value={String(stats.total)} detail={`${stats.paidCount} with value signals`} tone="info" />
				<Tile label="Pipeline value" value={compactMoney(stats.estimatedValue)} detail="sum of estimates" tone="good" />
				<Tile label="Best single lead" value={compactMoney(stats.topValue)} detail={`top score ${stats.topScore}`} tone="good" />
				<Tile label="Pursued" value={String(stats.pursued)} detail={`${stats.total - stats.pursued} untouched`} tone={stats.pursued ? 'good' : 'warn'} />
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
					<div className="segmented" role="group" aria-label="Filter by source">
						<button type="button" className={source === 'all' ? 'active' : ''} onClick={() => setSource('all')}>
							all <em>{opportunities.length}</em>
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
					<div className="segmented" role="group" aria-label="Sort leads">
						<button type="button" className={sort === 'value' ? 'active' : ''} onClick={() => setSort('value')}>value</button>
						<button type="button" className={sort === 'score' ? 'active' : ''} onClick={() => setSort('score')}>score</button>
					</div>
				</div>

				{visible.length ? (
					<div className="lead-table">
						{visible.map((lead) => {
							const index = opportunities.indexOf(lead);
							return (
								<a className="lead-row" href={`#/leads/${index}`} key={`${lead.url}-${index}`}>
									<span className="lead-row-value">{compactMoney(lead.estimated_value_usd || 0)}</span>
									<span className="lead-row-body">
										<strong>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
										<p>{lead.reason || 'No reason recorded.'}</p>
									</span>
									<span className="lead-row-meta">
										<Pill tone="neutral">{sourceLabel(lead.source)}</Pill>
										<Pill tone={scoreTone(lead.score)}>{lead.score || 0}</Pill>
										{lead.pursued ? <Pill tone="good">pursued</Pill> : null}
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
	return (
		<>
			<a className="btn back" href="#/leads"><ArrowLeft size={15} /> all leads</a>

			<SectionHead
				title={cleanTitle(lead.title) || 'Untitled lead'}
				blurb={lead.reason || 'No reason recorded for this lead.'}
				action={lead.url ? <a className="btn primary" href={lead.url} target="_blank" rel="noreferrer"><ExternalLink size={15} /> open source</a> : undefined}
			/>

			<div className="tile-row">
				<Tile label="Estimated value" value={compactMoney(lead.estimated_value_usd || 0)} tone="good" />
				<Tile label="Fit score" value={String(lead.score || 0)} detail="out of 100" tone={scoreTone(lead.score)} />
				<Tile label="Source" value={sourceLabel(lead.source)} detail={`lead ${index + 1} of ${total}`} tone="info" />
				<Tile label="Status" value={lead.pursued ? 'pursued' : 'open'} detail="in active queue" tone={lead.pursued ? 'good' : 'warn'} />
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
					) : null}
				</div>

				<div className="stack">
					<Card title="Lead facts">
						<KeyValue
							rows={[
								['Value', compactMoney(lead.estimated_value_usd || 0)],
								['Score', `${lead.score || 0}/100`],
								['Source', sourceLabel(lead.source)],
								['Pursued', lead.pursued ? 'yes' : 'no'],
								['Link', lead.url ? <a href={lead.url} target="_blank" rel="noreferrer">open ↗</a> : '—'],
							]}
						/>
					</Card>

					{lead.outreach_draft ? (
						<Disclosure title="Outreach draft" hint="Review before sending — nothing is sent automatically." >
							<div className="stack">
								<pre className="code-block">{lead.outreach_draft}</pre>
								<CopyButton text={lead.outreach_draft} label="copy draft" />
							</div>
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
