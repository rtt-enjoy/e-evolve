import { Check, Copy, ExternalLink, PlayCircle } from 'lucide-react';
import { useState } from 'react';
import { Pill, Progress } from '../common';
import { buildIssueUrl, type AutomationSuggestion } from '../../utils/suggestions';
import { money } from '../../utils/format';

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
          <Pill tone={suggestion.ready ? 'good' : 'warn'}>{suggestion.ready ? 'ready' : 'setup needed'}</Pill>
          <Pill tone={suggestion.free_tier ? 'good' : 'neutral'}>{suggestion.free_tier ? 'free tier' : 'paid'}</Pill>
          <Pill tone="info">{money(suggestion.estimated_weekly_usd, 0)} / week</Pill>
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
              {!suggestion.requiredSecrets.length ? <span>Credential names redacted</span> : null}
            </div>
            <Progress value={suggestion.readinessPercent} label={`${suggestion.readinessPercent}% prerequisites ready`} />
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
