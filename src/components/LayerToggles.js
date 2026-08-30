const options = [["pl280","PL-280 areas"],["state","State criminal jurisdiction"],["tribal","Tribal criminal jurisdiction"],["federal","Federal criminal jurisdiction"],["treaties","Treaty boundaries"]];
export default function LayerToggles({ layers, onChange }) {
  return (
    <aside className="toggles">
      <section>
        <h2>Layers</h2>
        {options.map(([key, label]) => (
          <label key={key}>
            <input type="checkbox" checked={layers[key]} onChange={() => onChange(key)} /> {label}
          </label>
        ))}
      </section>

      <section className="map-instructions" aria-label="Map instructions">
        <h2>Instructions</h2>
        <ol>
          <li>Move the year slider across 1776–present in 10-year steps.</li>
          <li>Toggle the layer controls to compare PL-280 areas, state, tribal, federal, and treaty boundaries.</li>
          <li>Click a state or boundary to view the era-specific jurisdiction details.</li>
          <li>Review the legal-shock timeline to see the top law events for each decade.</li>
        </ol>
      </section>
    </aside>
  );
}
