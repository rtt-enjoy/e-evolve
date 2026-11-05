import { useMemo } from 'react';
import { Card, Dot, Empty, KeyValue, Phase, Pill, Progress, SectionHead, Tile } from '../components/ui';
import { buildIssues, buildPhases, buildReadiness } from '../utils/dashboard';
import { ageLabel, featureLabel, formatDate, money } from '../utils/format';
import type { Status } from '../types/status';

export default function HealthSection({ status }: { status: Status }) {
	const readiness = useMemo(() => buildReadiness(status), [status]);
	const issues = useMemo(() => buildIssues(status), [status]);
	const freshness = ageLabel(status.last_run);
	const active = status.active_features || [];
	const inactive = status.inactive_features || [];
	const errors = status.errors || [];
	const secrets = Object.entries(status.secret_readiness || {});
	const phases = useMemo(() => buildPhases(status), [status]);

	return (
		<>
			<SectionHead
				title="Health"
				blurb="Cycle freshness, integration readiness, and anything currently broken."
			/>

			<div className="tile-row compact">
				<Tile label="Cycle freshness" value={freshness.label} detail={`runs hourly · #${status.total_runs || 0}`} tone={freshness.tone} />
				<Tile label="Readiness" value={readiness.total ? `${readiness.percent}%` : '—'} detail={`${readiness.ready}/${readiness.total} integrations`} tone={readiness.percent >= 60 ? 'good' : 'warn'} />
				<Tile label="Active modules" value={String(active.length)} detail={`${inactive.length} inactive`} tone={active.length ? 'good' : 'warn'} />
				<Tile label="Errors" value={String(errors.length)} detail={errors.length ? 'needs attention' : 'clean cycle'} tone={errors.length ? 'bad' : 'good'} />
			</div>

			<Card className="card-compact" title="Phase results" hint="The five phases of the last cycle.">
				<div className="phase-row compact">
					{phases.map((phase) => <Phase key={phase.name} {...phase} />)}
				</div>
			</Card>

			{errors.length ? (
				<Card className="card-compact" title="Cycle errors" hint="Raw error strings from the last run.">
					<div className="stack tight">
						{errors.map((error) => <pre className="code-block error" key={error}>{error}</pre>)}
					</div>
				</Card>
			) : null}

			<Card className="card-compact" title="Attention queue" action={<span className="card-meta">{issues.length} item{issues.length === 1 ? '' : 's'}</span>}>
				<div className="issue-list compact">
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

			<div className="split even">
				<div className="stack tight">
					<Card
						className="card-compact"
						title="Secret readiness"
						hint="Names and counts only. Values are never published."
						action={<span className="card-meta">{readiness.ready}/{readiness.total} ready</span>}
					>
						<Progress value={readiness.percent} />
						{secrets.length ? (
							<ul className="rowlist">
								{secrets.map(([name, info]) => {
									const missing = info.missing || [];
									const required = info.required_count || Math.max(1, (info.present || []).length + missing.length);
									const ready = (info.present_count || 0) >= required;
									return (
										<li key={name}>
											<Dot tone={ready ? 'good' : 'warn'} />
											<strong>{featureLabel(name)}</strong>
											{missing.length ? <code title={`missing: ${missing.join(', ')}`}>{missing.join(', ')}</code> : <span />}
											<Pill tone={ready ? 'good' : 'warn'}>{info.present_count || 0}/{required}</Pill>
										</li>
									);
								})}
							</ul>
						) : (
							<Empty text="No readiness data in this snapshot." />
						)}
					</Card>

					<Card
						className="card-compact"
						title="Modules"
						hint="Features detected from the environment."
						action={<span className="card-meta">{active.length} active · {inactive.length} inactive</span>}
					>
						<div className="module-grid">
							{active.map((feature) => (
								<span className="module-chip" key={feature}><Dot tone="good" />{featureLabel(feature)}</span>
							))}
							{inactive.map((feature) => (
								<span className="module-chip off" key={feature} title="inactive"><Dot />{featureLabel(feature)}</span>
							))}
							{!active.length && !inactive.length ? <Empty text="No module data detected." /> : null}
						</div>
					</Card>

					<Card className="card-compact" title="Action policy" hint="What the bot's API keys may do. Blocked actions are refused in code.">
						<div className="policy">
							<div>
								<span className="policy-label good">allowed</span>
								<div className="chips">
									{(status.external_action_policy?.allowed || []).map((item) => <Pill tone="good" key={item}>{item}</Pill>)}
								</div>
							</div>
							<div>
								<span className="policy-label bad">blocked</span>
								<div className="chips">
									{(status.external_action_policy?.blocked || []).map((item) => <Pill tone="bad" key={item}>{item}</Pill>)}
								</div>
							</div>
						</div>
					</Card>
				</div>

				<div className="stack tight">
					<Card className="card-compact" title="Run facts">
						<KeyValue
							compact
							rows={[
								['Last run', formatDate(status.last_run)],
								['Total cycles', String(status.total_runs || 0)],
								['Duration', `${status.last_cycle_seconds || 0}s`],
								['Week started', status.earnings?.week_started || '—'],
								['Mode', status.operation_mode || '—'],
							]}
						/>
					</Card>

					<Card
						className="card-compact"
						title="Receive wallet"
						hint="The only real source of earnings."
						action={!status.wallet?.configured ? (
							<Pill tone="warn">set USDT_WALLET_ADDRESS</Pill>
						) : status.wallet?.stale ? (
							<Pill tone="warn">last known · lookup failed</Pill>
						) : (
							<Pill tone="good">live from chain</Pill>
						)}
					>
						<KeyValue
							compact
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
						<p className="muted">Funds arrive at this address, so no withdrawal step exists. Outgoing transfers stay disabled by policy.</p>
					</Card>

					<Card className="card-compact" title="Configured secrets" hint="Present in the GitHub Actions environment.">
						<div className="chips mono">
							{(status.configured_github_secrets || []).map((secret) => <Pill tone="good" key={secret}>{secret}</Pill>)}
							{!(status.configured_github_secrets || []).length ? <Empty text="No configured secrets reported." /> : null}
						</div>
					</Card>
				</div>
			</div>
		</>
	);
}
