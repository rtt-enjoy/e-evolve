import { Activity, AlertTriangle, ArrowUpRight, Bot, CheckCircle2, CircleDollarSign, Clock3, Code2, ExternalLink, GitBranch, KeyRound, RefreshCw, ShieldCheck, TerminalSquare, WalletCards, XCircle } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { fetchStatus } from './api';
import { ageLabel, evolutionTone, featureLabel, formatDate, money } from './lib';
import type { Action, Status, Suggestion } from './types';

const emptyStatus: Status = {
  active_features: [],
  inactive_features: [],
  earnings: {},
  last_evolution: {},
  last_earning: { actions: [] },
  suggestions: [],
  errors: [],
};

export function App() {
  const [status, setStatus] = useState<Status>(emptyStatus);
  const [lastPoll, setLastPoll] = useState<Date | null>(null);
  const [loadError, setLoadError] = useState('');

  async function load() {
    try {
      const next = await fetchStatus();
      setStatus(next);
      setLastPoll(new Date());
      setLoadError('');
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : String(error));
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 60_000);
    return () => window.clearInterval(timer);
  }, []);

  const freshness = ageLabel(status.last_run);
  const earnings = status.earnings || {};
  const actions = status.last_earning?.actions || [];
  const active = status.active_features || [];
  const inactive = status.inactive_features || [];
  const errors = status.errors || [];
  const configuredSecrets = status.configured_github_secrets || [];
  const evolution = status.last_evolution || {};
  const workflows = Object.entries(status.llm_workflows || {});
  const weekPercent = Math.min(100, Math.round(((earnings.this_week_usd || 0) / 10) * 100));

  const issues = useMemo(() => buildIssues(status), [status]);
  const breakdown = Object.entries(earnings.breakdown || {}).sort((a, b) => b[1] - a[1]);
  const readiness = useMemo(() => buildReadiness(status), [status]);
  const health = useMemo(() => buildHealth(status, issues, readiness.percent), [status, issues, readiness.percent]);

  return (
    <div className="min-h-screen bg-ink text-text">
      <header className="border-b border-line bg-ink/95">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              <Pill tone={freshness.tone} icon={<Clock3 size={15} />}>{freshness.label}</Pill>
              <Pill tone={health.tone} icon={<ShieldCheck size={15} />}>{health.label}</Pill>
              <Pill tone="info" icon={<Bot size={15} />}>{status.llm_provider || 'unknown model'}</Pill>
              <Pill tone="neutral" icon={<GitBranch size={15} />}>v{status.version || '0.0.0'}</Pill>
            </div>
            <h1 className="text-3xl font-semibold tracking-normal md:text-5xl">E-Evolve Dashboard</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-soft">
              Live operations console for the hourly evolution cycle, earning modules, payout readiness, and owner action queue.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button className="icon-button" onClick={load} aria-label="Refresh status" title="Refresh status">
              <RefreshCw size={18} />
            </button>
            <a className="small-button" href="status.json"><ExternalLink size={15} />status.json</a>
            <a className="small-button" href="earnings-log.md"><TerminalSquare size={15} />earnings log</a>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-5 py-6">
        {loadError ? <Banner tone="bad" text={`Dashboard data load failed: ${loadError}`} /> : null}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric title="Total earnings" value={money(earnings.total_usd, 4)} detail={`${money(earnings.last_cycle_usd, 4)} last cycle`} icon={<CircleDollarSign />} />
          <Metric title="This week" value={money(earnings.this_week_usd, 4)} detail={`${weekPercent}% of $10 target`} icon={<Activity />} />
          <Metric title="Readiness" value={`${readiness.percent}%`} detail={`${readiness.ready}/${readiness.total} integrations ready`} icon={<KeyRound />} />
          <Metric title="Wallet" value={money(status.usdt_balance, 4)} detail={`${money(status.last_payout_total_usd, 4)} last payout`} icon={<WalletCards />} />
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

            <Panel title="Earnings Analysis" subtitle="Weekly progress and platform breakdown.">
              <Progress value={weekPercent} label={`${weekPercent}% weekly target`} />
              <div className="mt-5 space-y-3">
                {breakdown.length ? breakdown.map(([name, value]) => (
                  <div className="grid gap-3 sm:grid-cols-[140px_1fr_92px] sm:items-center" key={name}>
                    <strong className="text-sm">{featureLabel(name)}</strong>
                    <Progress value={Math.min(100, Math.round((value / Math.max(earnings.total_usd || 1, value)) * 100))} />
                    <span className="text-sm text-soft">{money(value, 4)}</span>
                  </div>
                )) : <Empty text="No earnings breakdown yet." />}
              </div>
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
                {(status.suggestions || []).slice(0, 5).map((suggestion) => <SuggestionCard suggestion={suggestion} key={suggestion.title} />)}
                {!(status.suggestions || []).length ? <Empty text="No suggestions yet." /> : null}
              </div>
            </Panel>
          </aside>
        </div>

        <footer className="mt-8 flex flex-col gap-2 border-t border-line py-5 text-sm text-soft md:flex-row md:items-center md:justify-between">
          <span>Last run {formatDate(status.last_run)}</span>
          <span>Dashboard polled {lastPoll ? formatDate(lastPoll.toISOString()) : 'not yet'}</span>
        </footer>
      </main>
    </div>
  );
}

function buildIssues(status: Status) {
  const issues: Array<{ tone: 'good' | 'warn' | 'bad' | 'info'; label: string; title: string; detail: string }> = [];
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

function buildReadiness(status: Status) {
  const entries = Object.values(status.secret_readiness || {});
  if (!entries.length) {
    return { ready: 0, total: 0, percent: 0 };
  }
  const ready = entries.filter((info) => {
    const required = info.required_count || Math.max(1, (info.present || []).length + (info.missing || []).length);
    return (info.present_count || 0) >= required;
  }).length;
  return { ready, total: entries.length, percent: Math.round((ready / entries.length) * 100) };
}

function buildHealth(status: Status, issues: Array<{ tone: string }>, readinessPercent: number): { tone: 'good' | 'warn' | 'bad' | 'info'; label: string } {
  if (issues.some((issue) => issue.tone === 'bad')) return { tone: 'bad', label: 'attention required' };
  if (ageLabel(status.last_run).tone !== 'good') return { tone: 'warn', label: 'stale cycle' };
  if (readinessPercent < 60) return { tone: 'warn', label: 'setup incomplete' };
  if ((status.last_earning?.actions || []).some((action) => action.success === false)) return { tone: 'warn', label: 'module warning' };
  return { tone: 'good', label: 'operational' };
}

function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

function StatusCell({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="status-cell">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </div>
  );
}

function Metric({ title, value, detail, icon }: { title: string; value: string; detail: string; icon: React.ReactNode }) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span>{title}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function Phase({ name, ok, detail, tone }: { name: string; ok: boolean; detail: string; tone?: 'good' | 'warn' | 'bad' | 'info' }) {
  const actualTone = tone || (ok ? 'good' : 'bad');
  return (
    <article className={`phase-card ${actualTone}`}>
      {actualTone === 'good' ? <CheckCircle2 size={18} /> : actualTone === 'bad' ? <XCircle size={18} /> : <AlertTriangle size={18} />}
      <strong>{name}</strong>
      <p>{detail}</p>
    </article>
  );
}

function Pill({ tone = 'neutral', icon, children }: { tone?: 'good' | 'warn' | 'bad' | 'info' | 'neutral'; icon?: React.ReactNode; children: React.ReactNode }) {
  return <span className={`pill ${tone}`}>{icon}{children}</span>;
}

function Progress({ value, label }: { value: number; label?: string }) {
  return (
    <div>
      {label ? <div className="mb-2 text-sm text-soft">{label}</div> : null}
      <div className="progress"><span style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div>
    </div>
  );
}

function ActionCard({ action }: { action: Action }) {
  const amount = typeof action.estimated_usd === 'number' ? action.estimated_usd : action.value_usd;
  return (
    <article className="action-card">
      <div className="mb-3 flex items-center justify-between gap-3">
        <strong>{action.platform || 'unknown'}</strong>
        <Pill tone={action.success === false ? 'bad' : 'good'}>{action.success === false ? 'failed' : 'success'}</Pill>
      </div>
      <p>{action.title || action.topic || action.symbol || action.error || 'Action recorded'}</p>
      {typeof amount === 'number' ? <span>{money(amount, 4)}</span> : null}
    </article>
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

function SuggestionCard({ suggestion }: { suggestion: Suggestion }) {
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

function Banner({ tone, text }: { tone: 'bad'; text: string }) {
  return <div className={`mb-6 banner ${tone}`}><AlertTriangle size={18} />{text}</div>;
}

function Empty({ text }: { text: string }) {
  return <p className="empty">{text}</p>;
}
