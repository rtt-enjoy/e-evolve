import type { Status } from './types';

export function money(value = 0, digits = 2): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: digits,
  }).format(value || 0);
}

export function formatDate(value?: string): string {
  if (!value) return 'never';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function ageLabel(value?: string): { label: string; tone: 'good' | 'warn' | 'bad' } {
  if (!value) return { label: 'never', tone: 'bad' };
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return { label: value, tone: 'warn' };
  const minutes = Math.max(0, Math.floor((Date.now() - date.getTime()) / 60000));
  if (minutes < 75) return { label: `${minutes}m ago`, tone: 'good' };
  if (minutes < 180) return { label: `${Math.floor(minutes / 60)}h ${minutes % 60}m ago`, tone: 'warn' };
  return { label: `${Math.floor(minutes / 60)}h ago`, tone: 'bad' };
}

export function featureLabel(feature: string): string {
  return feature
    .replace(/^llm_/, '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function evolutionTone(status: Status): 'good' | 'warn' | 'bad' | 'info' {
  const evolution = status.last_evolution || {};
  if (evolution.error) return evolution.error_type === 'api' ? 'warn' : 'bad';
  if ((evolution.changes_applied || []).length) return 'good';
  if ((evolution.summary || '').toLowerCase().includes('skipped')) return 'warn';
  return 'info';
}
