import { useMemo } from 'react';
import { SubmitBusinessPage } from './SubmitBusinessPage';
import { SuggestionPage } from './suggestions/SuggestionPage';
import { buildAutomationSuggestions, buildSuggestionStats } from '../utils/suggestions';
import type { Status } from '../types/status';

export function OfflineAgentView({
  status,
  view,
}: {
  status: Status;
  view: 'suggestions' | 'submit-business';
}) {
  const suggestions = useMemo(() => buildAutomationSuggestions(status), [status]);
  const suggestionStats = useMemo(() => buildSuggestionStats(suggestions), [suggestions]);

  if (view === 'submit-business') return <SubmitBusinessPage />;

  return <SuggestionPage status={status} suggestions={suggestions} stats={suggestionStats} />;
}
