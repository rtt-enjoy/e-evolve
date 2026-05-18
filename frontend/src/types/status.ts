export type Action = {
  platform?: string;
  success?: boolean;
  title?: string;
  topic?: string;
  symbol?: string;
  error?: string;
  url?: string;
  estimated_usd?: number;
  value_usd?: number;
  withdrawn_usd?: number;
  tx_id?: string | null;
};

export type Suggestion = {
  title?: string;
  description?: string;
  secret_needed?: string;
  free_tier?: boolean;
  estimated_weekly_usd?: number;
  how_to?: string[];
};

export type CodeTechOpportunity = {
  title?: string;
  url?: string;
  source?: string;
  score?: number;
  estimated_value_usd?: number;
  reason?: string;
  next_step?: string;
};

export type CodeTechEarning = {
  enabled?: boolean;
  last_refresh_at?: string;
  daily_target_usd?: number;
  refresh_hours?: number;
  opportunities?: CodeTechOpportunity[];
  requirements?: string[];
  focus?: string[];
  strategy_playbook?: string[];
  avoid_patterns?: string[];
};

export type Status = {
  version?: string;
  last_run?: string;
  total_runs?: number;
  active_features?: string[];
  inactive_features?: string[];
  llm_provider?: string;
  operation_mode?: string;
  external_action_policy?: {
    mode?: string;
    allowed?: string[];
    blocked?: string[];
  };
  llm_roles?: Record<string, string>;
  configured_github_secrets?: string[];
  secret_readiness?: Record<string, {
    active?: boolean;
    present_count?: number;
    required_count?: number;
    missing?: string[];
    present?: string[];
  }>;
  earnings?: {
    total_usd?: number;
    this_week_usd?: number;
    last_cycle_usd?: number;
    breakdown?: Record<string, number>;
    history?: number[];
  };
  last_evolution?: {
    summary?: string;
    changes_applied?: Array<{ file?: string; reason?: string }>;
    suggestions?: Suggestion[];
    error?: string | null;
    error_type?: string;
  };
  last_earning?: {
    actions?: Action[];
    total_usd?: number;
  };
  suggestions?: Suggestion[];
  errors?: string[];
  last_cycle_seconds?: number;
  github_repo?: string;
  usdt_balance?: number;
  last_payout_total_usd?: number;
  last_payout_tx?: string | null;
  llm_workflows?: Record<string, {
    provider?: string;
    model?: string;
    purpose?: string;
    active?: boolean;
    secret?: string;
  }>;
  article_daily?: {
    date?: string;
    published?: number;
  };
  code_tech_earning?: CodeTechEarning;
};
