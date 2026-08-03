import json

with open('Drawing.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

with open('data/campus_data.json', 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

geojson_str = json.dumps(geojson_data, indent=2)
campus_str = json.dumps(campus_data, indent=2)

fallback_js_content = f"""// Synchronous Embedded Failsafe Campus Dataset & Vector Drawings
window.FALLBACK_CAMPUS_DATA = {campus_str};

window.EMBEDDED_GEOJSON_DRAWINGS = {geojson_str};
"""

with open('js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(fallback_js_content)

print('Successfully regenerated js/campus_data_fallback.js with 100% embedded drawings!')
