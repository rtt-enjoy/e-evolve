import { Sparkles } from 'lucide-react';
import { useMemo } from 'react';
import { JsonNode } from '../components/JsonNode';
import { Card, Disclosure, Empty, Pill, SectionHead, Subhead, Tile } from '../components/ui';
import { CLAIMED_KEYS, unclaimedKeys } from '../sections/registry';
import { featureLabel } from '../utils/format';
import type { Status } from '../types/status';

export default function DataSection({ status }: { status: Status }) {
  const newKeys = useMemo(() => unclaimedKeys(status), [status]);
  const knownKeys = useMemo(
    () => Object.keys(status).filter((key) => CLAIMED_KEYS.has(key)).sort(),
    [status],
  );
  const totalKeys = Object.keys(status).length;

  return (
    <>
      <SectionHead
        title="Data"
        blurb="Every field in the snapshot. Fields the bot added after this dashboard was built appear here automatically."
      />

      <div className="tile-row">
        <Tile label="Snapshot fields" value={String(totalKeys)} detail="top-level keys" tone="info" />
        <Tile label="Rendered by sections" value={String(knownKeys.length)} detail="mapped to a view" tone="good" />
        <Tile label="New / unmapped" value={String(newKeys.length)} detail={newKeys.length ? 'shown generically below' : 'nothing new'} tone={newKeys.length ? 'warn' : 'neutral'} />
        <Tile label="Payload" value={`${Math.round(JSON.stringify(status).length / 1024)} kB` } detail="status.json size" tone="neutral" />
      </div>

      {newKeys.length ? (
        <Card
          title="New bot data"
          hint="These keys have no dedicated view yet, so they are rendered generically. No frontend change was needed for them to appear."
          action={<Pill tone="warn" icon={<Sparkles size={14} />}>{newKeys.length} new</Pill>}
        >
          <div className="stack">
            {newKeys.map((key) => (
              <Disclosure key={key} title={featureLabel(key)} hint={key} defaultOpen={newKeys.length <= 3}>
                <JsonNode value={status[key]} name={key} defaultOpen depth={0} />
              </Disclosure>
            ))}
          </div>
        </Card>
      ) : (
        <Card title="New bot data">
          <Empty text="No unmapped fields — every key in this snapshot has a dedicated view." />
        </Card>
      )}

      <Subhead>Full snapshot</Subhead>
      <Card hint="The complete status.json, expandable node by node.">
        <div className="stack">
          {Object.keys(status).sort().map((key) => (
            <Disclosure
              key={key}
              title={featureLabel(key)}
              hint={CLAIMED_KEYS.has(key) ? key : `${key} · unmapped`}
              count={countOf(status[key])}
            >
              <JsonNode value={status[key]} name={key} defaultOpen depth={0} />
            </Disclosure>
          ))}
        </div>
      </Card>

      <div className="legend">
        <span>Raw file: <a href="status.json">status.json</a></span>
        <span>Log: <a href="earnings-log.md">earnings-log.md</a></span>
      </div>
    </>
  );
}

function countOf(value: unknown): number | null {
  if (Array.isArray(value)) return value.length;
  if (value && typeof value === 'object') return Object.keys(value).length;
  return null;
}
