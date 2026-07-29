import xml.etree.ElementTree as ET
import json
import os
import urllib.request
import zipfile
import io

# 1. Fetch latest KML from Google My Maps if reachable, or parse local C:\Users\HP\Downloads\OCU.kml
kml_url = 'https://www.google.com/maps/d/kml?forcekml=1&mid=1oYCxIl6BMTSHj_dm2-vHSO0ORf6v1gQ'

kml_content = None

try:
    print("Fetching live KML stream from Google My Maps...")
    req = urllib.request.Request(kml_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    data = urllib.request.urlopen(req).read()
    if data.startswith(b'PK'):
        z = zipfile.ZipFile(io.BytesIO(data))
        for name in z.namelist():
            if name.endswith('.kml'):
                kml_content = z.read(name).decode('utf-8')
                break
    else:
        kml_content = data.decode('utf-8')
    print("Successfully fetched live KML from Google My Maps!")
except Exception as e:
    print(f"Network fetch fallback: {e}")

if not kml_content:
    print("Reading local file C:\\Users\\HP\\Downloads\\OCU.kml...")
    with open('fetched_doc.kml', 'r', encoding='utf-8') as f:
        kml_content = f.read()

# 2. Parse KML XML
root = ET.fromstring(kml_content)
ns = {'kml': 'http://www.opengis.net/kml/2.2'}

features = []
locations = []

def get_category_and_color(name):
    u = name.upper()
    if 'SECURITY' in u or 'GATE' in u:
        return 'Security & Entry', '#ef4444'
    if 'MTL' in u or 'CLASS' in u or 'DRAWING' in u or 'LECTUERE' in u:
        return 'Academic & Lecture Halls', '#8b5cf6'
    if 'LAB' in u or 'WORKSHOP' in u or 'IT' in u or 'CHART' in u:
        return 'Labs & Workshops', '#06b6d4'
    if 'DIVISION' in u or 'TRANSPORT' in u or 'ACCOUNT' in u or 'REGIONAL' in u:
        return 'Administrative', '#a855f7'
    if 'SPORT' in u or 'GYM' in u or 'COURT' in u or 'VOLLY' in u or 'BADMINTON' in u:
        return 'Sports & Rec', '#10b981'
    if 'CANTEEN' in u or 'HOSTAL' in u or 'AUDITORIUM' in u or 'UNION' in u:
        return 'Facilities & Dining', '#f59e0b'
    return 'Amenities', '#3b82f6'

# Helper for polygon centroid calculation
def calc_polygon_centroid(coords):
    pts = coords[:-1] if coords[0] == coords[-1] and len(coords) > 1 else coords
    if not pts:
        return 0.0, 0.0
    sum_lon = sum(p[0] for p in pts)
    sum_lat = sum(p[1] for p in pts)
    return sum_lat / len(pts), sum_lon / len(pts)

loc_index = 1

for placemark in root.findall('.//kml:Placemark', ns):
    name_el = placemark.find('kml:name', ns)
    name = name_el.text.strip() if name_el is not None and name_el.text else ''
    if not name:
        continue
    
    cat, color = get_category_and_color(name)
    
    # Polygon feature
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
                if coords[0] != coords[-1]:
                    coords.append(coords[0])
                
                c_lat, c_lon = calc_polygon_centroid(coords)
                loc_id = name.lower().replace(" ", "_").replace("'", "").replace("&", "and")
                
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coords]
                    },
                    "properties": {
                        "id": loc_id,
                        "name": name,
                        "category": cat,
                        "color": color,
                        "center_lat": c_lat,
                        "center_lon": c_lon
                    }
                })
                
                locations.append({
                    "id": loc_id,
                    "name": name,
                    "category": cat,
                    "lat": round(c_lat, 6),
                    "lon": round(c_lon, 6),
                    "door_lat": round(coords[0][1], 6),
                    "door_lon": round(coords[0][0], 6),
                    "translations": {
                        "en": name,
                        "si": name,
                        "ta": name
                    }
                })
                loc_index += 1

geojson = {
    "type": "FeatureCollection",
    "features": features
}

print(f"Extracted {len(features)} exact building polygons and centroids from OCU.kml!")

# Write GeoJSON
with open('Drawing.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

with open('public/data/Drawing.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

# Rebuild Campus Locations Data and Graph Nodes
nodes = {}
edges = []

for i, loc in enumerate(locations):
    n_id = loc['id']
    nodes[n_id] = {
        "id": n_id,
        "name": loc['name'],
        "lat": loc['lat'],
        "lon": loc['lon'],
        "accessible": True
    }

# Build graph connections between adjacent buildings
loc_list = list(locations)
for i in range(len(loc_list)):
    for j in range(i + 1, len(loc_list)):
        l1 = loc_list[i]
        l2 = loc_list[j]
        # Dist approximate in meters
        d = ((l1['lat'] - l2['lat'])**2 + (l1['lon'] - l2['lon'])**2)**0.5 * 111000
        if d < 150:
            edges.append({
                "from": l1['id'],
                "to": l2['id'],
                "weight": round(d, 1),
                "accessible": True
            })

campus_data = {
    "locations": locations,
    "graph": {
        "nodes": nodes,
        "edges": edges
    }
}

with open('public/data/campus_data.json', 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

with open('data/campus_data.json', 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

js_content = f"""// Global Failsafe Synchronous Embedded Dataset from OCU.kml
window.FALLBACK_CAMPUS_DATA = {json.dumps(campus_data, indent=2, ensure_ascii=False)};
window.FALLBACK_RAW_GEOJSON = {json.dumps(geojson, indent=2, ensure_ascii=False)};
"""

with open('js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

with open('public/js/campus_data_fallback.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Updated Drawing.geojson, campus_data.json, and campus_data_fallback.js cleanly!")
