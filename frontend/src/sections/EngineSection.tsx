import { AlertTriangle, ExternalLink } from 'lucide-react';
import type { ReactNode } from 'react';
import { AddedPill, Card, Dot, Fold, KeyValue, Pill, SectionHead } from '../components/ui';
import type { Tone } from '../components/ui';
import { engineChain, engineState } from '../utils/engine';
import { featureLabel, money } from '../utils/format';
import { rejectLabel } from '../utils/dashboard';
import { suggestionPrompt } from '../utils/suggestions';
import { CopyButton } from '../components/CopyButton';
import type { Status, Suggestion } from '../types/status';

/** One labelled paragraph of a proposal's reasoning. Renders nothing when empty. */
function Brief({ label, children }: { label: string; children?: ReactNode }) {
	if (!children) return null;
	return (
		<section className="brief-part">
			<h4>{label}</h4>
			{children}
		</section>
	);
}

function SuggestionRow({ suggestion }: { suggestion: Suggestion }) {
	const prompt = suggestionPrompt(suggestion);
	const steps = suggestion.how_to || [];
	return (
		<Fold
			title={suggestion.title || 'Untitled suggestion'}
			meta={
				<>
					{typeof suggestion.free_tier === 'boolean' ? <Pill tone={suggestion.free_tier ? 'good' : 'warn'}>{suggestion.free_tier ? 'free' : 'paid'}</Pill> : null}
					<AddedPill at={suggestion.discovered_at} />
				</>
			}
		>
			<div className="brief">
				<Brief label="Why">{suggestion.description ? <p>{suggestion.description}</p> : null}</Brief>
				<Brief label="You do">{suggestion.owner_action ? <p>{suggestion.owner_action}</p> : null}</Brief>
				<Brief label="Steps">
					{steps.length ? <ol className="steps">{steps.map((step) => <li key={step}>{step.replace(/^Step\s*\d+\s*:\s*/i, '')}</li>)}</ol> : null}
				</Brief>
				<Brief label="Prompt">
					<div className="prompt-box">
						<pre className="code-block">{prompt}</pre>
						<CopyButton text={prompt} label="copy prompt" />
					</div>
				</Brief>
			</div>
		</Fold>
	);
}

export default function EngineSection({ status }: { status: Status }) {
	// Every figure here is what the last cycle observed (status.llm_engine),
	// not the routing preference: a preference is not a live engine.
	const engine = engineState(status);
	const chain = engineChain(status, engine);
	const workflows = Object.entries(status.llm_workflows || {});
	const evolution = status.last_evolution || {};
	const actions = status.last_earning?.actions || [];
	const suggestions = evolution.suggestions || [];
	// Proposals park on an evolve/* branch and reach main only when merged.
	const branch = status.last_evolution_branch || evolution.branch || null;
	const pending = Boolean(status.evolution_pending_review && branch);
	const repo = status.github_repo && /^[\w.-]+\/[\w.-]+$/.test(status.github_repo) ? status.github_repo : null;
	const compareUrl = repo && branch && /^[\w./-]+$/.test(branch) ? `https://github.com/${repo}/compare/main...${branch}` : null;
	const evidence = (Array.isArray(evolution.evidence) ? evolution.evidence : evolution.evidence ? [evolution.evidence] : []).map(String);
	const changes = evolution.changes_applied || [];
	const evoTone: Tone = evolution.error ? 'bad' : pending ? 'info' : 'neutral';
	const hasDetail = Boolean(evolution.direction || evolution.money_path || evolution.verify || evidence.length || changes.length || branch || (evolution.summary || '').length > 220);

	const facts: Array<[string, ReactNode]> = [
		[engine.secret, engine.keySet === null ? 'not reported' : engine.keySet ? 'set' : 'not set'],
		...(engine.endpoint ? [['Endpoint', <code className="font-mono text-xs">{engine.endpoint.replace(/^https?:\/\//, '')}</code>] as [string, ReactNode]] : []),
		...(engine.reason ? [['Fallback reason', engine.reason] as [string, ReactNode]] : []),
		...(engine.fallback ? [['Fallback', `${engine.fallback.name} · ${engine.fallback.keySet === false ? 'key not set' : engine.fallback.reason || (engine.fallback.live === false ? 'off this cycle' : 'ready')}`] as [string, ReactNode]] : []),
		...(Object.keys(engine.calls).length ? [['Calls last cycle', Object.entries(engine.calls).map(([name, n]) => `${name} ${n}`).join(' · ')] as [string, ReactNode]] : []),
		...(status.version ? [['Bot version', status.version] as [string, ReactNode]] : []),
	];

	return (
		<>
			<SectionHead title="Engine" blurb="Which model writes for the bot, and what it did last cycle." />

			<section className="card card-compact engine-hero compact">
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

			<div className="split even">
				<Card className="card-compact" title="Roles" hint="Model that answered each job last cycle.">
					{workflows.length ? (
						<ul className="roles compact">
							{workflows.map(([role, workflow]) => {
								const serving = workflow.serving || workflow.provider || '';
								// The model that answered, not the role's preference: the
								// main engine's resolved model, or the fallback's.
								const model =
									serving === engine.provider
										? engine.model
										: serving === workflow.fallback_provider
											? workflow.fallback_model
											: workflow.model;
								const onFallback = workflow.primary_active === false || (serving === engine.provider && engine.tone === 'warn');
								return (
									<li key={role} title={workflow.purpose || undefined}>
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
					) : (
						<p className="muted">No role routing recorded in this snapshot.</p>
					)}
				</Card>

				<Card className="card-compact" title="Engine facts" hint="What the last cycle observed about the key.">
					<KeyValue compact rows={facts} />
				</Card>
			</div>

			<Card
				className="card-compact"
				title="Evolution proposal"
				hint="Lands on an evolve/* branch. Nothing reaches main until you merge it."
				action={
					compareUrl && pending
						? <a className="btn" href={compareUrl} target="_blank" rel="noreferrer">review diff <ExternalLink size={13} /></a>
						: <Pill tone={evoTone}>{evolution.error ? 'failed' : pending ? 'in review' : 'no proposal'}</Pill>
				}
			>
				<p className="proposal-summary">{evolution.summary || 'No evolution summary recorded.'}</p>
				{evolution.error ? <p className="error-text text-[13px]">{evolution.error}</p> : null}
				{hasDetail ? (
					<Fold title="Proposal details" meta={[evolution.proposed_version && `v${evolution.proposed_version}`, changes.length && `${changes.length} file${changes.length === 1 ? '' : 's'}`, evidence.length && `${evidence.length} evidence`].filter(Boolean).join(' · ')}>
						<div className="brief">
							<Brief label="Summary">{(evolution.summary || '').length > 220 ? <p>{evolution.summary}</p> : null}</Brief>
							<Brief label="Serves">{evolution.direction ? <p>{evolution.direction}</p> : null}</Brief>
							<Brief label="Money path">{evolution.money_path ? <p>{evolution.money_path}</p> : null}</Brief>
							<Brief label="How to verify">{evolution.verify ? <p>{evolution.verify}</p> : null}</Brief>
							<Brief label="Evidence">
								{evidence.length ? <ul className="bullets tight">{evidence.map((item) => <li key={item}>{item}</li>)}</ul> : null}
							</Brief>
							<Brief label="Files changed">
								{changes.length ? (
									<ul className="changes">
										{changes.map((change) => (
											<li key={`${change.file}-${change.reason}`}>
												<code>{change.file}</code>
												<p>{change.reason || 'Changed by evolution.'}</p>
											</li>
										))}
									</ul>
								) : null}
							</Brief>
							<Brief label="Branch">{branch ? <code className="font-mono text-xs">{branch}</code> : null}</Brief>
						</div>
					</Fold>
				) : null}
			</Card>

			{suggestions.length ? (
				<Card className="card-compact" title="Owner actions" hint="Steps the last evolution says only you can take. Open one for its prompt." action={<span className="card-meta">{suggestions.length}</span>}>
					<div className="folds">
						{suggestions.map((suggestion) => <SuggestionRow key={suggestion.title} suggestion={suggestion} />)}
					</div>
				</Card>
			) : null}

			{actions.length ? (
				<Card className="card-compact" title="Cycle actions" hint="What the research phase emitted." action={<span className="card-meta">{actions.length}</span>}>
					<ul className="actions-list">
						{actions.map((action, index) => (
							<li className={action.skipped ? 'held' : action.success === false ? 'bad' : 'good'} key={index}>
								<span className="action-platform">{action.platform || 'module'}</span>
								<span className="min-w-0 truncate">{action.skipped ? `Held back: ${rejectLabel(action.reject_code)}` : action.title || action.topic || action.symbol || action.error || 'Action recorded'}</span>
								{action.url ? <a href={action.url} target="_blank" rel="noreferrer">open ↗</a> : <span />}
								{typeof action.estimated_usd === 'number' ? <em>{money(action.estimated_usd, 4)}</em> : null}
							</li>
						))}
					</ul>
				</Card>
			) : null}
		</>
	);
}
