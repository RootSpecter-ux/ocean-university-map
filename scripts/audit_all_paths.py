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
        # Ignore shared exact endpoints
        if (abs(A[0]-C[0])<1e-6 and abs(A[1]-C[1])<1e-6) or (abs(A[0]-D[0])<1e-6 and abs(A[1]-D[1])<1e-6):
            continue
        if (abs(B[0]-C[0])<1e-6 and abs(B[1]-C[1])<1e-6) or (abs(B[0]-D[0])<1e-6 and abs(B[1]-D[1])<1e-6):
            continue
        if segments_intersect(A, B, C, D):
            return True
    return False

# Load GeoJSON
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

# Load campus_data.json
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

print("Auditing all 31 destination paths from Security Room...")
violations_found = []

for loc in locations:
    if loc['id'] == 'security_room': continue
    
    path_nodes = get_path('security_room', loc['id'])
    if not path_nodes:
        print(f"❌ NO PATH FOUND to {loc['name']}")
        continue
    
    # Check each segment of the calculated path against all 32 building polygons
    path_coords = [[nodes[nid]['lat'], nodes[nid]['lon']] for nid in path_nodes]
    
    has_violation = False
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
                has_violation = True
                violations_found.append({
                    "dest": loc['name'],
                    "segment": f"Step {step_idx+1}: {n1['name']} -> {n2['name']}",
                    "crossed_building": poly['name']
                })

if not violations_found:
    print("\nSUCCESS! 0 wall violations found across all 31 destination paths!")
else:
    print(f"\nFOUND {len(violations_found)} WALL VIOLATIONS across paths:")
    for v in violations_found:
        print(f" - Path to [{v['dest']}]: {v['segment']} cuts through [{v['crossed_building']}]")
