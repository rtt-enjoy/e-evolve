import { Menu, RefreshCw, X } from 'lucide-react';
import { Suspense, lazy, useEffect, useMemo, useRef, useState, type ComponentType } from 'react';
import { Banner, Dot, Empty, Pill } from './ui';
import { fetchStatus } from '../services/status';
import { availableSections, sectionById, SECTIONS, unclaimedKeys } from '../sections/registry';
import { buildHealth, buildIssues, buildReadiness } from '../utils/dashboard';
import { ageLabel, formatDate } from '../utils/format';
import { navigate, useRoute } from '../utils/route';
import type { Status } from '../types/status';

const emptyStatus: Status = {
  active_features: [],
  inactive_features: [],
  earnings: {},
  last_evolution: {},
  last_earning: { actions: [] },
  suggestions: [],
  errors: [],
};

/** One lazy component per registered section, created once at module load. */
const SECTION_VIEWS = new Map<string, ComponentType<{ status: Status }>>(
  SECTIONS.map((section) => [section.id, lazy(section.load)]),
);

export function App() {
  const [status, setStatus] = useState<Status>(emptyStatus);
  const [lastPoll, setLastPoll] = useState<Date | null>(null);
  const [loadError, setLoadError] = useState('');
  const [loading, setLoading] = useState(true);
  const [navOpen, setNavOpen] = useState(false);
  const route = useRoute();
  const mainRef = useRef<HTMLElement>(null);

  async function load() {
    try {
      const next = await fetchStatus();
      setStatus(next);
      setLastPoll(new Date());
      setLoadError('');
    } catch (error) {
      setLoadError(error instanceof Error ? error.message : String(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const timer = window.setInterval(load, 60_000);
    return () => window.clearInterval(timer);
  }, []);

  // Close the mobile drawer and scroll to top whenever the route changes.
  useEffect(() => {
    setNavOpen(false);
    mainRef.current?.scrollTo({ top: 0 });
  }, [route.section, route.detail]);

  const sections = useMemo(() => availableSections(status), [status]);
  const issues = useMemo(() => buildIssues(status), [status]);
  const readiness = useMemo(() => buildReadiness(status), [status]);
  const health = useMemo(() => buildHealth(status, issues, readiness.percent), [status, issues, readiness.percent]);
  const newKeys = useMemo(() => unclaimedKeys(status), [status]);
  const freshness = ageLabel(status.last_run);

  const active = sections.find((section) => section.id === route.section)
    // A hash pointing at a hidden or unknown section falls back to Overview.
    ?? sectionById(route.section)
    ?? sections[0];
  const View = active ? SECTION_VIEWS.get(active.id) : undefined;

  return (
    <div className={`shell ${navOpen ? 'nav-open' : ''}`}>
      <a className="skip-link" href="#main">Skip to content</a>

      <aside className="sidebar" aria-label="Sections">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true">E</div>
          <div className="min-w-0">
            <strong>E-Evolve</strong>
            <span>autonomous research bot</span>
          </div>
          <button className="icon-btn nav-close" type="button" onClick={() => setNavOpen(false)} aria-label="Close navigation">
            <X size={18} />
          </button>
        </div>

        <div className="live">
          <Dot tone={freshness.tone} />
          <span>{loading ? 'connecting' : freshness.label}</span>
          <em>{health.label}</em>
        </div>

        <nav>
          {sections.map((section) => {
            const badge = section.badge?.(status) ?? null;
            const isActive = active?.id === section.id;
            const isNewData = section.id === 'data' && newKeys.length > 0;
            return (
              <a
                key={section.id}
                href={`#/${section.id}`}
                className={isActive ? 'active' : ''}
                aria-current={isActive ? 'page' : undefined}
              >
                <span>{section.label}</span>
                {isNewData ? <em className="badge new">{newKeys.length} new</em> : badge ? <em className="badge">{badge}</em> : null}
              </a>
            );
          })}
        </nav>

        <div className="sidebar-foot">
          <Pill tone="info">{status.llm_provider || 'no provider'}</Pill>
          <Pill tone="neutral">v{status.version || '0.0.0'}</Pill>
          <div className="links">
            <a href="status.json">status.json</a>
            <a href="earnings-log.md">earnings log</a>
          </div>
        </div>
      </aside>

      <button className="nav-scrim" type="button" onClick={() => setNavOpen(false)} aria-hidden={!navOpen} tabIndex={-1} />

      <main className="main" id="main" ref={mainRef}>
        <div className="topbar">
          <button className="icon-btn nav-open-btn" type="button" onClick={() => setNavOpen(true)} aria-label="Open navigation">
            <Menu size={18} />
          </button>
          <div className="crumb">
            <span>{active?.label || 'Dashboard'}</span>
            {route.detail ? <em>detail</em> : null}
          </div>
          <div className="topbar-actions">
            <span className="poll">{lastPoll ? `synced ${formatDate(lastPoll.toISOString())}` : 'syncing'}</span>
            <button className="icon-btn" type="button" onClick={load} aria-label="Refresh now" title="Refresh now">
              <RefreshCw size={17} />
            </button>
          </div>
        </div>

        <div className="content">
          {loadError ? <Banner tone="bad" text={`Could not load status.json: ${loadError}`} /> : null}

          {View && active ? (
            <Suspense fallback={<Empty text={`Loading ${active.label.toLowerCase()}…`} />}>
              <View status={status} />
            </Suspense>
          ) : (
            <Empty text="No dashboard data yet." />
          )}

          <footer className="foot">
            <span>Cycle #{status.total_runs || 0} · last run {formatDate(status.last_run)}</span>
            <button type="button" className="linkish" onClick={() => navigate('data')}>inspect raw snapshot</button>
          </footer>
        </div>
      </main>
    </div>
  );
}
