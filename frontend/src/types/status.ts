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

/** One recurring-revenue model that survived the constraint matrix. */
export type MrrIdea = {
	name?: string;
	why_this_stack_fits?: string;
	narrow_niche?: string;
	first_proof_artifact?: string;
	who_pays?: string;
	monthly_price_usd?: string;
	runway_to_first_dollar?: string;
	owner_must_do_by_hand?: string;
};

/** A model the triage kept, before the LLM brief expands on it. */
export type MrrViableModel = {
	name?: string;
	mrr_model?: string;
	source_note?: string;
	bot_role?: string;
	score?: number;
	manual_steps?: string[];
};

/** A model this stack cannot support, with the reason. */
export type MrrRefusedModel = {
	name?: string;
	mrr_model?: string;
	reason?: string;
};

export type MrrIdeas = {
	enabled?: boolean;
	last_refresh_at?: string;
	refresh_hours?: number;
	constraints?: string[];
	summary?: string;
	ranked_ideas?: MrrIdea[];
	validation_steps?: string[];
	owner_actions?: string[];
	viable?: MrrViableModel[];
	refused?: MrrRefusedModel[];
	llm_used?: boolean;
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
	/**
	 * Whether the reader-to-wallet path is live, and if not, why. Masked
	 * address only — this is the diagnostic, not the ask.
	 */
	payout?: {
		enabled?: boolean;
		live?: boolean;
		network?: string | null;
		address_masked?: string | null;
		blocked_reason?: string | null;
	};
	/**
	 * The tip box. Present only when the same address is already being
	 * published in every article footer, and carries the address in FULL —
	 * a masked address renders a tip box nobody can pay.
	 */
	payout_public?: {
		address?: string;
		network?: string;
		heading?: string;
		note?: string;
		asset?: string;
	};
	/**
	 * Publishing context captured when on-chain money arrived. Correlated,
	 * never proof: a TRC-20 transfer carries no memo.
	 */
	attribution?: {
		receipts?: Array<{
			at?: string;
			amount_usd?: number;
			network?: string | null;
			confidence?: string;
			context?: {
				posts_live?: number;
				total_views?: number;
				best_title?: string | null;
				best_url?: string | null;
				best_views?: number;
				winning_tags?: string[];
				best_archetype?: string | null;
				footer_network?: string | null;
			};
		}>;
		receipt_count?: number;
		total_attributed_usd?: number;
		last_receipt_at?: string | null;
		by_archetype?: Array<{ archetype?: string; count?: number; usd?: number }>;
		by_tag?: Array<{ tag?: string; count?: number; usd?: number }>;
		note?: string;
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
	mrr_ideas?: MrrIdeas;

	/** New keys the bot adds over time land here and surface in the Data explorer. */
	[key: string]: unknown;
};
