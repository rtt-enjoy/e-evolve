import type { Suggestion } from '../types/status';

const AVOIDED_SECRET_PREFIXES = ['ANTHROPIC', 'BINANCE', 'TWITTER', 'ETH_', 'NFT_'];

const AVOIDED_TERMS = [
	'binance',
	'anthropic',
	'claude',
	'twitter',
	'crypto',
	'nft',
	'ethereum',
	'premium',
	'phone verification',
	'identity verification',
	'kyc',
];

function parseSecrets(value?: string | null): string[] {
	if (!value) return [];
	return value
		.split(/[,/+\s]+/)
		.map((part) => part.trim())
		.filter((part) => /^[A-Z0-9_]{4,}$/.test(part));
}

/**
 * Suggestions requiring paid tiers, funded wallets, or identity checks are out
 * of policy for this bot, so they never reach the dashboard.
 */
export function isAvoidedSuggestion(suggestion: Suggestion): boolean {
	if (suggestion.free_tier === false) return true;
	const secrets = parseSecrets(suggestion.secret_needed);
	if (secrets.some((secret) => AVOIDED_SECRET_PREFIXES.some((prefix) => secret.startsWith(prefix)))) return true;
	const haystack = `${suggestion.title || ''} ${suggestion.description || ''}`.toLowerCase();
	return AVOIDED_TERMS.some((term) => haystack.includes(term));
}

/**
 * One suggestion as text that can be pasted straight into a prompt box.
 * Only fields the bot actually wrote are included; nothing is invented.
 */
export function suggestionPrompt(suggestion: Suggestion): string {
	const lines = [`Work on this suggestion: ${suggestion.title || 'Untitled suggestion'}`];
	if (suggestion.description) lines.push('', suggestion.description);
	if (suggestion.owner_action) lines.push('', `Owner action: ${suggestion.owner_action}`);
	if ((suggestion.how_to || []).length) lines.push('', 'Steps:', ...(suggestion.how_to || []).map((step) => `- ${step}`));
	return lines.join('\n');
}
