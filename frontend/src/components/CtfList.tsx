import { ExternalLink } from 'lucide-react';
import { Pill } from './ui';
import { scoreTone } from '../utils/format';
import type { CtfEvent } from '../types/status';

/** "live now", "starts today", "in 3d" — whichever answers "can I enter this week?". */
export function startsLabel(event: CtfEvent): string {
	if (event.live) return 'live now';
	const days = event.days_until_start ?? 0;
	if (days < 1) return 'starts today';
	return `in ${Math.round(days)}d`;
}

/**
 * Ranked CTF rows. The prize text is the organiser's own claim, so it is shown
 * as written and never summed or valued: this is research, not earnings.
 */
export function CtfList({ events }: { events: CtfEvent[] }) {
	return (
		<ol className="lead-list">
			{events.map((event) => (
				<li key={event.id ?? event.url}>
					<a href={event.url || event.ctftime_url} target="_blank" rel="noreferrer">
						<span className={`score-chip ${scoreTone(event.score)}`}>{event.score || 0}</span>
						<span className="lead-body">
							<strong>{event.title || 'Untitled CTF'}</strong>
							<em>
								{startsLabel(event)}
								{event.format ? ` · ${event.format}` : ''}
								{` · ${event.pays && event.prizes ? event.prizes : 'no prize stated'}`}
							</em>
						</span>
						<span className="chips">
							{event.crypto ? <Pill tone="good">crypto</Pill> : event.pays ? <Pill tone="info">prize</Pill> : null}
							{event.beginner ? <Pill tone="neutral">beginner</Pill> : null}
						</span>
						<ExternalLink className="lead-arrow" size={15} />
					</a>
				</li>
			))}
		</ol>
	);
}
