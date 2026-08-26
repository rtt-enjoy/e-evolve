import { AlertTriangle, ArrowRight, CheckCircle2, ChevronRight, XCircle } from 'lucide-react';
import type { ReactNode } from 'react';
import { useState } from 'react';

export type Tone = 'good' | 'warn' | 'bad' | 'info' | 'neutral';

/* ---------------------------------------------------------------- containers */

export function Card({
	title,
	hint,
	action,
	children,
	className = '',
}: {
	title?: string;
	hint?: string;
	action?: ReactNode;
	children: ReactNode;
	className?: string;
}) {
	return (
		<section className={`card ${className}`}>
			{title ? (
				<header className="card-head">
					<div className="min-w-0">
						<h2>{title}</h2>
						{hint ? <p>{hint}</p> : null}
					</div>
					{action}
				</header>
			) : null}
			{children}
		</section>
	);
}

/** Collapsed by default — the mechanism for "show more only if interested". */
export function Disclosure({
	title,
	hint,
	count,
	defaultOpen = false,
	children,
}: {
	title: string;
	hint?: string;
	count?: number | null;
	defaultOpen?: boolean;
	children: ReactNode;
}) {
	const [open, setOpen] = useState(defaultOpen);
	return (
		<section className={`disclosure ${open ? 'open' : ''}`}>
			<button type="button" onClick={() => setOpen(!open)} aria-expanded={open}>
				<ChevronRight className="chevron" size={16} />
				<span className="min-w-0">
					<strong>{title}</strong>
					{hint ? <em>{hint}</em> : null}
				</span>
				{typeof count === 'number' ? <span className="count">{count}</span> : null}
			</button>
			{open ? <div className="disclosure-body">{children}</div> : null}
		</section>
	);
}

export function SectionHead({ title, blurb, action }: { title: string; blurb: string; action?: ReactNode }) {
	return (
		<header className="section-head">
			<div className="min-w-0">
				<h1>{title}</h1>
				<p>{blurb}</p>
			</div>
			{action}
		</header>
	);
}

export function Subhead({ children, action }: { children: ReactNode; action?: ReactNode }) {
	return (
		<div className="subhead">
			<h3>{children}</h3>
			{action}
		</div>
	);
}

/* ------------------------------------------------------------------- metrics */

/** Hero number. `to` turns the whole tile into a link to its detail section. */
export function Tile({
	label,
	value,
	detail,
	tone = 'neutral',
	spark,
	to,
}: {
	label: string;
	value: string;
	detail?: string;
	tone?: Tone;
	spark?: number[];
	to?: string;
}) {
	const body = (
		<>
			<span className="tile-label">{label}</span>
			<strong className={`tile-value ${tone}`}>{value}</strong>
			{spark && spark.length > 1 ? <Sparkline values={spark} tone={tone} /> : null}
			{detail ? <p className="tile-detail">{detail}</p> : null}
			{to ? <ArrowRight className="tile-arrow" size={15} /> : null}
		</>
	);
	return to ? <a className="tile is-link" href={to}>{body}</a> : <article className="tile">{body}</article>;
}

export function Stat({ label, value, detail }: { label: string; value: string; detail?: string }) {
	return (
		<div className="stat">
			<span>{label}</span>
			<strong>{value}</strong>
			{detail ? <p>{detail}</p> : null}
		</div>
	);
}

export function Sparkline({ values, tone = 'neutral' }: { values: number[]; tone?: Tone }) {
	const max = Math.max(...values, 0.0001);
	const points = values
		.map((value, index) => {
			const x = (index / Math.max(1, values.length - 1)) * 100;
			const y = 26 - (value / max) * 22;
			return `${x.toFixed(1)},${y.toFixed(1)}`;
		})
		.join(' ');
	return (
		<svg className={`spark ${tone}`} viewBox="0 0 100 28" preserveAspectRatio="none" aria-hidden="true">
			<polyline points={points} fill="none" strokeWidth="2" vectorEffect="non-scaling-stroke" />
		</svg>
	);
}

export function Progress({ value, label }: { value: number; label?: string }) {
	const clamped = Math.max(0, Math.min(100, value));
	return (
		<div className="progress-wrap">
			{label ? <div className="progress-label">{label}</div> : null}
			<div className="progress" role="progressbar" aria-valuenow={Math.round(clamped)} aria-valuemin={0} aria-valuemax={100}>
				<span style={{ width: `${clamped}%` }} />
			</div>
		</div>
	);
}

/* -------------------------------------------------------------------- badges */

export function Pill({ tone = 'neutral', icon, children }: { tone?: Tone; icon?: ReactNode; children: ReactNode }) {
	return <span className={`pill ${tone}`}>{icon}{children}</span>;
}

export function Dot({ tone = 'neutral' }: { tone?: Tone }) {
	return <span className={`dot ${tone}`} />;
}

export function Phase({ name, ok, detail, tone }: { name: string; ok: boolean; detail: string; tone?: Exclude<Tone, 'neutral'> }) {
	const actualTone = tone || (ok ? 'good' : 'bad');
	return (
		<article className={`phase ${actualTone}`}>
			{actualTone === 'good' ? <CheckCircle2 size={16} /> : actualTone === 'bad' ? <XCircle size={16} /> : <AlertTriangle size={16} />}
			<strong>{name}</strong>
			<p>{detail}</p>
		</article>
	);
}

/* --------------------------------------------------------------------- misc */

export function Banner({ tone, text }: { tone: 'bad' | 'warn'; text: string }) {
	return <div className={`banner ${tone}`}><AlertTriangle size={17} />{text}</div>;
}

export function Empty({ text }: { text: string }) {
	return <p className="empty">{text}</p>;
}

export function Bullets({ items, limit }: { items: string[]; limit?: number }) {
	const shown = typeof limit === 'number' ? items.slice(0, limit) : items;
	if (!shown.length) return <Empty text="Nothing recorded yet." />;
	return (
		<ul className="bullets">
			{shown.map((item, index) => <li key={`${index}-${item.slice(0, 24)}`}>{item}</li>)}
		</ul>
	);
}

export function KeyValue({ rows }: { rows: Array<[string, ReactNode]> }) {
	return (
		<dl className="keyvalue">
			{rows.map(([key, value]) => (
				<div key={key}>
					<dt>{key}</dt>
					<dd>{value}</dd>
				</div>
			))}
		</dl>
	);
}
