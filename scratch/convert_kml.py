import xml.etree.ElementTree as ET
import json
import os

def kml_to_geojson(kml_path):
    tree = ET.parse(kml_path)
    root = tree.getroot()
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

    features = []
    placemarks = root.findall('.//Placemark')
    
    for p in placemarks:
        name_elem = p.find('name')
        name = name_elem.text.strip() if name_elem is not None and name_elem.text else 'Unnamed Building'
        
        poly = p.find('.//Polygon')
        pt = p.find('.//Point')
        
        geom = None
        if poly is not None:
            coords_elem = poly.find('.//coordinates')
            if coords_elem is not None and coords_elem.text:
                raw_coords = coords_elem.text.strip().split()
                ring = []
                for c in raw_coords:
                    parts = c.split(',')
                    if len(parts) >= 2:
                        lon, lat = float(parts[0]), float(parts[1])
                        ring.append([lon, lat])
                if len(ring) > 2:
                    geom = {
                        'type': 'Polygon',
                        'coordinates': [ring]
                    }
        elif pt is not None:
            coords_elem = pt.find('coordinates')
            if coords_elem is not None and coords_elem.text:
                parts = coords_elem.text.strip().split(',')
                if len(parts) >= 2:
                    lon, lat = float(parts[0]), float(parts[1])
                    geom = {
                        'type': 'Point',
                        'coordinates': [lon, lat]
                    }
        
        if geom:
            features.append({
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'Name': name,
                    'description': f'Official Google My Maps Drawing for {name}'
                },
                'geometry': geom
            })
            
    return {
        'type': 'FeatureCollection',
        'features': features
    }

kml_file = r'C:\Users\HP\Downloads\OCU (1).kml'
if os.path.exists(kml_file):
    geojson = kml_to_geojson(kml_file)
    count = len(geojson['features'])
    print(f'Converted {count} features from KML!')

    with open('Drawing.geojson', 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
    print('Updated root Drawing.geojson successfully!')
