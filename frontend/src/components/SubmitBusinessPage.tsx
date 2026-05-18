import { ArrowRight, Building2, CheckCircle2, ExternalLink, Globe2, MapPin, Store } from 'lucide-react';
import { Panel, Pill } from './common';

const directories = [
  {
    name: 'Coinmap',
    href: 'https://coinmap.it/',
    bestFor: 'physical shops and local venues',
    action: 'Add the business to OpenStreetMap with payment:bitcoin=yes, or leave a map note for a local editor.',
    icon: <MapPin />,
  },
  {
    name: 'Spendabit',
    href: 'https://spendabit.co/merchant-suite',
    bestFor: 'online stores with Bitcoin checkout',
    action: 'Submit the store website, contact details, and confirmation that products can be purchased with Bitcoin.',
    icon: <Store />,
  },
  {
    name: 'BTC Map',
    href: 'https://btcmap.org/',
    bestFor: 'Lightning-friendly local businesses',
    action: 'Create or update the venue listing so nearby Bitcoin users can find current acceptance details.',
    icon: <Globe2 />,
  },
];

const checklist = [
  'Confirm the business currently accepts Bitcoin before listing it.',
  'Use the public website, physical address, and contact details customers already see.',
  'Include useful payment context such as on-chain, Lightning, gift card, or processor support.',
  'Recheck the listing after submission so customers are not sent to stale information.',
];

export function SubmitBusinessPage() {
  return (
    <div className="submit-business-page">
      <section className="submit-business-hero">
        <div className="submit-business-hero-copy">
          <div className="mb-4 flex flex-wrap gap-2">
            <Pill tone="good" icon={<CheckCircle2 size={14} />}>lead completed</Pill>
            <Pill tone="info" icon={<Building2 size={14} />}>submit your business</Pill>
          </div>
          <h2>Submit Your Bitcoin Business</h2>
          <p>
            Help customers find places that accept Bitcoin by choosing the directory that matches the business type,
            then submitting accurate, current details.
          </p>
        </div>
        <div className="submit-business-proof">
          <span>Original lead</span>
          <strong>Create custom page for "Submit your business"</strong>
          <a href="https://github.com/bitcoin-dot-org/Bitcoin.org/issues/1583">
            <ExternalLink size={15} /> view source issue
          </a>
        </div>
      </section>

      <section className="submit-directory-grid" aria-label="Bitcoin business directories">
        {directories.map((directory) => (
          <article className="submit-directory-card" key={directory.name}>
            <div className="submit-directory-icon">{directory.icon}</div>
            <span>{directory.bestFor}</span>
            <strong>{directory.name}</strong>
            <p>{directory.action}</p>
            <a className="small-button" href={directory.href}>
              open <ArrowRight size={15} />
            </a>
          </article>
        ))}
      </section>

      <div className="submit-business-layout">
        <Panel title="Before You Submit" subtitle="Good directory data keeps the Bitcoin spending experience trustworthy.">
          <ul className="submit-checklist">
            {checklist.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </Panel>

        <Panel title="Suggested Listing Copy" subtitle="Use this as a compact starting point for directory forms.">
          <div className="listing-template">
            <span>Business name</span>
            <p>One sentence about what customers can buy, where the business serves, and how Bitcoin payment works.</p>
            <span>Payment details</span>
            <p>Accepts Bitcoin via on-chain, Lightning, or payment processor. Add opening hours, delivery region, and support contact.</p>
          </div>
        </Panel>
      </div>
    </div>
  );
}
