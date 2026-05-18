import { Check, Copy, ExternalLink, PlayCircle, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { Pill, Progress } from '../common';
import { buildIssueUrl, type AutomationSuggestion } from '../../utils/suggestions';

export function AutomationSuggestionCard({
  suggestion,
  rank,
  repo,
}: {
  suggestion: AutomationSuggestion;
  rank: number;
  repo?: string;
}) {
  const [copied, setCopied] = useState(false);
  const issueUrl = repo ? buildIssueUrl(repo, suggestion) : '';

  async function copyCommand() {
    try {
      await navigator.clipboard.writeText(suggestion.command);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  }

  return (
    <article className={`automation-card ${suggestion.ready ? 'ready' : 'blocked'}`}>
      <div className="automation-rank">{rank}</div>
      <div className="min-w-0">
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <strong>{suggestion.title || 'Untitled suggestion'}</strong>
          <Pill tone={suggestion.source === 'code_tech' ? 'good' : 'neutral'}>{suggestion.sourceLabel}</Pill>
          <Pill tone={suggestion.ready ? 'good' : 'warn'}>{suggestion.ready ? 'ready' : 'setup needed'}</Pill>
          <Pill tone={suggestion.free_tier ? 'good' : 'neutral'}>{suggestion.free_tier ? 'free tier' : 'paid'}</Pill>
          {suggestion.noIdPath ? <Pill tone="good" icon={<ShieldCheck size={14} />}>no id path</Pill> : null}
        </div>
        <p>{suggestion.description || 'No description recorded.'}</p>

        <div className="automation-grid">
          <div>
            <h3 className="section-title">AI Will Do</h3>
            <ul className="check-list">
              {suggestion.automationPlan.map((item) => <li key={item}>{item}</li>)}
            </ul>
          </div>
          <div>
            <h3 className="section-title">Required To Complete</h3>
            <div className="secret-chip-list">
              {suggestion.requiredSecrets.map((secret) => (
                <code className={suggestion.missingSecrets.includes(secret) ? 'missing' : 'ready'} key={secret}>{secret}</code>
              ))}
              {!suggestion.requiredSecrets.length ? <span>No extra secrets required</span> : null}
            </div>
            <Progress value={suggestion.readinessPercent} label={`${suggestion.readinessPercent}% prerequisites ready`} />
            <p className="mt-3 text-cyan">{suggestion.blockerText}</p>
          </div>
        </div>

        {(suggestion.how_to || []).length ? (
          <div className="howto-box">
            {(suggestion.how_to || []).slice(0, 4).map((step) => <p key={step}>{step}</p>)}
          </div>
        ) : null}

        <div className="command-box">
          <code>{suggestion.command}</code>
          <button className="icon-button" type="button" onClick={copyCommand} aria-label="Copy command" title="Copy command">
            {copied ? <Check size={16} /> : <Copy size={16} />}
          </button>
        </div>
      </div>
      <div className="automation-actions">
        {suggestion.opportunityUrl ? (
          <a className="icon-button" href={suggestion.opportunityUrl} aria-label="Open opportunity" title="Open opportunity">
            <ExternalLink size={16} />
          </a>
        ) : null}
        {issueUrl ? (
          <a className="small-button" href={issueUrl}>
            <PlayCircle size={15} /> improve
          </a>
        ) : (
          <a className="small-button" href="setup.md">
            <ExternalLink size={15} /> setup
          </a>
        )}
      </div>
    </article>
  );
}
