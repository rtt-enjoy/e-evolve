import { ExternalLink, Eye, FileText, HandCoins, ShieldCheck } from 'lucide-react';
import { useMemo } from 'react';
import { Funnel } from '../components/Funnel';
import { BarList, Card, Empty, KeyValue, Pill, SectionHead, Subhead, Tile } from '../components/ui';
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
			.map(([code, count]) => ({ label: rejectLabel(code), value: count })),
		[rejects.counts],
	);
	const skipped = Object.keys(backfill.skipped || {}).length;
	const nextIssue = newsletter.published_at ? new Date(new Date(newsletter.published_at).getTime() + NEWSLETTER_INTERVAL_MS) : null;

	return (
		<>
			<SectionHead
				title="Reach"
				blurb="What was published, who read it, and whether every reader is shown a way to pay. Views are reach, not revenue."
			/>

			<div className="tile-row">
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

			<Card title="From reader to wallet">
				<Funnel status={status} />
			</Card>

			<div className="split">
				<div className="stack">
					<Card
						title="What readers engage with"
						hint={`Average engagement per article shape (a reaction counts as 25 views, a comment as 50). Rows under n=${MIN_ARCHETYPE_SAMPLE} are faint: too few posts to steer on.`}
					>
						<BarList rows={archetypes} />
					</Card>

					<Card
						title="Why drafts were held back"
						hint="Every gate refusal since tracking began. A gate that fires often is where articles are being lost."
					>
						<BarList rows={rejectRows} />
						{rejects.last_at ? (
							<p className="muted mt-4">
								Last: <strong className="text-text">{rejectLabel(rejects.last_reason)}</strong>, {formatDate(rejects.last_at)}.
								{rejects.last_detail ? ` ${rejects.last_detail}.` : ''}
							</p>
						) : null}
					</Card>
				</div>

				<div className="stack">
					<Card title="Best post" hint="Highest views on the account.">
						{stats.best_title ? (
							<>
								<a className="headline-link" href={stats.best_url} target="_blank" rel="noreferrer">
									{stats.best_title} <ExternalLink size={13} aria-hidden="true" />
								</a>
								<p className="muted mt-2">
									{(stats.best_views || 0).toLocaleString()} views
									{stats.total_views ? `, ${Math.round(((stats.best_views || 0) / stats.total_views) * 100)}% of all reach` : ''}
								</p>
								{(stats.winning_tags || []).length ? (
									<div className="chips mt-4">
										{(stats.winning_tags || []).map((tag) => <Pill key={tag}>#{tag}</Pill>)}
									</div>
								) : null}
							</>
						) : (
							<Empty text="No stats read back from dev.to yet." />
						)}
					</Card>

					<Card title="Publishing" hint="One article a day; one digest a week.">
						<KeyValue
							rows={[
								['Last article day', today.date ? `${today.date} · ${today.published || 0} published` : '—'],
								['Latest digest', newsletter.last_url
									? <a href={newsletter.last_url} target="_blank" rel="noreferrer">{newsletter.last_title || 'open'}</a>
									: newsletter.last_title || '—'],
								['Digest published', newsletter.published_at ? `${formatDate(newsletter.published_at)} · ${newsletter.last_item_count || 0} stories` : '—'],
								['Next digest due', nextIssue ? formatDate(nextIssue.toISOString()) : '—'],
								['Sources used', `${(status.article_history?.source_urls || []).length} articles · ${(status.newsletter_history?.source_urls || []).length} digest stories`],
							]}
						/>
					</Card>

					<Card title="Back catalogue" hint="Old posts retrofitted with the ask, then checked by a reader that shares none of the writer's inputs.">
						<KeyValue
							rows={[
								['Retrofitted', `${backfill.updated_total || 0} posts`],
								['Still to do', backfill.remaining === undefined ? '—' : String(backfill.remaining)],
								['Verified by re-reading', `${check.covered || 0} of ${check.published_total || 0}`],
								['Oldest check', typeof check.oldest_check_age_hours === 'number' ? `${Math.round(check.oldest_check_age_hours)}h ago` : '—'],
								['Agrees with self-report', check.agrees_with_backfill === true ? 'yes' : check.agrees_with_backfill === false ? 'no: trust the re-read' : 'not enough coverage yet'],
							]}
						/>
						{skipped ? <p className="muted mt-4">{skipped} retrofit attempts were rate-limited by dev.to and will be retried.</p> : null}
					</Card>
				</div>
			</div>

			<Subhead>Missing the ask</Subhead>
			<Card>
				{(check.missing || []).length ? (
					<ol className="lead-list">
						{(check.missing || []).map((post) => (
							<li key={post.id}>
								<a href={post.url} target="_blank" rel="noreferrer">
									<span className="lead-body">
										<strong>{post.title || `post ${post.id}`}</strong>
										<em>{(post.views || 0).toLocaleString()} views</em>
									</span>
									<ExternalLink className="lead-arrow" size={15} />
								</a>
							</li>
						))}
					</ol>
				) : (
					<Empty text={funnel.complete ? 'None. Every published post was re-read and carries the ask.' : 'None found so far. Coverage is still building.'} />
				)}
			</Card>
		</>
	);
}
