import json
import math
import os

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

def point_in_polygon(x, y, poly):
    # x=lon, y=lat
    n = len(poly)
    inside = False
    p1x, p1y = poly[0][0], poly[0][1]
    for i in range(n + 1):
        p2x, p2y = poly[i % n][0], poly[i % n][1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def segments_intersect(A, B, C, D):
    if min(A[0], B[0]) > max(C[0], D[0]) or max(A[0], B[0]) < min(C[0], D[0]):
        return False
    if min(A[1], B[1]) > max(C[1], D[1]) or max(A[1], B[1]) < min(C[1], D[1]):
        return False
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def segment_intersects_any_polygon(p1, p2, polygons, ignore_names=[]):
    A = [p1[1], p1[0]]
    B = [p2[1], p2[0]]
    
    for poly_info in polygons:
        if poly_info['name'] in ignore_names:
            continue
        coords = poly_info['coords']
        n = len(coords)
        for i in range(n - 1):
            C = coords[i][:2]
            D = coords[i+1][:2]
            if (abs(A[0]-C[0])<1e-6 and abs(A[1]-C[1])<1e-6) or (abs(A[0]-D[0])<1e-6 and abs(A[1]-D[1])<1e-6):
                continue
            if (abs(B[0]-C[0])<1e-6 and abs(B[1]-C[1])<1e-6) or (abs(B[0]-D[0])<1e-6 and abs(B[1]-D[1])<1e-6):
                continue
            if segments_intersect(A, B, C, D):
                return True
    return False

geojson_path = r'c:\Users\HP\OneDrive\Desktop\Map\Drawing.geojson'
output_dir = r'c:\Users\HP\OneDrive\Desktop\Map\public\data'

with open(geojson_path, 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Deduplicate polygons to 32 clean building boundaries
unique_polys = {}
for feat in geojson_data.get('features', []):
    if feat.get('geometry', {}).get('type') == 'Polygon':
        name = feat.get('properties', {}).get('name')
        if name:
            name = name.strip()
            coords = feat.get('geometry', {}).get('coordinates')[0]
            if name not in unique_polys:
                unique_polys[name] = coords

polygons = [{'name': k, 'coords': v} for k, v in unique_polys.items()]

campus_data_path = os.path.join(output_dir, 'campus_data.json')
with open(campus_data_path, 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

locations = campus_data['locations']

# 1. Building Entrance Doors - Strictly on OUTDOOR PERIMETER WALKAWAY (never inside interior)
building_entrances = {
    'security_room': {"lat": 6.97478, "lon": 79.87177, "door": "Main South Gate"},
    'sport_room': {"lat": 6.97495, "lon": 79.87170, "door": "West Door"},
    'union_room': {"lat": 6.97492, "lon": 79.87171, "door": "West Door"},
    'mtl_hall_04': {"lat": 6.97490, "lon": 79.87180, "door": "South Door"},
    'mtl_hall_03': {"lat": 6.97506, "lon": 79.87210, "door": "South Door"},
    'lecturers_washroom': {"lat": 6.97507, "lon": 79.87215, "door": "South Door"},
    'class_room_07': {"lat": 6.97508, "lon": 79.87219, "door": "South Door"},
    'volly_ball_court': {"lat": 6.97514, "lon": 79.87225, "door": "East Access"},
    'badminton_court': {"lat": 6.97519, "lon": 79.87203, "door": "North Access"},
    'lectueres_room': {"lat": 6.97491, "lon": 79.87184, "door": "South Entrance"},
    'training_and_account_division': {"lat": 6.97528, "lon": 79.87168, "door": "West Door"},
    'auditorium': {"lat": 6.97540, "lon": 79.87177, "door": "North Entrance"},
    'mtl_hall_02': {"lat": 6.97533, "lon": 79.87193, "door": "East Door"},
    'storage_room': {"lat": 6.97532, "lon": 79.87191, "door": "East Door"},
    'mtl_hall_01': {"lat": 6.97528, "lon": 79.87241, "door": "North Door"},
    'class_room_02': {"lat": 6.97525, "lon": 79.87234, "door": "North Door"},
    'class_room_03': {"lat": 6.97524, "lon": 79.87228, "door": "North Door"},
    'drawing_room': {"lat": 6.97523, "lon": 79.87216, "door": "North Door"},
    'class_room_04': {"lat": 6.97521, "lon": 79.87208, "door": "North Door"},
    'students_wash_room': {"lat": 6.97526, "lon": 79.87209, "door": "North Door"},
    'transport_division': {"lat": 6.97528, "lon": 79.87209, "door": "North Door"},
    'it_lab': {"lat": 6.97534, "lon": 79.87208, "door": "North Entrance"},
    'chart_room': {"lat": 6.97541, "lon": 79.87207, "door": "North Door"},
    'workshop': {"lat": 6.97562, "lon": 79.87186, "door": "West Gate Door"},
    'welding_workshop': {"lat": 6.97571, "lon": 79.87208, "door": "North Door"},
    'canteen': {"lat": 6.97565, "lon": 79.87157, "door": "Main Canteen Door"},
    'gym': {"lat": 6.97583, "lon": 79.87155, "door": "Gym Entrance"},
    'boys_hostals': {"lat": 6.97578, "lon": 79.87166, "door": "Hostel Gate Door"},
    'regional_center_mattakkuliya': {"lat": 6.97604, "lon": 79.87170, "door": "North Gate Door"},
    'class_room_08': {"lat": 6.97488, "lon": 79.87222, "door": "South Door"},
    'lab': {"lat": 6.97484, "lon": 79.87203, "door": "South Door"},
    'classrooms': {"lat": 6.97502, "lon": 79.87181, "door": "South Entrance"}
}

all_nodes = {}
for loc in locations:
    ent = building_entrances.get(loc['id'], {"lat": loc['lat'], "lon": loc['lon']})
    loc['lat'] = ent['lat']
    loc['lon'] = ent['lon']
    loc['doorName'] = ent.get('door', 'Main Entrance')
    all_nodes[loc['id']] = {
        "id": loc['id'],
        "name": loc['name'],
        "lat": ent['lat'],
        "lon": ent['lon'],
        "isBuilding": True
    }

# 2. Corner Waypoints with 2.5m Buffer
corner_nodes = []
c_idx = 0

for p in polygons:
    coords = p['coords']
    centroid_lat = sum(c[1] for c in coords) / len(coords)
    centroid_lon = sum(c[0] for c in coords) / len(coords)
    
    for pt in coords[:-1]:
        lon, lat = pt[0], pt[1]
        d_lat = lat - centroid_lat
        d_lon = lon - centroid_lon
        norm = math.sqrt(d_lat*d_lat + d_lon*d_lon)
        if norm > 0:
            buf_lat = lat + (d_lat / norm) * 0.000028 # ~2.5m buffer
            buf_lon = lon + (d_lon / norm) * 0.000028
        else:
            buf_lat, buf_lon = lat, lon
        
        is_inside = any(point_in_polygon(buf_lon, buf_lat, poly['coords']) for poly in polygons)
        if not is_inside:
            node_id = f"corner_{c_idx}"
            c_idx += 1
            corner_nodes.append({
                "id": node_id,
                "name": f"Pedestrian Walkway near {p['name']}",
                "lat": round(buf_lat, 6),
                "lon": round(buf_lon, 6),
                "isBuilding": False,
                "buildingName": p['name']
            })

for c in corner_nodes:
    all_nodes[c['id']] = c

# 3. Construct 100% Obstacle-Free Visibility Graph
node_list = list(all_nodes.values())
N = len(node_list)
valid_edges = []
added_pairs = set()

for i in range(N):
    n1 = node_list[i]
    p1 = [n1['lat'], n1['lon']]
    
    for j in range(i + 1, N):
        n2 = node_list[j]
        d = haversine(n1['lat'], n1['lon'], n2['lat'], n2['lon'])
        
        if d > 55: continue
        
        p2 = [n2['lat'], n2['lon']]
        
        ignore_names = []
        if n1.get('isBuilding'): ignore_names.append(n1['name'])
        if n2.get('isBuilding'): ignore_names.append(n2['name'])
        if n1.get('buildingName'): ignore_names.append(n1['buildingName'])
        if n2.get('buildingName'): ignore_names.append(n2['buildingName'])
        
        check_polys = [p for p in polygons if p['name'] not in ignore_names]
        
        if not segment_intersects_any_polygon(p1, p2, check_polys):
            pair = tuple(sorted([n1['id'], n2['id']]))
            if pair not in added_pairs:
                added_pairs.add(pair)
                valid_edges.append({
                    "source": n1['id'],
                    "target": n2['id'],
                    "distance": d,
                    "isAccessible": True
                })

print(f"Human Walkways v2 Graph: {len(all_nodes)} nodes, {len(valid_edges)} edges.")

campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
