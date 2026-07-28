import xml.etree.ElementTree as ET
import json
import re

kml_file = 'fetched_doc.kml'

tree = ET.parse(kml_file)
root = tree.getroot()

ns = {'kml': 'http://www.opengis.net/kml/2.2'}

features = []

for placemark in root.findall('.//kml:Placemark', ns):
    name_el = placemark.find('kml:name', ns)
    name = name_el.text.strip() if name_el is not None and name_el.text else ''
    
    style_el = placemark.find('kml:styleUrl', ns)
    style_url = style_el.text.strip() if style_el is not None and style_el.text else ''
    
    # Extract color hex if style is referenced
    style_color = "#6366f1"
    if '0288D1' in style_url: style_color = "#0288d1"
    elif '0097A7' in style_url: style_color = "#0097a7"
    elif '7CB342' in style_url: style_color = "#7cb342"
    elif 'D81B60' in style_url: style_color = "#d81b60"
    elif 'F57C00' in style_url: style_color = "#f57c00"
    elif 'E65100' in style_url: style_color = "#e65100"

    # Check Polygon
    polygon = placemark.find('.//kml:Polygon', ns)
    if polygon is not None:
        coord_el = polygon.find('.//kml:coordinates', ns)
        if coord_el is not None and coord_el.text:
            raw_coords = coord_el.text.strip().split()
            coords = []
            for c in raw_coords:
                parts = c.split(',')
                if len(parts) >= 2:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    coords.append([lon, lat])
            
            if coords:
                # Ensure closed ring
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    },
                    "properties": {
                        "name": name,
                        "styleUrl": style_url,
                        "color": style_color
                    }
                })

    # Check Point
    point = placemark.find('.//kml:Point', ns)
    if point is not None:
        coord_el = point.find('kml:coordinates', ns)
        if coord_el is not None and coord_el.text:
            parts = coord_el.text.strip().split(',')
            if len(parts) >= 2:
                lon = float(parts[0])
                lat = float(parts[1])
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "name": name,
                        "styleUrl": style_url,
                        "color": style_color
                    }
                })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

print(f"Extracted {len(features)} total features ({sum(1 for f in features if f['geometry']['type'] == 'Polygon')} Polygons, {sum(1 for f in features if f['geometry']['type'] == 'Point')} Points) from live OCU.kml!")

with open('Drawing.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

with open('public/data/Drawing.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

# Build window.FALLBACK_RAW_GEOJSON and window.FALLBACK_CAMPUS_DATA
with open('public/data/campus_data.json', 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

js_content = f"""// Global Fallback Embedded Campus Data & GeoJSON from OCU.kml
window.FALLBACK_CAMPUS_DATA = {json.dumps(campus_data, indent=2, ensure_ascii=False)};
window.FALLBACK_RAW_GEOJSON = {json.dumps(geojson, indent=2, ensure_ascii=False)};
"""

with open('js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

with open('public/js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Updated Drawing.geojson and campus_data_fallback.js successfully!")
