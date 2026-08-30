import eras from "../data/eras.json";

export default function EraLegend({ currentEra }) {
  return <nav className="era-legend" aria-label="Historical eras">{eras.map((era) => <span key={era.name} className={era.name === currentEra.name ? "era active" : "era"} style={{ "--era-color": era.color }}>{era.name}<small>{era.start}–{Math.min(era.end - 1, new Date().getFullYear())}</small></span>)}</nav>;
}
