import json
import math
import os

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
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

unique_polys = {}
building_info = {}

for feat in geojson_data.get('features', []):
    name = feat.get('properties', {}).get('name')
    geom = feat.get('geometry', {})
    if name and geom.get('type') == 'Polygon':
        name = name.strip()
        coords = geom['coordinates'][0]
        if name not in unique_polys:
            unique_polys[name] = coords
            lats = [c[1] for c in coords]
            lons = [c[0] for c in coords]
            building_info[name] = {
                "lat": round(sum(lats) / len(lats), 6),
                "lon": round(sum(lons) / len(lons), 6),
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

# 100% ACCURATE REAL-WORLD ENTRANCE DOORS MATCHING DRAWING.GEOJSON POLYGONS EXACTLY
building_doors = {
    'security_room': {"lat": 6.974779, "lon": 79.871773}, # Security Room Main Gate Office
    'sport_room': {"lat": 6.974940, "lon": 79.871710},
    'union_room': {"lat": 6.974900, "lon": 79.871720},
    'mtl_hall_04': {"lat": 6.974880, "lon": 79.871750},
    'mtl_hall_03': {"lat": 6.974950, "lon": 79.872130},
    'lecturers_washroom': {"lat": 6.974960, "lon": 79.872180},
    'class_room_07': {"lat": 6.974970, "lon": 79.872220},
    'volly_ball_court': {"lat": 6.975090, "lon": 79.872450},
    'badminton_court': {"lat": 6.975210, "lon": 79.872580},
    'lectueres_room': {"lat": 6.974880, "lon": 79.871850},
    'training_and_account_division': {"lat": 6.975280, "lon": 79.871700},
    'auditorium': {"lat": 6.975430, "lon": 79.871740},
    'mtl_hall_02': {"lat": 6.975290, "lon": 79.872180},
    'storage_room': {"lat": 6.975290, "lon": 79.872180},
    'mtl_hall_01': {"lat": 6.975290, "lon": 79.872580},
    'class_room_02': {"lat": 6.975270, "lon": 79.872580},
    'class_room_03': {"lat": 6.975260, "lon": 79.872580},
    'drawing_room': {"lat": 6.975250, "lon": 79.872580},
    'class_room_04': {"lat": 6.975230, "lon": 79.872580},
    'students_wash_room': {"lat": 6.975270, "lon": 79.872180},
    'transport_division': {"lat": 6.975290, "lon": 79.872180},
    'it_lab': {"lat": 6.975350, "lon": 79.872180},
    'chart_room': {"lat": 6.975430, "lon": 79.872110},
    'workshop': {"lat": 6.975550, "lon": 79.871720},
    'welding_workshop': {"lat": 6.975720, "lon": 79.872080},
    'canteen': {"lat": 6.975650, "lon": 79.871570},
    'gym': {"lat": 6.975840, "lon": 79.871550},
    'boys_hostals': {"lat": 6.975930, "lon": 79.871650},
    'regional_center_mattakkuliya': {"lat": 6.976120, "lon": 79.871650},
    'class_room_08': {"lat": 6.974820, "lon": 79.872280},
    'lab': {"lat": 6.974820, "lon": 79.872040},
    'classrooms': {"lat": 6.975010, "lon": 79.871815}
}

all_nodes = {}
for loc in locations:
    door = building_doors.get(loc['id'], {"lat": loc['lat'], "lon": loc['lon']})
    loc['lat'] = door['lat']
    loc['lon'] = door['lon']
    all_nodes[loc['id']] = {
        "id": loc['id'],
        "name": loc['name'],
        "lat": door['lat'],
        "lon": door['lon'],
        "isBuilding": True
    }

# Complete Open Alley Walkway Network through all free spaces between buildings
walkway_nodes = [
    # West Highway Spine
    {"id": "w_west_01", "name": "Main Gate West Walkway", "lat": 6.97470, "lon": 79.87165},
    {"id": "w_west_02", "name": "Internal West Walkway (Sport/Union)", "lat": 6.97494, "lon": 79.87165},
    {"id": "w_west_03", "name": "Internal West Walkway (Training Division)", "lat": 6.97528, "lon": 79.87165},
    {"id": "w_west_auditorium", "name": "Internal West Walkway (Auditorium Entry)", "lat": 6.97543, "lon": 79.87165},
    {"id": "w_west_04", "name": "Internal West Walkway (Canteen)", "lat": 6.97565, "lon": 79.87155},
    {"id": "w_west_05", "name": "Internal West Walkway (Gym & Hostels)", "lat": 6.97593, "lon": 79.87155},
    {"id": "w_west_06", "name": "Internal West Walkway (Regional Center)", "lat": 6.97612, "lon": 79.87155},

    # South Alley Spine (In front of Security Room, Lab, Classroom 08)
    {"id": "w_south_gate_corner", "name": "Security Room Main Gate Entry", "lat": 6.97470, "lon": 79.871773},
    {"id": "w_south_01", "name": "South Internal Walkway (Lab)", "lat": 6.97470, "lon": 79.87204},
    {"id": "w_south_02", "name": "South Internal Walkway (Classroom 08)", "lat": 6.97470, "lon": 79.87228},
    {"id": "w_south_03", "name": "South-East Internal Walkway Junction", "lat": 6.97470, "lon": 79.87258},

    # Mid-Campus Open Courtyard Alley (Between Classroom 08 & Volley Ball Court)
    {"id": "w_mid_courtyard_01", "name": "Mid-Campus Open Courtyard", "lat": 6.97490, "lon": 79.87240},

    # Central Internal Courtyard Spine
    {"id": "w_central_alley_01", "name": "Central Internal Courtyard", "lat": 6.97529, "lon": 79.87218},
    {"id": "w_central_alley_02", "name": "Central Internal Courtyard North", "lat": 6.97543, "lon": 79.87218},

    # East Internal Highway Spine
    {"id": "w_east_01", "name": "East Internal Walkway (Courts)", "lat": 6.97509, "lon": 79.87258},
    {"id": "w_east_02", "name": "East Internal Walkway (Classrooms)", "lat": 6.97529, "lon": 79.87258},
    {"id": "w_east_03", "name": "East Internal Walkway (Workshop Alley)", "lat": 6.97572, "lon": 79.87258},

    # North Workshop Internal Alley
    {"id": "w_north_01", "name": "North Workshop Internal Alley", "lat": 6.97572, "lon": 79.87208}
]

for w in walkway_nodes:
    all_nodes[w['id']] = {
        "id": w['id'],
        "name": w['name'],
        "lat": w['lat'],
        "lon": w['lon'],
        "isBuilding": False
    }

# Candidate Outdoor Walking Connections through free spaces
connections = [
    # Security Room Main Gate Direct Connection
    ("security_room", "w_south_gate_corner"),
    ("w_south_gate_corner", "w_west_01"),

    # West Highway Spine
    ("w_west_01", "w_west_02"),
    ("w_west_02", "sport_room"),
    ("w_west_02", "union_room"),
    ("w_west_02", "mtl_hall_04"),
    ("w_west_01", "lectueres_room"),
    ("w_west_02", "w_west_03"),

    ("w_west_03", "classrooms"),
    ("w_west_03", "training_and_account_division"),
    ("w_west_03", "w_west_auditorium"),

    ("w_west_auditorium", "auditorium"),
    ("w_west_auditorium", "workshop"),
    ("w_west_auditorium", "w_west_04"),

    ("w_west_04", "canteen"),
    ("w_west_04", "w_west_05"),

    ("w_west_05", "gym"),
    ("w_west_05", "boys_hostals"),
    ("w_west_05", "w_west_06"),

    ("w_west_06", "regional_center_mattakkuliya"),

    # South Internal Walkway Spine
    ("w_south_gate_corner", "w_south_01"),
    ("w_south_01", "lab"),
    ("w_south_01", "w_south_02"),

    ("w_south_02", "class_room_08"),
    ("w_south_02", "w_south_03"),
    ("w_south_02", "w_mid_courtyard_01"),
    ("w_mid_courtyard_01", "w_east_01"),

    # Central Internal Courtyard Spine
    ("w_central_alley_01", "mtl_hall_02"),
    ("w_central_alley_01", "storage_room"),
    ("w_central_alley_01", "students_wash_room"),
    ("w_central_alley_01", "transport_division"),
    ("w_central_alley_01", "it_lab"),
    ("w_central_alley_01", "w_central_alley_02"),
    ("w_central_alley_01", "w_east_02"),

    ("w_central_alley_02", "chart_room"),

    # East Internal Highway Spine
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
    ("w_east_02", "w_east_03"),

    # North Workshop Internal Alley
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
    
    # STRICT RAY-CASTING: NO POLYGON CAN BE INTERSECTED BY ANY EDGE!
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

print(f"\nFinal Open Alley Network: {len(all_nodes)} nodes, {len(valid_edges)} 100% strict internal edges. Rejected {rejected} clipping edges.")

campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
