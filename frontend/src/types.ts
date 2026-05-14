export type Action = {
  platform?: string;
  success?: boolean;
  title?: string;
  topic?: string;
  symbol?: string;
  error?: string;
  estimated_usd?: number;
  value_usd?: number;
};

export type Suggestion = {
  title?: string;
  description?: string;
  secret_needed?: string;
  free_tier?: boolean;
  how_to?: string[];
};

export type Status = {
  version?: string;
  last_run?: string;
  total_runs?: number;
  active_features?: string[];
  inactive_features?: string[];
  llm_provider?: string;
  llm_roles?: Record<string, string>;
  configured_github_secrets?: string[];
  secret_readiness?: Record<string, {
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
};
