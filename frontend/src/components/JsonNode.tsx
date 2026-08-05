import { ChevronRight } from 'lucide-react';
import { useState } from 'react';

/**
 * Generic renderer for arbitrary status.json values.
 *
 * This is what lets new backend fields show up without a frontend change:
 * anything the section registry does not claim is handed to this component.
 */
export function JsonNode({
  value,
  name,
  depth = 0,
  defaultOpen = false,
}: {
  value: unknown;
  name?: string;
  depth?: number;
  defaultOpen?: boolean;
}) {
  // Deep nodes start closed so a large payload does not explode on screen.
  const [open, setOpen] = useState(defaultOpen && depth < 2);

  if (value === null || value === undefined) return <Leaf name={name} className="null">null</Leaf>;

  if (typeof value === 'boolean') return <Leaf name={name} className={value ? 'true' : 'false'}>{String(value)}</Leaf>;

  if (typeof value === 'number') return <Leaf name={name} className="num">{formatNumber(value)}</Leaf>;

  if (typeof value === 'string') {
    if (isUrl(value)) {
      return (
        <Leaf name={name} className="str">
          <a href={value} target="_blank" rel="noreferrer">{value}</a>
        </Leaf>
      );
    }
    // Multi-line or long strings (codex prompts, drafts) get their own block.
    if (value.length > 160 || value.includes('\n')) {
      return (
        <div className="json-row block">
          {name ? <span className="json-key">{name}</span> : null}
          <pre className="code-block">{value}</pre>
        </div>
      );
    }
    return <Leaf name={name} className="str">{value}</Leaf>;
  }

  const isArray = Array.isArray(value);
  const entries = isArray
    ? (value as unknown[]).map((item, index) => [String(index), item] as const)
    : Object.entries(value as Record<string, unknown>);

  if (!entries.length) {
    return <Leaf name={name} className="null">{isArray ? 'empty list' : 'empty object'}</Leaf>;
  }

  return (
    <div className={`json-branch ${open ? 'open' : ''}`}>
      <button type="button" onClick={() => setOpen(!open)} aria-expanded={open}>
        <ChevronRight className="chevron" size={14} />
        {name ? <span className="json-key">{name}</span> : null}
        <span className="json-meta">{isArray ? `${entries.length} items` : `${entries.length} fields`}</span>
      </button>
      {open ? (
        <div className="json-children">
          {entries.map(([key, item]) => (
            <JsonNode key={key} name={key} value={item} depth={depth + 1} defaultOpen={depth < 1} />
          ))}
        </div>
      ) : null}
    </div>
  );
}

function Leaf({ name, className, children }: { name?: string; className: string; children: React.ReactNode }) {
  return (
    <div className="json-row">
      {name ? <span className="json-key">{name}</span> : null}
      <span className={`json-val ${className}`}>{children}</span>
    </div>
  );
}

function formatNumber(value: number): string {
  if (Number.isInteger(value)) return value.toLocaleString();
  return String(Number(value.toFixed(6)));
}

function isUrl(value: string): boolean {
  return /^https?:\/\/\S+$/.test(value);
}
