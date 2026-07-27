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

# 1. Building Door Entrance Locations (On outer perimeter edge)
building_entrances = {
    'security_room': {"lat": 6.97478, "lon": 79.87177},
    'sport_room': {"lat": 6.97495, "lon": 79.87170},
    'union_room': {"lat": 6.97492, "lon": 79.87171},
    'mtl_hall_04': {"lat": 6.97490, "lon": 79.87180},
    'mtl_hall_03': {"lat": 6.97506, "lon": 79.87210},
    'lecturers_washroom': {"lat": 6.97507, "lon": 79.87215},
    'class_room_07': {"lat": 6.97508, "lon": 79.87219},
    'volly_ball_court': {"lat": 6.97514, "lon": 79.87225},
    'badminton_court': {"lat": 6.97519, "lon": 79.87203},
    'lectueres_room': {"lat": 6.97491, "lon": 79.87184},
    'training_and_account_division': {"lat": 6.97528, "lon": 79.87168},
    'auditorium': {"lat": 6.97540, "lon": 79.87177},
    'mtl_hall_02': {"lat": 6.97533, "lon": 79.87193},
    'storage_room': {"lat": 6.97532, "lon": 79.87191},
    'mtl_hall_01': {"lat": 6.97528, "lon": 79.87241},
    'class_room_02': {"lat": 6.97525, "lon": 79.87234},
    'class_room_03': {"lat": 6.97524, "lon": 79.87228},
    'drawing_room': {"lat": 6.97523, "lon": 79.87216},
    'class_room_04': {"lat": 6.97521, "lon": 79.87208},
    'students_wash_room': {"lat": 6.97526, "lon": 79.87209},
    'transport_division': {"lat": 6.97528, "lon": 79.87209},
    'it_lab': {"lat": 6.97534, "lon": 79.87208},
    'chart_room': {"lat": 6.97541, "lon": 79.87207},
    'workshop': {"lat": 6.97562, "lon": 79.87186},
    'welding_workshop': {"lat": 6.97571, "lon": 79.87208},
    'canteen': {"lat": 6.97565, "lon": 79.87157},
    'gym': {"lat": 6.97583, "lon": 79.87155},
    'boys_hostals': {"lat": 6.97578, "lon": 79.87166},
    'regional_center_mattakkuliya': {"lat": 6.97604, "lon": 79.87170},
    'class_room_08': {"lat": 6.97488, "lon": 79.87222},
    'lab': {"lat": 6.97484, "lon": 79.87203},
    'classrooms': {"lat": 6.97502, "lon": 79.87181}
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

# 2. Outdoor Corridor Waypoints (Clear of all building polygons)
walkway_waypoints = [
    # WEST OUTDOOR HIGHWAY (Lon = 79.87154)
    {"id": "w_gate_stub", "name": "Main Gate Outdoor Connector", "lat": 6.97478, "lon": 79.87154},
    {"id": "w_west_road_south", "name": "West Outdoor Highway (South)", "lat": 6.97495, "lon": 79.87154},
    {"id": "w_west_road_training", "name": "West Outdoor Highway (Training & Account)", "lat": 6.97528, "lon": 79.87154},
    {"id": "w_west_road_cross", "name": "West Outdoor Highway (North Cross)", "lat": 6.97541, "lon": 79.87154},
    {"id": "w_west_road_canteen", "name": "West Outdoor Highway (Canteen Access)", "lat": 6.97565, "lon": 79.87154},
    {"id": "w_west_road_gym", "name": "West Outdoor Highway (Gym & Hostels)", "lat": 6.97583, "lon": 79.87154},
    {"id": "w_west_road_north", "name": "West Outdoor Highway (North Gate)", "lat": 6.97604, "lon": 79.87154},

    # NORTH CROSS ALLEYWAY (Lat = 6.97541 - Between Auditorium/Training & Workshop)
    {"id": "w_north_cross_mid", "name": "North Cross Alleyway (Central)", "lat": 6.97541, "lon": 79.87177},

    # SOUTH EAST CONNECTOR ROAD (Lat = 6.97478)
    {"id": "w_south_east_connector", "name": "South Outdoor Connector Path", "lat": 6.97478, "lon": 79.87203},

    # EAST OUTDOOR HIGHWAYS
    {"id": "w_east_corridor_south", "name": "East Outdoor Walkway (South)", "lat": 6.97484, "lon": 79.87203},
    {"id": "w_east_corridor_mid", "name": "East Outdoor Walkway (Mid)", "lat": 6.97541, "lon": 79.87205},
    {"id": "w_east_corridor_north", "name": "East Outdoor Walkway (North)", "lat": 6.97571, "lon": 79.87205},

    # FAR EAST CLASSROOMS HIGHWAY (Lon = 79.87260)
    {"id": "w_far_east_south", "name": "Far East Walkway (South)", "lat": 6.97514, "lon": 79.87260},
    {"id": "w_far_east_mid", "name": "Far East Walkway (Mid)", "lat": 6.97528, "lon": 79.87260}
]

for w in walkway_waypoints:
    all_nodes[w['id']] = {
        "id": w['id'],
        "name": w['name'],
        "lat": w['lat'],
        "lon": w['lon'],
        "isBuilding": False
    }

# 3. Candidate Edges to Connect Graph
connections = [
    # Gate -> West Highway Spine
    ("security_room", "w_gate_stub"),
    ("w_gate_stub", "w_west_road_south"),
    ("w_west_road_south", "sport_room"),
    ("w_west_road_south", "union_room"),
    ("w_west_road_south", "w_west_road_training"),

    # West Highway Spine -> Training & Account, Canteen, Gym, Hostels, Regional Center
    ("w_west_road_training", "training_and_account_division"),
    ("w_west_road_training", "w_west_road_cross"),
    ("w_west_road_cross", "auditorium"),
    ("w_west_road_cross", "w_north_cross_mid"),
    ("w_west_road_cross", "w_west_road_canteen"),
    ("w_west_road_canteen", "canteen"),
    ("w_west_road_canteen", "w_west_road_gym"),
    ("w_west_road_gym", "gym"),
    ("w_west_road_gym", "boys_hostals"),
    ("w_west_road_gym", "w_west_road_north"),
    ("w_west_road_north", "regional_center_mattakkuliya"),

    # Gate -> South East Connector
    ("security_room", "w_south_east_connector"),
    ("w_south_east_connector", "lab"),
    ("w_south_east_connector", "w_east_corridor_south"),

    # East Corridor South -> Classrooms 08, Lecturers, MTL Hall 04, MTL Hall 03
    ("w_east_corridor_south", "class_room_08"),
    ("w_east_corridor_south", "lectueres_room"),
    ("w_east_corridor_south", "mtl_hall_04"),
    ("w_east_corridor_south", "mtl_hall_03"),
    ("w_east_corridor_south", "lecturers_washroom"),
    ("w_east_corridor_south", "class_room_07"),
    ("w_east_corridor_south", "badminton_court"),
    ("w_east_corridor_south", "volly_ball_court"),
    ("w_east_corridor_south", "w_far_east_south"),
    ("w_east_corridor_south", "w_east_corridor_mid"),

    # North Cross Alleyway -> East Corridor Mid
    ("w_north_cross_mid", "workshop"),
    ("w_north_cross_mid", "w_east_corridor_mid"),

    # East Corridor Mid -> IT Lab, Transport, Washroom, Classrooms 02/03/04, Drawing Room
    ("w_east_corridor_mid", "classrooms"),
    ("w_east_corridor_mid", "mtl_hall_02"),
    ("w_east_corridor_mid", "storage_room"),
    ("w_east_corridor_mid", "class_room_04"),
    ("w_east_corridor_mid", "drawing_room"),
    ("w_east_corridor_mid", "class_room_03"),
    ("w_east_corridor_mid", "class_room_02"),
    ("w_east_corridor_mid", "mtl_hall_01"),
    ("w_east_corridor_mid", "students_wash_room"),
    ("w_east_corridor_mid", "transport_division"),
    ("w_east_corridor_mid", "it_lab"),
    ("w_east_corridor_mid", "chart_room"),
    ("w_east_corridor_mid", "w_east_corridor_north"),
    ("w_east_corridor_mid", "w_far_east_mid"),

    # Far East Highway
    ("w_far_east_south", "w_far_east_mid"),
    ("w_far_east_mid", "mtl_hall_01"),
    ("w_far_east_mid", "class_room_02"),

    # East Corridor North -> Welding Workshop
    ("w_east_corridor_north", "welding_workshop"),
    ("w_east_corridor_north", "workshop")
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
    
    ignore_names = []
    if n1['isBuilding']: ignore_names.append(n1['name'])
    if n2['isBuilding']: ignore_names.append(n2['name'])
    
    check_polys = [p for p in polygons if p['name'] not in ignore_names]
    
    intersects = segment_intersects_any_polygon(p1, p2, check_polys)
    
    if intersects:
        print(f"REJECTED EDGE: ({u} <-> {v}) intersects a building wall!")
        rejected += 1
        continue

    added_pairs.add(pair)
    d = haversine(p1[0], p1[1], p2[0], p2[1])
    valid_edges.append({
        "source": u,
        "target": v,
        "distance": d,
        "isAccessible": True
    })

print(f"\nFinal Graph: {len(all_nodes)} nodes, {len(valid_edges)} 100% outdoor edges. Rejected {rejected} clipping edges.")

campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
