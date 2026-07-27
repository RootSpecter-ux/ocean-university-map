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

# 100% OUTDOOR PERIMETER DOOR COORDINATES (Strictly outside all building polygons)
building_doors = {
    'security_room': {"lat": 6.97472, "lon": 79.87170}, # Outdoor Gate Door
    'sport_room': {"lat": 6.97494, "lon": 79.87165},
    'union_room': {"lat": 6.97490, "lon": 79.87165},
    'mtl_hall_04': {"lat": 6.97488, "lon": 79.87165},
    'mtl_hall_03': {"lat": 6.97495, "lon": 79.87213},
    'lecturers_washroom': {"lat": 6.97496, "lon": 79.87218},
    'class_room_07': {"lat": 6.97497, "lon": 79.87222},
    'volly_ball_court': {"lat": 6.97509, "lon": 79.87245},
    'badminton_court': {"lat": 6.97521, "lon": 79.87258},
    'lectueres_room': {"lat": 6.97488, "lon": 79.87165},
    'training_and_account_division': {"lat": 6.97528, "lon": 79.87165},
    'auditorium': {"lat": 6.97543, "lon": 79.87174}, # Outdoor Alley North of Training Division & Auditorium
    'mtl_hall_02': {"lat": 6.97529, "lon": 79.87218},
    'storage_room': {"lat": 6.97529, "lon": 79.87218},
    'mtl_hall_01': {"lat": 6.97529, "lon": 79.87258},
    'class_room_02': {"lat": 6.97527, "lon": 79.87258},
    'class_room_03': {"lat": 6.97526, "lon": 79.87258},
    'drawing_room': {"lat": 6.97525, "lon": 79.87258},
    'class_room_04': {"lat": 6.97523, "lon": 79.87258},
    'students_wash_room': {"lat": 6.97527, "lon": 79.87218},
    'transport_division': {"lat": 6.97529, "lon": 79.87218},
    'it_lab': {"lat": 6.97535, "lon": 79.87218},
    'chart_room': {"lat": 6.97543, "lon": 79.87218},
    'workshop': {"lat": 6.97555, "lon": 79.87165}, # Outdoor Alley West of Workshop
    'welding_workshop': {"lat": 6.97572, "lon": 79.87208},
    'canteen': {"lat": 6.97565, "lon": 79.87155},
    'gym': {"lat": 6.97584, "lon": 79.87155},
    'boys_hostals': {"lat": 6.97593, "lon": 79.87165},
    'regional_center_mattakkuliya': {"lat": 6.97612, "lon": 79.87165},
    'class_room_08': {"lat": 6.97470, "lon": 79.87228},
    'lab': {"lat": 6.97470, "lon": 79.87204},
    'classrooms': {"lat": 6.97501, "lon": 79.87165}
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

# Create dense outdoor walkway grid surrounding all building blocks
walkway_nodes = [
    # WEST HIGHWAY (Lon = 79.87154)
    {"id": "w_west_01", "name": "Main Gate West Connector", "lat": 6.97470, "lon": 79.87154},
    {"id": "w_west_02", "name": "West Outdoor Highway (Sport/Union)", "lat": 6.97494, "lon": 79.87154},
    {"id": "w_west_03", "name": "West Outdoor Highway (Training Division)", "lat": 6.97528, "lon": 79.87154},
    {"id": "w_west_auditorium", "name": "West Outdoor Highway (Auditorium Entry)", "lat": 6.97543, "lon": 79.87154},
    {"id": "w_west_04", "name": "West Outdoor Highway (Canteen)", "lat": 6.97565, "lon": 79.87154},
    {"id": "w_west_05", "name": "West Outdoor Highway (Gym & Hostels)", "lat": 6.97593, "lon": 79.87154},
    {"id": "w_west_06", "name": "West Outdoor Highway (Regional Center)", "lat": 6.97612, "lon": 79.87154},

    # SOUTH ALLEY (Lat = 6.97470)
    {"id": "w_south_gate_corner", "name": "Main Gate South Entry", "lat": 6.97470, "lon": 79.87170},
    {"id": "w_south_01", "name": "South Outdoor Alley (Lab Entrance)", "lat": 6.97470, "lon": 79.87204},
    {"id": "w_south_02", "name": "South Outdoor Alley (Classroom 08)", "lat": 6.97470, "lon": 79.87228},
    {"id": "w_south_03", "name": "South-East Highway Junction", "lat": 6.97470, "lon": 79.87258},

    # CENTRAL OUTDOOR ALLEY (Lon = 79.87218)
    {"id": "w_central_alley_01", "name": "Central Outdoor Alley (Mid)", "lat": 6.97529, "lon": 79.87218},
    {"id": "w_central_alley_02", "name": "Central Outdoor Alley (North)", "lat": 6.97543, "lon": 79.87218},

    # EAST OUTDOOR HIGHWAY (Lon = 79.87258)
    {"id": "w_east_01", "name": "East Outdoor Highway (Courts/Classroom 07)", "lat": 6.97509, "lon": 79.87258},
    {"id": "w_east_02", "name": "East Outdoor Highway (MTL 01 / Classrooms)", "lat": 6.97529, "lon": 79.87258},
    {"id": "w_east_03", "name": "East Outdoor Highway (North Workshop Alley)", "lat": 6.97572, "lon": 79.87258},

    # NORTH WORKSHOP ALLEY (Lat = 6.97572)
    {"id": "w_north_01", "name": "North Workshop Alley (Welding Workshop)", "lat": 6.97572, "lon": 79.87208}
]

for w in walkway_nodes:
    all_nodes[w['id']] = {
        "id": w['id'],
        "name": w['name'],
        "lat": w['lat'],
        "lon": w['lon'],
        "isBuilding": False
    }

# Candidate Outdoor Walking Connections
connections = [
    # West Highway Spine
    ("security_room", "w_south_gate_corner"),
    ("w_south_gate_corner", "w_west_01"),
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

    # South Outdoor Alley Spine
    ("w_south_gate_corner", "w_south_01"),
    ("w_south_01", "lab"),
    ("w_south_01", "w_south_02"),

    ("w_south_02", "class_room_08"),
    ("w_south_02", "w_south_03"),

    # Central Outdoor Alley Spine
    ("w_central_alley_01", "mtl_hall_02"),
    ("w_central_alley_01", "storage_room"),
    ("w_central_alley_01", "students_wash_room"),
    ("w_central_alley_01", "transport_division"),
    ("w_central_alley_01", "it_lab"),
    ("w_central_alley_01", "w_central_alley_02"),
    ("w_central_alley_01", "w_east_02"),

    ("w_central_alley_02", "chart_room"),

    # East Outdoor Highway Spine
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

print(f"\nFinal Graph: {len(all_nodes)} nodes, {len(valid_edges)} 100% strict outdoor edges. Rejected {rejected} clipping edges.")

campus_data['locations'] = locations
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
