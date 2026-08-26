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
	codex_prompt?: string;
	outreach_draft?: string;
	pursued?: boolean;
	archived_at?: string | null;
};

export type FreeAiService = {
	name?: string;
	what_it_does?: string;
	free_tier?: string;
	credit_card_required?: string;
	earn_with_it?: string;
	price_guide?: string;
};

export type EarningIdea = {
	idea?: string;
	who_pays?: string;
	deliverable?: string;
	price_usd?: string;
	time_to_first_dollar?: string;
	free_stack?: string;
};

export type OnlineAiBrief = {
	summary?: string;
	free_ai_services?: FreeAiService[];
	easy_earning_ideas?: EarningIdea[];
	owner_actions?: string[];
};

export type ReferenceSource = {
	title?: string;
	url?: string;
	takeaway?: string;
};

export type CodeTechEarning = {
	enabled?: boolean;
	last_refresh_at?: string;
	daily_target_usd?: number;
	refresh_hours?: number;
	opportunities?: CodeTechOpportunity[];
	requirements?: string[];
	focus?: string[];
	free_ai_focus?: string[];
	strategy_playbook?: string[];
	avoid_patterns?: string[];
	monetization_patterns?: string[];
	remote_service_niches?: string[];
	reference_sources?: ReferenceSource[];
	online_ai_brief?: OnlineAiBrief;
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
		/** Live on-chain USDT balance of the receive wallet. Real money. */
		confirmed_usd?: number;
		/** Lifetime sum of observed balance increases. Survives manual withdrawals. */
		received_total_usd?: number;
		/** Increase observed during the last cycle. */
		last_received_usd?: number;
		source?: string;
		/** Activity value, NOT revenue: publishing reach, no payment attached. */
		total_usd?: number;
		this_week_usd?: number;
		last_cycle_usd?: number;
		week_started?: string;
		breakdown?: Record<string, number>;
		/** Trend spark of real wallet receipts. */
		history?: number[];
	};
	wallet?: {
		configured?: boolean;
		address_masked?: string | null;
		network?: string | null;
		confirmed_usd?: number;
		received_total_usd?: number;
		last_received_usd?: number;
		last_received_at?: string | null;
		checked_at?: string | null;
		stale?: boolean;
		error?: string | null;
	};
	last_evolution?: {
		summary?: string;
		changes_applied?: Array<{ file?: string; reason?: string }>;
		suggestions?: Suggestion[];
		error?: string | null;
		error_type?: string;
		version_bumped_to?: string;
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

	/** New keys the bot adds over time land here and surface in the Data explorer. */
	[key: string]: unknown;
};
