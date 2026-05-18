import { Ban, Check, CheckCircle2, Copy, KeyRound, PlayCircle, ShieldCheck, Sparkles, TrendingUp, WandSparkles } from 'lucide-react';
import type { ReactNode } from 'react';
import { useMemo, useState } from 'react';
import { AutomationSuggestionCard } from './AutomationSuggestionCard';
import { Empty, MiniStat, Panel, Pill } from '../common';
import { inferRepoFromLocation, readyCommands, uniqueMissingSecrets, type AutomationSuggestion, type buildSuggestionStats } from '../../utils/suggestions';
import type { Status } from '../../types/status';

const completedLeads = [
  {
    title: 'Renovate Dashboard',
    url: 'https://github.com/dettanym/prose/issues/8',
    result: 'Triaged the live Renovate dashboard and removed it from the active suggestion queue.',
    proof: [
      'Config migration PR is available from the dashboard checkbox.',
      'Repository problem is an update failure; pin-dependencies is the errored branch.',
      '@tsconfig/node20 has a replacement path to @tsconfig/node22.',
      'Lookup failures affect kubernetes-dashboard, app-template, and ghcr.io/onedr0p/jellyfin Helm paths.',
    ],
  },
  {
    title: 'Submit your business',
    url: 'https://github.com/bitcoin-dot-org/Bitcoin.org/issues/1583',
    result: 'Built the Bitcoin business submission page and removed that lead from active suggestions.',
    proof: [
      'Directory choices are available for physical venues, online stores, and Lightning-friendly businesses.',
      'Submission checklist and suggested listing copy are available from the dashboard.',
    ],
  },
];

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
  const ready = suggestions.filter((suggestion) => suggestion.ready);
  const blocked = suggestions.filter((suggestion) => !suggestion.ready);
  const commandBatch = useMemo(() => readyCommands(suggestions).join('\n'), [suggestions]);
  const [copiedBatch, setCopiedBatch] = useState(false);

  async function copyBatch() {
    if (!commandBatch) return;
    try {
      await navigator.clipboard.writeText(commandBatch);
      setCopiedBatch(true);
      window.setTimeout(() => setCopiedBatch(false), 1600);
    } catch {
      setCopiedBatch(false);
    }
  }

  return (
    <div className="suggestion-page">
      <section className="suggestion-hero">
        <div>
          <div className="mb-4 flex flex-wrap gap-2">
            <Pill tone="info" icon={<WandSparkles size={14} />}>ai workflow ready</Pill>
            <Pill tone={stats.readyCount ? 'good' : 'warn'} icon={<KeyRound size={14} />}>{stats.readyCount}/{stats.total} ready</Pill>
            <Pill tone="good" icon={<ShieldCheck size={14} />}>no id first</Pill>
            <Pill tone="info" icon={<TrendingUp size={14} />}>{stats.total} tracked ideas</Pill>
          </div>
          <h2>Suggestions To Earn More</h2>
          <p>
            Each card avoids exchange identity checks, phone-gated social APIs, paid LLM subscriptions, and funded wallets.
            Complete the lightweight setup, then launch the improvement request for the next evolution cycle.
          </p>
        </div>
        <div className="suggestion-hero-panel">
          <span>Best next move</span>
          <strong>{top?.title || 'No suggestion selected'}</strong>
          <p>{top?.nextAction || 'Run an evolution cycle to refresh the queue.'}</p>
        </div>
      </section>

      <section className="suggestion-stat-grid">
        <MiniStat icon={<Sparkles />} label="Suggestions" value={String(stats.total)} detail="ranked by bot output" />
        <MiniStat icon={<CheckCircle2 />} label="Ready now" value={String(stats.readyCount)} detail="setup complete" />
        <MiniStat icon={<KeyRound />} label="Setup gaps" value={String(stats.missingSecrets)} detail="named secrets" />
        <MiniStat icon={<TrendingUp />} label="Upside ideas" value={String(stats.total)} detail="estimated values hidden" />
      </section>

      <div className="suggestion-layout">
        <div className="space-y-4">
          {ready.length ? (
            <section className="launchpad">
              <div>
                <span>Ready automation</span>
                <strong>{ready.length} item{ready.length === 1 ? '' : 's'} can run without new secrets</strong>
                <p>Queue these commands through a bot-command issue or command.txt for the next evolution cycle.</p>
              </div>
              <div className="command-stack">
                <code>{commandBatch || 'No ready commands'}</code>
                <button className="icon-button" type="button" onClick={copyBatch} aria-label="Copy ready commands" title="Copy ready commands">
                  {copiedBatch ? <Check size={16} /> : <Copy size={16} />}
                </button>
              </div>
            </section>
          ) : null}

          {ready.map((suggestion, index) => (
            <AutomationSuggestionCard
              key={suggestion.id}
              rank={index + 1}
              repo={repo}
              suggestion={suggestion}
            />
          ))}
          {blocked.length ? <h3 className="section-title pt-2">Waiting On Setup</h3> : null}
          {blocked.map((suggestion, index) => (
            <AutomationSuggestionCard
              key={suggestion.id}
              rank={ready.length + index + 1}
              repo={repo}
              suggestion={suggestion}
            />
          ))}
          {!suggestions.length ? <Empty text="No earning suggestions are available yet. Run an evolution cycle to generate new ideas." /> : null}
        </div>

        <aside className="suggestion-side">
          <Panel title="No-ID Free Path" subtitle="Best fit when Binance, Claude premium, phone checks, and paid services are off the table.">
            <div className="path-list">
              <WorkflowStep icon={<ShieldCheck />} title="Use first" text="Code-tech leads, dev.to articles, GitHub Pages, and Groq/Gemini/OpenRouter free LLM capacity." />
              <WorkflowStep icon={<KeyRound />} title="Add only light secrets" text="Start with GROQ_API_KEY or GEMINI_API_KEY, then DEV_TO_API_KEY when you want publishing." />
              <WorkflowStep icon={<Ban />} title="Avoid for now" text="Binance trading, Claude/Anthropic paid access, Twitter/X API posting, Ethereum NFTs, and withdrawal flows." />
            </div>
          </Panel>

          <Panel title="Completed Code-Tech Leads" subtitle="Finished leads stay visible here without crowding the active queue.">
            <div className="completed-lead-list">
              {completedLeads.map((lead) => (
                <article className="completed-lead-card" key={lead.title}>
                  <div>
                    <Pill tone="good" icon={<CheckCircle2 size={14} />}>done</Pill>
                    <strong>{lead.title}</strong>
                    <p>{lead.result}</p>
                  </div>
                  <ul>
                    {lead.proof.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                  <a className="inline-link" href={lead.url}>view source issue</a>
                </article>
              ))}
            </div>
          </Panel>

          <Panel title="How It Runs" subtitle="The page prepares the request; GitHub Actions performs the work.">
            <div className="automation-steps">
              <WorkflowStep icon={<KeyRound />} title="Complete prerequisites" text="Add required credentials as GitHub Actions secrets." />
              <WorkflowStep icon={<Sparkles />} title="Improve suggestion" text="Open the prefilled bot-command issue or add the command to command.txt." />
              <WorkflowStep icon={<PlayCircle />} title="Workflow executes" text="The hourly cycle passes the request to the evolution agent and commits safe changes." />
              <WorkflowStep icon={<Check />} title="Suggestion is done" text="The next dashboard refresh shows changed files, updated suggestions, and readiness." />
            </div>
          </Panel>

          <Panel title="Required Setup" subtitle="Secret names are shown so setup is actionable; values are never stored here.">
            <div className="setup-list">
              {missingSecrets.map((secret) => <code key={secret}>{secret}</code>)}
              {!missingSecrets.length ? <Empty text="No missing credentials for the listed suggestions." /> : null}
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
