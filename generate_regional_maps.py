import json
from pathlib import Path
import pandas as pd

WORKSPACE = Path(__file__).resolve().parent
OUTPUT_HTML = WORKSPACE / "regional_mmip_maps.html"

REGIONS = [
    {
        "id": "nm_tx",
        "title": "New Mexico and Texas",
        "file": WORKSPACE / "New Mexico and Texas.xlsx",
        "center": [31.9, -102.8],
        "zoom": 5.2,
    },
    {
        "id": "ak",
        "title": "Alaska",
        "file": WORKSPACE / "North Dakota and Alaska.xlsx",
        "center": [64.5, -149.5],
        "zoom": 4.3,
    },
    {
        "id": "nd",
        "title": "North Dakota",
        "file": WORKSPACE / "North Dakota and Alaska.xlsx",
        "center": [47.8, -103.3],
        "zoom": 6.0,
    },
]

COLOR_MAP = {
    "man_camp": "#2563eb",
    "extraction_region": "#f59e0b",
    "extraction_site": "#8b5cf6",
    "jurisdiction_context": "#0ea5e9",
    "tribal_land": "#16a34a",
}


def normalize_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def infer_radius_km(category, name):
    text = (name or "").lower()
    if category == "jurisdiction_context":
        if "statewide" in text or "state" in text or "tribal" in text:
            return 500
        if "county" in text or "borough" in text or "parish" in text:
            return 220
        return 180
    if category == "tribal_land":
        return 130
    if category == "extraction_region":
        return 110
    return 70


def build_buffer_polygon(lat, lon, radius_km, segments=32):
    # Approximate a circular buffer in lat/lon space.
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    earth_radius_km = 6371
    coords = []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        dx = radius_km / earth_radius_km
        lat_offset = math.degrees(math.asin(math.sin(lat_rad) * math.cos(dx) + math.cos(lat_rad) * math.sin(dx) * math.cos(angle)))
        lon_offset = math.degrees(lon_rad + math.atan2(math.sin(angle) * math.sin(dx) * math.cos(lat_rad), math.cos(dx) - math.sin(lat_rad) * math.sin(lat_offset)))
        coords.append([lon_offset, lat_offset])
    coords.append(coords[0])
    return coords


def build_region_data(region):
    df = pd.read_excel(region["file"])
    rows = []
    for _, row in df.iterrows():
        category = normalize_text(row.get("category", "")).lower().replace(" ", "_")
        if not category:
            continue
        lat = row.get("latitude")
        lon = row.get("longitude")
        if pd.isna(lat) or pd.isna(lon):
            continue
        try:
            lat = float(lat)
            lon = float(lon)
        except Exception:
            continue
        name = normalize_text(row.get("name"))
        city = normalize_text(row.get("city"))
        state = normalize_text(row.get("state"))
        address = normalize_text(row.get("address_or_detail"))
        operator_owner = normalize_text(row.get("operator_owner"))
        notes = normalize_text(row.get("notes"))
        row_data = {
            "category": category,
            "name": name,
            "type": normalize_text(row.get("type")),
            "city": city,
            "state": state,
            "address": address,
            "operator_owner": operator_owner,
            "notes": notes,
            "lat": lat,
            "lon": lon,
            "color": COLOR_MAP.get(category, "#64748b"),
            "radius_km": infer_radius_km(category, name),
        }
        if category == "jurisdiction_context":
            row_data["polygon"] = build_buffer_polygon(lat, lon, row_data["radius_km"])
        rows.append(row_data)
    return rows


import math


def build_html(regions_data):
    region_tabs = []
    for region in regions_data:
        items = []
        for item in region["items"]:
            category = item["category"]
            label = item["name"] or item["city"] or item["type"] or category
            items.append(
                {
                    "category": category,
                    "name": label,
                    "lat": item["lat"],
                    "lon": item["lon"],
                    "color": item["color"],
                    "radius_km": item["radius_km"],
                    "polygon": item.get("polygon"),
                    "type": item["type"],
                    "city": item["city"],
                    "state": item["state"],
                    "address": item["address"],
                    "operator_owner": item["operator_owner"],
                    "notes": item["notes"],
                }
            )
        region_tabs.append((region["id"], region["title"], items, region["center"], region["zoom"]))

    tabs = []
    tab_scripts = []
    for region_id, title, items, center, zoom in region_tabs:
        items_json = json.dumps(items)
        tabs.append(f"<div class=\"tab-pane\" id=\"{region_id}\">\n  <div id=\"map-{region_id}\" class=\"map\"></div>\n</div>")
        tab_scripts.append(f"""
        const map_{region_id} = L.map('map-{region_id}').setView({center}, {zoom});
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
          attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map_{region_id});
        const items_{region_id} = {items_json};
        items_{region_id}.forEach(item => {{
          if (item.category === 'jurisdiction_context' && item.polygon) {{
            L.polygon(item.polygon, {{
              color: item.color,
              fillColor: item.color,
              fillOpacity: 0.18,
              weight: 1.5,
              dashArray: '4 4'
            }}).bindPopup(`<div style=\"min-width:220px;\"><strong>${{item.name}}</strong><br/>Category: ${{item.category}}<br/>City: ${{item.city || 'N/A'}}<br/>State: ${{item.state || 'N/A'}}<br/>Notes: ${{item.notes || 'N/A'}}</div>`).addTo(map_{region_id});
          }} else {{
            L.circleMarker([item.lat, item.lon], {{
              radius: item.category === 'extraction_region' ? 7 : 6,
              color: item.color,
              fillColor: item.color,
              fillOpacity: 0.8,
              weight: 1.5
            }}).bindPopup(`<div style=\"min-width:220px;\"><strong>${{item.name}}</strong><br/>Category: ${{item.category}}<br/>Type: ${{item.type || 'N/A'}}<br/>City: ${{item.city || 'N/A'}}<br/>State: ${{item.state || 'N/A'}}<br/>Address: ${{item.address || 'N/A'}}<br/>Operator/Owner: ${{item.operator_owner || 'N/A'}}<br/>Notes: ${{item.notes || 'N/A'}}</div>`).addTo(map_{region_id});
          }}
        }});
        """)

    html = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>Regional MMIP Maps</title>
  <link rel=\"stylesheet\" href=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.css\" />
  <script src=\"https://unpkg.com/leaflet@1.9.4/dist/leaflet.js\"></script>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; background: #f8fafc; }}
    .wrap {{ display: flex; flex-direction: column; height: 100vh; }}
    .tabs {{ display: flex; gap: 8px; padding: 12px; background: #0f172a; color: white; }}
    .tab {{ padding: 8px 12px; cursor: pointer; border-radius: 6px; background: #334155; }}
    .tab.active {{ background: #2563eb; }}
    .map {{ height: calc(100vh - 56px); width: 100%; }}
    .tab-pane {{ display: none; }}
    .tab-pane.active {{ display: block; }}
    .legend {{ position: absolute; right: 18px; top: 72px; z-index: 1000; background: white; padding: 10px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); }}
    .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 0.9rem; margin-bottom: 4px; }}
    .swatch {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"tabs\">
      <div class=\"tab active\" data-target=\"nm_tx\">New Mexico and Texas</div>
      <div class=\"tab\" data-target=\"ak\">Alaska</div>
      <div class=\"tab\" data-target=\"nd\">North Dakota</div>
    </div>
    <div style=\"position:relative; flex:1;\">
      <div class=\"legend\">
        <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#2563eb\"></span>Man camp</div>
        <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#f59e0b\"></span>Extraction region</div>
        <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#8b5cf6\"></span>Extraction site</div>
        <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#0ea5e9\"></span>Jurisdiction context</div>
        <div class=\"legend-item\"><span class=\"swatch\" style=\"background:#16a34a\"></span>Tribal land</div>
      </div>
      {' '.join(tabs)}
    </div>
  </div>
  <script>
    document.querySelectorAll('.tab').forEach(tab => {{
      tab.addEventListener('click', () => {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.target).classList.add('active');
      }});
    }});
    document.getElementById('nm_tx').classList.add('active');
    {''.join(tab_scripts)}
  </script>
</body>
</html>"""
    return html


if __name__ == '__main__':
    regions_data = []
    for region in REGIONS:
        region_items = build_region_data(region)
        regions_data.append({
            "id": region["id"],
            "title": region["title"],
            "items": region_items,
            "center": region["center"],
            "zoom": region["zoom"],
        })
    OUTPUT_HTML.write_text(build_html(regions_data), encoding="utf-8")
    print(f"Wrote {OUTPUT_HTML}")
