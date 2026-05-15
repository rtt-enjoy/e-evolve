import { featureLabel } from './format';
import type { Status, Suggestion } from '../types/status';

export type AutomationSuggestion = Suggestion & {
  id: string;
  requiredSecrets: string[];
  missingSecrets: string[];
  readinessPercent: number;
  ready: boolean;
  command: string;
  automationPlan: string[];
};

export function buildAutomationSuggestions(status: Status): AutomationSuggestion[] {
  const source = [...(status.suggestions || [])];
  const existingSecrets = new Set(source.flatMap((suggestion) => parseSecrets(suggestion.secret_needed)));

  for (const [feature, info] of Object.entries(status.secret_readiness || {})) {
    const missing = info.missing || [];
    if (!missing.length || missing.every((secret) => existingSecrets.has(secret))) continue;
    source.push({
      title: `Activate ${featureLabel(feature)}`,
      description: `Let the AI workflow use ${featureLabel(feature).toLowerCase()} automatically once the missing setup is complete.`,
      secret_needed: missing.join(', '),
      estimated_weekly_usd: 0,
      free_tier: true,
      how_to: missing.map((secret) => `Add ${secret} as a GitHub Actions secret`),
    });
  }

  return source.slice(0, 12).map((suggestion, index) => {
    const requiredSecrets = parseSecrets(suggestion.secret_needed);
    const missingSecrets = requiredSecrets.filter((secret) => !hasConfiguredSecret(status, secret));
    const readinessPercent = requiredSecrets.length
      ? Math.round(((requiredSecrets.length - missingSecrets.length) / requiredSecrets.length) * 100)
      : 100;
    const title = suggestion.title || `Suggestion ${index + 1}`;
    return {
      ...suggestion,
      title,
      id: `${title}-${index}`,
      requiredSecrets,
      missingSecrets,
      readinessPercent,
      ready: readinessPercent === 100,
      command: `improve suggestion ${title}`,
      automationPlan: buildAutomationPlan(suggestion),
    };
  });
}

export function buildSuggestionStats(suggestions: AutomationSuggestion[]) {
  return {
    total: suggestions.length,
    readyCount: suggestions.filter((suggestion) => suggestion.ready).length,
    missingSecrets: uniqueMissingSecrets(suggestions).length,
    weeklyUsd: suggestions.reduce((sum, suggestion) => sum + (suggestion.estimated_weekly_usd || 0), 0),
  };
}

export function uniqueMissingSecrets(suggestions: AutomationSuggestion[]) {
  return Array.from(new Set(suggestions.flatMap((suggestion) => suggestion.missingSecrets))).sort();
}

export function buildIssueUrl(repo: string, suggestion: AutomationSuggestion) {
  const title = suggestion.command;
  const body = [
    suggestion.command,
    '',
    `Suggestion: ${suggestion.title}`,
    `Expected result: ${suggestion.description || 'Improve this earning suggestion through the AI workflow.'}`,
    suggestion.requiredSecrets.length ? `Required secrets: ${suggestion.requiredSecrets.join(', ')}` : 'Required secrets: none',
  ].join('\n');
  return `https://github.com/${repo}/issues/new?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}&labels=bot-command`;
}

export function inferRepoFromLocation() {
  const host = window.location.hostname;
  const path = window.location.pathname.split('/').filter(Boolean)[0];
  if (!host.endsWith('.github.io') || !path) return '';
  return `${host.replace('.github.io', '')}/${path}`;
}

function buildAutomationPlan(suggestion: Suggestion) {
  const title = (suggestion.title || '').toLowerCase();
  if (title.includes('twitter') || title.includes('x')) {
    return ['Generate earning-focused thread ideas', 'Post through the configured Twitter module', 'Record the action and estimated value'];
  }
  if (title.includes('medium') || title.includes('article')) {
    return ['Repurpose article output for the new channel', 'Publish with the configured integration', 'Track duplicated reach without extra LLM spend'];
  }
  if (title.includes('llm') || title.includes('anthropic') || title.includes('groq') || title.includes('gemini')) {
    return ['Route the right task to the best model', 'Use fallback capacity when a free tier is limited', 'Keep evolution running with fewer skipped cycles'];
  }
  if (title.includes('crypto') || title.includes('binance')) {
    return ['Read configured balances and strategy limits', 'Run bounded trade analysis automatically', 'Log every action for dashboard review'];
  }
  return ['Turn the suggestion into a bounded code change', 'Run verification in the GitHub workflow', 'Commit the completed improvement automatically'];
}

function parseSecrets(value?: string | null) {
  if (!value) return [];
  return value
    .split(/[,/+\s]+/)
    .map((part) => part.trim())
    .filter((part) => /^[A-Z0-9_]{4,}$/.test(part));
}

function hasConfiguredSecret(status: Status, secret: string) {
  if ((status.configured_github_secrets || []).includes(secret)) return true;
  return Object.values(status.secret_readiness || {}).some((info) => (info.present || []).includes(secret));
}
