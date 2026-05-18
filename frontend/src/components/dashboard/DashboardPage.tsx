import { Activity, ArrowUpRight, Code2, ExternalLink, KeyRound, Send, WalletCards } from 'lucide-react';
import { ActionCard } from './cards';
import { EarningCommandCenter } from './EarningCommandCenter';
import { Empty, Metric, Panel, Phase, Pill, Progress, StatusCell } from '../common';
import { buildEarningModules, buildIssues, buildOpportunityStats, buildReadiness } from '../../utils/dashboard';
import { clampPercent, evolutionTone, featureLabel, formatDate, money } from '../../utils/format';
import { isAvoidedSuggestion } from '../../utils/suggestions';
import type { Status } from '../../types/status';

export function DashboardPage({ status }: { status: Status }) {
  const earnings = status.earnings || {};
  const actions = status.last_earning?.actions || [];
  const active = status.active_features || [];
  const inactive = status.inactive_features || [];
  const errors = status.errors || [];
  const configuredSecrets = status.configured_github_secrets || [];
  const evolution = status.last_evolution || {};
  const workflows = Object.entries(status.llm_workflows || {});
  const dailyTarget = status.code_tech_earning?.daily_target_usd || 10;
  const weekTarget = dailyTarget * 7;
  const weekPercent = clampPercent(((earnings.this_week_usd || 0) / Math.max(1, weekTarget)) * 100);
  const issues = buildIssues(status);
  const breakdown = Object.entries(earnings.breakdown || {}).sort((a, b) => b[1] - a[1]);
  const readiness = buildReadiness(status);
  const earningModules = buildEarningModules(status);
  const opportunities = status.code_tech_earning?.opportunities || [];
  const opportunityStats = buildOpportunityStats(opportunities);
  const visibleSuggestions = (status.suggestions || []).filter((suggestion) => !isAvoidedSuggestion(suggestion));
  const lastWalletSend = [...actions].reverse().find((action) => action.success !== false && typeof action.withdrawn_usd === 'number');

  return (
    <>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <Metric title="Wallet money" value={money(status.usdt_balance, 4)} detail="settled USDT wallet balance" icon={<WalletCards />} />
        <Metric title="Sent to wallet" value={money(lastWalletSend?.withdrawn_usd, 4)} detail={status.last_payout_tx ? `tx ${status.last_payout_tx}` : 'no payout tx recorded'} icon={<Send />} />
        <Metric title="Readiness" value={`${readiness.percent}%`} detail={`${readiness.ready}/${readiness.total} integrations ready`} icon={<KeyRound />} />
        <Metric title="Earning cycle" value={`${weekPercent}%`} detail="estimated cycle values hidden" icon={<Activity />} />
      </section>

      <section className="control-strip mt-4">
        <StatusCell label="Runs" value={String(status.total_runs || 0)} detail={`${status.last_cycle_seconds || 0}s last cycle`} />
        <StatusCell label="Modules" value={`${active.length} active`} detail={`${inactive.length} inactive`} />
        <StatusCell label="LLM Roles" value={String(Object.keys(status.llm_roles || {}).length || workflows.length)} detail={workflows.length ? 'workflow routing enabled' : 'single provider'} />
        <StatusCell label="Article Day" value={String(status.article_daily?.published ?? 0)} detail={status.article_daily?.date || 'no daily record'} />
      </section>

      <div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_400px]">
        <div className="space-y-6">
          <Panel title="Workflow Status" subtitle="Current health across the generated status snapshot.">
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
              <Phase name="Status" ok={Boolean(status.last_run)} detail={formatDate(status.last_run)} />
              <Phase name="Commands" ok detail="command.txt ready" />
              <Phase name="Evolution" ok={!evolution.error} detail={evolution.summary || 'idle'} tone={evolutionTone(status)} />
              <Phase name="Earning" ok={actions.every((action) => action.success !== false)} detail={`${actions.length} actions`} />
              <Phase name="Update" ok={!errors.length} detail={errors.length ? `${errors.length} errors` : 'saved'} />
            </div>
          </Panel>

          <Panel title="Operator Queue" subtitle="Prioritized work to keep the bot productive.">
            <div className="space-y-3">
              {issues.map((issue, index) => (
                <article className="issue-card" key={issue.title}>
                  <div className="issue-rank">{index + 1}</div>
                  <div>
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <strong>{issue.title}</strong>
                      <Pill tone={issue.tone}>{issue.label}</Pill>
                    </div>
                    <p>{issue.detail}</p>
                  </div>
                </article>
              ))}
            </div>
          </Panel>

          <Panel title="Earning Command Center" subtitle="Targets, channels, opportunity pipeline, and repeatable execution templates.">
            <EarningCommandCenter
              status={status}
              breakdown={breakdown}
              earningModules={earningModules}
              opportunities={opportunities}
              opportunityStats={opportunityStats}
              weekPercent={weekPercent}
              weekTarget={weekTarget}
            />
          </Panel>

          <Panel title="LLM Routing" subtitle="Provider roles used by evolution, research, and content generation.">
            <div className="grid gap-3 md:grid-cols-3">
              {workflows.length ? workflows.map(([role, workflow]) => (
                <article className="route-card" key={role}>
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <strong>{featureLabel(role)}</strong>
                    <Pill tone={workflow.active ? 'good' : 'warn'}>{workflow.provider || 'unknown'}</Pill>
                  </div>
                  <p>{workflow.model || 'No model configured'}</p>
                  <span>{workflow.purpose || 'No purpose recorded'}</span>
                </article>
              )) : <Empty text="No workflow routing data yet." />}
            </div>
          </Panel>

          <Panel title="Last Evolution" subtitle="Latest code evolution result and suggestions.">
            <div className="space-y-3">
              <article className="item-row">
                <Code2 className="mt-1 shrink-0 text-accent" size={18} />
                <div>
                  <strong>{evolution.summary || 'No evolution summary yet.'}</strong>
                  {evolution.error ? <p className="text-red">{evolution.error}</p> : null}
                </div>
              </article>
              {(evolution.changes_applied || []).map((change) => (
                <article className="code-card" key={`${change.file}-${change.reason}`}>
                  <code>{change.file}</code>
                  <p>{change.reason || 'Changed by evolution.'}</p>
                </article>
              ))}
              {!(evolution.changes_applied || []).length ? <Empty text="No files changed in the latest evolution." /> : null}
            </div>
          </Panel>

          <Panel title="Last Cycle Actions" subtitle="Earning module actions emitted by the latest cycle.">
            <div className="grid gap-3 md:grid-cols-2">
              {actions.length ? actions.map((action, index) => <ActionCard action={action} key={index} />) : <Empty text="No actions recorded in the latest cycle." />}
            </div>
          </Panel>
        </div>

        <aside className="space-y-6">
          <Panel title="Secret Readiness" subtitle="Names and readiness only, never values.">
            <div className="mb-4">
              <div className="mb-2 flex items-end justify-between gap-4">
                <strong className="text-3xl font-semibold">{readiness.percent}%</strong>
                <span className="text-sm text-soft">{readiness.ready} of {readiness.total} integrations</span>
              </div>
              <Progress value={readiness.percent} />
            </div>
            <div className="mb-4 flex flex-wrap gap-2">
              {configuredSecrets.slice(0, 12).map((secret) => <Pill tone="good" key={secret}>{secret}</Pill>)}
            </div>
            <div className="space-y-3">
              {Object.entries(status.secret_readiness || {}).map(([name, info]) => {
                const required = info.required_count || Math.max(1, (info.present || []).length + (info.missing || []).length);
                const percent = Math.round(((info.present_count || 0) / required) * 100);
                return (
                  <div className="secret-card" key={name}>
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <strong>{featureLabel(name)}</strong>
                      <Pill tone={percent === 100 ? 'good' : 'warn'}>{info.present_count || 0}/{required}</Pill>
                    </div>
                    <Progress value={percent} />
                    {(info.missing || []).length ? <code>{(info.missing || []).join(', ')}</code> : null}
                  </div>
                );
              })}
            </div>
          </Panel>

          <Panel title="Active Modules" subtitle="Detected earning and model features.">
            <div className="module-list">
              {active.map((feature) => <ModuleLine feature={feature} active key={feature} />)}
              {inactive.slice(0, 8).map((feature) => <ModuleLine feature={feature} key={feature} />)}
              {!active.length && !inactive.length ? <Empty text="No module data detected." /> : null}
            </div>
          </Panel>

          <Panel title="Growth Suggestions" subtitle="Bot-proposed setup ideas.">
            <div className="space-y-3">
              {visibleSuggestions.slice(0, 5).map((suggestion) => <SuggestionCard suggestion={suggestion} key={suggestion.title} />)}
              {!visibleSuggestions.length ? <Empty text="No no-ID/free suggestions yet. Check the Suggestions tab for code-tech leads." /> : null}
            </div>
          </Panel>
        </aside>
      </div>
    </>
  );
}

function ModuleLine({ feature, active = false }: { feature: string; active?: boolean }) {
  return (
    <div className="module-line">
      <span className={`status-dot ${active ? 'good' : 'warn'}`} />
      <strong>{featureLabel(feature)}</strong>
      <Pill tone={active ? 'good' : 'neutral'}>{active ? 'active' : 'inactive'}</Pill>
    </div>
  );
}

function SuggestionCard({ suggestion }: { suggestion: NonNullable<Status['suggestions']>[number] }) {
  return (
    <article className="suggestion-card">
      <div className="flex items-start justify-between gap-3">
        <strong>{suggestion.title}</strong>
        <Pill tone={suggestion.free_tier ? 'good' : 'warn'}>{suggestion.free_tier ? 'free' : 'paid'}</Pill>
      </div>
      <p>{suggestion.description}</p>
      {suggestion.secret_needed ? <code>{suggestion.secret_needed}</code> : null}
      {(suggestion.how_to || []).length ? (
        <a className="inline-link" href="setup.md">
          setup notes <ArrowUpRight size={13} />
        </a>
      ) : null}
    </article>
  );
}
