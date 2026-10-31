import { AlertTriangle, ExternalLink, FileText } from 'lucide-react';
import type { ReactNode } from 'react';
import { Bullets, Card, Disclosure, Dot, Empty, KeyValue, Pill, SectionHead, Subhead } from '../components/ui';
import type { Tone } from '../components/ui';
import { engineChain, engineState } from '../utils/engine';
import { featureLabel, formatDate, money } from '../utils/format';
import { rejectLabel } from '../utils/dashboard';
import type { Status } from '../types/status';

export default function EngineSection({ status }: { status: Status }) {
	// Every figure here is what the last cycle observed (status.llm_engine),
	// not the routing preference: a preference is not a live engine.
	const engine = engineState(status);
	const chain = engineChain(status, engine);
	const workflows = Object.entries(status.llm_workflows || {});
	const evolution = status.last_evolution || {};
	const actions = status.last_earning?.actions || [];
	// Proposals park on an evolve/* branch and reach main only when merged.
	const branch = status.last_evolution_branch || evolution.branch || null;
	const pending = Boolean(status.evolution_pending_review && branch);
	const repo = status.github_repo && /^[\w.-]+\/[\w.-]+$/.test(status.github_repo) ? status.github_repo : null;
	const compareUrl = repo && branch && /^[\w./-]+$/.test(branch) ? `https://github.com/${repo}/compare/main...${branch}` : null;
	const evidence = Array.isArray(evolution.evidence) ? evolution.evidence : evolution.evidence ? [evolution.evidence] : [];
	const evoTone: Tone = evolution.error ? 'bad' : pending ? 'info' : 'neutral';

	return (
		<>
			<SectionHead title="Engine" blurb="Which model writes for the bot, and what it did last cycle." />

			<section className="card engine-hero">
				<div className="engine-hero-top">
					<div className="min-w-0">
						<span className="engine-eyebrow">Main engine · {engine.name}</span>
						<div className="engine-model">
							<Dot tone={engine.tone} />
							<code>{engine.model}</code>
						</div>
						<p className="engine-detail">{engine.detail}</p>
					</div>
					<Pill tone={engine.tone}>{engine.label}</Pill>
				</div>

				{engine.modelNote ? (
					<p className="engine-note">
						<AlertTriangle size={15} aria-hidden="true" />
						{engine.modelNote}
					</p>
				) : null}

				<ol className="chain" aria-label="Fallback order">
					{chain.map((step, index) => (
						<li key={step.name} className={`chain-step tone-${step.tone}`}>
							<span className="chain-num">{index + 1}</span>
							<div className="min-w-0">
								<strong>{step.name}</strong>
								<code>{step.model}</code>
							</div>
							<span className="chain-state">
								{step.state}
								{step.calls ? <em>{step.calls} call{step.calls === 1 ? '' : 's'}</em> : null}
							</span>
						</li>
					))}
				</ol>
			</section>

			<Subhead>Roles</Subhead>
			{workflows.length ? (
				<Card className="p-0 sm:p-0">
					<ul className="roles">
						{workflows.map(([role, workflow]) => {
							const serving = workflow.serving || workflow.provider || '';
							// The model that answered, not the role's preference: the
							// main engine's resolved model, or the fallback's.
							const model =
								serving === engine.provider
									? engine.model
									: serving === workflow.fallback_provider
										? workflow.fallback_model
										: serving === workflow.last_resort_provider
											? workflow.last_resort_model
											: workflow.model;
							const onFallback = workflow.primary_active === false || (serving === engine.provider && engine.tone === 'warn');
							return (
								<li key={role}>
									<div className="min-w-0">
										<strong>{featureLabel(role)}</strong>
										<p>{workflow.purpose || 'No purpose recorded.'}</p>
									</div>
									<code>{model || '—'}</code>
									<Pill tone={!workflow.active ? 'neutral' : onFallback ? 'warn' : 'good'}>
										{!workflow.active ? 'idle' : onFallback ? `fallback · ${serving}` : serving}
									</Pill>
								</li>
							);
						})}
					</ul>
				</Card>
			) : (
				<Card><Empty text="No role routing recorded in this snapshot." /></Card>
			)}

			<Subhead>Last cycle</Subhead>
			<div className="split">
				<div className="stack">
					<Card
						title="Evolution proposal"
						hint="Lands on an evolve/* branch. Nothing reaches main until you merge it."
						action={
							compareUrl && pending
								? <a className="btn" href={compareUrl} target="_blank" rel="noreferrer">review diff <ExternalLink size={13} /></a>
								: <Pill tone={evoTone}>{evolution.error ? 'failed' : pending ? 'in review' : 'no proposal'}</Pill>
						}
					>
						<p className="prose lead-in">{evolution.summary || 'No evolution summary recorded.'}</p>
						{evolution.error ? <p className="error-text mt-3">{evolution.error}</p> : null}
						{evolution.direction || evolution.money_path || evolution.verify || branch ? (
							<div className="mt-4">
								<KeyValue
									rows={[
										...(branch ? [['Branch', <code className="font-mono text-xs">{branch}</code>] as [string, ReactNode]] : []),
										...(evolution.direction ? [['Serves', evolution.direction] as [string, ReactNode]] : []),
										...(evolution.money_path ? [['Money path', evolution.money_path] as [string, ReactNode]] : []),
										...(evolution.verify ? [['How to verify', evolution.verify] as [string, ReactNode]] : []),
									]}
								/>
							</div>
						) : null}
						{evidence.length ? <div className="mt-4"><Bullets items={evidence.map(String)} /></div> : null}
						{(evolution.changes_applied || []).length ? (
							<div className="stack mt-4">
								{(evolution.changes_applied || []).map((change) => (
									<div className="change" key={`${change.file}-${change.reason}`}>
										<code>{change.file}</code>
										<p>{change.reason || 'Changed by evolution.'}</p>
									</div>
								))}
							</div>
						) : null}
					</Card>

					<Card title="Cycle actions" hint="What the research phase emitted.">
						{actions.length ? (
							<div className="stack">
								{actions.map((action, index) => (
									<div className={`action ${action.skipped ? 'held' : action.success === false ? 'bad' : 'good'}`} key={index}>
										<span className="action-platform">
											<FileText size={15} />
											{action.platform || 'module'}
										</span>
										<p>{action.skipped ? `Held back: ${rejectLabel(action.reject_code)}` : action.title || action.topic || action.symbol || action.error || 'Action recorded'}</p>
										{action.url ? <a href={action.url} target="_blank" rel="noreferrer">open ↗</a> : null}
										{typeof action.estimated_usd === 'number' ? <em>{money(action.estimated_usd, 4)}</em> : null}
									</div>
								))}
							</div>
						) : (
							<Empty text="No actions recorded in the latest cycle." />
						)}
					</Card>
				</div>

				<div className="stack">
					<Card title="Cycle facts">
						<KeyValue
							rows={[
								['Cycle', `#${status.total_runs || 0}`],
								['Last run', formatDate(status.last_run)],
								['Duration', `${status.last_cycle_seconds || 0}s`],
								['Version', status.version || '—'],
								[engine.secret, engine.keySet === null ? 'not reported' : engine.keySet ? 'set' : 'not set'],
								...(engine.endpoint ? [['Endpoint', <code className="font-mono text-xs">{engine.endpoint}</code>] as [string, ReactNode]] : []),
								...(engine.reason ? [['Fallback reason', engine.reason] as [string, ReactNode]] : []),
							]}
						/>
					</Card>

					{(evolution.suggestions || []).length ? (
						<Disclosure title="Evolution suggestions" hint="Owner actions proposed with the last evolution" count={evolution.suggestions?.length}>
							<div className="stack">
								{(evolution.suggestions || []).map((suggestion) => (
									<article className="suggestion" key={suggestion.title}>
										<div className="suggestion-head">
											<strong>{suggestion.title}</strong>
											{typeof suggestion.free_tier === 'boolean' ? (
												<Pill tone={suggestion.free_tier ? 'good' : 'warn'}>{suggestion.free_tier ? 'free' : 'paid'}</Pill>
											) : null}
										</div>
										<p className="prose">{suggestion.description}</p>
										{suggestion.owner_action ? <p className="prose"><strong>You do:</strong> {suggestion.owner_action}</p> : null}
										{(suggestion.how_to || []).length ? (
											<ul className="bullets">
												{(suggestion.how_to || []).map((step) => <li key={step}>{step}</li>)}
											</ul>
										) : null}
									</article>
								))}
							</div>
						</Disclosure>
					) : null}

					{Object.keys(status.llm_roles || {}).length ? (
						<Disclosure title="Raw role map" hint="role → provider" count={Object.keys(status.llm_roles || {}).length}>
							<KeyValue rows={Object.entries(status.llm_roles || {}).map(([role, provider]) => [role, provider])} />
						</Disclosure>
					) : null}
				</div>
			</div>
		</>
	);
}
