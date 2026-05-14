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

const PHASES = [
  { key: 'status', label: 'Status', detail: 'Loads status.json, counts the cycle, and detects secrets.' },
  { key: 'commands', label: 'Commands', detail: 'Applies owner orders from command.txt or labelled GitHub Issues.' },
  { key: 'evolution', label: 'Evolution', detail: 'Plans and applies up to three safe code changes.' },
  { key: 'earning', label: 'Earning', detail: 'Runs enabled earning modules and records actions.' },
  { key: 'update', label: 'Update', detail: 'Saves status, dashboard, logs, and commits cycle state.' },
];

const LOGIC_NODES = [
  { key: 'secrets', title: 'Secrets activate modules', body: 'GitHub Actions secrets are read as environment variables. Present secret groups become active_features.' },
  { key: 'commands', title: 'Owner orders steer one cycle', body: 'Commands are parsed into runtime overrides and removed before status is persisted.' },
  { key: 'evolution', title: 'Evolution changes source', body: 'The LLM receives status and code context, then returns complete file contents within safety limits.' },
  { key: 'earnings', title: 'Earning modules emit actions', body: 'Each module returns success or failure records that feed earnings, errors, and dashboard diagnostics.' },
  { key: 'dashboard', title: 'Dashboard mirrors status.json', body: 'GitHub Pages polls the public status snapshot and updates panels without a page reload.' },
];

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
      previousStatus: null,
      changePulses: [],
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
    phaseRows() {
      return PHASES.map((phase) => this.phaseState(phase));
    },
    logicNodes() {
      return LOGIC_NODES.map((node) => ({
        ...node,
        state: this.logicState(node.key),
      }));
    },
    configuredSecrets() {
      return (this.status.configured_github_secrets || [])
        .slice()
        .sort()
        .map((name) => ({
          name,
          label: name.replace(/_API_KEY|_TOKEN|_SECRET|_ADDRESS/g, '').replace(/_/g, ' '),
        }));
    },
    failedActions() {
      return this.actions.filter((action) => action && action.success === false);
    },
    problemItems() {
      const items = [];
      if (this.cycleHealth.cls !== 'good') {
        items.push({
          key: 'cycle-age',
          title: 'Workflow cycle is ' + this.cycleHealth.label,
          detail: 'The last status update was ' + this.ageLabel(this.status.last_run) + '. Check GitHub Actions if this is unexpected.',
          cls: this.cycleHealth.cls,
          fix: 'Open Actions or run status report',
        });
      }
      (this.status.errors || []).slice(-6).forEach((error, index) => {
        items.push({
          key: 'error-' + index + '-' + error,
          title: 'Cycle error',
          detail: String(error),
          cls: 'bad',
          fix: 'Read the failing phase and rerun after correcting setup',
        });
      });
      if (this.evolution.error) {
        items.push({
          key: 'evolution-error',
          title: this.evolutionErrorLabel,
          detail: this.evolution.error,
          cls: this.evolutionStatus.cls,
          fix: this.evolution.error_type === 'free_limit' ? 'Wait for quota or add another LLM key' : 'Review last evolution output',
        });
      }
      this.failedActions.slice(0, 5).forEach((action, index) => {
        items.push({
          key: 'failed-action-' + index,
          title: (action.platform || 'module') + ' action failed',
          detail: action.error || action.title || action.topic || 'The module returned a failed action.',
          cls: 'bad',
          fix: 'Check module secrets, quota, and external API access',
        });
      });
      this.opportunityItems.slice(0, 3).forEach((item) => {
        items.push({
          key: 'setup-' + item.name,
          title: 'Setup gap: ' + item.name,
          detail: item.note,
          cls: 'warn',
          fix: 'Add the secret or decide to keep that module disabled',
        });
      });
      if (!items.length) {
        items.push({
          key: 'healthy',
          title: 'No current blockers detected',
          detail: 'The last public status snapshot has no errors, failed actions, or high-priority missing setup.',
          cls: 'good',
          fix: 'Watch the next cycle',
        });
      }
      return items;
    },
    evolutionSuggestions() {
      const byTitle = new Map();
      [...(this.evolution.suggestions || []), ...this.suggestions].forEach((item) => {
        if (item && item.title && !byTitle.has(item.title)) byTitle.set(item.title, item);
      });
      return Array.from(byTitle.values()).slice(0, 6);
    },
    suggestions() {
      return this.status.suggestions || [];
    },
    actions() {
      return (this.status.last_earning && this.status.last_earning.actions) || [];
    },
    evolutionStatus() {
      const evo = this.evolution || {};
      if (evo.error_type === 'free_limit') {
        return { label: 'free limit', cls: 'warn' };
      }
      if (evo.error) {
        return { label: 'needs review', cls: 'bad' };
      }
      return { label: 'ok', cls: 'good' };
    },
    evolutionErrorLabel() {
      const labels = {
        free_limit: 'Free-tier API limit reached',
        '413': 'Prompt too large',
        json: 'JSON parse error',
        api: 'API error',
      };
      return labels[(this.evolution || {}).error_type] || 'Evolution error';
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
    phaseState(phase) {
      if (phase.key === 'status') {
        return { ...phase, cls: this.cycleHealth.cls, statusLabel: this.cycleHealth.label, meta: this.fmtDate(this.status.last_run) };
      }
      if (phase.key === 'commands') {
        const hadCommands = Boolean((this.status.last_commands || []).length || (this.status.command_history || []).length);
        return { ...phase, cls: hadCommands ? 'info' : 'good', statusLabel: hadCommands ? 'orders applied' : 'standing by', meta: hadCommands ? 'owner override detected' : 'no pending public orders' };
      }
      if (phase.key === 'evolution') {
        return { ...phase, cls: this.evolutionStatus.cls, statusLabel: this.evolutionStatus.label, meta: this.evolution.summary || 'no summary yet' };
      }
      if (phase.key === 'earning') {
        if (this.failedActions.length) return { ...phase, cls: 'bad', statusLabel: this.failedActions.length + ' failed', meta: this.failedActions[0].error || 'module failure' };
        if (this.actions.length) return { ...phase, cls: 'good', statusLabel: this.actions.length + ' actions', meta: money(this.earn.last_cycle_usd || 0, 4) + ' last cycle' };
        return { ...phase, cls: 'warn', statusLabel: 'no actions', meta: 'modules may be inactive, capped, or waiting for setup' };
      }
      return { ...phase, cls: (this.status.errors || []).length ? 'bad' : 'good', statusLabel: (this.status.errors || []).length ? 'saved with errors' : 'saved', meta: 'dashboard polls status.json every minute' };
    },
    logicState(key) {
      if (key === 'secrets') return this.configuredSecrets.length ? 'good' : 'warn';
      if (key === 'commands') return this.commands.length ? 'info' : 'good';
      if (key === 'evolution') return this.evolutionStatus.cls;
      if (key === 'earnings') return this.failedActions.length ? 'bad' : (this.actions.length ? 'good' : 'warn');
      return this.online ? 'good' : 'bad';
    },
    summarizeStatusChanges(previous, next) {
      const pulses = [];
      if (!previous || !next) return pulses;
      const prevSecrets = new Set(previous.configured_github_secrets || []);
      const nextSecrets = new Set(next.configured_github_secrets || []);
      Array.from(nextSecrets).filter((name) => !prevSecrets.has(name)).sort().forEach((name) => {
        pulses.push({ kind: 'secret', cls: 'good', title: 'New secret detected', detail: name });
      });
      const prevEvo = previous.last_evolution || {};
      const nextEvo = next.last_evolution || {};
      const prevEvoKey = JSON.stringify([prevEvo.summary, prevEvo.version_bumped_to, prevEvo.error, prevEvo.changes_applied]);
      const nextEvoKey = JSON.stringify([nextEvo.summary, nextEvo.version_bumped_to, nextEvo.error, nextEvo.changes_applied]);
      if (prevEvoKey !== nextEvoKey) {
        pulses.push({
          kind: 'evolution',
          cls: nextEvo.error ? 'bad' : 'info',
          title: nextEvo.error ? 'Evolution needs review' : 'Evolution updated',
          detail: nextEvo.summary || 'New evolution result received',
        });
      }
      const prevErrors = (previous.errors || []).join('\n');
      const nextErrors = (next.errors || []).join('\n');
      if (prevErrors !== nextErrors) {
        pulses.push({
          kind: 'errors',
          cls: (next.errors || []).length ? 'bad' : 'good',
          title: (next.errors || []).length ? 'Errors changed' : 'Errors cleared',
          detail: (next.errors || []).slice(-1)[0] || 'No errors in the latest snapshot',
        });
      }
      if ((previous.total_runs || 0) !== (next.total_runs || 0)) {
        pulses.push({
          kind: 'cycle',
          cls: 'info',
          title: 'New cycle snapshot',
          detail: 'Cycle #' + (next.total_runs || 0) + ' finished in ' + (next.last_cycle_seconds || 0) + 's',
        });
      }
      return pulses;
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
        const nextStatus = await response.json();
        const previous = this.loaded ? this.status : null;
        const pulses = this.summarizeStatusChanges(previous, nextStatus);
        if (pulses.length) {
          const stamped = pulses.map((pulse) => ({ ...pulse, at: new Date().toISOString() }));
          this.changePulses = [...stamped, ...this.changePulses].slice(0, 8);
        }
        this.previousStatus = previous;
        this.status = nextStatus;
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

        <section class="ops-grid">
          <section class="panel">
            <div class="panel-head"><div><h3>Workflow Status</h3><p>Current phase health from the latest public status snapshot.</p></div><span class="tag" :class="cycleHealth.cls">{{ ageLabel(status.last_run) }}</span></div>
            <div class="panel-body phase-list">
              <article v-for="phase in phaseRows" :key="phase.key" class="phase-item">
                <span class="phase-index" :class="phase.cls">{{ phase.statusLabel }}</span>
                <div>
                  <strong>{{ phase.label }} · {{ phase.detail }}</strong>
                  <p class="muted">{{ phase.meta }}</p>
                </div>
              </article>
            </div>
          </section>

          <section class="panel">
            <div class="panel-head"><div><h3>Live Change Pulse</h3><p>New cycles, evolutions, errors, and secrets appear here after polling.</p></div><span class="tag info">60s poll</span></div>
            <div class="panel-body pulse-list">
              <article v-for="pulse in changePulses" :key="pulse.at + pulse.title + pulse.detail" class="pulse-item">
                <span class="tag" :class="pulse.cls">{{ pulse.kind }}</span>
                <div><strong>{{ pulse.title }}</strong><p class="muted">{{ pulse.detail }}</p></div>
                <time>{{ ageLabel(pulse.at) }}</time>
              </article>
              <p v-if="!changePulses.length" class="empty">Waiting for the next status change.</p>
            </div>
          </section>
        </section>

        <section class="panel project-map">
          <div class="panel-head"><div><h3>Project Logic Map</h3><p>How this repo turns secrets and owner orders into evolution, earning actions, and dashboard state.</p></div></div>
          <div class="panel-body logic-grid">
            <article v-for="node in logicNodes" :key="node.key" class="logic-node">
              <span class="stage-dot" :class="node.state"></span>
              <strong>{{ node.title }}</strong>
              <p class="muted">{{ node.body }}</p>
            </article>
          </div>
        </section>

        <section class="panel problem-board">
          <div class="panel-head"><div><h3>Problems And Corrections</h3><p>Errors, failed actions, stale workflow signals, and the most useful setup suggestions.</p></div><span class="tag" :class="problemItems[0] ? problemItems[0].cls : 'good'">{{ problemItems.length }} items</span></div>
          <div class="panel-body problem-list">
            <article v-for="item in problemItems" :key="item.key" class="problem-item">
              <span class="tag" :class="item.cls">{{ item.cls }}</span>
              <div><strong>{{ item.title }}</strong><p class="muted">{{ item.detail }}</p></div>
              <code>{{ item.fix }}</code>
            </article>
          </div>
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
              <div class="panel-head"><div><h3>Last Evolution</h3><p>The latest code evolution result.</p></div><span class="tag" :class="evolutionStatus.cls">{{ evolutionStatus.label }}</span></div>
              <div class="panel-body evo-list">
                <div class="evo-item">
                  <strong>{{ evolution.summary || 'No evolution summary yet.' }}</strong>
                  <p v-if="evolution.error" class="muted"><strong>{{ evolutionErrorLabel }}:</strong> {{ evolution.error }}</p>
                </div>
                <div v-for="change in evolution.changes_applied || []" :key="change.file + change.reason" class="evo-item">
                  <span class="code-pill">{{ change.file }}</span>
                  <p class="muted">{{ change.reason }}</p>
                </div>
                <div v-if="evolutionSuggestions.length" class="evo-item">
                  <strong>Evolution suggestions</strong>
                  <div class="suggestion-stack">
                    <article v-for="item in evolutionSuggestions" :key="item.title" class="suggestion-mini">
                      <div class="row"><strong>{{ item.title }}</strong><span v-if="item.secret_needed" class="tag info">{{ item.secret_needed }}</span></div>
                      <p class="muted">{{ item.description }}</p>
                      <ol v-if="item.how_to && item.how_to.length">
                        <li v-for="step in item.how_to" :key="step">{{ step }}</li>
                      </ol>
                    </article>
                  </div>
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
                <div class="configured-strip" v-if="configuredSecrets.length">
                  <span v-for="secret in configuredSecrets" :key="secret.name" class="tag good" :title="secret.name">{{ secret.label }}</span>
                </div>
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
