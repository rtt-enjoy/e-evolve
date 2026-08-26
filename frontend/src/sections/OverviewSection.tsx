import { ArrowUpRight, ExternalLink } from 'lucide-react';
import { useMemo } from 'react';
import { Card, Empty, Phase, Pill, SectionHead, Stat, Tile } from '../components/ui';
import { buildIssues, buildOpportunityStats, buildReadiness, sortLeads } from '../utils/dashboard';
import { ageLabel, cleanTitle, compactMoney, evolutionTone, formatDate, money, scoreTone, sourceLabel } from '../utils/format';
import type { Status } from '../types/status';

export default function OverviewSection({ status }: { status: Status }) {
	const earnings = status.earnings || {};
	const wallet = status.wallet || {};
	// "Earned" means money confirmed on-chain at the receive address — nothing
	// else. Article publishing reports $0 because dev.to and Medium do not pay,
	// so activity counts are shown separately and never summed into revenue.
	const confirmed = wallet.confirmed_usd ?? earnings.confirmed_usd ?? 0;
	const receivedTotal = wallet.received_total_usd ?? earnings.received_total_usd ?? 0;
	const lastReceived = wallet.last_received_usd ?? earnings.last_received_usd ?? 0;
	const opportunities = status.code_tech_earning?.opportunities || [];
	const stats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
	const readiness = useMemo(() => buildReadiness(status), [status]);
	const issues = useMemo(() => buildIssues(status), [status]);
	const topLeads = useMemo(() => sortLeads(opportunities, 'value').slice(0, 4), [opportunities]);
	const evolution = status.last_evolution || {};
	const errors = status.errors || [];
	const actions = status.last_earning?.actions || [];
	const freshness = ageLabel(status.last_run);
	const history = earnings.history || [];

	return (
		<>
			<SectionHead
				title="Overview"
				blurb="The five things worth knowing right now. Everything else lives one click away."
			/>

			<div className="tile-row">
				<Tile
					label="Earned (on-chain)"
					value={money(confirmed)}
					detail={
						!wallet.configured
							? 'no wallet address set'
							: wallet.stale
								? 'chain lookup unavailable · last known'
								: `${money(receivedTotal)} received all-time${
										lastReceived > 0 ? ` · +${money(lastReceived)} this cycle` : ''
									}`
					}
					tone={confirmed > 0 ? 'good' : 'neutral'}
					spark={history}
					to="#/health"
				/>
				<Tile
					label="Pipeline value"
					value={compactMoney(stats.estimatedValue)}
					detail={`${stats.total} leads · top ${compactMoney(stats.topValue)}`}
					tone="info"
					to="#/leads"
				/>
				<Tile
					label="Readiness"
					value={readiness.total ? `${readiness.percent}%` : '—'}
					detail={`${readiness.ready}/${readiness.total} integrations`}
					tone={readiness.percent >= 60 ? 'good' : 'warn'}
					to="#/health"
				/>
				<Tile
					label="Last cycle"
					value={freshness.label}
					detail={`#${status.total_runs || 0} · ${status.last_cycle_seconds || 0}s`}
					tone={freshness.tone}
					to="#/health"
				/>
			</div>

			<div className="split">
				<div className="stack">
					<Card
						title="Top leads by value"
						hint="Highest-value opportunities from the current research queue."
						action={<a className="btn" href="#/leads">all {stats.total} leads <ArrowUpRight size={14} /></a>}
					>
						{topLeads.length ? (
							<ol className="lead-list">
								{topLeads.map((lead) => {
									const index = opportunities.indexOf(lead);
									return (
										<li key={`${lead.url}-${index}`}>
											<a href={`#/leads/${index}`}>
												<span className="lead-value">{compactMoney(lead.estimated_value_usd || 0)}</span>
												<span className="lead-body">
													<strong>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
													<em>{sourceLabel(lead.source)}</em>
												</span>
												<Pill tone={scoreTone(lead.score)}>{lead.score || 0}</Pill>
											</a>
										</li>
									);
								})}
							</ol>
						) : (
							<Empty text="No research leads in the queue yet." />
						)}
					</Card>

					<Card title="Cycle phases" hint="Where the last run spent its five phases.">
						<div className="phase-row">
							<Phase name="Status" ok={Boolean(status.last_run)} detail={formatDate(status.last_run)} />
							<Phase name="Commands" ok detail="queue ready" />
							<Phase name="Evolution" ok={!evolution.error} detail={evolution.error ? 'failed' : 'Codex-owned'} tone={evolutionTone(status)} />
							<Phase name="Research" ok={actions.every((action) => action.success !== false)} detail={`${stats.total} leads`} />
							<Phase name="Update" ok={!errors.length} detail={errors.length ? `${errors.length} errors` : 'saved'} />
						</div>
					</Card>
				</div>

				<div className="stack">
					<Card title="Needs attention" hint="Ranked by urgency; click through to act.">
						<div className="issue-list">
							{issues.map((issue) => {
								const body = (
									<>
										<Pill tone={issue.tone}>{issue.label}</Pill>
										<span className="min-w-0">
											<strong>{issue.title}</strong>
											<p>{issue.detail}</p>
										</span>
										{issue.section ? <ArrowUpRight className="shrink-0" size={15} /> : null}
									</>
								);
								return issue.section ? (
									<a className="issue is-link" href={`#/${issue.section}`} key={issue.title}>{body}</a>
								) : (
									<div className="issue" key={issue.title}>{body}</div>
								);
							})}
						</div>
					</Card>

					<Card title="At a glance">
						<div className="stat-grid">
							<Stat label="Cycles run" value={String(status.total_runs || 0)} detail={`${status.last_cycle_seconds || 0}s last`} />
							<Stat label="Articles today" value={String(status.article_daily?.published || 0)} detail={status.article_daily?.date || 'no date'} />
							<Stat label="Active modules" value={String((status.active_features || []).length)} detail={`${(status.inactive_features || []).length} idle`} />
							<Stat label="LLM roles" value={String(Object.keys(status.llm_workflows || status.llm_roles || {}).length)} detail={status.llm_provider || 'none'} />
						</div>
					</Card>

					<Card title="Where earnings come from" hint="Only confirmed on-chain USDT counts as earned.">
						<div className="stat-grid">
							<Stat
								label="Wallet balance"
								value={money(confirmed)}
								detail={wallet.address_masked
									? `${wallet.network || 'USDT'} · ${wallet.address_masked}`
									: 'no address configured'}
							/>
							<Stat
								label="Received all-time"
								value={money(receivedTotal)}
								detail={wallet.last_received_at
									? `last ${formatDate(wallet.last_received_at)}`
									: 'nothing received yet'}
							/>
							<Stat
								label="Articles published"
								value={String(status.article_daily?.published || 0)}
								detail="reach, not revenue — pays $0"
							/>
							<Stat
								label="Pipeline (unrealised)"
								value={compactMoney(stats.estimatedValue)}
								detail={`${stats.total} leads awaiting payment`}
							/>
						</div>
						<p className="muted mt-4">
							Clients pay this address directly, so funds arrive already at their
							destination — there is no transfer step. Publishing platforms pay
							nothing, so they are counted as activity only.
						</p>
					</Card>

					<Card title="Action policy" hint="What the bot's API keys are permitted to do.">
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
						<a className="btn mt-4" href="earnings-log.md"><ExternalLink size={14} /> earnings log</a>
					</Card>
				</div>
			</div>
		</>
	);
}
