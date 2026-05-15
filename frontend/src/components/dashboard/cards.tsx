import { Pill } from '../common';
import { money } from '../../utils/format';
import type { Action } from '../../types/status';

export function ActionCard({ action }: { action: Action }) {
  const amount = typeof action.estimated_usd === 'number' ? action.estimated_usd : action.value_usd;
  return (
    <article className="action-card">
      <div className="mb-3 flex items-center justify-between gap-3">
        <strong>{action.platform || 'unknown'}</strong>
        <Pill tone={action.success === false ? 'bad' : 'good'}>{action.success === false ? 'failed' : 'success'}</Pill>
      </div>
      <p>{action.title || action.topic || action.symbol || action.error || 'Action recorded'}</p>
      {typeof amount === 'number' ? <span>{money(amount, 4)}</span> : null}
    </article>
  );
}
