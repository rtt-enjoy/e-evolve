import { useEffect, useState } from 'react';

export type Route = { section: string; detail: string | null };

/** `#/leads/3` -> { section: 'leads', detail: '3' } */
export function parseHash(hash: string): Route {
	const parts = hash.replace(/^#\/?/, '').split('/').filter(Boolean);
	return { section: parts[0] || 'overview', detail: parts[1] ? decodeURIComponent(parts[1]) : null };
}

export function toHash(section: string, detail?: string | null): string {
	return detail ? `#/${section}/${encodeURIComponent(detail)}` : `#/${section}`;
}

export function navigate(section: string, detail?: string | null): void {
	const next = toHash(section, detail);
	if (window.location.hash !== next) window.location.hash = next;
}

export function useRoute(): Route {
	const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash));

	useEffect(() => {
		function onChange() {
			setRoute(parseHash(window.location.hash));
		}
		window.addEventListener('hashchange', onChange);
		return () => window.removeEventListener('hashchange', onChange);
	}, []);

	return route;
}
