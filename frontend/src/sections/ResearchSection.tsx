import { AlertTriangle, ExternalLink, Lightbulb, ListChecks, Target } from 'lucide-react';
import { Bullets, Card, Disclosure, Empty, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { formatDate } from '../utils/format';
import { isAvoidedSuggestion } from '../utils/suggestions';
import type { Status } from '../types/status';

export default function ResearchSection({ status }: { status: Status }) {
	const codeTech = status.code_tech_earning || {};
	const brief = codeTech.online_ai_brief || {};
	const services = brief.free_ai_services || [];
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
		<>
			<SectionHead
				title="Research"
				blurb={`Free-tier AI services and earning playbooks from the research cycle. Last refreshed ${formatDate(codeTech.last_refresh_at)}.`}
			/>

			<div className="tile-row">
				<Tile label="Free services" value={String(services.length)} detail="no credit card required" tone="good" />
				<Tile label="Earning ideas" value={String(ideas.length)} detail="with pricing guidance" tone="info" />
				<Tile label="Owner actions" value={String(ownerActions.length)} detail="manual setup steps" tone={ownerActions.length ? 'warn' : 'neutral'} />
				<Tile label="Bot suggestions" value={String(suggestions.length)} detail="free-tier only" tone="neutral" />
				<Tile label="MRR models kept" value={String(mrrViable.length)} detail={`${mrrRefused.length} refused`} tone={mrrViable.length ? 'good' : 'neutral'} />
			</div>

			{brief.summary ? (
				<Card title="Current thesis" hint="The strongest angle the research cycle identified.">
					<p className="prose lead-in">{brief.summary}</p>
				</Card>
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
				<Disclosure title="Strategy playbook" hint="How to convert research into income" count={codeTech.strategy_playbook?.length}>
					<Bullets items={codeTech.strategy_playbook || []} />
				</Disclosure>
				<Disclosure title="Focus areas" hint="Where to look for leads" count={codeTech.focus?.length}>
					<Bullets items={codeTech.focus || []} />
				</Disclosure>
				<Disclosure title="Free-AI focus" hint="Service categories being tracked" count={codeTech.free_ai_focus?.length}>
					<Bullets items={codeTech.free_ai_focus || []} />
				</Disclosure>
				<Disclosure title="Monetization patterns" hint="Repeatable ways to charge" count={codeTech.monetization_patterns?.length}>
					<Bullets items={codeTech.monetization_patterns || []} />
				</Disclosure>
				<Disclosure title="Service niches" hint="Remote work categories in scope" count={codeTech.remote_service_niches?.length}>
					<Bullets items={codeTech.remote_service_niches || []} />
				</Disclosure>
				<Disclosure title="Lead requirements" hint="What a lead must satisfy" count={codeTech.requirements?.length}>
					<Bullets items={codeTech.requirements || []} />
				</Disclosure>
				<Disclosure title="Avoid patterns" hint="Disqualifies a lead immediately" count={codeTech.avoid_patterns?.length}>
					<Bullets items={codeTech.avoid_patterns || []} />
				</Disclosure>
				{suggestions.length ? (
					<Disclosure title="Bot suggestions" hint="Ideas proposed by the last cycle" count={suggestions.length}>
						<div className="stack">
							{suggestions.map((suggestion) => (
								<article className="suggestion" key={suggestion.title}>
									<div className="suggestion-head">
										<strong>{suggestion.title}</strong>
										<Pill tone={suggestion.free_tier ? 'good' : 'warn'}>{suggestion.free_tier ? 'free' : 'paid'}</Pill>
									</div>
									<p className="prose">{suggestion.description}</p>
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
				<span><AlertTriangle size={14} /> avoid patterns reject them</span>
				<span><Lightbulb size={14} /> ideas become leads</span>
			</div>
		</>
	);
}
