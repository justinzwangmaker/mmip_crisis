import json
import re
from pathlib import Path
import pandas as pd

WORKSPACE = Path(r"c:\Users\justi\OneDrive\Personal Academia\12th Grade\Dr. Zhao Research")
CASE_FILE = WORKSPACE / "WA_MMIP_Case_Dataset.xlsx"
JURIS_FILE = WORKSPACE / "MMIP_50_State_Jurisdiction_Dataset.xlsx"
OUTPUT_HTML = WORKSPACE / "wa_mmip_map.html"


def parse_date(value):
    if pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
    if m:
        month, day, year = map(int, m.groups())
        return pd.Timestamp(year=year, month=month, day=day)
    try:
        return pd.to_datetime(text, errors="coerce")
    except Exception:
        return None


county_centers = {
    "Adams County": [46.98, -118.57],
    "Asotin County": [46.00, -117.03],
    "Benton County": [46.26, -119.48],
    "Chelan County": [47.78, -120.34],
    "Clallam County": [48.09, -123.88],
    "Clark County": [45.74, -122.49],
    "Columbia County": [46.29, -117.92],
    "Cowlitz County": [46.16, -122.75],
    "Douglas County": [47.70, -119.87],
    "Ferry County": [48.58, -118.48],
    "Franklin County": [46.54, -118.89],
    "Garfield County": [46.47, -117.49],
    "Grant County": [47.21, -119.51],
    "Grays Harbor County": [47.16, -123.80],
    "Island County": [48.11, -122.45],
    "Jefferson County": [47.77, -123.74],
    "King County": [47.50, -121.98],
    "Kitsap County": [47.57, -122.62],
    "Kittitas County": [46.99, -120.89],
    "Klickitat County": [45.84, -121.02],
    "Lewis County": [46.63, -122.20],
    "Lincoln County": [47.60, -118.44],
    "Mason County": [47.31, -123.23],
    "Okanogan County": [48.67, -119.69],
    "Pacific County": [46.55, -123.95],
    "Pend Oreille County": [48.57, -117.34],
    "Pierce County": [47.10, -122.18],
    "San Juan County": [48.57, -123.01],
    "Skagit County": [48.46, -121.82],
    "Skamania County": [45.70, -121.99],
    "Snohomish County": [47.93, -121.83],
    "Spokane County": [47.66, -117.42],
    "Stevens County": [48.55, -117.93],
    "Thurston County": [46.94, -122.83],
    "Wahkiakum County": [46.29, -123.40],
    "Walla Walla County": [46.06, -118.33],
    "Whatcom County": [48.83, -122.22],
    "Whitman County": [46.88, -117.57],
    "Yakima County": [46.60, -120.54],
}

reservation_centers = {
    "Yakama Reservation": [46.19, -120.90],
    "Muckleshoot Reservation": [47.30, -121.95],
    "Puyallup Reservation": [47.16, -122.30],
    "Spokane Reservation": [47.69, -117.65],
    "Colville Reservation": [48.54, -118.15],
    "Swinomish Reservation": [48.50, -122.50],
    "Tulalip Reservation": [48.07, -122.27],
    "Quinault Reservation": [47.46, -124.28],
    "Nisqually Reservation": [47.07, -122.68],
    "Lummi Reservation": [48.77, -122.68],
}

missing_df = pd.read_excel(CASE_FILE, sheet_name="WA Missing Persons 2015-26")
homicide_df = pd.read_excel(CASE_FILE, sheet_name="Documented Homicide Cases")

missing_df = missing_df.copy()
homicide_df = homicide_df.copy()

missing_df["source_sheet"] = "Missing Persons"
missing_df["case_date"] = missing_df["Missing Date"].apply(parse_date)
missing_df["case_label"] = missing_df["Name"].astype(str)
missing_df["case_type"] = missing_df["Missing-Person Category (WSP)"].fillna("Missing Person")
missing_df["county"] = missing_df["County"].fillna("Unknown").astype(str)
missing_df["reservation"] = missing_df["Reservation (if applicable)"].fillna("").astype(str)
missing_df["jurisdiction_text"] = missing_df["Jurisdiction Flag (Clean Classification)"].fillna("").astype(str)
missing_df["status"] = missing_df["Status (as of dataset snapshot)"].fillna("").astype(str)

homicide_df["source_sheet"] = "Documented Homicide"
homicide_df["case_date"] = homicide_df["Date of Death"].apply(parse_date)
homicide_df["case_label"] = homicide_df["Name"].astype(str)
homicide_df["case_type"] = homicide_df["Case Type"].fillna("Homicide")
homicide_df["county"] = homicide_df["County"].fillna("Unknown").astype(str)
homicide_df["reservation"] = homicide_df["Reservation"].fillna("").astype(str)
homicide_df["jurisdiction_text"] = homicide_df["Contested Jurisdiction - Claude's Analysis"].fillna("").astype(str)
homicide_df["status"] = homicide_df["Solved / Prosecuted Status"].fillna("").astype(str)

all_cases = pd.concat([missing_df, homicide_df], ignore_index=True)


def classify_jurisdiction(text):
    text = str(text).lower()
    contested = any(token in text for token in ["contested", "contradict", "disputed", "checkerboard", "unclear", "ambiguous", "mixed"])
    if "federal/tribal" in text or "federal" in text or "tribal" in text:
        entity = "Federal/Tribal"
    elif "state" in text:
        entity = "State"
    else:
        entity = "State"
    if contested:
        entity = "Contested"
    return entity, contested

all_cases[["jurisdiction_entity", "contested"]] = pd.DataFrame(
    all_cases["jurisdiction_text"].apply(classify_jurisdiction).tolist(), index=all_cases.index
)

records = []
for _, row in all_cases.iterrows():
    if pd.isna(row["case_date"]):
        continue
    county_key = row["county"].strip() if isinstance(row["county"], str) and row["county"].strip() else "Unknown"
    reservation_val = str(row["reservation"]).strip()
    reservation_none_identified = any(token in reservation_val.lower() for token in ["none", "not identified", "unknown", "n/a", ""])
    location_unknown = False
    if reservation_val in reservation_centers:
        lat, lon = reservation_centers[reservation_val]
    elif county_key in county_centers:
        lat, lon = county_centers[county_key]
    else:
        lat, lon = 47.5, -120.74
        location_unknown = True
    records.append({
        "name": str(row["case_label"]),
        "date": row["case_date"].strftime("%Y-%m-%d"),
        "year": int(row["case_date"].year),
        "county": str(row["county"]),
        "reservation": str(row["reservation"]),
        "case_type": str(row["case_type"]),
        "source_sheet": str(row["source_sheet"]),
        "status": str(row["status"]),
        "jurisdiction_text": str(row["jurisdiction_text"]),
        "jurisdiction_entity": str(row["jurisdiction_entity"]),
        "contested": bool(row["contested"]),
        "location_unknown": location_unknown,
        "reservation_none_identified": reservation_none_identified,
        "lat": lat,
        "lon": lon,
    })

records_sorted = sorted(records, key=lambda r: r["date"])

jurisdiction_progress = {}
for rec in records_sorted:
    year = rec["year"]
    jurisdiction_progress.setdefault(year, {"State": 0, "Federal/Tribal": 0, "Contested": 0})
    if rec["contested"]:
        jurisdiction_progress[year]["Contested"] += 1
    elif rec["jurisdiction_entity"] == "Federal/Tribal":
        jurisdiction_progress[year]["Federal/Tribal"] += 1
    else:
        jurisdiction_progress[year]["State"] += 1

jurisdiction_df = pd.read_excel(JURIS_FILE, sheet_name="50-State MMIP Jurisdiction")
wa_row = jurisdiction_df[jurisdiction_df["State"].astype(str).str.contains("Washington", case=False, na=False)]
wa_summary = {}
if not wa_row.empty:
    row = wa_row.iloc[0]
    wa_summary = {
        "framework": str(row["Jurisdictional Framework"]),
        "contradictory": str(row["Contradictory? (Flagged)"]),
        "notes": str(row["Contradiction / Complication Notes"]),
    }

html = """<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Washington MMIP Jurisdiction Map</title>
  <link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\" />
  <script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script>
  <script src=\"https://cdn.jsdelivr.net/gh/python-visualization/folium@main/folium/templates/leaflet_heat.min.js\"></script>
  <style>
    body { margin: 0; font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; }
    .layout { display: grid; grid-template-columns: 320px 1fr; height: 100vh; }
    .sidebar { background: #111827; padding: 18px; overflow-y: auto; border-right: 1px solid #334155; }
    h1 { margin-top: 0; font-size: 1.2rem; }
    .card { background: #1f2937; border: 1px solid #475569; border-radius: 10px; padding: 12px; margin-bottom: 12px; }
    .legend { display: grid; gap: 6px; margin-top: 8px; }
    .legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.92rem; }
    .swatch { width: 12px; height: 12px; border-radius: 50%; display: inline-block; border: 1px solid #fff; }
    .controls label { display: block; font-size: 0.9rem; margin-bottom: 6px; }
    input[type=\"range\"] { width: 100%; }
    .note { font-size: 0.9rem; line-height: 1.4; color: #cbd5e1; }
    #map { height: 100vh; }
    .summary { font-size: 0.95rem; margin-top: 6px; }
    .bar { height: 8px; background: #334155; border-radius: 999px; overflow: hidden; margin-top: 6px; }
    .bar > div { height: 100%; }
    .toggle-row { display: flex; align-items: center; gap: 8px; }
  </style>
</head>
<body>
  <div class=\"layout\">
    <div class=\"sidebar\">
      <h1>Washington MMIP Jurisdiction Map</h1>
      <div class=\"card\">
        <strong>What this shows</strong>
        <div class=\"note\">This map combines Washington MMIP case records with the statewide jurisdiction framework so each case can be reviewed by year and by the entity that appears to hold legal authority.</div>
      </div>
      <div class=\"card\">
        <strong>Washington legal framework</strong>
        <div class=\"note\">Framework: __FRAMEWORK__<br/><br/>Contradictory: __CONTRADICTORY__<br/><br/>__NOTES__</div>
      </div>
      <div class=\"card controls\">
        <label for=\"dateSlider\">Case date slider</label>
        <input id=\"dateSlider\" type=\"range\" min=\"2015\" max=\"2026\" step=\"1\" value=\"2026\" />
        <div class=\"summary\" id=\"dateSummary\">Showing cases through 2026</div>
      </div>
      <div class=\"card controls\">
        <label for=\"jurisdictionSlider\">Jurisdiction-hold progression</label>
        <input id=\"jurisdictionSlider\" type=\"range\" min=\"2015\" max=\"2026\" step=\"1\" value=\"2026\" />
        <div class=\"summary\" id=\"jurisdictionSummary\">Dominant authority for 2026</div>
        <div id=\"jurisdictionBars\"></div>
      </div>
      <div class=\"card\">
        <div class=\"toggle-row\"><input type=\"checkbox\" id=\"heatToggle\" checked /><label for=\"heatToggle\">Show case concentration heatmap</label></div>
        <div class=\"legend\">
          <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#0ea5e9\"></span>State</div>
          <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#10b981\"></span>Federal/Tribal</div>
          <div class="legend-item"><span class="swatch" style="background:#ef4444"></span>Contested</div>
          <div class="legend-item"><span class="swatch" style="background:#64748b; border-style:dashed;"></span>Unknown/unclear location</div>
          <div class="legend-item"><span class="swatch" style="background:#94a3b8; border-style:dashed;"></span>Reservation not identified</div>
        </div>
        <div class="note" style="margin-top:8px;">Unknown-location cases are shown with a dashed marker and the popup notes when no reservation is identified.</div>
      </div>
    </div>
    <div id=\"map\"></div>
  </div>

  <script>
    const baseCases = __CASES__;
    const jurisdictionProgress = __JURISDICTION_PROGRESS__;
    const map = L.map('map').setView([47.5, -120.74], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const markerStyles = {
      'State': '#0ea5e9',
      'Federal/Tribal': '#10b981',
      'Local/Municipal': '#f59e0b',
      'Mixed/Unclear': '#8b5cf6'
    };

    let heatLayer = null;
    let caseMarkers = [];

    function markerColor(record) {
      if (record.reservation_none_identified) return '#94a3b8';
      if (record.contested) return '#ef4444';
      return markerStyles[record.jurisdiction_entity] || '#8b5cf6';
    }

    function popupHtml(record) {
      const locationText = record.location_unknown ? 'Unknown/Unclear (mapped near state center)' : (record.reservation || record.county || 'Unknown');
      const reservationText = record.reservation_none_identified ? 'Reservation not identified' : (record.reservation || 'Not listed');
      return `
        <div style="line-height:1.4; min-width:220px;">
          <strong>${record.name}</strong><br/>
          Date: ${record.date}<br/>
          Location: ${locationText}<br/>
          Reservation: ${reservationText}<br/>
          Type: ${record.case_type}<br/>
          Jurisdiction: ${record.jurisdiction_entity}<br/>
          Contested: ${record.contested ? 'Yes' : 'No'}<br/>
          Status: ${record.status || 'N/A'}
        </div>`;
    }

    function renderMarkers(filterYear) {
      caseMarkers.forEach(m => map.removeLayer(m));
      caseMarkers = [];
      const visible = baseCases.filter(r => r.year <= filterYear);
      visible.forEach(record => {
        const marker = L.circleMarker([record.lat, record.lon], {
          radius: record.contested ? 9 : 7,
          color: markerColor(record),
          weight: record.contested ? 2 : 1,
          fillColor: markerColor(record),
          fillOpacity: 0.7,
          dashArray: record.location_unknown || record.reservation_none_identified ? '4 4' : null
        }).bindPopup(popupHtml(record));
        marker.addTo(map);
        caseMarkers.push(marker);
      });
      updateHeatmap(visible);
    }

    function updateHeatmap(records) {
      if (heatLayer) map.removeLayer(heatLayer);
      const heatToggle = document.getElementById('heatToggle');
      if (!heatToggle.checked) return;
      const points = records.map(r => [r.lat, r.lon, 0.55]);
      if (points.length) {
        heatLayer = L.heatLayer(points, { radius: 26, blur: 20, maxZoom: 8 }).addTo(map);
      }
    }

    function updateJurisdictionSummary(year) {
      const summary = document.getElementById('jurisdictionSummary');
      const bars = document.getElementById('jurisdictionBars');
      const data = jurisdictionProgress[year] || {'State':0,'Federal/Tribal':0,'Contested':0};
      const entries = Object.entries(data).filter(([, value]) => value > 0);
      const dominant = entries.length ? entries.sort((a, b) => b[1] - a[1])[0][0] : 'No data';
      summary.textContent = `Dominant authority for ${year}: ${dominant}`;
      const total = entries.reduce((sum, [, value]) => sum + value, 0);
      bars.innerHTML = entries.map(([name, value]) => {
        const pct = total ? Math.round(value / total * 100) : 0;
        const color = name === 'State' ? '#0ea5e9' : name === 'Federal/Tribal' ? '#10b981' : '#ef4444';
        return `<div style=\"margin-top:8px;\"><div style=\"font-size:0.86rem; margin-bottom:3px;\">${name}: ${value} cases</div><div class=\"bar\"><div style=\"width:${pct}%; background:${color};\"></div></div></div>`;
      }).join('');
    }

    document.getElementById('dateSlider').addEventListener('input', (e) => {
      const year = Number(e.target.value);
      document.getElementById('dateSummary').textContent = `Showing cases through ${year}`;
      renderMarkers(year);
    });

    document.getElementById('jurisdictionSlider').addEventListener('input', (e) => {
      const year = Number(e.target.value);
      updateJurisdictionSummary(year);
    });

    document.getElementById('heatToggle').addEventListener('change', () => {
      const year = Number(document.getElementById('dateSlider').value);
      renderMarkers(year);
    });

    renderMarkers(2026);
    updateJurisdictionSummary(2026);
  </script>
</body>
</html>"""

html = html.replace("__CASES__", json.dumps(records_sorted))
html = html.replace("__JURISDICTION_PROGRESS__", json.dumps(jurisdiction_progress))
html = html.replace("__FRAMEWORK__", wa_summary.get("framework", "N/A"))
html = html.replace("__CONTRADICTORY__", wa_summary.get("contradictory", "N/A"))
html = html.replace("__NOTES__", wa_summary.get("notes", ""))

OUTPUT_HTML.write_text(html, encoding="utf-8")
print(f"Wrote {OUTPUT_HTML}")
