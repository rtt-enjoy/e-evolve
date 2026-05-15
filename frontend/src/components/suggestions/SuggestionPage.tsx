import { Check, CheckCircle2, CircleDollarSign, KeyRound, PlayCircle, Sparkles, TrendingUp, WandSparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import { AutomationSuggestionCard } from './AutomationSuggestionCard';
import { Empty, MiniStat, Panel, Pill } from '../common';
import { inferRepoFromLocation, uniqueMissingSecrets, type AutomationSuggestion, type buildSuggestionStats } from '../../utils/suggestions';
import { money } from '../../utils/format';
import type { Status } from '../../types/status';

export function SuggestionPage({
  status,
  suggestions,
  stats,
}: {
  status: Status;
  suggestions: AutomationSuggestion[];
  stats: ReturnType<typeof buildSuggestionStats>;
}) {
  const top = suggestions[0];
  const repo = status.github_repo || inferRepoFromLocation();
  const missingSecrets = uniqueMissingSecrets(suggestions);

  return (
    <div className="suggestion-page">
      <section className="suggestion-hero">
        <div>
          <div className="mb-4 flex flex-wrap gap-2">
            <Pill tone="info" icon={<WandSparkles size={14} />}>ai workflow ready</Pill>
            <Pill tone={stats.readyCount ? 'good' : 'warn'} icon={<KeyRound size={14} />}>{stats.readyCount}/{stats.total} ready</Pill>
            <Pill tone="good" icon={<CircleDollarSign size={14} />}>{money(stats.weeklyUsd, 0)} weekly upside</Pill>
          </div>
          <h2>Suggestions To Earn More</h2>
          <p>
            Each card is an earning improvement the AI agent can refine and implement through the existing GitHub workflow.
            Add the required keys, then launch the improvement request for the next evolution cycle.
          </p>
        </div>
        <div className="suggestion-hero-panel">
          <span>Best next move</span>
          <strong>{top?.title || 'No suggestion selected'}</strong>
          <p>{top?.ready ? 'Ready for AI implementation.' : 'Waiting on setup before automation can finish.'}</p>
        </div>
      </section>

      <section className="suggestion-stat-grid">
        <MiniStat icon={<Sparkles />} label="Suggestions" value={String(stats.total)} detail="ranked by bot output" />
        <MiniStat icon={<CheckCircle2 />} label="Ready now" value={String(stats.readyCount)} detail="all secrets present" />
        <MiniStat icon={<KeyRound />} label="Missing keys" value={String(stats.missingSecrets)} detail="shown per card" />
        <MiniStat icon={<TrendingUp />} label="Weekly upside" value={money(stats.weeklyUsd, 0)} detail="estimated by bot" />
      </section>

      <div className="suggestion-layout">
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <AutomationSuggestionCard
              key={suggestion.id}
              rank={index + 1}
              repo={repo}
              suggestion={suggestion}
            />
          ))}
          {!suggestions.length ? <Empty text="No earning suggestions are available yet. Run an evolution cycle to generate new ideas." /> : null}
        </div>

        <aside className="suggestion-side">
          <Panel title="How It Runs" subtitle="The page prepares the request; GitHub Actions performs the work.">
            <div className="automation-steps">
              <WorkflowStep icon={<KeyRound />} title="Complete prerequisites" text="Add the listed API keys or tokens as GitHub Actions secrets." />
              <WorkflowStep icon={<Sparkles />} title="Improve suggestion" text="Open the prefilled bot-command issue or add the command to command.txt." />
              <WorkflowStep icon={<PlayCircle />} title="Workflow executes" text="The hourly cycle passes the request to the evolution agent and commits safe changes." />
              <WorkflowStep icon={<Check />} title="Suggestion is done" text="The next dashboard refresh shows changed files, updated suggestions, and readiness." />
            </div>
          </Panel>

          <Panel title="Required Setup" subtitle="Secrets still needed across the current suggestion list.">
            <div className="setup-list">
              {missingSecrets.map((secret) => <code key={secret}>{secret}</code>)}
              {!missingSecrets.length ? <Empty text="No missing secrets for the listed suggestions." /> : null}
            </div>
          </Panel>
        </aside>
      </div>
    </div>
  );
}

function WorkflowStep({ icon, title, text }: { icon: ReactNode; title: string; text: string }) {
  return (
    <article className="workflow-step">
      <div>{icon}</div>
      <strong>{title}</strong>
      <p>{text}</p>
    </article>
  );
}
