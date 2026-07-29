import json

with open('data/campus_data.json', 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

with open('Drawing.geojson', 'r', encoding='utf-8') as f:
    raw_geojson = json.load(f)

inline_script = f"""
  <!-- Direct Synchronous Embedded Campus Data & GeoJSON Building Drawings from OCU1.kml -->
  <script>
    window.FALLBACK_CAMPUS_DATA = {json.dumps(campus_data, ensure_ascii=False)};
    window.FALLBACK_RAW_GEOJSON = {json.dumps(raw_geojson, ensure_ascii=False)};
  </script>
"""

for file_path in ['index.html', 'public/index.html']:
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Replace existing fallback script tag or insert before </head>
    if '<!-- Embedded Fallback Dataset' in html:
        parts = html.split('<!-- Embedded Fallback Dataset')
        sub_parts = parts[1].split('</head>')
        new_html = parts[0] + inline_script + '\n</head>' + sub_parts[1]
    else:
        new_html = html.replace('</head>', inline_script + '\n</head>')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print(f"Successfully embedded inline datasets into {file_path}!")

print("Embedded datasets into index.html and public/index.html completely!")
