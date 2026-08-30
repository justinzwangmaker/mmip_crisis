import { CURRENT_YEAR, normalizeDecade } from "../utils/sliderLogic";

export default function Slider({ year, onChange }) {
  return (
    <section className="slider-panel">
      <label htmlFor="year-slider">Year: <strong>{year}</strong> · <span>10-year steps</span></label>
      <input id="year-slider" type="range" min="1776" max={CURRENT_YEAR} step="10" value={year} onChange={(event) => onChange(normalizeDecade(event.target.value))} />
      <div className="slider-ends">
        <span>1776</span>
        <span>Present</span>
      </div>
    </section>
  );
}
