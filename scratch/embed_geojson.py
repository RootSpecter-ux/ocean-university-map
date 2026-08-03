import json
import re

with open('Drawing.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

with open('js/campus_data_fallback.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace window.EMBEDDED_GEOJSON_DRAWINGS = ...
geojson_str = json.dumps(geojson_data, indent=2)
new_content = re.sub(
    r'window\.EMBEDDED_GEOJSON_DRAWINGS\s*=\s*\{.*?\};',
    f'window.EMBEDDED_GEOJSON_DRAWINGS = {geojson_str};',
    content,
    flags=re.DOTALL
)

with open('js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Embedded new GeoJSON drawings into js/campus_data_fallback.js!')
