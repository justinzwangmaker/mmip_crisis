import { useState } from "react";
import Slider from "./components/Slider";
import EraLegend from "./components/EraLegend";
import LayerToggles from "./components/LayerToggles";
import LegalShockTimeline from "./components/LegalShockTimeline";
import MapView from "./components/MapView";
import { getEra } from "./utils/eraLookup";
import { normalizeDecade } from "./utils/sliderLogic";
import "leaflet/dist/leaflet.css";
import "./styles.css";

export default function App() {
  const [year, setYear] = useState(normalizeDecade(new Date().getFullYear()));
  const [layers, setLayers] = useState({ pl280:true, state:true, tribal:true, federal:true, treaties:true });
  const era = getEra(year);
  return <main className="app"><header><div><p className="eyebrow">United States · 1776–present</p><h1>Checkerboard History Map</h1></div><Slider year={year} onChange={setYear} /><EraLegend currentEra={era} /></header><div className="map-shell"><LayerToggles layers={layers} onChange={(key) => setLayers((current) => ({ ...current, [key]: !current[key] }))} /><MapView year={year} era={era} layers={layers} /></div><LegalShockTimeline year={year} era={era} /></main>;
}
