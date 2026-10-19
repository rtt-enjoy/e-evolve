import { Bot, ExternalLink, FileText, GitBranch } from 'lucide-react';
import type { ReactNode } from 'react';
import { Bullets, Card, Disclosure, Empty, KeyValue, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { atriaState } from '../utils/engine';
import { featureLabel, formatDate, money } from '../utils/format';
import { rejectLabel } from '../utils/dashboard';
import type { Status } from '../types/status';

export default function EngineSection({ status }: { status: Status }) {
	const workflows = Object.entries(status.llm_workflows || {});
	const evolution = status.last_evolution || {};
	const actions = status.last_earning?.actions || [];
	// Proposals park on an evolve/* branch and reach main only when merged.
	const branch = status.last_evolution_branch || evolution.branch || null;
	const pending = Boolean(status.evolution_pending_review && branch);
	const repo = status.github_repo && /^[\w.-]+\/[\w.-]+$/.test(status.github_repo) ? status.github_repo : null;
	const compareUrl = repo && branch && /^[\w./-]+$/.test(branch) ? `https://github.com/${repo}/compare/main...${branch}` : null;
	const evidence = Array.isArray(evolution.evidence) ? evolution.evidence : evolution.evidence ? [evolution.evidence] : [];
	// Atria is the main engine. Its tile reports what the last cycle observed
	// (key set, calls answered, fallback reason), not the routing preference.
	const atria = atriaState(status);
	const calls = Object.entries(atria.calls);
	const totalCalls = calls.reduce((sum, [, n]) => sum + n, 0);

	return (
		<>
			<SectionHead
				title="Engine"
				blurb="Which model handles which role, and what the last cycle actually did."
			/>

			<div className="tile-row">
				<Tile label="Main engine" value={atria.model} detail={atria.detail} tone={atria.tone} icon={<Bot size={15} />} />
				<Tile
					label="Served last cycle"
					value={atria.live === null ? '—' : atria.serving}
					detail={calls.length ? calls.map(([provider, n]) => `${provider} ${n}`).join(' · ') : 'no calls recorded'}
					tone={atria.tone}
				/>
				<Tile label="LLM calls" value={String(totalCalls)} detail="responses returned last cycle" tone="neutral" />
				<Tile
					label="Evolution"
					value={evolution.error ? 'failed' : pending ? 'in review' : 'no proposal'}
					detail={pending ? `v${evolution.proposed_version || '?'} on a review branch` : `running v${status.version || '0.0.0'}`}
					tone={evolution.error ? 'bad' : pending ? 'info' : 'neutral'}
					icon={<GitBranch size={15} />}
				/>
			</div>

			<Subhead>Role routing</Subhead>
			{workflows.length ? (
				<div className="grid-3">
					{workflows.map(([role, workflow]) => (
						<Card key={role} className="route">
							<div className="route-head">
								<span className="route-icon"><Bot size={16} /></span>
								<div className="min-w-0">
									<strong>{featureLabel(role)}</strong>
									<em>{workflow.serving || workflow.provider || 'unknown provider'}</em>
								</div>
								{/* `primary_active` only says Atria was not latched off; when it
								    answered none of the cycle's calls the fallback did the work. */}
								<Pill tone={!workflow.active || workflow.primary_active === false || (workflow.provider === 'atria' && atria.tone === 'warn') ? 'warn' : 'good'}>
									{!workflow.active ? 'idle' : workflow.primary_active === false || (workflow.provider === 'atria' && atria.tone === 'warn') ? 'fallback' : 'active'}
								</Pill>
							</div>
							<code className="route-model">{workflow.model || 'no model configured'}</code>
							{workflow.fallback_model ? (
								<span className="route-secret">fallback → {workflow.fallback_provider}: {workflow.fallback_model}</span>
							) : null}
							<p className="prose">{workflow.purpose || 'No purpose recorded.'}</p>
							{workflow.secret ? <span className="route-secret">{workflow.secret}</span> : null}
						</Card>
					))}
				</div>
			) : (
				<Card><Empty text="No role routing recorded in this snapshot." /></Card>
			)}

			<Subhead>Last cycle</Subhead>
			<div className="split">
				<div className="stack">
					<Card
						title="Latest evolution proposal"
						hint="Proposals land on an evolve/* branch. Nothing reaches main until you merge it."
						action={compareUrl && pending ? <a className="btn" href={compareUrl} target="_blank" rel="noreferrer">review diff <ExternalLink size={13} /></a> : undefined}
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
						{evidence.length ? (
							<div className="mt-4">
								<Bullets items={evidence.map(String)} />
							</div>
						) : null}
						{(evolution.changes_applied || []).length ? (
							<div className="stack mt-4">
								{(evolution.changes_applied || []).map((change) => (
									<div className="change" key={`${change.file}-${change.reason}`}>
										<code>{change.file}</code>
										<p>{change.reason || 'Changed by evolution.'}</p>
									</div>
								))}
							</div>
						) : (
							<p className="muted mt-4">No files changed this cycle.</p>
						)}
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
					<Card title="Atria" hint="The main engine, as the last cycle saw it.">
						<KeyValue
							rows={[
								['Status', <Pill tone={atria.tone}>{atria.label}</Pill>],
								['ATRIA_API_KEY', atria.keySet === null ? 'not reported' : atria.keySet ? 'set' : 'not set'],
								['Model', atria.model],
								['Calls answered', calls.length ? calls.map(([provider, n]) => `${provider}: ${n}`).join(', ') : 'none recorded'],
								['Fallback reason', atria.reason || '—'],
							]}
						/>
					</Card>

					<Card title="Cycle facts">
						<KeyValue
							rows={[
								['Version', status.version || '—'],
								['Cycle', `#${status.total_runs || 0}`],
								['Duration', `${status.last_cycle_seconds || 0}s`],
								['Last run', formatDate(status.last_run)],
								['Mode', status.operation_mode || '—'],
								['Provider', status.llm_provider || '—'],
							]}
						/>
					</Card>

					{(evolution.suggestions || []).length ? (
						<Disclosure title="Evolution suggestions" hint="Repair ideas from the last cycle" count={evolution.suggestions?.length}>
							<div className="stack">
								{(evolution.suggestions || []).map((suggestion) => (
									<article className="suggestion" key={suggestion.title}>
										<div className="suggestion-head">
											<strong>{suggestion.title}</strong>
											<Pill tone={suggestion.free_tier ? 'good' : 'warn'}>{suggestion.free_tier ? 'free' : 'paid'}</Pill>
										</div>
										<p className="prose">{suggestion.description}</p>
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
