import { ExternalLink, Eye, FileText, HandCoins, ShieldCheck } from 'lucide-react';
import { useMemo } from 'react';
import { BarList, Card, Empty, Fold, KeyValue, Pill, SectionHead, Tile } from '../components/ui';
import { buildFunnel, rejectLabel } from '../utils/dashboard';
import { formatDate } from '../utils/format';
import type { Status } from '../types/status';

/**
 * Mirrors devto_stats._MIN_ARCHETYPE_SAMPLE: below this many posts a row's mean
 * is not steered on by the bot, so it is drawn faint here rather than read as
 * a finding.
 */
const MIN_ARCHETYPE_SAMPLE = 3;
const NEWSLETTER_INTERVAL_MS = 168 * 3_600_000;
/** The gates that cost the most drafts are the finding; a long tail is not. */
const MAX_REJECT_ROWS = 5;

export default function ReachSection({ status }: { status: Status }) {
	const stats = status.article_stats || {};
	const interest = status.article_interest || {};
	const rejects = status.article_rejects || {};
	const newsletter = status.newsletter_daily || {};
	const backfill = status.backfill || {};
	const check = status.receipt_check || {};
	const funnel = useMemo(() => buildFunnel(status), [status]);
	const today = status.article_daily || {};

	const archetypes = useMemo(
		() => [...(interest.archetypes || [])]
			.sort((a, b) => (b.avg_engagement || 0) - (a.avg_engagement || 0))
			.map((row) => ({
				label: row.archetype || 'unknown',
				value: Math.round(row.avg_engagement || 0),
				note: `n=${row.count || 0}`,
				muted: (row.count || 0) < MIN_ARCHETYPE_SAMPLE,
				title: `${row.archetype}: ${Math.round(row.avg_engagement || 0)} avg engagement over ${row.count || 0} posts. Best: ${row.best_title || '—'}`,
			})),
		[interest.archetypes],
	);
	const rejectRows = useMemo(
		() => Object.entries(rejects.counts || {})
			.sort((a, b) => b[1] - a[1])
			.slice(0, MAX_REJECT_ROWS)
			.map(([code, count]) => ({ label: rejectLabel(code), value: count })),
		[rejects.counts],
	);
	const missing = check.missing || [];
	const skipped = Object.keys(backfill.skipped || {}).length;
	const nextIssue = newsletter.published_at ? new Date(new Date(newsletter.published_at).getTime() + NEWSLETTER_INTERVAL_MS) : null;
	const share = stats.total_views ? Math.round(((stats.best_views || 0) / stats.total_views) * 100) : 0;

	return (
		<>
			<SectionHead
				title="Reach"
				blurb="What was published, who read it, and whether every reader is shown a way to pay. Views are reach, not revenue."
			/>

			<div className="tile-row compact">
				<Tile label="Posts live" value={String(stats.count || 0)} detail={`${newsletter.published || 0} newsletter issues among them`} tone="info" icon={<FileText size={15} />} />
				<Tile label="Lifetime views" value={(stats.total_views || 0).toLocaleString()} detail={`${Math.round(stats.avg_views || 0)} per post on average`} tone="info" icon={<Eye size={15} />} />
				<Tile
					label="Carry the ask"
					value={funnel.covered ? `${funnel.withAsk}/${funnel.published}` : '—'}
					detail={funnel.complete ? 'verified by re-reading each post' : `${check.unverified || 0} not yet re-read`}
					tone={funnel.gap ? 'bad' : funnel.complete ? 'good' : 'warn'}
					icon={<HandCoins size={15} />}
				/>
				<Tile
					label="Drafts held back"
					value={String(rejects.total || 0)}
					detail={rejects.last_reason ? `last: ${rejectLabel(rejects.last_reason)}` : 'no gate has fired'}
					tone="neutral"
					icon={<ShieldCheck size={15} />}
				/>
			</div>

			<div className="split even">
				<div className="stack tight">
					<Card
						className="card-compact"
						title="What readers engage with"
						hint={`Mean engagement per article shape. Faint rows have under ${MIN_ARCHETYPE_SAMPLE} posts: too few to steer on.`}
					>
						<BarList rows={archetypes} />
					</Card>

					{rejectRows.length ? (
						<Card
							className="card-compact"
							title="Why drafts were held back"
							hint="Gate refusals since tracking began. The busiest gate is where articles are lost."
						>
							<BarList rows={rejectRows} />
							{rejects.last_at ? (
								<p className="muted">
									Last: <strong className="text-text">{rejectLabel(rejects.last_reason)}</strong>, {formatDate(rejects.last_at)}.
									{rejects.last_detail ? ` ${rejects.last_detail}.` : ''}
								</p>
							) : null}
						</Card>
					) : null}
				</div>

				<div className="stack tight">
					<Card className="card-compact" title="Best post">
						{stats.best_title ? (
							<>
								<a className="headline-link" href={stats.best_url} target="_blank" rel="noreferrer">
									{stats.best_title} <ExternalLink size={13} aria-hidden="true" />
								</a>
								<p className="muted">
									{(stats.best_views || 0).toLocaleString()} views{share ? `, ${share}% of all reach` : ''}
								</p>
								{(stats.winning_tags || []).length ? (
									<div className="chips mono">
										{(stats.winning_tags || []).map((tag) => <Pill key={tag}>#{tag}</Pill>)}
									</div>
								) : null}
							</>
						) : (
							<Empty text="No stats read back from dev.to yet." />
						)}
					</Card>

					<Card className="card-compact" title="Publishing" hint="One article a day, one digest a week.">
						<KeyValue
							compact
							rows={[
								["Today's article", today.date ? `${today.date} · ${today.published || 0} published` : '—'],
								['Latest digest', newsletter.last_url
									? <a href={newsletter.last_url} target="_blank" rel="noreferrer">{newsletter.last_title || 'open'}</a>
									: newsletter.last_title || '—'],
								['Next digest due', nextIssue ? formatDate(nextIssue.toISOString()) : '—'],
							]}
						/>
					</Card>

					<Card
						className="card-compact"
						title="Does every reader see the ask?"
						hint="Old posts are retrofitted, then re-read by a checker that shares none of the writer's inputs."
					>
						<KeyValue
							compact
							rows={[
								['Re-read', `${check.covered || 0} of ${check.published_total || 0} posts`],
								['Retrofitted', `${backfill.updated_total || 0} done · ${backfill.remaining === undefined ? '—' : backfill.remaining} to do`],
								['Oldest check', typeof check.oldest_check_age_hours === 'number' ? `${Math.round(check.oldest_check_age_hours)}h ago` : '—'],
								['Agrees with self-report', check.agrees_with_backfill === true ? 'yes' : check.agrees_with_backfill === false ? 'no: trust the re-read' : 'not enough coverage yet'],
							]}
						/>
						{missing.length ? (
							<Fold title="Posts without the ask" meta={<Pill tone="bad">{missing.length}</Pill>} defaultOpen>
								<ul className="actions-list">
									{missing.map((post) => (
										<li className="bad" key={post.id}>
											<span className="action-platform">no ask</span>
											<span className="min-w-0 truncate">{post.title || `post ${post.id}`}</span>
											{post.url ? <a href={post.url} target="_blank" rel="noreferrer">open ↗</a> : <span />}
											<em>{(post.views || 0).toLocaleString()} views</em>
										</li>
									))}
								</ul>
							</Fold>
						) : null}
						{skipped && backfill.remaining ? <p className="muted">{skipped} retrofit attempts were rate-limited by dev.to and will be retried.</p> : null}
					</Card>
				</div>
			</div>
		</>
	);
}
