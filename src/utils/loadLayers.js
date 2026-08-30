import treatySeed from "../data/treatyBoundaries.json";

const parseYear = (value) => {
  if (typeof value === "number" && Math.abs(value) > 1000000) return new Date(value).getUTCFullYear();
  const match = String(value ?? "").match(/(17|18|19)\d{2}/);
  return match ? Number(match[0]) : null;
};

export async function loadTreatyBoundaries() {
  if (treatySeed.features.length) return treatySeed;
  const response = await fetch(treatySeed.source.geojsonEndpoint);
  if (!response.ok) throw new Error("The treaty-boundary service could not be loaded.");
  const result = await response.json();
  const fields = treatySeed.source.dateFields;
  return {
    type: "FeatureCollection",
    features: result.features.filter((record) => record.geometry?.rings?.length).map((record) => ({
      type: "Feature",
      properties: {
        ...record.attributes,
        year: Math.min(...fields.map((field) => parseYear(record.attributes[Object.keys(record.attributes).find((key) => key.endsWith(field))])).filter(Boolean), 9999),
        tribe: record.attributes[Object.keys(record.attributes).find((key) => key.endsWith("presdaytrb"))] || record.attributes[Object.keys(record.attributes).find((key) => key.endsWith("schdtrb"))] || "Historical cession"
      },
      geometry: { type: "Polygon", coordinates: record.geometry.rings }
    })).filter((feature) => feature.properties.year !== 9999)
  };
}

export function visibleTreaties(collection, year) {
  return {
    ...collection,
    features: collection.features.filter((feature) => feature.properties.year <= year)
  };
}
