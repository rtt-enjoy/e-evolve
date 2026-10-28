import { ArrowUpRight, Eye, HandCoins, Newspaper, Wallet } from 'lucide-react';
import { useMemo } from 'react';
import { Card, Empty, KeyValue, Phase, Pill, SectionHead, Stat, Tile } from '../components/ui';
import { CopyButton } from '../components/CopyButton';
import { CtfList } from '../components/CtfList';
import { Funnel } from '../components/Funnel';
import { buildFunnel, buildIssues, buildOpportunityStats, buildPhases, sortLeads } from '../utils/dashboard';
import { cleanTitle, formatDate, money, scoreTone, sourceLabel } from '../utils/format';
import type { Status } from '../types/status';

/**
 * Whether today's article is out. The bot counts a day in the publish window's
 * own UTC offset ("06:00-12:00 UTC+9"), so "today" is read the same way here;
 * a window-less snapshot falls back to UTC.
 */
function articleToday(daily: NonNullable<Status['article_daily']>): { published: boolean; window: string } {
	const window = daily.window || '';
	const offset = Number(/UTC([+-]\d+)/.exec(window)?.[1] || 0);
	const local = new Date(Date.now() + offset * 3_600_000).toISOString().slice(0, 10);
	return { published: daily.date === local && (daily.published || 0) > 0, window };
}

export default function OverviewSection({ status }: { status: Status }) {
	const earnings = status.earnings || {};
	const wallet = status.wallet || {};
	// "Earned" means money confirmed on-chain at the receive address -- nothing
	// else. Publishing reports $0 because dev.to pays nothing, so reach is shown
	// as reach and never summed into revenue.
	const confirmed = wallet.confirmed_usd ?? earnings.confirmed_usd ?? 0;
	const receivedTotal = wallet.received_total_usd ?? earnings.received_total_usd ?? 0;
	const lastReceived = wallet.last_received_usd ?? earnings.last_received_usd ?? 0;
	const opportunities = status.code_tech_earning?.opportunities || [];
	const stats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
	const issues = useMemo(() => buildIssues(status), [status]);
	const phases = useMemo(() => buildPhases(status), [status]);
	const funnel = useMemo(() => buildFunnel(status), [status]);
	// Channels -- where money arrives -- ranked by score, which ranks by how
	// passive the income is. `demand` is the pre-rename alias of `channel`.
	const topLeads = useMemo(
		() => sortLeads(
			opportunities.filter((lead) => lead.kind === 'channel' || lead.kind === 'demand' || !lead.kind),
			'score',
		).slice(0, 4),
		[opportunities],
	);
	const article = articleToday(status.article_daily || {});
	const ctfEvents = (status.ctf_bounty?.events || []).slice(0, 4);
	const articleStats = status.article_stats || {};
	// The ask. `payout_public` only exists when the same address is already
	// printed in every published article, so this page exposes nothing the
	// articles do not.
	const payout = status.payout || {};
	const tip = status.payout_public;
	const attribution = status.attribution || {};

	return (
		<>
			<SectionHead
				title="Overview"
				blurb="Is it earning, is it running, and what needs you. Detail lives one click away."
			/>

			<div className="tile-row">
				<Tile
					label="Earned on-chain"
					value={money(confirmed)}
					detail={
						!wallet.configured
							? 'no wallet address set'
							: wallet.stale
								? 'chain lookup unavailable · last known'
								: `${money(receivedTotal)} received all-time${lastReceived > 0 ? ` · +${money(lastReceived)} this cycle` : ''}`
					}
					tone={confirmed > 0 ? 'good' : 'neutral'}
					spark={earnings.history}
					to="#/health"
					icon={<Wallet size={15} />}
				/>
				<Tile
					label="Readers reached"
					value={funnel.views.toLocaleString()}
					detail={`${funnel.posts} posts · ${Math.round(articleStats.avg_views || 0)} avg views`}
					tone="info"
					to="#/reach"
					icon={<Eye size={15} />}
				/>
				<Tile
					label="Shown a way to pay"
					value={funnel.covered ? `${funnel.withAsk}/${funnel.published}` : '—'}
					detail={!funnel.live ? 'receive path is off' : funnel.gap ? `${funnel.gap} posts missing the ask` : funnel.complete ? 'every post, verified' : 'verification in progress'}
					tone={!funnel.live || funnel.gap ? 'bad' : funnel.complete ? 'good' : 'warn'}
					to="#/reach"
					icon={<HandCoins size={15} />}
				/>
				<Tile
					label="Today's article"
					value={article.published ? 'Published' : 'Pending'}
					detail={article.window ? `goes out ${article.window}` : 'one article a day'}
					tone={article.published ? 'good' : 'neutral'}
					to="#/reach"
					icon={<Newspaper size={15} />}
				/>
			</div>

			<Card title="From reader to wallet" hint="Reach only earns where a reader is asked, and only on-chain money counts.">
				<Funnel status={status} />
			</Card>

			<div className="split">
				<div className="stack">
					<Card title="Needs attention" hint="Ranked by urgency. Click through to act.">
						<div className="issue-list">
							{issues.map((issue) => {
								const body = (
									<>
										<Pill tone={issue.tone}>{issue.label}</Pill>
										<span className="min-w-0">
											<strong>{issue.title}</strong>
											<p>{issue.detail}</p>
										</span>
										{issue.section ? <ArrowUpRight className="issue-arrow" size={15} /> : null}
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

					<Card title="Last cycle, phase by phase">
						<div className="phase-row">
							{phases.map((phase) => <Phase key={phase.name} {...phase} />)}
						</div>
					</Card>
				</div>

				<div className="stack">
					<Card
						title="CTF bounties to enter"
						hint="Online, open to anyone. Ranked by stated prize, then how soon."
						action={<a className="btn" href="#/research">all {status.ctf_bounty?.enterable ?? 0} <ArrowUpRight size={14} /></a>}
					>
						{ctfEvents.length ? <CtfList events={ctfEvents} /> : <Empty text="No open CTFs found yet." />}
					</Card>

					{tip?.address ? (
						<Card title={tip.heading || 'Support this work'} hint="The address printed at the end of every published article.">
							{tip.note ? <p className="muted">{tip.note}</p> : null}
							<div className="tip-address mt-4">
								<code>{tip.address}</code>
								<CopyButton text={tip.address} label="copy" />
							</div>
							<div className="chips mt-3">
								<Pill tone="neutral">{tip.asset || 'USDT'} · {tip.network || 'on-chain'}</Pill>
							</div>
						</Card>
					) : (
						<Card title="Receive path" hint="Reach earns nothing without a way for a reader to pay.">
							<p className="muted">No payment path is published right now, so every view is multiplied by zero.</p>
							<div className="mt-4">
								<Pill tone="bad">{payout.blocked_reason || 'receive path not live'}</Pill>
							</div>
						</Card>
					)}

					{(attribution.receipt_count || 0) > 0 ? (
						<Card title="What was live when money arrived" hint="Correlated context, not proof: a transfer carries no memo.">
							<div className="stat-grid">
								<Stat label="Receipts" value={String(attribution.receipt_count || 0)} detail={attribution.last_receipt_at ? `last ${formatDate(attribution.last_receipt_at)}` : 'none yet'} />
								<Stat label="Attributed" value={money(attribution.total_attributed_usd || 0)} detail="on-chain, correlated" />
							</div>
							{(attribution.by_archetype || []).length ? (
								<div className="mt-4">
									<KeyValue
										rows={(attribution.by_archetype || []).slice(0, 4).map((row) => [
											String(row.archetype || 'unknown'),
											`${money(row.usd || 0)} · n=${row.count || 0}`,
										])}
									/>
								</div>
							) : null}
						</Card>
					) : null}

					<Card
						title="Top ways to get paid"
						hint="Ranked by how passive the income is."
						action={<a className="btn" href="#/leads">all {stats.total} <ArrowUpRight size={14} /></a>}
					>
						{topLeads.length ? (
							<ol className="lead-list">
								{topLeads.map((lead) => {
									const index = opportunities.indexOf(lead);
									return (
										<li key={`${lead.url}-${index}`}>
											<a href={`#/leads/${index}`}>
												<span className={`score-chip ${scoreTone(lead.score)}`}>{lead.score || 0}</span>
												<span className="lead-body">
													<strong>{cleanTitle(lead.title) || 'Untitled lead'}</strong>
													<em>{sourceLabel(lead.source)}{lead.cost_usd === 0 ? ' · free' : ''}</em>
												</span>
											</a>
										</li>
									);
								})}
							</ol>
						) : (
							<Empty text="No research leads in the queue yet." />
						)}
					</Card>
				</div>
			</div>
		</>
	);
}
