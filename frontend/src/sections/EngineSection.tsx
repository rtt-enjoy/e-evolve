import { Bot, FileText } from 'lucide-react';
import { Card, Disclosure, Empty, KeyValue, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { evolutionTone, featureLabel, formatDate, money } from '../utils/format';
import type { Status } from '../types/status';

export default function EngineSection({ status }: { status: Status }) {
	const workflows = Object.entries(status.llm_workflows || {});
	const evolution = status.last_evolution || {};
	const actions = status.last_earning?.actions || [];
	const tone = evolutionTone(status);
	const models = new Set(workflows.map(([, workflow]) => workflow.model).filter(Boolean));

	return (
		<>
			<SectionHead
				title="Engine"
				blurb="Which model handles which role, and what the last cycle actually did."
			/>

			<div className="tile-row">
				<Tile label="Provider" value={status.llm_provider || 'none'} detail={`${workflows.length} roles routed`} tone="info" />
				<Tile label="Distinct models" value={String(models.size)} detail="across all roles" tone="neutral" />
				<Tile label="Articles today" value={String(status.article_daily?.published || 0)} detail={status.article_daily?.date || 'no date'} tone={status.article_daily?.published ? 'good' : 'neutral'} />
				<Tile label="Evolution" value={evolution.error ? 'failed' : 'Codex-owned'} detail={`v${evolution.version_bumped_to || status.version || '0.0.0'}`} tone={tone === 'info' ? 'neutral' : tone} />
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
									<em>{workflow.provider || 'unknown provider'}</em>
								</div>
								<Pill tone={workflow.active ? 'good' : 'warn'}>{workflow.active ? 'active' : 'idle'}</Pill>
							</div>
							<code className="route-model">{workflow.model || 'no model configured'}</code>
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
					<Card title="Evolution result" hint="Automatic code changes are disabled; Codex owns implementation.">
						<p className="prose lead-in">{evolution.summary || 'No evolution summary recorded.'}</p>
						{evolution.error ? <p className="error-text">{evolution.error}</p> : null}
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
									<div className={`action ${action.success === false ? 'bad' : 'good'}`} key={index}>
										<span className="action-platform">
											<FileText size={15} />
											{action.platform || 'module'}
										</span>
										<p>{action.title || action.topic || action.symbol || action.error || 'Action recorded'}</p>
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
