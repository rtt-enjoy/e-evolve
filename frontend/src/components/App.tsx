import { Activity, AlertTriangle, ArrowUpRight, BarChart3, Bot, BriefcaseBusiness, CalendarDays, Check, CheckCircle2, CircleDollarSign, ClipboardCheck, Clock3, Code2, Copy, ExternalLink, GitBranch, KeyRound, ListChecks, PlayCircle, RefreshCw, ShieldCheck, Sparkles, Target, TerminalSquare, TrendingUp, WalletCards, WandSparkles, XCircle } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { fetchStatus } from '../services/status';
import { ageLabel, clampPercent, evolutionTone, featureLabel, formatDate, money, scoreTone, shortText } from '../utils/format';
import type { Action, CodeTechOpportunity, Status, Suggestion } from '../types/status';

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
  const [view, setView] = useState<'dashboard' | 'suggestions'>(() => window.location.hash === '#suggestions' ? 'suggestions' : 'dashboard');

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
  const dailyTarget = status.code_tech_earning?.daily_target_usd || 10;
  const weekTarget = dailyTarget * 7;
  const weekPercent = clampPercent(((earnings.this_week_usd || 0) / Math.max(1, weekTarget)) * 100);

  const issues = useMemo(() => buildIssues(status), [status]);
  const breakdown = Object.entries(earnings.breakdown || {}).sort((a, b) => b[1] - a[1]);
  const readiness = useMemo(() => buildReadiness(status), [status]);
  const health = useMemo(() => buildHealth(status, issues, readiness.percent), [status, issues, readiness.percent]);
  const earningModules = useMemo(() => buildEarningModules(status), [status]);
  const opportunities = status.code_tech_earning?.opportunities || [];
  const opportunityStats = useMemo(() => buildOpportunityStats(opportunities), [opportunities]);
  const automationSuggestions = useMemo(() => buildAutomationSuggestions(status), [status]);
  const suggestionStats = useMemo(() => buildSuggestionStats(automationSuggestions), [automationSuggestions]);

  function changeView(nextView: 'dashboard' | 'suggestions') {
    setView(nextView);
    window.history.replaceState(null, '', nextView === 'suggestions' ? '#suggestions' : window.location.pathname);
  }

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
            <div className="view-switch" aria-label="Dashboard view">
              <button className={view === 'dashboard' ? 'active' : ''} onClick={() => changeView('dashboard')} type="button">
                <BarChart3 size={15} /> dashboard
              </button>
              <button className={view === 'suggestions' ? 'active' : ''} onClick={() => changeView('suggestions')} type="button">
                <Sparkles size={15} /> suggestions
              </button>
            </div>
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

        {view === 'suggestions' ? (
          <SuggestionPage
            status={status}
            suggestions={automationSuggestions}
            stats={suggestionStats}
          />
        ) : (
          <>
        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <Metric title="Total earnings" value={money(earnings.total_usd, 4)} detail={`${money(earnings.last_cycle_usd, 4)} last cycle`} icon={<CircleDollarSign />} />
          <Metric title="This week" value={money(earnings.this_week_usd, 4)} detail={`${weekPercent}% of ${money(weekTarget, 0)} target`} icon={<Activity />} />
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
                {(status.suggestions || []).slice(0, 5).map((suggestion) => <SuggestionCard suggestion={suggestion} key={suggestion.title} />)}
                {!(status.suggestions || []).length ? <Empty text="No suggestions yet." /> : null}
              </div>
            </Panel>
          </aside>
        </div>
          </>
        )}

        <footer className="mt-8 flex flex-col gap-2 border-t border-line py-5 text-sm text-soft md:flex-row md:items-center md:justify-between">
          <span>Last run {formatDate(status.last_run)}</span>
          <span>Dashboard polled {lastPoll ? formatDate(lastPoll.toISOString()) : 'not yet'}</span>
        </footer>
      </main>
    </div>
  );
}

type AutomationSuggestion = Suggestion & {
  id: string;
  requiredSecrets: string[];
  missingSecrets: string[];
  readinessPercent: number;
  ready: boolean;
  command: string;
  automationPlan: string[];
};

function SuggestionPage({
  status,
  suggestions,
  stats,
}: {
  status: Status;
  suggestions: AutomationSuggestion[];
  stats: ReturnType<typeof buildSuggestionStats>;
}) {
  const top = suggestions[0];

  return (
    <div className="suggestion-page">
      <section className="suggestion-hero">
        <div>
          <div className="mb-4 flex flex-wrap gap-2">
            <Pill tone="info" icon={<WandSparkles size={14} />}>ai workflow ready</Pill>
            <Pill tone={stats.readyCount ? 'good' : 'warn'} icon={<KeyRound size={14} />}>{stats.readyCount}/{stats.total} ready</Pill>
            <Pill tone="good" icon={<CircleDollarSign size={14} />}>{money(stats.weeklyUsd, 0)} weekly upside</Pill>
          </div>
          <h2>Suggestions To Earn More</h2>
          <p>
            Each card is an earning improvement the AI agent can refine and implement through the existing GitHub workflow.
            Add the required keys, then launch the improvement request for the next evolution cycle.
          </p>
        </div>
        <div className="suggestion-hero-panel">
          <span>Best next move</span>
          <strong>{top?.title || 'No suggestion selected'}</strong>
          <p>{top?.ready ? 'Ready for AI implementation.' : 'Waiting on setup before automation can finish.'}</p>
        </div>
      </section>

      <section className="suggestion-stat-grid">
        <MiniStat icon={<Sparkles />} label="Suggestions" value={String(stats.total)} detail="ranked by bot output" />
        <MiniStat icon={<CheckCircle2 />} label="Ready now" value={String(stats.readyCount)} detail="all secrets present" />
        <MiniStat icon={<KeyRound />} label="Missing keys" value={String(stats.missingSecrets)} detail="shown per card" />
        <MiniStat icon={<TrendingUp />} label="Weekly upside" value={money(stats.weeklyUsd, 0)} detail="estimated by bot" />
      </section>

      <div className="suggestion-layout">
        <div className="space-y-4">
          {suggestions.map((suggestion, index) => (
            <AutomationSuggestionCard
              key={suggestion.id}
              rank={index + 1}
              repo={status.github_repo || inferRepoFromLocation()}
              suggestion={suggestion}
            />
          ))}
          {!suggestions.length ? <Empty text="No earning suggestions are available yet. Run an evolution cycle to generate new ideas." /> : null}
        </div>

        <aside className="suggestion-side">
          <Panel title="How It Runs" subtitle="The page prepares the request; GitHub Actions performs the work.">
            <div className="automation-steps">
              <WorkflowStep icon={<KeyRound />} title="Complete prerequisites" text="Add the listed API keys or tokens as GitHub Actions secrets." />
              <WorkflowStep icon={<Sparkles />} title="Improve suggestion" text="Open the prefilled bot-command issue or add the command to command.txt." />
              <WorkflowStep icon={<PlayCircle />} title="Workflow executes" text="The hourly cycle passes the request to the evolution agent and commits safe changes." />
              <WorkflowStep icon={<Check />} title="Suggestion is done" text="The next dashboard refresh shows changed files, updated suggestions, and readiness." />
            </div>
          </Panel>

          <Panel title="Required Setup" subtitle="Secrets still needed across the current suggestion list.">
            <div className="setup-list">
              {uniqueMissingSecrets(suggestions).map((secret) => <code key={secret}>{secret}</code>)}
              {!uniqueMissingSecrets(suggestions).length ? <Empty text="No missing secrets for the listed suggestions." /> : null}
            </div>
          </Panel>
        </aside>
      </div>
    </div>
  );
}

function AutomationSuggestionCard({
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
              {!suggestion.requiredSecrets.length ? <span>No extra API keys required</span> : null}
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

function WorkflowStep({ icon, title, text }: { icon: React.ReactNode; title: string; text: string }) {
  return (
    <article className="workflow-step">
      <div>{icon}</div>
      <strong>{title}</strong>
      <p>{text}</p>
    </article>
  );
}

function EarningCommandCenter({
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
          <h3>{money(status.earnings?.this_week_usd, 4)} this week</h3>
          <p>{weekPercent}% of {money(weekTarget, 0)} weekly target. Last opportunity refresh {formatDate(codeTech.last_refresh_at)}.</p>
        </div>
        <div className="earning-progress">
          <Progress value={weekPercent} />
          <span>{money(status.earnings?.last_cycle_usd, 4)} last cycle</span>
        </div>
      </div>

      <div className="earning-stat-grid">
        <MiniStat icon={<Target />} label="Daily target" value={money(codeTech.daily_target_usd, 0)} />
        <MiniStat icon={<ListChecks />} label="Opportunities" value={String(opportunityStats.total)} detail={`${opportunityStats.paidCount} with value`} />
        <MiniStat icon={<TrendingUp />} label="Pipeline value" value={money(opportunityStats.estimatedValue, 0)} />
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
            {!opportunities.length ? <Empty text="No earning opportunities are available yet." /> : null}
          </div>
        </div>
        <div>
          <h3 className="section-title mb-3">Channel Matrix</h3>
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
          <h3 className="section-title mb-3">Revenue Mix</h3>
          <div className="space-y-3">
            {breakdown.length ? breakdown.map(([name, value]) => (
              <div className="revenue-row" key={name}>
                <div className="flex items-center justify-between gap-3">
                  <strong>{featureLabel(name)}</strong>
                  <span>{money(value, 4)}</span>
                </div>
                <Progress value={clampPercent((value / Math.max(status.earnings?.total_usd || 1, value)) * 100)} />
              </div>
            )) : <Empty text="No earnings breakdown yet." />}
          </div>
          <div className="mt-4">
            <h3 className="section-title mb-3">Latest Actions</h3>
            <div className="space-y-2">
              {actions.slice(0, 3).map((action, index) => <CompactAction action={action} key={index} />)}
              {!actions.length ? <Empty text="No earning actions recorded." /> : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MiniStat({ icon, label, value, detail }: { icon: React.ReactNode; label: string; value: string; detail?: string }) {
  return (
    <article className="mini-stat">
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <p>{detail}</p> : null}
    </article>
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
          {(opportunity.estimated_value_usd || 0) > 0 ? <Pill tone="good">{money(opportunity.estimated_value_usd, 0)}</Pill> : null}
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
  const amount = typeof action.estimated_usd === 'number' ? action.estimated_usd : action.value_usd;
  return (
    <article className="compact-action">
      <span className={`status-dot ${action.success === false ? 'bad' : 'good'}`} />
      <strong>{action.platform || 'module'}</strong>
      <p>{shortText(action.title || action.topic || action.symbol || action.error || 'Action recorded', 52)}</p>
      {typeof amount === 'number' ? <em>{money(amount, 4)}</em> : null}
    </article>
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

function buildEarningModules(status: Status) {
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
      detail: missingLabel(readiness.articles_medium?.missing),
      value: moduleActionValue(actions, 'medium'),
    },
    {
      key: 'twitter',
      name: 'Twitter/X',
      active: Boolean(readiness.twitter?.active || status.active_features?.includes('twitter')),
      detail: missingLabel(readiness.twitter?.missing),
      value: moduleActionValue(actions, 'twitter'),
    },
    {
      key: 'crypto_binance',
      name: 'Binance Trading',
      active: Boolean(readiness.crypto_binance?.active || status.active_features?.includes('crypto_binance')),
      detail: missingLabel(readiness.crypto_binance?.missing),
      value: money(status.usdt_balance, 4),
    },
    {
      key: 'nft_ethereum',
      name: 'NFT Minting',
      active: Boolean(readiness.nft_ethereum?.active || status.active_features?.includes('nft_ethereum')),
      detail: missingLabel(readiness.nft_ethereum?.missing),
      value: moduleActionValue(actions, 'nft'),
    },
  ];

  return modules.map((module) => ({
    ...module,
    label: module.active ? 'ready' : 'setup',
    tone: module.active ? 'good' as const : 'warn' as const,
  }));
}

function buildOpportunityStats(opportunities: CodeTechOpportunity[]) {
  return {
    total: opportunities.length,
    paidCount: opportunities.filter((opportunity) => (opportunity.estimated_value_usd || 0) > 0).length,
    estimatedValue: opportunities.reduce((sum, opportunity) => sum + (opportunity.estimated_value_usd || 0), 0),
    topScore: opportunities.reduce((top, opportunity) => Math.max(top, opportunity.score || 0), 0),
  };
}

function buildAutomationSuggestions(status: Status): AutomationSuggestion[] {
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

function buildSuggestionStats(suggestions: AutomationSuggestion[]) {
  return {
    total: suggestions.length,
    readyCount: suggestions.filter((suggestion) => suggestion.ready).length,
    missingSecrets: uniqueMissingSecrets(suggestions).length,
    weeklyUsd: suggestions.reduce((sum, suggestion) => sum + (suggestion.estimated_weekly_usd || 0), 0),
  };
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

function uniqueMissingSecrets(suggestions: AutomationSuggestion[]) {
  return Array.from(new Set(suggestions.flatMap((suggestion) => suggestion.missingSecrets))).sort();
}

function buildIssueUrl(repo: string, suggestion: AutomationSuggestion) {
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

function inferRepoFromLocation() {
  const host = window.location.hostname;
  const path = window.location.pathname.split('/').filter(Boolean)[0];
  if (!host.endsWith('.github.io') || !path) return '';
  return `${host.replace('.github.io', '')}/${path}`;
}

function missingLabel(missing?: string[]) {
  if (!missing?.length) return 'All required secrets present';
  return `${missing.length} secrets missing`;
}

function moduleActionValue(actions: Action[], platform: string) {
  const count = actions.filter((action) => (action.platform || '').toLowerCase().includes(platform.toLowerCase())).length;
  return count ? `${count} latest actions` : '';
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
