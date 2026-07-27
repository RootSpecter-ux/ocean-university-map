import json
import math
import heapq

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

with open(r'c:\Users\HP\OneDrive\Desktop\Map\Drawing.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

polygons = []
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

with open(r'c:\Users\HP\OneDrive\Desktop\Map\public\data\campus_data.json', 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

nodes = {n['id']: n for n in campus_data['graph']['nodes']}
edges = campus_data['graph']['edges']
locations = campus_data['locations']

adj = {n: [] for n in nodes}
for e in edges:
    adj[e['source']].append((e['target'], e['distance']))
    adj[e['target']].append((e['source'], e['distance']))

def get_path(start, goal):
    queue = [(0, start, [start])]
    visited = set()
    while queue:
        (d, current, path) = heapq.heappop(queue)
        if current in visited: continue
        visited.add(current)
        if current == goal: return path
        for (neighbor, dist) in adj.get(current, []):
            if neighbor not in visited:
                heapq.heappush(queue, (d + dist, neighbor, path + [neighbor]))
    return None

print(f"Auditing ALL pair combinations across {len(locations)} locations...")
total_pairs = 0
violations_found = []

for i, loc1 in enumerate(locations):
    for j, loc2 in enumerate(locations):
        if i >= j: continue
        total_pairs += 1
        
        path_nodes = get_path(loc1['id'], loc2['id'])
        if not path_nodes:
            violations_found.append({
                "type": "NO_PATH",
                "pair": f"{loc1['name']} <-> {loc2['name']}"
            })
            continue
        
        path_coords = [[nodes[nid]['lat'], nodes[nid]['lon']] for nid in path_nodes]
        for step_idx in range(len(path_coords) - 1):
            p1 = path_coords[step_idx]
            p2 = path_coords[step_idx + 1]
            n1 = nodes[path_nodes[step_idx]]
            n2 = nodes[path_nodes[step_idx + 1]]
            
            ignore = []
            if n1.get('isBuilding'): ignore.append(n1['name'])
            if n2.get('isBuilding'): ignore.append(n2['name'])
            if n1.get('buildingName'): ignore.append(n1['buildingName'])
            if n2.get('buildingName'): ignore.append(n2['buildingName'])
            
            for poly in polygons:
                if segment_intersects_polygon_strict(p1, p2, poly['coords'], poly['name'], ignore_names=ignore):
                    violations_found.append({
                        "type": "WALL_CROSS",
                        "pair": f"{loc1['name']} <-> {loc2['name']}",
                        "segment": f"{n1['name']} -> {n2['name']}",
                        "building": poly['name']
                    })

print(f"\nAudited {total_pairs} location pair paths.")
if not violations_found:
    print("SUCCESS! ALL origin-destination pairs across campus have 0 wall violations!")
else:
    print(f"Found {len(violations_found)} issues:")
    for v in violations_found[:10]:
        print(f" - {v}")
