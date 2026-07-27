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

def segment_intersects_polygon_strict(p1, p2, poly_coords):
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

# 1. Door Access Endpoints (Outdoors on perimeter)
building_entrances = {
    'security_room': {"lat": 6.97475, "lon": 79.87177},
    'sport_room': {"lat": 6.97494, "lon": 79.87170},
    'union_room': {"lat": 6.97490, "lon": 79.87171},
    'mtl_hall_04': {"lat": 6.97489, "lon": 79.87180},
    'mtl_hall_03': {"lat": 6.97507, "lon": 79.87210},
    'lecturers_washroom': {"lat": 6.97508, "lon": 79.87215},
    'class_room_07': {"lat": 6.97509, "lon": 79.87219},
    'volly_ball_court': {"lat": 6.97515, "lon": 79.87225},
    'badminton_court': {"lat": 6.97521, "lon": 79.87203},
    'lectueres_room': {"lat": 6.97490, "lon": 79.87184},
    'training_and_account_division': {"lat": 6.97528, "lon": 79.87168},
    'auditorium': {"lat": 6.97542, "lon": 79.87177},
    'mtl_hall_02': {"lat": 6.97534, "lon": 79.87193},
    'storage_room': {"lat": 6.97533, "lon": 79.87191},
    'mtl_hall_01': {"lat": 6.97529, "lon": 79.87241},
    'class_room_02': {"lat": 6.97527, "lon": 79.87234},
    'class_room_03': {"lat": 6.97526, "lon": 79.87228},
    'drawing_room': {"lat": 6.97525, "lon": 79.87216},
    'class_room_04': {"lat": 6.97523, "lon": 79.87208},
    'students_wash_room': {"lat": 6.97527, "lon": 79.87209},
    'transport_division': {"lat": 6.97529, "lon": 79.87209},
    'it_lab': {"lat": 6.97535, "lon": 79.87208},
    'chart_room': {"lat": 6.97543, "lon": 79.87207},
    'workshop': {"lat": 6.97563, "lon": 79.87172},
    'welding_workshop': {"lat": 6.97572, "lon": 79.87208},
    'canteen': {"lat": 6.97565, "lon": 79.87157},
    'gym': {"lat": 6.97584, "lon": 79.87155},
    'boys_hostals': {"lat": 6.97593, "lon": 79.87166},
    'regional_center_mattakkuliya': {"lat": 6.97612, "lon": 79.87170},
    'class_room_08': {"lat": 6.97482, "lon": 79.87222},
    'lab': {"lat": 6.97482, "lon": 79.87204},
    'classrooms': {"lat": 6.97501, "lon": 79.87180}
}

all_nodes = {}
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

# 2. Open Pedestrian Highway Nodes (100% Outdoor Open Spaces)
walkway_waypoints = [
    # WEST HIGHWAY (Lon = 79.87154)
    {"id": "w_west_01", "name": "Main Gate West Exit", "lat": 6.97475, "lon": 79.87154},
    {"id": "w_west_02", "name": "West Outdoor Highway (Sport/Union)", "lat": 6.97494, "lon": 79.87154},
    {"id": "w_west_03", "name": "West Outdoor Highway (Training Division)", "lat": 6.97528, "lon": 79.87154},
    {"id": "w_west_04", "name": "West Outdoor Highway (Auditorium/Canteen)", "lat": 6.97565, "lon": 79.87154},
    {"id": "w_west_05", "name": "West Outdoor Highway (Gym & Hostels)", "lat": 6.97593, "lon": 79.87154},
    {"id": "w_west_06", "name": "West Outdoor Highway (Regional Center)", "lat": 6.97612, "lon": 79.87154},

    # SOUTH OUTDOOR ALLEY (Lat = 6.97482, South of Lab & Class Room 08)
    {"id": "w_south_01", "name": "South Outdoor Alley (Lab Entrance)", "lat": 6.97482, "lon": 79.87204},
    {"id": "w_south_02", "name": "South Outdoor Alley (Classroom 08 Entrance)", "lat": 6.97482, "lon": 79.87222},
    {"id": "w_south_03", "name": "South-East Highway Junction", "lat": 6.97482, "lon": 79.87265},

    # EAST OUTDOOR HIGHWAY (Lon = 79.87265, East of all eastern buildings)
    {"id": "w_east_01", "name": "East Outdoor Highway (Courts/Classroom 07)", "lat": 6.97509, "lon": 79.87265},
    {"id": "w_east_02", "name": "East Outdoor Highway (MTL 01 / Classrooms)", "lat": 6.97529, "lon": 79.87265},
    {"id": "w_east_03", "name": "East Outdoor Highway (North Workshop Alley)", "lat": 6.97572, "lon": 79.87265},

    # NORTH WORKSHOP ALLEY (Lat = 6.97572, North of Workshop)
    {"id": "w_north_01", "name": "North Workshop Alley (Welding Workshop)", "lat": 6.97572, "lon": 79.87208}
]

for w in walkway_waypoints:
    all_nodes[w['id']] = {
        "id": w['id'],
        "name": w['name'],
        "lat": w['lat'],
        "lon": w['lon'],
        "isBuilding": False
    }

# 3. Candidate Edges
connections = [
    # West Highway Spine
    ("security_room", "w_west_01"),
    ("w_west_01", "w_west_02"),
    ("w_west_02", "sport_room"),
    ("w_west_02", "union_room"),
    ("w_west_02", "mtl_hall_04"),
    ("w_west_02", "lectueres_room"),
    ("w_west_02", "w_west_03"),

    ("w_west_03", "training_and_account_division"),
    ("w_west_03", "auditorium"),
    ("w_west_03", "classrooms"),
    ("w_west_03", "w_west_04"),

    ("w_west_04", "canteen"),
    ("w_west_04", "workshop"),
    ("w_west_04", "w_west_05"),

    ("w_west_05", "gym"),
    ("w_west_05", "boys_hostals"),
    ("w_west_05", "w_west_06"),

    ("w_west_06", "regional_center_mattakkuliya"),

    # South Alley Spine (South of Lab / Class Room 08)
    ("security_room", "w_south_01"),
    ("w_south_01", "lab"),
    ("w_south_01", "w_south_02"),

    ("w_south_02", "class_room_08"),
    ("w_south_02", "w_south_03"),

    # East Highway Spine (East of all eastern buildings)
    ("w_south_03", "w_east_01"),
    ("w_east_01", "volly_ball_court"),
    ("w_east_01", "class_room_07"),
    ("w_east_01", "lecturers_washroom"),
    ("w_east_01", "mtl_hall_03"),
    ("w_east_01", "badminton_court"),
    ("w_east_01", "w_east_02"),

    ("w_east_02", "mtl_hall_01"),
    ("w_east_02", "class_room_02"),
    ("w_east_02", "class_room_03"),
    ("w_east_02", "drawing_room"),
    ("w_east_02", "class_room_04"),
    ("w_east_02", "students_wash_room"),
    ("w_east_02", "transport_division"),
    ("w_east_02", "it_lab"),
    ("w_east_02", "chart_room"),
    ("w_east_02", "mtl_hall_02"),
    ("w_east_02", "storage_room"),
    ("w_east_02", "w_east_03"),

    # North Workshop Alley
    ("w_east_03", "w_north_01"),
    ("w_north_01", "welding_workshop")
]

valid_edges = []
added_pairs = set()
rejected = 0

for u, v in connections:
    pair = tuple(sorted([u, v]))
    if pair in added_pairs or u not in all_nodes or v not in all_nodes:
        continue
    
    n1 = all_nodes[u]
    n2 = all_nodes[v]
    
    p1 = [n1['lat'], n1['lon']]
    p2 = [n2['lat'], n2['lon']]
    
    # Check STRICTLY against ALL 32 building polygons without ignoring ANY polygon!
    has_intersection = False
    for poly in polygons:
        if segment_intersects_polygon_strict(p1, p2, poly['coords']):
            has_intersection = True
            print(f"STRICT REJECT: Edge ({u} <-> {v}) intersects [{poly['name']}]!")
            rejected += 1
            break
            
    if not has_intersection:
        added_pairs.add(pair)
        d = haversine(p1[0], p1[1], p2[0], p2[1])
        valid_edges.append({
            "source": u,
            "target": v,
            "distance": d,
            "isAccessible": True
        })

print(f"\nFinal Graph: {len(all_nodes)} nodes, {len(valid_edges)} 100% strict outdoor edges. Rejected {rejected} clipping edges.")

campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
