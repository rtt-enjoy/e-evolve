import { Check, Copy } from 'lucide-react';
import { useState } from 'react';

export function CopyButton({ text, label = 'Copy' }: { text: string; label?: string }) {
	const [copied, setCopied] = useState(false);

	async function copy() {
		try {
			await navigator.clipboard.writeText(text);
			setCopied(true);
			window.setTimeout(() => setCopied(false), 1600);
		} catch {
			setCopied(false);
		}
	}

	return (
		<button className="btn" type="button" onClick={copy} disabled={!text}>
			{copied ? <Check size={15} /> : <Copy size={15} />}
			{copied ? 'copied' : label}
		</button>
	);
}
