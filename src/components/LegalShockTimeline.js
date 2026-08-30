import events from "../data/legalShockEvents.json";

export default function LegalShockTimeline({ year, era }) {
  const current = events.filter((event) => Math.floor(event.year / 10) * 10 === year);
  const shown = current.length ? current : events.filter((event) => event.era === era.name).slice(0, 5);
  return <section className="timeline" aria-live="polite"><div><strong>Legal shocks</strong><span>{current.length ? ` in the ${year}s` : ` defining ${era.name}`}</span></div><div className="events">{shown.map((event) => <article key={`${event.year}-${event.law_name}`}><b>{event.year}</b><strong>{event.law_name}</strong><em>{event.citation}</em><p>{event.jurisdiction_effect}</p><p>{event.land_effect}</p></article>)}</div></section>;
}
