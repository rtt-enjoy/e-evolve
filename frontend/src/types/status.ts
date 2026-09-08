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

/** How a lead's price was established. `none` means nobody published one. */
export type LeadValueBasis = 'posted_salary' | 'stated_rate' | 'none';

/**
 * `channel` = a place the product gets listed and paid for. `asset` = free
 * tooling or reach to build and market it with.
 *
 * These replaced `demand`/`supply`. That pair described a freelance queue:
 * `demand` meant somebody is hiring, which is not passive income -- income per
 * unit of the owner's work is a job. The old names are still accepted because
 * `status.json` is committed and a snapshot written before the rename carries
 * them.
 */
export type LeadKind = 'channel' | 'asset' | 'demand' | 'supply';

export type CodeTechOpportunity = {
	title?: string;
	url?: string;
	source?: string;
	/** Who is paying, when the source names them. Rarely set for a channel. */
	buyer?: string;
	kind?: LeadKind;
	score?: number;
	score_parts?: Record<string, number>;
	/**
	 * null when no price was published -- never 0. A zero sums into totals and
	 * sorts as the cheapest lead; null forces the UI to render an em dash.
	 */
	value_usd?: number | null;
	value_basis?: LeadValueBasis;
	value_note?: string;
	/** When the market posted it, vs when this bot saw it. */
	posted_at?: string | null;
	discovered_at?: string;
	age_hours?: number | null;
	reason?: string;
	next_step?: string;
	codex_prompt?: string;
	/**
	 * What the owner pays to use this channel. Unlike `value_usd`, `0` is
	 * meaningful here and means free to list -- so this renders as "Free",
	 * never as an em dash. null means no cost was published.
	 */
	cost_usd?: number | null;
	/** The one-time step the owner must do by hand. Empty means none. */
	manual_setup?: string;
	/** When and where this row's terms were last checked by hand. */
	verified_note?: string;
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

/** What the current demand leads have in common, and what to sell into it. */
export type MarketTheme = {
	theme?: string;
	evidence?: string;
	offer?: string;
};

export type OnlineAiBrief = {
	summary?: string;
	market_themes?: MarketTheme[];
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
	/** Counts describe the leads in this snapshot, not the full ranked list. */
	channel_count?: number;
	asset_count?: number;
	/** Rows needing a one-time signup or fee before they can earn anything. */
	needs_setup_count?: number;
	/** Pre-rename aliases; still written so an older build reads something true. */
	demand_count?: number;
	supply_count?: number;
	priced_count?: number;
	/** How many leads ranked in total; the rest are in the markdown report. */
	ranked_total?: number;
	requirements?: string[];
	focus?: string[];
	free_ai_focus?: string[];
	strategy_playbook?: string[];
	avoid_patterns?: string[];
	monetization_patterns?: string[];
	product_shapes?: string[];
	/** Platforms refused, and why -- so a dead one cannot return to the page. */
	refused_channels?: { name?: string; why?: string }[];
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
	 * What a reader actually sees on the published posts, read back through
	 * the unauthenticated dev.to API. Every other field here is written by the
	 * code whose work it reports — `backfill.remaining` read 0 for fourteen
	 * cycles while no post on the account carried an ask. This one looked.
	 *
	 * `agrees_with_backfill: false` means a self-reported field is wrong, and
	 * the observation is the half to believe.
	 */
	receipt_check?: {
		/** Posts read this cycle. A sample size, capped by max_per_cycle — not coverage. */
		checked?: number;
		with_footer?: number;
		/** Missing an ask *within this cycle's sample*. Use known_without_footer for the catalogue. */
		without_footer?: number;
		unreachable?: number;
		/** Published posts with a fresh observation on record. */
		covered?: number;
		published_total?: number;
		unverified?: number;
		coverage_complete?: boolean | null;
		/**
		 * Posts observed to carry no ask, whether or not they were in this
		 * cycle's sample. A gap must not disappear because the rotation moved
		 * on — that would erase the finding with the mechanism that found it.
		 */
		known_without_footer?: number;
		oldest_check_age_hours?: number | null;
		verified_ids?: Array<{ id?: number; at?: string; ok?: boolean }>;
		missing?: Array<{
			id?: number;
			title?: string;
			views?: number;
			url?: string;
		}>;
		last_run?: string | null;
		last_reason?: string | null;
		agrees_with_backfill?: boolean | null;
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
