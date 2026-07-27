import json
import math
import os
import heapq

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def segments_intersect(A, B, C, D):
    if min(A[0], B[0]) > max(C[0], D[0]) or max(A[0], B[0]) < min(C[0], D[0]):
        return False
    if min(A[1], B[1]) > max(C[1], D[1]) or max(A[1], B[1]) < min(C[1], D[1]):
        return False
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def point_in_polygon(x, y, poly):
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

# Deduplicate building polygons
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

# 1. Collect all building centroids / doors and building corners
all_nodes = {}

# Add building nodes (at polygon centroids or doors)
building_entrances = {
    'security_room': {"lat": 6.97478, "lon": 79.87177},
    'canteen': {"lat": 6.97565, "lon": 79.87157},
    'auditorium': {"lat": 6.97540, "lon": 79.87177},
    'gym': {"lat": 6.97583, "lon": 79.87155},
    'regional_center_mattakkuliya': {"lat": 6.97604, "lon": 79.87170}
}

for loc in locations:
    ent = building_entrances.get(loc['id'], {"lat": loc['lat'], "lon": loc['lon']})
    loc['lat'] = ent['lat']
    loc['lon'] = ent['lon']
    all_nodes[loc['id']] = {
        "id": loc['id'],
        "name": loc['name'],
        "lat": ent['lat'],
        "lon": ent['lon'],
        "isBuilding": True
    }

# 2. Extract polygon corner vertices and buffer them slightly (1-2 meters out)
corner_nodes = []
c_idx = 0

for p in polygons:
    coords = p['coords']
    centroid_lat = sum(c[1] for c in coords) / len(coords)
    centroid_lon = sum(c[0] for c in coords) / len(coords)
    
    for pt in coords[:-1]: # unique corners
        lon, lat = pt[0], pt[1]
        # Buffer vertex 1.5 meters away from centroid to place it on outdoor walkway
        d_lat = lat - centroid_lat
        d_lon = lon - centroid_lon
        norm = math.sqrt(d_lat*d_lat + d_lon*d_lon)
        if norm > 0:
            buf_lat = lat + (d_lat / norm) * 0.00003 # ~3 meters outward
            buf_lon = lon + (d_lon / norm) * 0.00003
        else:
            buf_lat, buf_lon = lat, lon
        
        # Verify point is outdoors (not inside any building polygon)
        is_inside = any(point_in_polygon(buf_lon, buf_lat, poly['coords']) for poly in polygons)
        if not is_inside:
            node_id = f"corner_{c_idx}"
            c_idx += 1
            corner_nodes.append({
                "id": node_id,
                "name": f"Walkway Corner near {p['name']}",
                "lat": round(buf_lat, 6),
                "lon": round(buf_lon, 6),
                "isBuilding": False,
                "buildingName": p['name']
            })

print(f"Extracted {len(corner_nodes)} outdoor corner waypoints.")

for c in corner_nodes:
    all_nodes[c['id']] = c

# 3. Construct Visibility Graph by testing all pairs
node_list = list(all_nodes.values())
N = len(node_list)
valid_edges = []
added_pairs = set()

print(f"Building Visibility Graph across {N} nodes...")

for i in range(N):
    n1 = node_list[i]
    p1 = [n1['lat'], n1['lon']]
    
    for j in range(i + 1, N):
        n2 = node_list[j]
        d = haversine(n1['lat'], n1['lon'], n2['lat'], n2['lon'])
        
        # Max visibility range threshold (60 meters) for dense realistic paths
        if d > 55:
            continue
        
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

print(f"Constructed Visibility Graph with {len(all_nodes)} nodes and {len(valid_edges)} 100% obstacle-free edges.")

# Update campus_data
campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
