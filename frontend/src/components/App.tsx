import { BarChart3, Bot, Building2, Clock3, ExternalLink, GitBranch, RefreshCw, ShieldCheck, Sparkles, TerminalSquare } from 'lucide-react';
import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import { DashboardPage } from './dashboard/DashboardPage';
import { Banner, Empty, Pill } from './common';
import { fetchStatus } from '../services/status';
import { buildHealth, buildIssues, buildReadiness } from '../utils/dashboard';
import { ageLabel, formatDate } from '../utils/format';
import type { Status } from '../types/status';

type View = 'dashboard' | 'suggestions' | 'submit-business';
declare const __OFFLINE_AGENT_MODE__: boolean;

const offlineAgentMode = __OFFLINE_AGENT_MODE__;
const OfflineAgentView = offlineAgentMode
  ? lazy(() => import('./OfflineAgentView').then((module) => ({ default: module.OfflineAgentView })))
  : null;

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
  const [view, setView] = useState<View>(() => {
    if (offlineAgentMode && window.location.hash === '#suggestions') return 'suggestions';
    if (offlineAgentMode && window.location.hash === '#submit-business') return 'submit-business';
    return 'dashboard';
  });

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
  const issues = useMemo(() => buildIssues(status), [status]);
  const readiness = useMemo(() => buildReadiness(status), [status]);
  const health = useMemo(() => buildHealth(status, issues, readiness.percent), [status, issues, readiness.percent]);

  function changeView(nextView: View) {
    if (!offlineAgentMode && nextView !== 'dashboard') return;
    setView(nextView);
    const hash = nextView === 'suggestions' ? '#suggestions' : nextView === 'submit-business' ? '#submit-business' : window.location.pathname;
    window.history.replaceState(null, '', hash);
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
              {offlineAgentMode
                ? 'Local operations console with offline agent tools, earning research, and owner action queues.'
                : 'Online status console for the hourly research cycle, readiness, and public run history.'}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <div className={`mode-strip ${offlineAgentMode ? 'offline' : ''}`} aria-label="Frontend mode">
              <span className="active">online</span>
              {offlineAgentMode ? <span>offline agents</span> : null}
            </div>
            <div className={`view-switch ${offlineAgentMode ? 'with-offline' : ''}`} aria-label="Dashboard view">
              <button className={view === 'dashboard' ? 'active' : ''} onClick={() => changeView('dashboard')} type="button">
                <BarChart3 size={15} /> dashboard
              </button>
              {offlineAgentMode ? (
                <>
                  <button className={view === 'suggestions' ? 'active' : ''} onClick={() => changeView('suggestions')} type="button">
                    <Sparkles size={15} /> suggestions
                  </button>
                  <button className={view === 'submit-business' ? 'active' : ''} onClick={() => changeView('submit-business')} type="button">
                    <Building2 size={15} /> submit business
                  </button>
                </>
              ) : null}
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

        {offlineAgentMode && OfflineAgentView && (view === 'suggestions' || view === 'submit-business') ? (
          <Suspense fallback={<Empty text="Loading offline agent tools." />}>
            <OfflineAgentView status={status} view={view} />
          </Suspense>
        ) : (
          <DashboardPage status={status} />
        )}

        <footer className="mt-8 flex flex-col gap-2 border-t border-line py-5 text-sm text-soft md:flex-row md:items-center md:justify-between">
          <span>Last run {formatDate(status.last_run)}</span>
          <span>Dashboard polled {lastPoll ? formatDate(lastPoll.toISOString()) : 'not yet'}</span>
        </footer>
      </main>
    </div>
  );
}
