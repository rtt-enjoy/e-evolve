import { ageLabel, money } from './format';
import type { Action, CodeTechOpportunity, Status } from '../types/status';

export type Issue = {
  tone: 'good' | 'warn' | 'bad' | 'info';
  label: string;
  title: string;
  detail: string;
};

export function buildIssues(status: Status): Issue[] {
  const issues: Issue[] = [];
  const fresh = ageLabel(status.last_run);
  if (fresh.tone !== 'good') {
    issues.push({ tone: fresh.tone, label: fresh.tone === 'bad' ? 'urgent' : 'watch', title: 'Workflow freshness needs attention', detail: `Latest run is ${fresh.label}. Check GitHub Actions if this is unexpected.` });
  }
  if (status.last_evolution?.error) {
    issues.push({ tone: 'bad', label: 'repair', title: 'Evolution failed', detail: status.last_evolution.error });
  }
  for (const error of status.errors || []) {
    issues.push({ tone: 'bad', label: 'error', title: 'Cycle error', detail: error });
  }
  const failed = (status.last_earning?.actions || []).filter((action) => action.success === false);
  for (const action of failed.slice(0, 3)) {
    issues.push({ tone: 'warn', label: 'module', title: `${action.platform || 'module'} action failed`, detail: action.error || action.title || 'Inspect module output.' });
  }
  const readiness = buildReadiness(status);
  if (readiness.percent < 60) {
    issues.push({ tone: 'warn', label: 'setup', title: 'Integration readiness is low', detail: `${readiness.ready} of ${readiness.total} integrations are fully configured.` });
  }
  if (!issues.length) {
    issues.push({ tone: 'good', label: 'clear', title: 'No urgent corrections', detail: 'Workflow freshness, evolution, and latest actions look healthy.' });
  }
  return issues.slice(0, 6);
}

export function buildReadiness(status: Status) {
  const entries = Object.values(status.secret_readiness || {});
  if (!entries.length) {
    return { ready: 0, total: 0, percent: 0 };
  }
  const ready = entries.filter((info) => {
    const required = info.required_count || Math.max(1, info.present_count || 0);
    return (info.present_count || 0) >= required;
  }).length;
  return { ready, total: entries.length, percent: Math.round((ready / entries.length) * 100) };
}

export function buildEarningModules(status: Status) {
  const readiness = status.secret_readiness || {};
  const actions = status.last_earning?.actions || [];
  const modules = [
    {
      key: 'code_techs',
      name: 'Code Techs',
      active: Boolean(status.code_tech_earning?.enabled),
      detail: `${status.code_tech_earning?.opportunities?.length || 0} opportunities tracked`,
      value: `${money(status.code_tech_earning?.daily_target_usd, 0)} daily target`,
    },
    {
      key: 'articles_devto',
      name: 'Dev.to Articles',
      active: Boolean(readiness.articles_devto?.active || status.active_features?.includes('articles_devto')),
      detail: `${status.article_daily?.published ?? 0} published on ${status.article_daily?.date || 'latest day'}`,
      value: moduleActionValue(actions, 'dev.to'),
    },
    {
      key: 'articles_medium',
      name: 'Medium',
      active: Boolean(readiness.articles_medium?.active || status.active_features?.includes('articles_medium')),
      detail: readinessLabel(readiness.articles_medium),
      value: moduleActionValue(actions, 'medium'),
    },
    {
      key: 'twitter',
      name: 'Twitter/X',
      active: Boolean(readiness.twitter?.active || status.active_features?.includes('twitter')),
      detail: readinessLabel(readiness.twitter),
      value: moduleActionValue(actions, 'twitter'),
    },
    {
      key: 'crypto_binance',
      name: 'Binance Trading',
      active: Boolean(readiness.crypto_binance?.active || status.active_features?.includes('crypto_binance')),
      detail: readinessLabel(readiness.crypto_binance),
      value: money(status.usdt_balance, 4),
    },
    {
      key: 'nft_ethereum',
      name: 'NFT Minting',
      active: Boolean(readiness.nft_ethereum?.active || status.active_features?.includes('nft_ethereum')),
      detail: readinessLabel(readiness.nft_ethereum),
      value: moduleActionValue(actions, 'nft'),
    },
  ];

  return modules.map((module) => ({
    ...module,
    label: module.active ? 'ready' : 'setup',
    tone: module.active ? 'good' as const : 'warn' as const,
  }));
}

export function buildOpportunityStats(opportunities: CodeTechOpportunity[]) {
  return {
    total: opportunities.length,
    paidCount: opportunities.filter((opportunity) => (opportunity.estimated_value_usd || 0) > 0).length,
    estimatedValue: opportunities.reduce((sum, opportunity) => sum + (opportunity.estimated_value_usd || 0), 0),
    topScore: opportunities.reduce((top, opportunity) => Math.max(top, opportunity.score || 0), 0),
  };
}

export function buildHealth(status: Status, issues: Array<{ tone: string }>, readinessPercent: number): { tone: 'good' | 'warn' | 'bad' | 'info'; label: string } {
  if (issues.some((issue) => issue.tone === 'bad')) return { tone: 'bad', label: 'attention required' };
  if (ageLabel(status.last_run).tone !== 'good') return { tone: 'warn', label: 'stale cycle' };
  if (readinessPercent < 60) return { tone: 'warn', label: 'setup incomplete' };
  if ((status.last_earning?.actions || []).some((action) => action.success === false)) return { tone: 'warn', label: 'module warning' };
  return { tone: 'good', label: 'operational' };
}

function readinessLabel(info?: { active?: boolean; present_count?: number; required_count?: number }) {
  const required = info?.required_count || 0;
  const present = info?.present_count || 0;
  if (!required) return 'No setup data';
  if (present >= required) return 'All required credentials present';
  return `${Math.max(0, required - present)} credentials missing`;
}

function moduleActionValue(actions: Action[], platform: string) {
  const count = actions.filter((action) => (action.platform || '').toLowerCase().includes(platform.toLowerCase())).length;
  return count ? `${count} latest actions` : '';
}
