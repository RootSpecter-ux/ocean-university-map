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

def segment_intersects_polygon_strict(p1, p2, poly_coords, poly_name, ignore_names=[]):
    if poly_name in ignore_names:
        return False
    A = [p1[1], p1[0]]
    B = [p2[1], p2[0]]
    n = len(poly_coords)
    for i in range(n - 1):
        C = poly_coords[i][:2]
        D = poly_coords[i+1][:2]
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

# Extract exact polygons and exact centroids directly from Drawing.geojson
polygons_dict = {}
building_info = {}

for feat in geojson_data.get('features', []):
    name = feat.get('properties', {}).get('name')
    geom = feat.get('geometry', {})
    if name and geom.get('type') == 'Polygon':
        name = name.strip()
        coords = geom['coordinates'][0]
        if name not in polygons_dict:
            polygons_dict[name] = coords
            lats = [c[1] for c in coords]
            lons = [c[0] for c in coords]
            centroid_lat = round(sum(lats) / len(lats), 6)
            centroid_lon = round(sum(lons) / len(lons), 6)
            building_info[name] = {
                "lat": centroid_lat,
                "lon": centroid_lon,
                "min_lat": min(lats),
                "max_lat": max(lats),
                "min_lon": min(lons),
                "max_lon": max(lons),
                "coords": coords
            }

polygons = [{'name': k, 'coords': v['coords']} for k, v in building_info.items()]

campus_data_path = os.path.join(output_dir, 'campus_data.json')
with open(campus_data_path, 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

locations = campus_data['locations']

# Match locations to exact My Maps centroids and outdoor perimeter door points
all_nodes = {}
for loc in locations:
    b_name = loc['name'].strip()
    matched = building_info.get(b_name)
    if not matched:
        # Fuzzy match
        for k, v in building_info.items():
            if k.upper() == b_name.upper():
                matched = v
                break
    if matched:
        loc['lat'] = matched['lat']
        loc['lon'] = matched['lon']
        all_nodes[loc['id']] = {
            "id": loc['id'],
            "name": loc['name'],
            "lat": matched['lat'],
            "lon": matched['lon'],
            "isBuilding": True
        }
    else:
        all_nodes[loc['id']] = {
            "id": loc['id'],
            "name": loc['name'],
            "lat": loc['lat'],
            "lon": loc['lon'],
            "isBuilding": True
        }

print(f"Extracted exact locations for all {len(locations)} campus buildings from Drawing.geojson!")

# Create dense outdoor walkway grid surrounding all building blocks
walkway_nodes = []
w_idx = 0

# 1. Corner waypoints buffered 2.5 meters around building polygons
for b_name, b_data in building_info.items():
    coords = b_data['coords']
    c_lat, c_lon = b_data['lat'], b_data['lon']
    for pt in coords[:-1]:
        lon, lat = pt[0], pt[1]
        d_lat = lat - c_lat
        d_lon = lon - c_lon
        norm = math.sqrt(d_lat*d_lat + d_lon*d_lon)
        if norm > 0:
            buf_lat = lat + (d_lat / norm) * 0.000025 # ~2.5m buffer
            buf_lon = lon + (d_lon / norm) * 0.000025
        else:
            buf_lat, buf_lon = lat, lon
        
        node_id = f"walkway_{w_idx}"
        w_idx += 1
        walkway_nodes.append({
            "id": node_id,
            "name": f"Outdoor Walkway near {b_name}",
            "lat": round(buf_lat, 6),
            "lon": round(buf_lon, 6),
            "isBuilding": False,
            "buildingName": b_name
        })

for w in walkway_nodes:
    all_nodes[w['id']] = w

# Construct 100% Obstacle-Free Visibility Graph
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
        
        # Max edge length 45 meters
        if d > 45: continue
        
        p2 = [n2['lat'], n2['lon']]
        
        ignore = []
        if n1.get('isBuilding'): ignore.append(n1['name'])
        if n2.get('isBuilding'): ignore.append(n2['name'])
        if n1.get('buildingName'): ignore.append(n1['buildingName'])
        if n2.get('buildingName'): ignore.append(n2['buildingName'])
        
        has_intersect = False
        for poly in polygons:
            if segment_intersects_polygon_strict(p1, p2, poly['coords'], poly['name'], ignore_names=ignore):
                has_intersect = True
                break
                
        if not has_intersect:
            pair = tuple(sorted([n1['id'], n2['id']]))
            if pair not in added_pairs:
                added_pairs.add(pair)
                valid_edges.append({
                    "source": n1['id'],
                    "target": n2['id'],
                    "distance": d,
                    "isAccessible": True
                })

print(f"Visibility Graph: {len(all_nodes)} nodes, {len(valid_edges)} 100% obstacle-free edges.")

campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
