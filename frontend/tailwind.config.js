/**
 * Colours are read from CSS custom properties (see src/styles/styles.css), so
 * the dark and light themes share one palette. Each variable holds an RGB
 * triplet, which is what lets Tailwind's opacity modifiers (`bg-accent/10`)
 * keep working.
 *
 * @type {import('tailwindcss').Config}
 */
const token = (name) => `rgb(var(--c-${name}) / <alpha-value>)`;

export default {
	content: ['./index.html', './src/**/*.{ts,tsx}'],
	theme: {
		extend: {
			colors: {
				ink: token('bg'),
				panel: token('surface'),
				panel2: token('surface-2'),
				panel3: token('surface-3'),
				line: token('border'),
				soft: token('muted'),
				faint: token('faint'),
				text: token('text'),
				accent: token('accent'),
				green: token('good'),
				red: token('bad'),
				yellow: token('warn'),
				cyan: token('info'),
			},
			fontFamily: {
				sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
				mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
			},
			boxShadow: {
				// Per-theme: a heavy black drop shadow reads as dirt on a light page.
				panel: 'var(--shadow-card)',
				glow: '0 0 0 1px rgb(var(--c-accent) / .35), 0 8px 30px -8px rgb(var(--c-accent) / .45)',
			},
		},
	},
	plugins: [],
};
