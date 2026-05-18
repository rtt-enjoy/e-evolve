import { ageLabel } from './format';
import type { CodeTechOpportunity, Status } from '../types/status';

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
  const modules = [
    {
      key: 'code_techs',
      name: 'Code-Tech Research',
      active: Boolean(status.code_tech_earning?.enabled),
      detail: `${status.code_tech_earning?.opportunities?.length || 0} ranked suggestions tracked`,
      value: `${Math.round(status.code_tech_earning?.daily_target_usd || 0)} usd daily target`,
    },
    {
      key: 'research_policy',
      name: 'Action API Guard',
      active: status.operation_mode === 'research_suggestions_only',
      detail: 'Keys are limited to RAG, research, market analysis, suggestions, and drafts',
      value: 'no publish/post/trade/mint/payout',
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
