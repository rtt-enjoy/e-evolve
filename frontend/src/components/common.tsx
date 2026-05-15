import { AlertTriangle, CheckCircle2, XCircle } from 'lucide-react';
import type { ReactNode } from 'react';

export type Tone = 'good' | 'warn' | 'bad' | 'info' | 'neutral';

export function Panel({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <section className="panel">
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <h2>{title}</h2>
          <p>{subtitle}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

export function StatusCell({ label, value, detail }: { label: string; value: string; detail: string }) {
  return (
    <div className="status-cell">
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </div>
  );
}

export function Metric({ title, value, detail, icon }: { title: string; value: string; detail: string; icon: ReactNode }) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span>{title}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

export function Phase({ name, ok, detail, tone }: { name: string; ok: boolean; detail: string; tone?: Exclude<Tone, 'neutral'> }) {
  const actualTone = tone || (ok ? 'good' : 'bad');
  return (
    <article className={`phase-card ${actualTone}`}>
      {actualTone === 'good' ? <CheckCircle2 size={18} /> : actualTone === 'bad' ? <XCircle size={18} /> : <AlertTriangle size={18} />}
      <strong>{name}</strong>
      <p>{detail}</p>
    </article>
  );
}

export function Pill({ tone = 'neutral', icon, children }: { tone?: Tone; icon?: ReactNode; children: ReactNode }) {
  return <span className={`pill ${tone}`}>{icon}{children}</span>;
}

export function Progress({ value, label }: { value: number; label?: string }) {
  return (
    <div>
      {label ? <div className="mb-2 text-sm text-soft">{label}</div> : null}
      <div className="progress"><span style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div>
    </div>
  );
}

export function MiniStat({ icon, label, value, detail }: { icon: ReactNode; label: string; value: string; detail?: string }) {
  return (
    <article className="mini-stat">
      <div>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <p>{detail}</p> : null}
    </article>
  );
}

export function Banner({ tone, text }: { tone: 'bad'; text: string }) {
  return <div className={`mb-6 banner ${tone}`}><AlertTriangle size={18} />{text}</div>;
}

export function Empty({ text }: { text: string }) {
  return <p className="empty">{text}</p>;
}
