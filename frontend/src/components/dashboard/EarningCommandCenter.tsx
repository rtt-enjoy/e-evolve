import { AlertTriangle, ArrowUpRight, BarChart3, BriefcaseBusiness, CalendarDays, ClipboardCheck, ExternalLink, ListChecks, Target, TrendingUp } from 'lucide-react';
import { Empty, MiniStat, Pill, Progress } from '../common';
import { clampPercent, featureLabel, formatDate, money, scoreTone, shortText } from '../../utils/format';
import type { Action, CodeTechOpportunity, Status } from '../../types/status';
import type { buildEarningModules, buildOpportunityStats } from '../../utils/dashboard';

export function EarningCommandCenter({
  status,
  breakdown,
  earningModules,
  opportunities,
  opportunityStats,
  weekPercent,
  weekTarget,
}: {
  status: Status;
  breakdown: Array<[string, number]>;
  earningModules: ReturnType<typeof buildEarningModules>;
  opportunities: CodeTechOpportunity[];
  opportunityStats: ReturnType<typeof buildOpportunityStats>;
  weekPercent: number;
  weekTarget: number;
}) {
  const codeTech = status.code_tech_earning || {};
  const actions = status.last_earning?.actions || [];
  const latestOpportunity = opportunities[0];

  return (
    <div className="space-y-5">
      <div className="earning-hero">
        <div>
          <div className="mb-3 flex flex-wrap gap-2">
            <Pill tone={codeTech.enabled ? 'good' : 'warn'} icon={<BriefcaseBusiness size={14} />}>{codeTech.enabled ? 'code tech enabled' : 'code tech idle'}</Pill>
            <Pill tone="info" icon={<CalendarDays size={14} />}>refresh every {codeTech.refresh_hours || 24}h</Pill>
          </div>
          <h3>{opportunityStats.total} research leads</h3>
          <p>{weekPercent}% of the weekly target. Last opportunity refresh {formatDate(codeTech.last_refresh_at)}.</p>
        </div>
        <div className="earning-progress">
          <Progress value={weekPercent} />
          <span>suggestions only; external actions are blocked</span>
        </div>
      </div>

      <div className="earning-stat-grid">
        <MiniStat icon={<Target />} label="Daily target" value={String(Math.round(codeTech.daily_target_usd || 0))} detail="usd target" />
        <MiniStat icon={<ListChecks />} label="Opportunities" value={String(opportunityStats.total)} detail={`${opportunityStats.paidCount} value signals`} />
        <MiniStat icon={<TrendingUp />} label="Value signals" value={String(opportunityStats.paidCount)} />
        <MiniStat icon={<BarChart3 />} label="Top score" value={String(opportunityStats.topScore)} detail="fit score" />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_260px]">
        <div>
          <div className="mb-3 flex items-center justify-between gap-3">
            <h3 className="section-title">Opportunity Pipeline</h3>
            {latestOpportunity?.url ? <a className="inline-link mt-0" href={latestOpportunity.url}>top lead <ArrowUpRight size={13} /></a> : null}
          </div>
          <div className="opportunity-list">
            {opportunities.slice(0, 5).map((opportunity, index) => <OpportunityCard opportunity={opportunity} rank={index + 1} key={`${opportunity.url}-${index}`} />)}
            {!opportunities.length ? <Empty text="No research opportunities are available yet." /> : null}
          </div>
        </div>
        <div>
          <h3 className="section-title mb-3">Research Matrix</h3>
          <div className="earning-module-grid">
            {earningModules.map((module) => (
              <article className="earning-module-card" key={module.name}>
                <div className="flex items-start justify-between gap-3">
                  <strong>{module.name}</strong>
                  <Pill tone={module.tone}>{module.label}</Pill>
                </div>
                <p>{module.detail}</p>
                {module.value ? <span>{module.value}</span> : null}
              </article>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <TemplateList title="Proof Template" icon={<ClipboardCheck />} items={codeTech.requirements || []} />
        <TemplateList title="Focus Areas" icon={<Target />} items={codeTech.focus || []} />
        <TemplateList title="Avoid" icon={<AlertTriangle />} items={codeTech.avoid_patterns || []} />
      </div>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_280px]">
        <TemplateList title="Strategy Playbook" icon={<ListChecks />} items={codeTech.strategy_playbook || []} />
        <div>
          <h3 className="section-title mb-3">Estimated Mix</h3>
          <div className="space-y-3">
            {breakdown.length ? breakdown.map(([name, value]) => (
              <div className="revenue-row" key={name}>
                <div className="flex items-center justify-between gap-3">
                  <strong>{featureLabel(name)}</strong>
                  <span>{value.toFixed(4)} est</span>
                </div>
                <Progress value={clampPercent((value / Math.max(status.earnings?.total_usd || 1, value)) * 100)} />
              </div>
            )) : <Empty text="No suggestion value breakdown yet." />}
          </div>
          <div className="mt-4">
            <h3 className="section-title mb-3">Latest Research Actions</h3>
            <div className="space-y-2">
              {actions.slice(0, 3).map((action, index) => <CompactAction action={action} key={index} />)}
              {!actions.length ? <Empty text="No research actions recorded." /> : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function OpportunityCard({ opportunity, rank }: { opportunity: CodeTechOpportunity; rank: number }) {
  const score = opportunity.score || 0;
  return (
    <article className="opportunity-card">
      <div className="opportunity-rank">{rank}</div>
      <div className="min-w-0">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <strong>{opportunity.title || 'Untitled opportunity'}</strong>
          <Pill tone={scoreTone(score)}>{score} score</Pill>
          <Pill tone="neutral">{opportunity.source || 'source'}</Pill>
        </div>
        <p>{shortText(opportunity.reason || 'No reason recorded.', 130)}</p>
        {opportunity.next_step ? <span>{shortText(opportunity.next_step, 140)}</span> : null}
      </div>
      {opportunity.url ? <a className="icon-button" href={opportunity.url} aria-label="Open opportunity" title="Open opportunity"><ExternalLink size={16} /></a> : null}
    </article>
  );
}

function TemplateList({ title, icon, items }: { title: string; icon: React.ReactNode; items: string[] }) {
  return (
    <article className="template-list">
      <div className="template-title">
        {icon}
        <h3>{title}</h3>
      </div>
      <ul>
        {items.slice(0, 5).map((item) => <li key={item}>{item}</li>)}
      </ul>
      {!items.length ? <Empty text="No template entries recorded." /> : null}
    </article>
  );
}

function CompactAction({ action }: { action: Action }) {
  const amount = typeof action.withdrawn_usd === 'number' ? action.withdrawn_usd : undefined;
  return (
    <article className="compact-action">
      <span className={`status-dot ${action.success === false ? 'bad' : 'good'}`} />
      <strong>{action.platform || 'module'}</strong>
      <p>{shortText(action.title || action.topic || action.symbol || action.error || 'Action recorded', 52)}</p>
      {typeof amount === 'number' ? <em>{money(amount, 4)}</em> : null}
    </article>
  );
}
