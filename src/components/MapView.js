import { useEffect, useMemo, useState } from "react";
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet";
import { feature } from "topojson-client";
import stateTopology from "us-atlas/states-10m.json";
import zoneData from "../data/jurisdictionZones.json";
import { loadTreatyBoundaries, visibleTreaties } from "../utils/loadLayers";

const states = feature(stateTopology, stateTopology.objects.states);
const mandatory = new Set(zoneData.pl280.mandatory);
const optional = new Set(zoneData.pl280.optional);

export default function MapView({ year, era, layers }) {
  const [treaties, setTreaties] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { loadTreatyBoundaries().then(setTreaties).catch((cause) => setError(cause.message)); }, []);
  const activeTreaties = useMemo(() => treaties && visibleTreaties(treaties, year), [treaties, year]);
  const zone = zoneData.zones.find((item) => item.era === era.name);
  const stateStyle = (layer) => {
    const id = String(layer.id).padStart(2, "0");
    if (layers.pl280 && year >= 1953 && (mandatory.has(id) || (id === zoneData.pl280.alaska && year >= 1959))) return { color: "#8a2638", weight: 1, fillColor: "#d6604d", fillOpacity: .62 };
    if (layers.pl280 && year >= 1953 && optional.has(id)) return { color: "#b36b20", weight: 1, fillColor: "#f3b75c", fillOpacity: .45, dashArray: "5 3" };
    return { color: "#64748b", weight: .8, fillColor: layers.state ? "#dbeafe" : "#eef2f5", fillOpacity: layers.state ? .36 : .14 };
  };
  const treatyStyle = { color: "#653b94", weight: 1.2, fillColor: "#9b6bc5", fillOpacity: .12 };
  const zoneStyle = (kind) => kind === "tribal" ? { color: "#1c6c62", weight: 1, fillColor: "#4ca596", fillOpacity: .11 } : { color: "#315f91", weight: 1, fillColor: "#7197bf", fillOpacity: .08 };
  const onEachState = (item, layer) => layer.bindPopup(`<strong>${item.id}</strong><br>${zone.state}`);
  const onTreaty = (item, layer) => layer.bindPopup(`<strong>${item.properties.tribe}</strong><br>Recorded date: ${item.properties.year || "undated"}<br><small>Historical cession boundary; not present Indian country.</small>`);
  return <section className="map-wrap"><MapContainer center={[39,-98]} zoom={4} minZoom={3} className="map" scrollWheelZoom><TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" /><GeoJSON data={states} style={stateStyle} onEachFeature={onEachState} />{layers.tribal && activeTreaties && <GeoJSON data={activeTreaties} style={zoneStyle("tribal")} onEachFeature={onTreaty} />}{layers.federal && activeTreaties && <GeoJSON data={activeTreaties} style={zoneStyle("federal")} onEachFeature={onTreaty} />}{layers.treaties && activeTreaties && <GeoJSON data={activeTreaties} style={treatyStyle} onEachFeature={onTreaty} />}</MapContainer><div className="map-note"><strong>{era.name}</strong><br />{layers.state && zone.state}<br />{layers.tribal && zone.tribal}<br />{layers.federal && zone.federal}{error && <span className="error">{error}</span>}</div></section>;
}
