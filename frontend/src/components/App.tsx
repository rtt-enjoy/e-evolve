import { ChevronRight, Menu, Monitor, Moon, RefreshCw, Sparkles, Sun, X } from 'lucide-react';
import { Suspense, lazy, useEffect, useMemo, useRef, useState, type ComponentType } from 'react';
import { Banner, Dot, Empty, Pill } from './ui';
import { availableSections, sectionById, SECTIONS, unclaimedKeys } from '../sections/registry';
import { buildHealth, buildIssues, buildReadiness } from '../utils/dashboard';
import { ageLabel, formatDate } from '../utils/format';
import { nextCycle, sinceLabel, useNow, useStatusSync } from '../utils/sync';
import { navigate, useRoute } from '../utils/route';
import type { Status } from '../types/status';
import { engineState } from '../utils/engine';

type Theme = 'system' | 'light' | 'dark';
const THEME_KEY = 'e-evolve-theme';
const THEME_ORDER: Theme[] = ['system', 'light', 'dark'];
const THEME_ICON = { system: Monitor, light: Sun, dark: Moon } as const;

function readTheme(): Theme {
	try {
		const saved = localStorage.getItem(THEME_KEY);
		return saved === 'light' || saved === 'dark' ? saved : 'system';
	} catch {
		return 'system';
	}
}

/** Pins `data-theme` on <html>; "system" removes it so the OS preference wins. */
function useTheme(): [Theme, () => void] {
	const [theme, setTheme] = useState<Theme>(readTheme);
	useEffect(() => {
		const root = document.documentElement;
		if (theme === 'system') delete root.dataset.theme;
		else root.dataset.theme = theme;
		try {
			if (theme === 'system') localStorage.removeItem(THEME_KEY);
			else localStorage.setItem(THEME_KEY, theme);
		} catch {
			// Storage blocked: the choice still applies for this visit.
		}
	}, [theme]);
	const cycle = () => setTheme((current) => THEME_ORDER[(THEME_ORDER.indexOf(current) + 1) % THEME_ORDER.length]);
	return [theme, cycle];
}

/** One lazy component per registered section, created once at module load. */
const SECTION_VIEWS = new Map<string, ComponentType<{ status: Status }>>(
	SECTIONS.map((section) => [section.id, lazy(section.load)]),
);

export function App() {
	const { status, source, lastPoll, error: loadError, loading, refreshing, notice, dismiss, refresh } = useStatusSync();
	const now = useNow();
	const [navOpen, setNavOpen] = useState(false);
	const [theme, cycleTheme] = useTheme();
	const ThemeIcon = THEME_ICON[theme];
	const route = useRoute();
	const mainRef = useRef<HTMLElement>(null);

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
	const next = nextCycle(status.last_run, now);
	const engine = engineState(status);

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
					<span>{loading ? 'connecting' : `cycle ${freshness.label}`}</span>
					<em>{health.label} · {next.label}</em>
				</div>

				<nav>
					{sections.map((section) => {
						const badge = section.badge?.(status) ?? null;
						const isActive = active?.id === section.id;
						const isNewData = section.id === 'data' && newKeys.length > 0;
						const Icon = section.icon;
						return (
							<a
								key={section.id}
								href={`#/${section.id}`}
								className={isActive ? 'active' : ''}
								aria-current={isActive ? 'page' : undefined}
							>
								<Icon className="nav-icon" size={17} strokeWidth={2} />
								<span>{section.label}</span>
								{isNewData ? <em className="badge new">{newKeys.length} new</em> : badge ? <em className="badge">{badge}</em> : null}
							</a>
						);
					})}
				</nav>

				<div className="sidebar-foot">
					<Pill tone={engine.tone}>{engine.label}</Pill>
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
					<nav className="crumb" aria-label="Breadcrumb">
						<a href="#/overview">E-Evolve</a>
						<ChevronRight size={14} aria-hidden="true" />
						{route.detail ? (
							<>
								<a href={`#/${active?.id || ''}`}>{active?.label || 'Dashboard'}</a>
								<ChevronRight size={14} aria-hidden="true" />
								<span>detail</span>
							</>
						) : (
							<span>{active?.label || 'Dashboard'}</span>
						)}
					</nav>
					<div className="topbar-actions">
						<span
							className={`sync ${loadError ? 'bad' : refreshing ? 'busy' : 'ok'}`}
							title={lastPoll ? `Last checked ${formatDate(lastPoll.toISOString())} from ${source === 'repo' ? 'the repository (newer than Pages)' : 'GitHub Pages'}. Checks every minute while this tab is open.` : 'Connecting'}
						>
							<span className="sync-dot" aria-hidden="true" />
							{loadError ? 'offline' : `synced ${sinceLabel(lastPoll, now)}`}
							<em>{next.label}</em>
						</span>
						<button
							className="icon-btn"
							type="button"
							onClick={cycleTheme}
							aria-label={`Theme: ${theme}. Switch theme`}
							title={`Theme: ${theme}`}
						>
							<ThemeIcon size={17} />
						</button>
						<button className={`icon-btn ${refreshing ? 'spinning' : ''}`} type="button" onClick={refresh} aria-label="Refresh now" title="Refresh now">
							<RefreshCw size={17} />
						</button>
					</div>
				</div>

				<div className="content">
					{loadError ? <Banner tone="bad" text={`Could not refresh status.json (${loadError}). Showing the last snapshot that loaded.`} /> : null}

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

			<div className="toast-region" aria-live="polite">
				{notice ? (
					<div className="toast" role="status" key={notice.run}>
						<Sparkles size={16} className="toast-icon" aria-hidden="true" />
						<div className="min-w-0">
							<strong>Cycle #{notice.run} landed</strong>
							<p>{notice.changes.length ? notice.changes.join(' · ') : 'No headline numbers moved.'}</p>
						</div>
						<button className="icon-btn" type="button" onClick={dismiss} aria-label="Dismiss">
							<X size={15} />
						</button>
					</div>
				) : null}
			</div>
		</div>
	);
}
