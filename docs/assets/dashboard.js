import { createApp } from 'vue';

const POLL_MS = 60000;
const WORKFLOW_FILE = 'evolve.yml';
const DEFAULT_REF = 'main';
const STORAGE_KEYS = {
  repo: 'e-evolve.githubRepo',
  token: 'e-evolve.githubToken',
  ref: 'e-evolve.workflowRef',
};

const ORDER_PRESETS = [
  ['force articles 2', 'Fill today\'s article quota'],
  ['force articles 1', 'Publish one buyer-intent article'],
  ['post thread', 'Distribute the latest article'],
  ['status report', 'Audit setup and failures'],
  ['skip evolution', 'Protect earning cycle once'],
  ['force trade conservative', 'Only when Binance is funded'],
  ['force mint 1', 'Only when wallet is funded'],
  ['reset earnings', 'Start a fresh weekly view'],
];

const REVENUE_STAGES = [
  { key: 'model', label: 'Model', detail: 'Generate articles and upgrades', features: ['llm_groq', 'llm_gemini', 'llm_openrouter', 'llm_anthropic'] },
  { key: 'publish', label: 'Publish', detail: 'Ship buyer-intent content', features: ['articles_devto', 'articles_medium'] },
  { key: 'convert', label: 'Convert', detail: 'Send readers to a CTA or wallet', features: ['usdt_wallet'] },
  { key: 'distribute', label: 'Distribute', detail: 'Turn posts into repeat reach', features: ['twitter'] },
  { key: 'payout', label: 'Payout', detail: 'Move funds when thresholds hit', features: ['crypto_payout'] },
];

const SECRET_IMPACT = {
  MEDIUM_INTEGRATION_TOKEN: 94,
  EARN_CTA_URL: 90,
  USDT_WALLET_ADDRESS: 86,
  TWITTER_API_KEY: 72,
  TWITTER_API_SECRET: 72,
  TWITTER_ACCESS_TOKEN: 72,
  TWITTER_ACCESS_SECRET: 72,
  OPENROUTER_API_KEY: 64,
  GEMINI_API_KEY: 62,
  ANTHROPIC_API_KEY: 56,
  BINANCE_WITHDRAW_ADDRESS: 48,
  BINANCE_API_KEY: 42,
  BINANCE_SECRET_KEY: 42,
  ETH_PRIVATE_KEY: 24,
  ETH_WALLET_ADDRESS: 24,
};

const MODULE_LABELS = {
  llm_anthropic: 'Anthropic',
  llm_gemini: 'Gemini',
  llm_openrouter: 'OpenRouter',
  llm_groq: 'Groq',
  articles_devto: 'dev.to articles',
  articles_medium: 'Medium articles',
  usdt_wallet: 'USDT wallet',
  twitter: 'Twitter / X',
  crypto_binance: 'Crypto trading',
  crypto_payout: 'Payout automation',
  nft_ethereum: 'NFT minting',
};

function money(value, digits = 2) {
  const n = Number(value || 0);
  return '$' + n.toFixed(digits);
}

function fmtDate(iso) {
  if (!iso) return 'never';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return String(iso);
  return d.toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
}

function ageLabel(iso) {
  if (!iso) return 'never';
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return 'unknown';
  const secs = Math.max(0, Math.floor((Date.now() - d.getTime()) / 1000));
  if (secs < 90) return 'just now';
  if (secs < 3600) return Math.floor(secs / 60) + 'm ago';
  if (secs < 86400) return Math.floor(secs / 3600) + 'h ago';
  return Math.floor(secs / 86400) + 'd ago';
}

function compactNumber(value) {
  return new Intl.NumberFormat('en', { notation: 'compact' }).format(Number(value || 0));
}

function pct(done, total) {
  if (!total) return 0;
  return Math.max(0, Math.min(100, Math.round(Number(done || 0) / Number(total) * 100)));
}

function providerClass(provider) {
  if (provider === 'gemini') return 'info';
  if (provider === 'groq') return 'warn';
  if (provider === 'openrouter') return 'good';
  return 'info';
}

function cycleState(lastRun) {
  if (!lastRun) return { label: 'never run', cls: 'bad' };
  const d = new Date(lastRun);
  if (Number.isNaN(d.getTime())) return { label: 'unknown', cls: 'warn' };
  const mins = Math.floor((Date.now() - d.getTime()) / 60000);
  if (mins <= 75) return { label: 'healthy', cls: 'good' };
  if (mins <= 180) return { label: 'late', cls: 'warn' };
  return { label: 'stalled', cls: 'bad' };
}

function inferGitHubRepo() {
  const host = window.location.hostname;
  if (!host.endsWith('.github.io')) return '';
  const owner = host.slice(0, -'.github.io'.length);
  const repo = window.location.pathname.split('/').filter(Boolean)[0];
  return owner && repo ? owner + '/' + repo : '';
}

createApp({
  data() {
    return {
      status: {},
      loaded: false,
      online: true,
      lastPoll: null,
      ORDER_PRESETS,
      commands: [],
      customCommand: '',
      copyLabel: 'Copy',
      activeCommandGroup: 'earn',
      githubRepo: localStorage.getItem(STORAGE_KEYS.repo) || inferGitHubRepo(),
      githubToken: localStorage.getItem(STORAGE_KEYS.token) || '',
      workflowRef: localStorage.getItem(STORAGE_KEYS.ref) || DEFAULT_REF,
      dispatchState: 'idle',
      dispatchMessage: '',
    };
  },

  computed: {
    earn() {
      return this.status.earnings || {};
    },
    active() {
      return this.status.active_features || [];
    },
    inactive() {
      return this.status.inactive_features || [];
    },
    cycleHealth() {
      return cycleState(this.status.last_run);
    },
    workflows() {
      return Object.entries(this.status.llm_workflows || {}).map(([name, item]) => ({
        name,
        ...item,
      }));
    },
    secrets() {
      return Object.entries(this.status.secret_readiness || {}).map(([name, item]) => ({
        name,
        label: MODULE_LABELS[name] || name,
        percent: pct(item.present_count, item.required_count),
        ...item,
      }));
    },
    focusItems() {
      const missing = new Set(this.secrets.flatMap((item) => item.missing || []));
      const active = new Set(this.active);
      const cards = [];

      if (active.has('articles_devto') && missing.has('MEDIUM_INTEGRATION_TOKEN')) {
        cards.push(['Dual-publish articles', 'Add Medium to reuse every dev.to article with no extra model call.', 'MEDIUM_INTEGRATION_TOKEN']);
      }
      if (active.has('articles_devto') && !this.status.usdt_wallet) {
        cards.push(['Add a conversion target', 'Set a wallet, sponsor, tip, newsletter, or product CTA for every article.', 'USDT_WALLET_ADDRESS or EARN_CTA_URL']);
      }
      if (missing.has('TWITTER_API_KEY')) {
        cards.push(['Turn articles into distribution', 'Activate the social module only when your X developer access is ready.', 'TWITTER_API_KEY']);
      }
      if (missing.has('BINANCE_WITHDRAW_ADDRESS') && active.has('usdt_wallet')) {
        cards.push(['Finish payout automation', 'The wallet is known; add exchange withdrawal settings when you are ready.', 'BINANCE_WITHDRAW_ADDRESS']);
      }
      if (!cards.length) {
        cards.push(['Keep the loop healthy', 'All obvious setup gaps are covered. Watch cycle age, errors, and article output.', 'status report']);
      }
      if (active.has('articles_devto')) {
        cards.unshift(['Protect article quality', 'The normal schedule is capped at two generated articles per UTC day, with separate topic seeds for each post.', 'articles.daily_limit = 2']);
      }

      return cards.map((card, index) => ({ rank: index + 1, title: card[0], body: card[1], action: card[2] }));
    },
    opportunityItems() {
      const missingSecrets = new Set(this.secrets.flatMap((item) => item.missing || []));
      if (this.active.includes('articles_devto') && !this.status.usdt_wallet) missingSecrets.add('EARN_CTA_URL');
      const rows = Array.from(missingSecrets).map((name) => ({
        name,
        impact: SECRET_IMPACT[name] || 35,
        note: this.opportunityNote(name),
      }));
      return rows.sort((a, b) => b.impact - a.impact).slice(0, 5);
    },
    revenueStages() {
      const active = new Set(this.active);
      return REVENUE_STAGES.map((stage) => {
        const readyCount = stage.features.filter((feature) => active.has(feature)).length;
        const ready = readyCount > 0;
        return {
          ...stage,
          ready,
          readyCount,
          total: stage.features.length,
          cls: ready ? 'good' : 'warn',
        };
      });
    },
    commandGroups() {
      return {
        earn: this.ORDER_PRESETS.slice(0, 3),
        protect: this.ORDER_PRESETS.slice(3, 5),
        funded: this.ORDER_PRESETS.slice(5, 7),
        admin: this.ORDER_PRESETS.slice(7),
      };
    },
    activePresets() {
      return this.commandGroups[this.activeCommandGroup] || this.commandGroups.earn;
    },
    suggestions() {
      return this.status.suggestions || [];
    },
    actions() {
      return (this.status.last_earning && this.status.last_earning.actions) || [];
    },
    articleDaily() {
      const daily = this.status.article_daily || {};
      return {
        date: daily.date || 'not started',
        published: Number(daily.published || 0),
        limit: 2,
      };
    },
    articleProgress() {
      return pct(this.articleDaily.published, this.articleDaily.limit);
    },
    activeModules() {
      const freeNames = new Set(['llm_groq', 'llm_gemini', 'llm_openrouter', 'articles_devto', 'articles_medium', 'usdt_wallet']);
      return this.secrets
        .filter((item) => item.active)
        .map((item) => ({
          name: item.name,
          label: item.label,
          free: freeNames.has(item.name),
          role: item.name.startsWith('llm_') ? 'model' : 'earning',
        }));
    },
    evolution() {
      return this.status.last_evolution || {};
    },
    breakdown() {
      const entries = Object.entries(this.earn.breakdown || {});
      const max = Math.max(...entries.map(([, value]) => Number(value || 0)), 1);
      return entries.map(([name, value]) => ({
        name,
        value: Number(value || 0),
        percent: Math.round(Number(value || 0) / max * 100),
      }));
    },
    commandText: {
      get() {
        return this.commands.length ? this.commands.join('\n') : '# no commands';
      },
      set(value) {
        this.commands = value.split('\n').map((line) => line.trim()).filter(Boolean).filter((line) => line !== '# no commands');
      },
    },
    weeklyProjection() {
      const history = (this.earn.history || []).map(Number).filter((n) => n > 0);
      if (!history.length) return money(0);
      const avg = history.reduce((sum, n) => sum + n, 0) / history.length;
      return money(avg * 168);
    },
    baselineProjection() {
      const perPublish = 0.02;
      const dailyLimit = Math.max(1, Number(this.articleDaily.limit || 2));
      return money(perPublish * dailyLimit * 7);
    },
    nextBestAction() {
      if (this.opportunityItems.length) {
        return 'Add ' + this.opportunityItems[0].name;
      }
      if (this.articleDaily.published < this.articleDaily.limit) {
        return 'Run force articles 1';
      }
      return 'Watch next cycle';
    },
    weekGoalPercent() {
      return pct(this.earn.this_week_usd || 0, 10);
    },
    canDispatchWorkflow() {
      return Boolean(this.githubRepo.trim() && this.githubToken.trim() && this.workflowRef.trim() && this.dispatchState !== 'running');
    },
    dispatchStatusClass() {
      if (this.dispatchState === 'success') return 'good';
      if (this.dispatchState === 'error') return 'bad';
      return '';
    },
  },

  methods: {
    money,
    fmtDate,
    ageLabel,
    compactNumber,
    providerClass,
    moduleLabel(name) {
      return MODULE_LABELS[name] || name;
    },
    opportunityNote(name) {
      const notes = {
        MEDIUM_INTEGRATION_TOKEN: 'Doubles article reach without another generation.',
        EARN_CTA_URL: 'Gives each article a conversion path.',
        USDT_WALLET_ADDRESS: 'Lets the dashboard show a payment destination.',
        TWITTER_API_KEY: 'Starts distribution beyond publishing platforms.',
        TWITTER_API_SECRET: 'Required with the X posting keys.',
        TWITTER_ACCESS_TOKEN: 'Required with the X posting keys.',
        TWITTER_ACCESS_SECRET: 'Required with the X posting keys.',
        OPENROUTER_API_KEY: 'Adds cheap research and second opinions.',
        GEMINI_API_KEY: 'Unblocks stronger upgrade planning.',
        ANTHROPIC_API_KEY: 'Adds a premium evolution fallback.',
        BINANCE_WITHDRAW_ADDRESS: 'Completes automated payout routing.',
        BINANCE_API_KEY: 'Only useful when funded trading or payouts are intended.',
        BINANCE_SECRET_KEY: 'Only useful when funded trading or payouts are intended.',
      };
      return notes[name] || 'Optional module setup.';
    },
    addCommand(cmd) {
      if (!this.commands.includes(cmd)) this.commands.push(cmd);
    },
    addCustomCommand() {
      const cmd = this.customCommand.trim();
      if (cmd) this.addCommand(cmd);
      this.customCommand = '';
    },
    clearCommands() {
      this.commands = [];
    },
    rememberWorkflowSettings() {
      const repo = this.githubRepo.trim();
      const ref = this.workflowRef.trim() || DEFAULT_REF;
      if (repo) localStorage.setItem(STORAGE_KEYS.repo, repo);
      if (this.githubToken.trim()) localStorage.setItem(STORAGE_KEYS.token, this.githubToken.trim());
      localStorage.setItem(STORAGE_KEYS.ref, ref);
    },
    async runWorkflow() {
      const repo = this.githubRepo.trim();
      const token = this.githubToken.trim();
      const ref = this.workflowRef.trim() || DEFAULT_REF;
      if (!repo || !token) {
        this.dispatchState = 'error';
        this.dispatchMessage = 'Add a repo and a GitHub token with Actions write access.';
        return;
      }
      this.rememberWorkflowSettings();
      this.dispatchState = 'running';
      this.dispatchMessage = 'Ordering GitHub Actions to run evolve...';
      try {
        const response = await fetch(`https://api.github.com/repos/${repo}/actions/workflows/${WORKFLOW_FILE}/dispatches`, {
          method: 'POST',
          headers: {
            Accept: 'application/vnd.github+json',
            Authorization: `Bearer ${token}`,
            'X-GitHub-Api-Version': '2022-11-28',
          },
          body: JSON.stringify({ ref }),
        });
        if (response.status !== 204) {
          let detail = '';
          try {
            const payload = await response.json();
            detail = payload.message ? ': ' + payload.message : '';
          } catch (err) {
            detail = response.statusText ? ': ' + response.statusText : '';
          }
          throw new Error(`GitHub returned ${response.status}${detail}`);
        }
        this.dispatchState = 'success';
        this.dispatchMessage = `evolve workflow queued on ${ref}.`;
      } catch (err) {
        this.dispatchState = 'error';
        this.dispatchMessage = err.message || 'Workflow dispatch failed.';
      }
    },
    async copyCommands() {
      try {
        await navigator.clipboard.writeText(this.commandText);
        this.copyLabel = 'Copied';
      } catch (err) {
        this.copyLabel = 'Select text';
      }
      setTimeout(() => { this.copyLabel = 'Copy'; }, 1600);
    },
    downloadCommands() {
      const blob = new Blob([this.commandText], { type: 'text/plain' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'command.txt';
      a.click();
      URL.revokeObjectURL(a.href);
    },
    async loadStatus() {
      try {
        const response = await fetch('status.json?ts=' + Date.now(), { cache: 'no-store' });
        if (!response.ok) throw new Error('status fetch failed');
        this.status = await response.json();
        this.loaded = true;
        this.online = true;
        this.lastPoll = new Date().toISOString();
      } catch (err) {
        this.online = false;
        this.loaded = true;
      }
    },
  },

  mounted() {
    this.loadStatus();
    setInterval(this.loadStatus, POLL_MS);
  },

  template: `
    <div class="app-shell">
      <header class="topbar">
        <div class="topbar-inner">
          <div class="brand">
            <div class="brand-mark">EE</div>
            <div>
              <h1>E-Evolve</h1>
              <p>Self-improving earning bot dashboard</p>
            </div>
          </div>
          <div class="top-actions">
            <span class="live-chip"><span class="live-dot" :class="{ error: !online }"></span>{{ online ? 'live' : 'offline' }}</span>
            <a class="chip" href="status.json">status.json</a>
            <a class="chip" href="earnings-log.md">earnings log</a>
          </div>
        </div>
      </header>

      <main class="page" v-if="loaded">
        <section class="hero">
          <div class="hero-main">
            <p class="eyebrow">GitHub Actions automation</p>
            <h2>{{ money(earn.total_usd) }} earned, next move: {{ nextBestAction }}</h2>
            <p class="hero-copy">
              Current version {{ status.version || 'unknown' }} runs with {{ active.length }} active modules.
              Last cycle finished {{ ageLabel(status.last_run) }} in {{ status.last_cycle_seconds || 0 }} seconds.
            </p>
            <div class="hero-meta">
              <span v-for="feature in active" :key="feature" class="tag good">{{ moduleLabel(feature) }}</span>
              <span v-if="!active.length" class="tag bad">No active modules</span>
            </div>
          </div>
          <aside class="summary-panel">
            <div class="summary-row"><span>Last run</span><strong>{{ fmtDate(status.last_run) }}</strong></div>
            <div class="summary-row"><span>Provider</span><strong>{{ status.llm_provider || 'unknown' }}</strong></div>
            <div class="summary-row"><span>Cycle health</span><strong><span class="tag" :class="cycleHealth.cls">{{ cycleHealth.label }}</span></strong></div>
            <div class="summary-row"><span>Article quota</span><strong>{{ articleDaily.published }}/{{ articleDaily.limit }} today</strong></div>
            <div class="summary-row"><span>This week</span><strong>{{ money(earn.this_week_usd) }}</strong></div>
            <div class="summary-row"><span>Projection</span><strong>{{ weeklyProjection }}/week</strong></div>
          </aside>
        </section>

        <section class="metrics">
          <article class="metric-card"><div class="metric-label">Total earned</div><div class="metric-value good">{{ money(earn.total_usd) }}</div><div class="metric-note">Lifetime estimate</div></article>
          <article class="metric-card"><div class="metric-label">This week</div><div class="metric-value warn">{{ money(earn.this_week_usd) }}</div><div class="metric-note">Goal progress {{ weekGoalPercent }}%</div></article>
          <article class="metric-card"><div class="metric-label">Cycles</div><div class="metric-value">{{ compactNumber(status.total_runs) }}</div><div class="metric-note">Hourly runner history</div></article>
          <article class="metric-card"><div class="metric-label">Modules</div><div class="metric-value">{{ active.length }}/{{ active.length + inactive.length }}</div><div class="metric-note">{{ inactive.length }} waiting for setup</div></article>
        </section>

        <section class="cockpit">
          <section class="panel">
            <div class="panel-head"><div><h3>Revenue Pipeline</h3><p>Where the loop is ready, and where money can leak.</p></div><span class="tag" :class="cycleHealth.cls">{{ cycleHealth.label }}</span></div>
            <div class="panel-body pipeline">
              <article v-for="stage in revenueStages" :key="stage.key" class="pipeline-stage" :class="{ ready: stage.ready }">
                <span class="stage-dot" :class="stage.cls"></span>
                <div>
                  <strong>{{ stage.label }}</strong>
                  <p>{{ stage.detail }}</p>
                </div>
                <span class="tag" :class="stage.cls">{{ stage.readyCount }}/{{ stage.total }}</span>
              </article>
            </div>
          </section>

          <section class="panel">
            <div class="panel-head"><div><h3>Highest-Leverage Setup</h3><p>Ranked by likely earning impact for this bot.</p></div><span class="tag info">{{ baselineProjection }}/wk base</span></div>
            <div class="panel-body opportunity-list">
              <article v-for="item in opportunityItems" :key="item.name" class="opportunity-item">
                <div class="opportunity-score"><strong>{{ item.impact }}</strong><span>impact</span></div>
                <div>
                  <strong>{{ item.name }}</strong>
                  <p class="muted">{{ item.note }}</p>
                </div>
              </article>
              <p v-if="!opportunityItems.length" class="empty">No obvious setup gaps. Keep publishing and watch conversion data.</p>
            </div>
          </section>
        </section>

        <div class="layout">
          <div class="stack">
            <section class="panel">
              <div class="panel-head"><div><h3>Active Earning Loop</h3><p>Free-first setup, current module health, and today's publishing pace.</p></div><span class="tag good">$0 infrastructure</span></div>
              <div class="panel-body">
                <div class="active-grid">
                  <article v-for="mod in activeModules" :key="mod.name" class="active-module">
                    <span class="module-dot" :class="mod.role"></span>
                    <div>
                      <strong>{{ mod.label }}</strong>
                      <p>{{ mod.free ? 'Free/no-verification path' : 'Needs funded or approved access' }}</p>
                    </div>
                    <span class="tag" :class="mod.free ? 'good' : 'warn'">{{ mod.role }}</span>
                  </article>
                  <p v-if="!activeModules.length" class="empty">No active modules detected.</p>
                </div>
                <div class="quota-card">
                  <div class="quota-top"><strong>Daily article target</strong><span>{{ articleDaily.published }}/{{ articleDaily.limit }}</span></div>
                  <div class="bar"><div class="bar-fill" :style="{ width: articleProgress + '%' }"></div></div>
                  <p class="muted">Normal cycles stop after two successful article generations per UTC day. Use owner orders only for deliberate experiments.</p>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>AI Model Workflow</h3><p>Role-based model routing currently detected by the bot.</p></div></div>
              <div class="panel-body grid-3">
                <article v-for="flow in workflows" :key="flow.name" class="card">
                  <div class="card-top"><h4>{{ flow.name }}</h4><span class="tag" :class="flow.active ? 'good' : 'warn'">{{ flow.active ? 'ready' : 'missing' }}</span></div>
                  <p><strong>{{ flow.provider }}</strong></p>
                  <p class="code-pill">{{ flow.model }}</p>
                  <p>{{ flow.purpose }}</p>
                </article>
                <p v-if="!workflows.length" class="empty">No workflow data yet.</p>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Revenue Focus</h3><p>Next practical moves based on active modules and missing secrets.</p></div></div>
              <div class="panel-body focus-list">
                <article v-for="item in focusItems" :key="item.title" class="focus-item">
                  <span class="focus-rank">{{ item.rank }}</span>
                  <div><div class="row"><strong>{{ item.title }}</strong><span class="tag info">{{ item.action }}</span></div><p class="muted">{{ item.body }}</p></div>
                </article>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Earnings Analysis</h3><p>Breakdown and weekly goal progress.</p></div><span class="tag warn">{{ weekGoalPercent }}% of $10/wk</span></div>
              <div class="panel-body">
                <div class="bar"><div class="bar-fill" :style="{ width: weekGoalPercent + '%' }"></div></div>
                <div class="secret-list" style="margin-top:14px">
                  <div v-for="item in breakdown" :key="item.name" class="secret-item">
                    <strong>{{ item.name }}</strong>
                    <div class="bar"><div class="bar-fill" :style="{ width: item.percent + '%' }"></div></div>
                    <span>{{ money(item.value, 4) }}</span>
                  </div>
                  <p v-if="!breakdown.length" class="empty">No earnings breakdown yet.</p>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Last Evolution</h3><p>The latest code evolution result.</p></div><span class="tag" :class="evolution.error ? 'bad' : 'good'">{{ evolution.error ? 'needs review' : 'ok' }}</span></div>
              <div class="panel-body evo-list">
                <div class="evo-item">
                  <strong>{{ evolution.summary || 'No evolution summary yet.' }}</strong>
                  <p v-if="evolution.error" class="muted">{{ evolution.error }}</p>
                </div>
                <div v-for="change in evolution.changes_applied || []" :key="change.file + change.reason" class="evo-item">
                  <span class="code-pill">{{ change.file }}</span>
                  <p class="muted">{{ change.reason }}</p>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Last Cycle Actions</h3><p>Actions emitted by earning modules during the last cycle.</p></div></div>
              <div class="panel-body action-list">
                <article v-for="action in actions" :key="JSON.stringify(action)" class="action-item">
                  <div class="row"><strong>{{ action.platform || 'unknown' }}</strong><span class="tag" :class="action.success ? 'good' : 'bad'">{{ action.success ? 'success' : 'failed' }}</span></div>
                  <p class="muted">{{ action.title || action.topic || action.symbol || action.error || 'Action recorded' }}</p>
                </article>
                <p v-if="!actions.length" class="empty">No actions recorded in the latest cycle.</p>
              </div>
            </section>
          </div>

          <aside class="stack">
            <section class="panel">
              <div class="panel-head"><div><h3>Secret Readiness</h3><p>Values are detected, never shown.</p></div></div>
              <div class="panel-body secret-list">
                <div v-for="secret in secrets" :key="secret.name" class="secret-item">
                  <strong>{{ secret.label }}</strong>
                  <div class="bar"><div class="bar-fill" :style="{ width: secret.percent + '%' }"></div></div>
                  <span class="tag" :class="secret.active ? 'good' : 'warn'">{{ secret.present_count }}/{{ secret.required_count }}</span>
                  <code v-if="secret.missing && secret.missing.length" style="grid-column:1 / -1">{{ secret.missing.join(', ') }}</code>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Owner Orders</h3><p>Build command.txt for the next cycle.</p></div></div>
              <div class="panel-body">
                <div class="dispatch-card">
                  <div class="row"><strong>Run evolve now</strong><span class="tag info">workflow_dispatch</span></div>
                  <div class="field-grid">
                    <label class="field-label">Repository
                      <input class="cmd-input" v-model="githubRepo" placeholder="owner/repo" @change="rememberWorkflowSettings">
                    </label>
                    <label class="field-label">Ref
                      <input class="cmd-input" v-model="workflowRef" placeholder="main" @change="rememberWorkflowSettings">
                    </label>
                  </div>
                  <label class="field-label">GitHub token
                    <input class="cmd-input" type="password" v-model="githubToken" placeholder="Fine-grained token with Actions write" @change="rememberWorkflowSettings">
                  </label>
                  <div class="button-row">
                    <button class="small-btn primary" :disabled="!canDispatchWorkflow" @click="runWorkflow">{{ dispatchState === 'running' ? 'Ordering...' : 'Run evolve' }}</button>
                    <a class="small-btn" :href="'https://github.com/' + githubRepo + '/actions/workflows/evolve.yml'" target="_blank" rel="noopener">Open Actions</a>
                  </div>
                  <p class="status-line" :class="dispatchStatusClass">{{ dispatchMessage || 'Token stays in this browser local storage, never in status.json.' }}</p>
                </div>
                <div class="segmented">
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'earn' }" @click="activeCommandGroup = 'earn'">Earn</button>
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'protect' }" @click="activeCommandGroup = 'protect'">Protect</button>
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'funded' }" @click="activeCommandGroup = 'funded'">Funded</button>
                  <button class="segment-btn" :class="{ active: activeCommandGroup === 'admin' }" @click="activeCommandGroup = 'admin'">Admin</button>
                </div>
                <div class="preset-grid">
                  <button v-for="preset in activePresets" :key="preset[0]" class="preset-btn" @click="addCommand(preset[0])">
                    <strong>{{ preset[0] }}</strong><span>{{ preset[1] }}</span>
                  </button>
                </div>
                <div class="cmd-row">
                  <input class="cmd-input" v-model="customCommand" @keyup.enter="addCustomCommand" placeholder="Custom order">
                  <button class="small-btn" @click="addCustomCommand">Add</button>
                </div>
                <textarea class="command-area" v-model="commandText"></textarea>
                <div class="button-row">
                  <button class="small-btn primary" @click="copyCommands">{{ copyLabel }}</button>
                  <button class="small-btn" @click="downloadCommands">Download</button>
                  <button class="small-btn danger" @click="clearCommands">Clear</button>
                </div>
              </div>
            </section>

            <section class="panel">
              <div class="panel-head"><div><h3>Growth Suggestions</h3><p>Bot-proposed setup ideas.</p></div></div>
              <div class="panel-body action-list">
                <article v-for="item in suggestions" :key="item.title" class="action-item">
                  <div class="row"><strong>{{ item.title }}</strong><span class="tag" :class="item.free_tier ? 'good' : 'warn'">{{ item.free_tier ? 'free' : 'paid' }}</span></div>
                  <p class="muted">{{ item.description }}</p>
                  <span v-if="item.secret_needed" class="code-pill">{{ item.secret_needed }}</span>
                </article>
                <p v-if="!suggestions.length" class="empty">No suggestions yet.</p>
              </div>
            </section>
          </aside>
        </div>

        <footer class="footer">
          <span>Updated {{ lastPoll ? fmtDate(lastPoll) : 'not yet' }}</span>
          <span>GitHub Pages static Vue dashboard</span>
        </footer>
      </main>
    </div>
  `,
}).mount('#app');
