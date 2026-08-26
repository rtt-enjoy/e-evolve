import { useMemo } from 'react';
import { Card, Dot, Empty, KeyValue, Phase, Pill, Progress, SectionHead, Subhead, Tile } from '../components/ui';
import { buildIssues, buildReadiness } from '../utils/dashboard';
import { ageLabel, evolutionTone, featureLabel, formatDate, money } from '../utils/format';
import type { Status } from '../types/status';

export default function HealthSection({ status }: { status: Status }) {
	const readiness = useMemo(() => buildReadiness(status), [status]);
	const issues = useMemo(() => buildIssues(status), [status]);
	const freshness = ageLabel(status.last_run);
	const active = status.active_features || [];
	const inactive = status.inactive_features || [];
	const errors = status.errors || [];
	const secrets = Object.entries(status.secret_readiness || {});
	const evolution = status.last_evolution || {};
	const actions = status.last_earning?.actions || [];

	return (
		<>
			<SectionHead
				title="Health"
				blurb="Cycle freshness, integration readiness, and anything currently broken."
			/>

			<div className="tile-row">
				<Tile label="Cycle freshness" value={freshness.label} detail={`runs hourly · #${status.total_runs || 0}`} tone={freshness.tone} />
				<Tile label="Readiness" value={readiness.total ? `${readiness.percent}%` : '—'} detail={`${readiness.ready}/${readiness.total} integrations`} tone={readiness.percent >= 60 ? 'good' : 'warn'} />
				<Tile label="Active modules" value={String(active.length)} detail={`${inactive.length} inactive`} tone={active.length ? 'good' : 'warn'} />
				<Tile label="Errors" value={String(errors.length)} detail={errors.length ? 'needs attention' : 'clean cycle'} tone={errors.length ? 'bad' : 'good'} />
			</div>

			<Card title="Phase results" hint="The five phases of the last cycle.">
				<div className="phase-row">
					<Phase name="Status" ok={Boolean(status.last_run)} detail={formatDate(status.last_run)} />
					<Phase name="Commands" ok detail="queue ready" />
					<Phase name="Evolution" ok={!evolution.error} detail={evolution.error ? 'failed' : 'skipped by design'} tone={evolutionTone(status)} />
					<Phase name="Research" ok={actions.every((action) => action.success !== false)} detail={`${actions.length} actions`} />
					<Phase name="Update" ok={!errors.length} detail={errors.length ? `${errors.length} errors` : 'saved'} />
				</div>
			</Card>

			{errors.length ? (
				<Card title="Cycle errors" hint="Raw error strings from the last run.">
					<div className="stack">
						{errors.map((error) => <pre className="code-block error" key={error}>{error}</pre>)}
					</div>
				</Card>
			) : null}

			<Subhead>Attention queue</Subhead>
			<Card>
				<div className="issue-list">
					{issues.map((issue) => (
						<div className="issue" key={issue.title}>
							<Pill tone={issue.tone}>{issue.label}</Pill>
							<span className="min-w-0">
								<strong>{issue.title}</strong>
								<p>{issue.detail}</p>
							</span>
						</div>
					))}
				</div>
			</Card>

			<Subhead>Integrations</Subhead>
			<div className="split">
				<div className="stack">
					<Card title="Secret readiness" hint="Names and counts only — values are never published.">
						<div className="mb-5">
							<div className="readiness-head">
								<strong>{readiness.total ? `${readiness.percent}%` : '—'}</strong>
								<span>{readiness.ready} of {readiness.total} integrations ready</span>
							</div>
							<Progress value={readiness.percent} />
						</div>
						{secrets.length ? (
							<div className="stack">
								{secrets.map(([name, info]) => {
									const required = info.required_count || Math.max(1, (info.present || []).length + (info.missing || []).length);
									const percent = Math.round(((info.present_count || 0) / required) * 100);
									return (
										<div className="secret" key={name}>
											<div className="secret-head">
												<strong>{featureLabel(name)}</strong>
												<Pill tone={percent === 100 ? 'good' : 'warn'}>{info.present_count || 0}/{required}</Pill>
											</div>
											<Progress value={percent} />
											{(info.missing || []).length ? <code className="missing">missing: {(info.missing || []).join(', ')}</code> : null}
										</div>
									);
								})}
							</div>
						) : (
							<Empty text="No readiness data in this snapshot." />
						)}
					</Card>
				</div>

				<div className="stack">
					<Card title="Modules" hint="Features detected from the environment.">
						<div className="module-list">
							{active.map((feature) => (
								<div className="module" key={feature}>
									<Dot tone="good" />
									<strong>{featureLabel(feature)}</strong>
									<Pill tone="good">active</Pill>
								</div>
							))}
							{inactive.map((feature) => (
								<div className="module" key={feature}>
									<Dot tone="warn" />
									<strong>{featureLabel(feature)}</strong>
									<Pill tone="neutral">inactive</Pill>
								</div>
							))}
							{!active.length && !inactive.length ? <Empty text="No module data detected." /> : null}
						</div>
					</Card>

					<Card title="Configured secrets" hint="Present in the GitHub Actions environment.">
						<div className="chips">
							{(status.configured_github_secrets || []).map((secret) => <Pill tone="good" key={secret}>{secret}</Pill>)}
							{!(status.configured_github_secrets || []).length ? <Empty text="No configured secrets reported." /> : null}
						</div>
					</Card>

					<Card title="Run facts">
						<KeyValue
							rows={[
								['Last run', formatDate(status.last_run)],
								['Total cycles', String(status.total_runs || 0)],
								['Duration', `${status.last_cycle_seconds || 0}s`],
								['Week started', status.earnings?.week_started || '—'],
								['Mode', status.operation_mode || '—'],
							]}
						/>
					</Card>

					<Card title="Receive wallet" hint="The only real source of earnings. Clients pay this address directly.">
						<KeyValue
							rows={[
								['Address', status.wallet?.address_masked || 'not configured'],
								['Network', status.wallet?.network || '—'],
								['Confirmed balance', money(status.wallet?.confirmed_usd ?? status.usdt_balance ?? 0)],
								['Received all-time', money(status.wallet?.received_total_usd || 0)],
								['Last received', status.wallet?.last_received_at
									? `${money(status.wallet?.last_received_usd || 0)} · ${formatDate(status.wallet.last_received_at)}`
									: 'nothing yet'],
								['Checked', formatDate(status.wallet?.checked_at || undefined)],
							]}
						/>
						{!status.wallet?.configured ? (
							<Pill tone="warn">set USDT_WALLET_ADDRESS</Pill>
						) : status.wallet?.stale ? (
							<Pill tone="warn">chain lookup failed — showing last known</Pill>
						) : (
							<Pill tone="good">reading live from chain</Pill>
						)}
						<p className="muted mt-4">
							Funds arrive already at this address, so no withdrawal step exists.
							Outgoing transfers stay disabled by policy.
						</p>
					</Card>
				</div>
			</div>
		</>
	);
}
