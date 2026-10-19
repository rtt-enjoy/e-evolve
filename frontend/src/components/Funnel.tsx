import { ChevronRight, Eye, Wallet, HandCoins } from 'lucide-react';
import { buildFunnel } from '../utils/dashboard';
import { money } from '../utils/format';
import type { Status } from '../types/status';

/**
 * The whole earning path in one row: readers reached, readers shown a way to
 * pay, money that actually arrived.
 *
 * Doctrine Principle 5 -- measure the funnel, not the last stage. A lone
 * `$0.00` cannot say whether nobody tipped or nobody was asked, and those need
 * opposite fixes, so the verdict line under the stages says which it is.
 */
export function Funnel({ status }: { status: Status }) {
	const funnel = buildFunnel(status);
	const askValue = funnel.covered ? `${funnel.withAsk} / ${funnel.published}` : '—';
	const askDetail = !funnel.live
		? 'no ask is being published'
		: funnel.complete
			? 'posts verified by re-reading them'
			: `${funnel.covered} of ${funnel.published} re-read so far`;

	return (
		<div className="funnel">
			<ol className="funnel-steps">
				<li>
					<span className="funnel-label"><Eye size={15} aria-hidden="true" /> Readers reached</span>
					<strong key={funnel.views}>{funnel.views.toLocaleString()}</strong>
					<em>views across {funnel.posts} posts</em>
				</li>
				<ChevronRight className="funnel-arrow" size={18} aria-hidden="true" />
				<li>
					<span className="funnel-label"><HandCoins size={15} aria-hidden="true" /> Shown a way to pay</span>
					<strong key={askValue}>{askValue}</strong>
					<em>{askDetail}</em>
				</li>
				<ChevronRight className="funnel-arrow" size={18} aria-hidden="true" />
				<li>
					<span className="funnel-label"><Wallet size={15} aria-hidden="true" /> Received on-chain</span>
					<strong key={funnel.received}>{money(funnel.received)}</strong>
					<em>the only figure counted as earned</em>
				</li>
			</ol>
			<p className={`funnel-verdict ${funnel.verdict.tone}`}>{funnel.verdict.text}</p>
		</div>
	);
}
