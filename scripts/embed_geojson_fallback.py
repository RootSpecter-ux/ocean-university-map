import json
import os

geojson_path = r'c:\Users\HP\OneDrive\Desktop\Map\Drawing.geojson'
fallback_js_path = r'c:\Users\HP\OneDrive\Desktop\Map\js\campus_data_fallback.js'
public_fallback_js_path = r'c:\Users\HP\OneDrive\Desktop\Map\public\js\campus_data_fallback.js'

with open(geojson_path, 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

campus_data_path = r'c:\Users\HP\OneDrive\Desktop\Map\public\data\campus_data.json'
with open(campus_data_path, 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

js_content = f"""// Fallback Embedded Campus Data & GeoJSON for 100% Instant CDN Reliability
const FALLBACK_CAMPUS_DATA = {json.dumps(campus_data, indent=2, ensure_ascii=False)};

const FALLBACK_RAW_GEOJSON = {json.dumps(geojson_data, indent=2, ensure_ascii=False)};
"""

with open(fallback_js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

with open(public_fallback_js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Successfully embedded FALLBACK_RAW_GEOJSON into js/campus_data_fallback.js!")
