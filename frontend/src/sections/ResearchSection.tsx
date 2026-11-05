import { AlertTriangle, ExternalLink, Lightbulb, ListChecks, Search, Target } from 'lucide-react';
import { useMemo, useState } from 'react';
import { AddedPill, Banner, Bullets, Card, Disclosure, Empty, KeyValue, Pill, SectionHead, Subhead } from '../components/ui';
import { formatDate, hoursSince, leadAge } from '../utils/format';
import {
	CATEGORIES,
	buildResearchRows,
	closesSoon,
	isFresh,
	researchSourceName,
	sortResearch,
	timing,
	type ResearchCategory,
	type ResearchRow,
	type ResearchSort,
} from '../utils/research';
import { isAvoidedSuggestion } from '../utils/suggestions';
import type { Status } from '../types/status';

/** Rows a group shows before "show more", so 80 rows do not become a 6,000px page. */
const GROUP_PAGE = 12;

type QuickFilter = 'prize' | 'crypto' | 'nokyc' | 'fresh';

/**
 * Same list as Leads on purpose: this page reuses the `.lead-row*`,
 * `.leads-stats`, `.leads-chip*` and `.lead-group*` classes, so the two pages
 * read as one system. A change to those classes changes both pages.
 */
function ResearchListRow({ row }: { row: ResearchRow }) {
	// Two clocks, never merged: when the bot put the row on this page (the
	// thing that says "is this new to me"), and the source's own timing.
	const listedHours = hoursSince(row.discovered_at);
	const listed = leadAge(listedHours);
	const reason = [row.prize || 'no prize stated', row.detail].filter(Boolean).join(' · ');
	return (
		<div className="lead-row">
			<a className="lead-row-link" href={row.url || undefined} target="_blank" rel="noreferrer">
				<span className={`score-chip ${row.score >= 85 ? 'good' : row.score >= 60 ? 'info' : row.score >= 35 ? 'warn' : 'bad'}`} title="research score, out of 100">
					{row.score}
				</span>
				<span className="lead-row-body">
					<strong title={row.title}>{row.title}</strong>
					<p title={reason}>{reason}</p>
				</span>
				<span className="lead-row-meta">
					{row.crypto ? <Pill tone="good">crypto</Pill> : null}
					{row.kyc === 'not required' ? <Pill tone="good">no KYC</Pill> : null}
					{row.beginner ? <Pill tone="neutral">beginner</Pill> : null}
					<span className="lead-row-time">
						{/* The listed time is the row's freshness. A snapshot from before
						    the stamp existed says so instead of implying a time. */}
						<b className={listed.tone} title={row.discovered_at ? `Listed on this page ${formatDate(row.discovered_at)}` : undefined}>
							{row.discovered_at ? `Listed ${formatDate(row.discovered_at)} · ${listed.label} ago` : 'Listed time not recorded'}
						</b>
						<span>
							{researchSourceName(row.source)} · {timing(row)}
						</span>
					</span>
				</span>
			</a>
			{row.url ? (
				<span className="lead-row-source grid place-items-center text-faint" aria-hidden="true">
					<ExternalLink size={15} />
				</span>
			) : (
				<span className="lead-row-source" aria-hidden="true" />
			)}
		</div>
	);
}

export default function ResearchSection({ status }: { status: Status }) {
	const [query, setQuery] = useState('');
	const [category, setCategory] = useState<ResearchCategory | 'all'>('all');
	const [quick, setQuick] = useState<Set<QuickFilter>>(new Set());
	// Newest first by default: the page exists to show what was added.
	const [sort, setSort] = useState<ResearchSort>('newest');
	const [limit, setLimit] = useState<Record<string, number>>({});

	const ctf = status.ctf_bounty || {};
	const feed = status.research_feed || {};
	const rows = useMemo(() => buildResearchRows(status), [status]);

	const counts = useMemo(() => {
		const byCategory = new Map<ResearchCategory, number>();
		for (const row of rows) byCategory.set(row.category, (byCategory.get(row.category) || 0) + 1);
		return {
			byCategory,
			fresh: rows.filter(isFresh).length,
			soon: rows.filter(closesSoon).length,
			prize: rows.filter((row) => row.pays).length,
			crypto: rows.filter((row) => row.crypto).length,
			nokyc: rows.filter((row) => row.kyc === 'not required').length,
		};
	}, [rows]);

	const toggleQuick = (key: QuickFilter) =>
		setQuick((current) => {
			const next = new Set(current);
			if (next.has(key)) next.delete(key);
			else next.add(key);
			return next;
		});

	const visible = useMemo(() => {
		const needle = query.trim().toLowerCase();
		const filtered = rows.filter((row) => {
			if (category !== 'all' && row.category !== category) return false;
			if (quick.has('prize') && !row.pays) return false;
			if (quick.has('crypto') && !row.crypto) return false;
			if (quick.has('nokyc') && row.kyc !== 'not required') return false;
			if (quick.has('fresh') && !isFresh(row)) return false;
			if (!needle) return true;
			return [row.title, row.prize, row.detail, row.source].some((field) => (field || '').toLowerCase().includes(needle));
		});
		return sortResearch(filtered, sort);
	}, [rows, query, category, quick, sort]);

	const lastRefresh = [ctf.last_refresh_at, feed.last_refresh_at].filter(Boolean).sort().pop();
	const stale = ctf.last_reason === 'fetch_failed' || feed.last_reason === 'fetch_failed';
	const failed = [...(ctf.last_reason === 'fetch_failed' ? ['CTFtime'] : []), ...(feed.failed_sources || [])];
	const sourceStats = feed.source_stats || [];

	const chip = (active: boolean, onClick: () => void, label: string, count?: number, pressed?: boolean) => (
		<button key={label} type="button" className={`leads-chip ${active ? 'active' : ''}`} aria-pressed={pressed} onClick={onClick}>
			{label}
			{typeof count === 'number' ? <em>{count}</em> : null}
		</button>
	);

	return (
		<>
			<SectionHead
				title="Research"
				blurb={`Prizes and bounties you could enter, from CTFs to hackathons and crypto bounty boards. Refreshed every 3h, last ${formatDate(lastRefresh)}.`}
			/>

			{/* Counts only: a prize is the organiser's claim, so nothing is summed. */}
			<div className="leads-stats" aria-label="Research counts">
				<div><span>Open items</span><strong>{rows.length}</strong></div>
				<div><span>Listed in 24h</span><strong>{counts.fresh}</strong></div>
				<div><span>Closing in 7d</span><strong>{counts.soon}</strong></div>
				<div><span>Prize stated</span><strong>{counts.prize}</strong></div>
				<div><span>Pays crypto</span><strong>{counts.crypto}</strong></div>
			</div>

			{stale || failed.length ? (
				<Banner tone="warn" text={`Could not reach ${failed.join(', ') || 'a source'} last cycle. Its rows are the last list that loaded.`} />
			) : null}

			<Card className="card-compact">
				<div className="leads-toolbar">
					<label className="search">
						<Search size={16} />
						<input
							type="search"
							placeholder="Search prizes and bounties…"
							value={query}
							onChange={(event) => setQuery(event.target.value)}
							aria-label="Search research"
						/>
					</label>
					<div className="leads-chips" role="group" aria-label="Sort research">
						{chip(sort === 'newest', () => setSort('newest'), 'newest')}
						{chip(sort === 'ending', () => setSort('ending'), 'ending soon')}
						{chip(sort === 'score', () => setSort('score'), 'score')}
					</div>
				</div>

				<div className="leads-chips" role="group" aria-label="Filter research">
					{chip(category === 'all', () => setCategory('all'), 'all', rows.length)}
					{CATEGORIES.filter((entry) => counts.byCategory.get(entry.key)).map((entry) =>
						chip(category === entry.key, () => setCategory(entry.key), entry.title.toLowerCase(), counts.byCategory.get(entry.key)),
					)}
					<span className="leads-sep" aria-hidden="true" />
					{chip(quick.has('prize'), () => toggleQuick('prize'), 'prize', counts.prize, quick.has('prize'))}
					{chip(quick.has('crypto'), () => toggleQuick('crypto'), 'crypto', counts.crypto, quick.has('crypto'))}
					{chip(quick.has('nokyc'), () => toggleQuick('nokyc'), 'no KYC', counts.nokyc, quick.has('nokyc'))}
					{chip(quick.has('fresh'), () => toggleQuick('fresh'), 'last 24h', counts.fresh, quick.has('fresh'))}
				</div>

				{visible.length ? (
					CATEGORIES.map((group) => {
						const groupRows = visible.filter((row) => row.category === group.key);
						if (!groupRows.length) return null;
						const cap = limit[group.key] || GROUP_PAGE;
						return (
							<section className="lead-group" key={group.key}>
								<header className="lead-group-head">
									<strong>{group.title}</strong>
									<span>{groupRows.length}</span>
									<em>{group.hint}</em>
								</header>
								<div className="lead-table">
									{groupRows.slice(0, cap).map((row) => (
										<ResearchListRow key={row.id} row={row} />
									))}
								</div>
								{groupRows.length > cap ? (
									<button
										type="button"
										className="btn lead-more"
										onClick={() => setLimit((current) => ({ ...current, [group.key]: cap + GROUP_PAGE }))}
									>
										Show {Math.min(GROUP_PAGE, groupRows.length - cap)} more · {groupRows.length - cap} left
									</button>
								) : null}
							</section>
						);
					})
				) : (
					<Empty text={rows.length ? 'Nothing matches this filter.' : 'No research rows yet. The next cycle checks again.'} />
				)}
			</Card>

			{/* Everything below is reference, so it starts closed: the summary line
			    is visible and the detail is one click away. */}
			<Subhead>Reference</Subhead>
			<div className="stack tight">
				<Disclosure title="Read before registering" hint="what a listed prize does and does not mean" count={4}>
					<Bullets
						items={[
							'A prize is the organiser’s own claim. Payout and identity checks are not published for CTFs, hackathons or Superteam, so open the rules page first.',
							'Immunefi states whether a program asks for KYC. Programs that do are not listed here, because the identity check is the one gate you cannot pass.',
							'Winning pays once, for your own work. It is not passive income and never counts as earnings on this dashboard.',
							'The bot only lists. It never registers, submits, or contacts anyone.',
						]}
					/>
				</Disclosure>

				<Disclosure title="Where rows come from" hint="read on every refresh, no keys" count={sourceStats.length + 1}>
					<KeyValue
						compact
						rows={[
							['CTFtime', `${ctf.fetched ?? 0} fetched · ${ctf.enterable ?? 0} enterable · ${(ctf.events || []).length} shown`],
							...sourceStats.map((entry): [string, string] => [
								entry.label || researchSourceName(entry.source),
								entry.ok === false
									? 'unreachable last refresh · showing the last good rows'
									: `${entry.fetched ?? 0} fetched · ${entry.kept ?? 0} usable${entry.screened ? ` · ${entry.screened} screened out` : ''}`,
							]),
						]}
					/>
					<p className="muted">
						{feed.pool_total ?? 0} candidates in the pool; each group shows the newest rows first, then the best scoring.
					</p>
				</Disclosure>

				<Disclosure title="Probed and left out" hint="checked, so they are not re-checked" count={6}>
					<Bullets
						items={[
							'Sherlock: the live list is finished contests, and its payouts require KYC.',
							'HackerOne and Bugcrowd program data: 19 MB, undated, and payouts need an ID.',
							'GitHub bounty labels: bot spam and "send one real email" tasks.',
							'Devfolio: hackathons are onsite in India.',
							'Algora and DoraHacks: no public JSON (HTML or a bot challenge).',
							'Cantina: no public API.',
						]}
					/>
				</Disclosure>

				<Disclosure title="Earlier research" hint="free AI services, earning ideas, MRR triage and guardrails" count={null}>
					<EarlierResearch status={status} />
				</Disclosure>
			</div>
		</>
	);
}

/** The research the page led with before CTFs: kept, but behind a click. */
function EarlierResearch({ status }: { status: Status }) {
	const codeTech = status.code_tech_earning || {};
	const brief = codeTech.online_ai_brief || {};
	const services = brief.free_ai_services || [];
	const themes = brief.market_themes || [];
	const ideas = brief.easy_earning_ideas || [];
	const ownerActions = brief.owner_actions || [];
	const suggestions = (status.suggestions || []).filter((suggestion) => !isAvoidedSuggestion(suggestion));
	const mrr = status.mrr_ideas || {};
	const mrrRanked = mrr.ranked_ideas || [];
	const mrrViable = mrr.viable || [];
	const mrrRefused = mrr.refused || [];
	const mrrSteps = mrr.validation_steps || [];
	const mrrActions = mrr.owner_actions || [];

	return (
				<div className="stack">
				{brief.summary ? (
					<Card title="Current thesis" hint="The strongest angle the research cycle identified.">
						<p className="prose lead-in">{brief.summary}</p>
					</Card>
				) : null}

				{themes.length ? (
					<>
						{/* What the *current* demand leads have in common. The rest of
						    this page is about supply — which free tools exist — and
						    this is the half that says what people are paying for. */}
						<Subhead>What the market is asking for</Subhead>
						<div className="grid-2">
							{themes.map((theme, index) => (
								<Card key={`${theme.theme}-${index}`} title={theme.theme || 'Theme'} action={<AddedPill at={theme.discovered_at} />}>
									<div className="stack">
										{theme.offer ? <p className="prose lead-in">{theme.offer}</p> : null}
										{theme.evidence ? <p className="muted">Seen in: {theme.evidence}</p> : null}
									</div>
								</Card>
							))}
						</div>
					</>
				) : null}

				<Subhead>Free AI services</Subhead>
				{services.length ? (
					<div className="grid-2">
						{services.map((service) => (
							<Card key={service.name || Math.random()} className="service">
								<div className="service-head">
									<strong>{service.name || 'Unnamed service'}</strong>
									<Pill tone={service.credit_card_required === 'no' ? 'good' : 'warn'}>
										{service.credit_card_required === 'no' ? 'no card' : `card: ${service.credit_card_required || '?'}`}
									</Pill>
								</div>
								<p className="prose">{service.what_it_does || 'No description recorded.'}</p>
								<dl className="mini-kv">
									<div><dt>free tier</dt><dd>{service.free_tier || 'unknown'}</dd></div>
									<div><dt>earn with it</dt><dd>{service.earn_with_it || '—'}</dd></div>
									<div><dt>price guide</dt><dd className="accent">{service.price_guide || '—'}</dd></div>
								</dl>
							</Card>
						))}
					</div>
				) : (
					<Card><Empty text="No free-service research recorded yet." /></Card>
				)}

				<Subhead>Earning ideas</Subhead>
				{ideas.length ? (
					<div className="stack">
						{ideas.map((idea) => (
							<Card key={idea.idea || Math.random()} className="idea">
								<div className="idea-head">
									<div className="min-w-0">
										<strong>{idea.idea || 'Unnamed idea'}</strong>
										<p>{idea.who_pays ? `Buyers: ${idea.who_pays}` : 'No buyer recorded.'}</p>
									</div>
									<div className="idea-price">
										<span>{idea.price_usd || '—'}</span>
										<em>{idea.time_to_first_dollar || 'unknown'}</em>
									</div>
								</div>
								<dl className="mini-kv">
									<div><dt>deliverable</dt><dd>{idea.deliverable || '—'}</dd></div>
									<div><dt>free stack</dt><dd>{idea.free_stack || '—'}</dd></div>
								</dl>
							</Card>
						))}
					</div>
				) : (
					<Card><Empty text="No earning ideas recorded yet." /></Card>
				)}

				<Subhead>Recurring revenue (MRR) triage</Subhead>
				{mrrViable.length || mrrRefused.length ? (
					<div className="stack">
						{mrr.summary ? (
							<Card title="Best current angle" hint="The strongest recurring-revenue fit for this stack.">
								<p className="prose lead-in">{mrr.summary}</p>
							</Card>
						) : null}

						{mrrRanked.length ? (
							<div className="stack">
								{mrrRanked.map((idea) => (
									<Card key={idea.name || Math.random()} className="idea">
										<div className="idea-head">
											<div className="min-w-0">
												<strong>{idea.name || 'Unnamed model'}</strong>
												<p>{idea.narrow_niche ? `Niche: ${idea.narrow_niche}` : 'No niche recorded.'}</p>
												<AddedPill at={idea.discovered_at} />
											</div>
											<div className="idea-price">
												<span>{idea.monthly_price_usd || '—'}</span>
												<em>{idea.runway_to_first_dollar || 'unknown'}</em>
											</div>
										</div>
										<dl className="mini-kv">
											<div><dt>who pays</dt><dd>{idea.who_pays || '—'}</dd></div>
											<div><dt>first proof</dt><dd>{idea.first_proof_artifact || '—'}</dd></div>
											<div><dt>why this stack</dt><dd>{idea.why_this_stack_fits || '—'}</dd></div>
											<div><dt>you do by hand</dt><dd>{idea.owner_must_do_by_hand || '—'}</dd></div>
										</dl>
									</Card>
								))}
							</div>
						) : mrrViable.length ? (
							<Card title="Surviving models" hint="Deterministic triage; no LLM brief this refresh.">
								<div className="stack">
									{mrrViable.map((model) => (
										<article className="suggestion" key={model.name || Math.random()}>
											<div className="suggestion-head">
												<strong>{model.name || 'Unnamed model'}</strong>
												<Pill tone="info">{model.bot_role || 'none'}</Pill>
												<AddedPill at={model.discovered_at} />
											</div>
											<p className="prose">{model.mrr_model || 'No MRR model recorded.'}</p>
											{(model.manual_steps || []).length ? (
												<Bullets items={model.manual_steps || []} />
											) : null}
										</article>
									))}
								</div>
							</Card>
						) : null}

						{mrrSteps.length ? (
							<Disclosure title="Validate without outreach" hint="Inbound only — the bot cannot contact anyone" count={mrrSteps.length} defaultOpen>
								<Bullets items={mrrSteps} />
							</Disclosure>
						) : null}

						{/* The refusals are the point: this is where the owner looks when
						    wondering why an idea they read about was not built. */}
						{mrrRefused.length ? (
							<Disclosure title="Refused, and why" hint="Needs a blocked action or absent infrastructure" count={mrrRefused.length}>
								<div className="stack">
									{mrrRefused.map((model) => (
										<article className="suggestion" key={model.name || Math.random()}>
											<div className="suggestion-head">
												<strong>{model.name || 'Unnamed model'}</strong>
												<Pill tone="warn">refused</Pill>
												<AddedPill at={model.discovered_at} />
											</div>
											<p className="prose">{model.reason || 'No reason recorded.'}</p>
											{model.mrr_model ? <code>{model.mrr_model}</code> : null}
										</article>
									))}
								</div>
							</Disclosure>
						) : null}

						{mrrActions.length ? (
							<Disclosure title="MRR next actions" hint="Most valuable first" count={mrrActions.length}>
								<Bullets items={mrrActions} />
							</Disclosure>
						) : null}
					</div>
				) : (
					<Card><Empty text="No MRR triage recorded yet." /></Card>
				)}

				<Subhead>Strategy and guardrails</Subhead>
				<div className="stack">
					{ownerActions.length ? (
						<Disclosure title="Owner actions" hint="Steps only a human can do" count={ownerActions.length} defaultOpen>
							<Bullets items={ownerActions} />
						</Disclosure>
					) : null}
					<Disclosure title="Focus areas" hint="Where to look for leads" count={codeTech.focus?.length}>
						<Bullets items={codeTech.focus || []} />
					</Disclosure>
					<Disclosure title="Free-AI focus" hint="Service categories being tracked" count={codeTech.free_ai_focus?.length}>
						<Bullets items={codeTech.free_ai_focus || []} />
					</Disclosure>
					<Disclosure title="Lead requirements" hint="What a lead must satisfy" count={codeTech.requirements?.length}>
						<Bullets items={codeTech.requirements || []} />
					</Disclosure>
					{suggestions.length ? (
						<Disclosure title="Bot suggestions" hint="Ideas proposed by the last cycle" count={suggestions.length}>
							<div className="stack">
								{suggestions.map((suggestion) => (
									<article className="suggestion" key={suggestion.title}>
										<div className="suggestion-head">
											<strong>{suggestion.title}</strong>
											{typeof suggestion.free_tier === 'boolean' ? (
												<Pill tone={suggestion.free_tier ? 'good' : 'warn'}>{suggestion.free_tier ? 'free' : 'paid'}</Pill>
											) : null}
										</div>
										<AddedPill at={suggestion.discovered_at} />
										<p className="prose">{suggestion.description}</p>
										{suggestion.owner_action ? <p className="prose"><strong>You do:</strong> {suggestion.owner_action}</p> : null}
										{suggestion.secret_needed ? <code>{suggestion.secret_needed}</code> : null}
										{(suggestion.how_to || []).length ? <Bullets items={suggestion.how_to || []} /> : null}
									</article>
								))}
							</div>
						</Disclosure>
					) : null}
					{(codeTech.reference_sources || []).length ? (
						<Disclosure title="Reference sources" hint="Where the research came from" count={codeTech.reference_sources?.length}>
							<div className="stack">
								{(codeTech.reference_sources || []).map((source) => (
									<a className="reference" key={source.url} href={source.url} target="_blank" rel="noreferrer">
										<span className="min-w-0">
											<strong>{source.title || source.url}</strong>
											<p>{source.takeaway || 'No takeaway recorded.'}</p>
										</span>
										<ExternalLink className="shrink-0" size={15} />
									</a>
								))}
							</div>
						</Disclosure>
					) : null}
				</div>

				<div className="legend">
					<span><Target size={14} /> focus drives lead discovery</span>
					<span><ListChecks size={14} /> requirements filter candidates</span>
					<span><AlertTriangle size={14} /> avoid patterns (on Leads) reject them</span>
					<span><Lightbulb size={14} /> ideas become leads</span>
				</div>
				</div>
	);
}
