import { featureLabel, money, shortText } from './format';
import type { CodeTechOpportunity, Status, Suggestion } from '../types/status';

export type AutomationSuggestion = Suggestion & {
  id: string;
  source: 'suggestion' | 'evolution' | 'code_tech';
  sourceLabel: string;
  requiredSecrets: string[];
  missingSecrets: string[];
  readinessPercent: number;
  ready: boolean;
  command: string;
  automationPlan: string[];
  nextAction: string;
  blockerText: string;
  priorityScore: number;
  opportunityUrl?: string;
  noIdPath: boolean;
};

const COMPLETED_CODE_TECH_LEADS = new Set([
  'renovate dashboard 🤖',
  'create custom page for "submit your business"',
]);

const AVOIDED_SECRET_PREFIXES = ['ANTHROPIC', 'BINANCE', 'TWITTER', 'ETH_', 'NFT_'];

const AVOIDED_FEATURES = new Set([
  'llm_anthropic',
  'twitter',
  'crypto_binance',
  'crypto_payout',
  'nft_ethereum',
]);

export function buildAutomationSuggestions(status: Status): AutomationSuggestion[] {
  const source: Array<{ suggestion: Suggestion; source: AutomationSuggestion['source'] }> = [
    ...(status.suggestions || []).map((suggestion) => ({ suggestion, source: 'suggestion' as const })),
    ...((status.last_evolution?.suggestions || []) as Suggestion[]).map((suggestion) => ({ suggestion, source: 'evolution' as const })),
  ];
  const existingSecrets = new Set(source.flatMap((entry) => parseSecrets(entry.suggestion.secret_needed)));

  for (const [feature, info] of Object.entries(status.secret_readiness || {})) {
    if (AVOIDED_FEATURES.has(feature)) continue;
    const missing = info.missing || [];
    if (!missing.length || missing.every((secret) => existingSecrets.has(secret))) continue;
    source.push({
      source: 'suggestion',
      suggestion: {
        title: `Activate ${featureLabel(feature)}`,
        description: `Let the AI workflow use ${featureLabel(feature).toLowerCase()} automatically once the missing setup is complete.`,
        secret_needed: missing.join(', '),
        estimated_weekly_usd: 0,
        free_tier: true,
        how_to: missing.map((secret) => `Add ${secret} as a GitHub Actions secret`),
      },
    });
  }

  for (const opportunity of (status.code_tech_earning?.opportunities || []).filter((lead) => !isCompletedCodeTechLead(lead)).slice(0, 5)) {
    source.push({
      source: 'code_tech',
      suggestion: codeTechSuggestion(opportunity, status.code_tech_earning?.daily_target_usd || 10),
    });
  }

  return dedupeSuggestions(source.filter((entry) => !isAvoidedSuggestion(entry.suggestion))).map(({ suggestion, source: suggestionSource }, index) => {
    const requiredSecrets = parseSecrets(suggestion.secret_needed);
    const missingSecrets = requiredSecrets.filter((secret) => !hasConfiguredSecret(status, secret));
    const readinessPercent = requiredSecrets.length
      ? Math.round(((requiredSecrets.length - missingSecrets.length) / requiredSecrets.length) * 100)
      : 100;
    const title = suggestion.title || `Suggestion ${index + 1}`;
    const sourceLabel = sourceLabelFor(suggestionSource);
    const priorityScore = priorityFor(suggestion, readinessPercent, suggestionSource);
    return {
      ...suggestion,
      title,
      id: `${suggestionSource}-${title}-${index}`,
      source: suggestionSource,
      sourceLabel,
      requiredSecrets,
      missingSecrets,
      readinessPercent,
      ready: readinessPercent === 100,
      command: `improve suggestion ${title}`,
      automationPlan: buildAutomationPlan(suggestion),
      nextAction: buildNextAction(suggestion, missingSecrets),
      blockerText: missingSecrets.length ? `${missingSecrets.length} missing credential${missingSecrets.length === 1 ? '' : 's'}` : 'ready for next evolution cycle',
      priorityScore,
      opportunityUrl: suggestionSource === 'code_tech' ? suggestion.how_to?.find((step) => step.startsWith('Open '))?.replace(/^Open /, '') : undefined,
      noIdPath: isNoIdSuggestion(suggestion),
    };
  }).sort((a, b) => b.priorityScore - a.priorityScore).slice(0, 12);
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

export function readyCommands(suggestions: AutomationSuggestion[], limit = 3) {
  return suggestions
    .filter((suggestion) => suggestion.ready)
    .slice(0, limit)
    .map((suggestion) => suggestion.command);
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

function isCompletedCodeTechLead(opportunity: CodeTechOpportunity) {
  return COMPLETED_CODE_TECH_LEADS.has((opportunity.title || '').trim().toLowerCase());
}

function buildAutomationPlan(suggestion: Suggestion) {
  const title = (suggestion.title || '').toLowerCase();
  if (title.includes('code-tech') || title.includes('code tech')) {
    return ['Reproduce the lead from public proof', 'Prepare the smallest credible patch or offer', 'Turn the result into tracked earning pipeline work'];
  }
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

function buildNextAction(suggestion: Suggestion, missingSecrets: string[]) {
  if (missingSecrets.length) {
    return `Add ${missingSecrets[0]}${missingSecrets.length > 1 ? ` and ${missingSecrets.length - 1} more` : ''}`;
  }
  const next = (suggestion.how_to || []).find((step) => !step.toLowerCase().startsWith('open '));
  return next || 'Launch the improve suggestion command';
}

function codeTechSuggestion(opportunity: CodeTechOpportunity, dailyTarget: number): Suggestion {
  const title = opportunity.title || 'Untitled code-tech lead';
  const value = opportunity.estimated_value_usd || dailyTarget;
  const specialized = specializeCodeTechLead(opportunity);
  return {
    title: `Code-tech lead: ${title}`,
    description: specialized?.description || [
      shortText(opportunity.reason || 'No-secret maintenance lead from the active code-tech queue.', 130),
      opportunity.next_step ? `Next: ${shortText(opportunity.next_step, 120)}` : '',
    ].filter(Boolean).join(' '),
    secret_needed: '',
    estimated_weekly_usd: Math.max(0, value),
    free_tier: true,
    how_to: specialized?.howTo || [
      opportunity.url ? `Open ${opportunity.url}` : '',
      opportunity.next_step || 'Reproduce the issue and prepare one focused patch.',
      `Use value signal ${money(opportunity.estimated_value_usd || 0, 0)} and score ${opportunity.score || 0}/100 to decide effort.`,
    ].filter(Boolean),
  };
}

function specializeCodeTechLead(opportunity: CodeTechOpportunity) {
  const title = (opportunity.title || '').toLowerCase();
  const isAnnouncementMaintenanceLead = title.includes('notification')
    && title.includes('announcements')
    && title.includes('maintenance mode');
  if (!isAnnouncementMaintenanceLead) return null;

  return {
    description: [
      'Bounty lead for two scoped admin features: a markdown site announcement with expiry/RBAC and env-driven deployment maintenance mode.',
      'Deliverable needs docs plus short demo evidence.',
    ].join(' '),
    howTo: [
      opportunity.url ? `Open ${opportunity.url}` : '',
      'Verify the bounty is still open, then map existing admin settings, RBAC, env, and deployment docs before coding.',
      'Implement one active announcement with markdown links, expiration handling, read permission defaults, and top-of-site placement.',
      'Add maintenance-mode env handling with a user-facing message, document the env var, and capture a short demo for the PR.',
    ].filter(Boolean),
  };
}

function dedupeSuggestions(entries: Array<{ suggestion: Suggestion; source: AutomationSuggestion['source'] }>) {
  const seen = new Set<string>();
  const out: Array<{ suggestion: Suggestion; source: AutomationSuggestion['source'] }> = [];
  for (const entry of entries) {
    const key = `${(entry.suggestion.title || '').toLowerCase()}:${entry.suggestion.secret_needed || ''}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(entry);
  }
  return out;
}

function priorityFor(suggestion: Suggestion, readinessPercent: number, source: AutomationSuggestion['source']) {
  const value = suggestion.estimated_weekly_usd || 0;
  const sourceBoost = source === 'code_tech' ? 40 : source === 'evolution' ? 15 : 0;
  const noIdBoost = isNoIdSuggestion(suggestion) ? 25 : 0;
  return sourceBoost + noIdBoost + readinessPercent + Math.min(40, value);
}

function sourceLabelFor(source: AutomationSuggestion['source']) {
  if (source === 'code_tech') return 'ready lead';
  if (source === 'evolution') return 'last evolution';
  return 'bot suggestion';
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

export function isAvoidedSuggestion(suggestion: Suggestion) {
  const title = (suggestion.title || '').toLowerCase();
  const description = (suggestion.description || '').toLowerCase();
  const secrets = parseSecrets(suggestion.secret_needed);
  if (suggestion.free_tier === false) return true;
  if (secrets.some((secret) => AVOIDED_SECRET_PREFIXES.some((prefix) => secret.startsWith(prefix)))) return true;
  return [title, description].some((text) => (
    text.includes('binance')
    || text.includes('anthropic')
    || text.includes('claude')
    || text.includes('twitter')
    || text.includes('crypto')
    || text.includes('nft')
    || text.includes('ethereum')
    || text.includes('premium')
    || text.includes('phone verification')
    || text.includes('identity verification')
    || text.includes('kyc')
  ));
}

function isNoIdSuggestion(suggestion: Suggestion) {
  return suggestion.free_tier !== false && !isAvoidedSuggestion(suggestion);
}
