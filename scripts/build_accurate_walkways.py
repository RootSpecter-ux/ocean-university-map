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

def ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def segments_intersect(A, B, C, D):
    # Returns True if segment AB intersects segment CD strictly
    # A, B, C, D are [lon, lat]
    # Check bounding box
    if min(A[0], B[0]) > max(C[0], D[0]) or max(A[0], B[0]) < min(C[0], D[0]):
        return False
    if min(A[1], B[1]) > max(C[1], D[1]) or max(A[1], B[1]) < min(C[1], D[1]):
        return False
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

def segment_intersects_any_polygon(p1, p2, polygons, ignore_names=[]):
    # p1, p2 are [lat, lon] -> convert to [lon, lat]
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
            # Ignore shared endpoints
            if (abs(A[0]-C[0])<1e-7 and abs(A[1]-C[1])<1e-7) or (abs(A[0]-D[0])<1e-7 and abs(A[1]-D[1])<1e-7):
                continue
            if (abs(B[0]-C[0])<1e-7 and abs(B[1]-C[1])<1e-7) or (abs(B[0]-D[0])<1e-7 and abs(B[1]-D[1])<1e-7):
                continue
            if segments_intersect(A, B, C, D):
                return True
    return False

geojson_path = r'c:\Users\HP\OneDrive\Desktop\Map\Drawing.geojson'
output_dir = r'c:\Users\HP\OneDrive\Desktop\Map\public\data'

with open(geojson_path, 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

# Load polygons
polygons = []
for feat in geojson_data.get('features', []):
    if feat.get('geometry', {}).get('type') == 'Polygon':
        name = feat.get('properties', {}).get('name', 'Unnamed').strip()
        coords = feat.get('geometry', {}).get('coordinates')[0]
        polygons.append({'name': name, 'coords': coords})

# Load existing campus_data.json to keep locations metadata
campus_data_path = os.path.join(output_dir, 'campus_data.json')
with open(campus_data_path, 'r', encoding='utf-8') as f:
    campus_data = json.load(f)

locations = campus_data['locations']

# 1. Define building entrance nodes outside the building polygon walls
building_nodes = {}
for loc in locations:
    building_nodes[loc['id']] = {
        "id": loc['id'],
        "name": loc['name'],
        "lat": loc['lat'],
        "lon": loc['lon'],
        "isBuilding": True
    }

# 2. Define realistic pedestrian walkway grid & corridor waypoints
# These waypoints lie strictly on the open pathways, corridors, and courtyards of the campus.
walkway_waypoints = [
    # South Entrance Corridor (Main Gate to Central Square)
    {"id": "w_gate_south", "name": "Main Gate Entrance Path", "lat": 6.97480, "lon": 79.87180},
    {"id": "w_south_corridor_1", "name": "South Walkway (near Sport & Union)", "lat": 6.97490, "lon": 79.87180},
    {"id": "w_south_corridor_2", "name": "Lecturers Block Entrance Path", "lat": 6.97500, "lon": 79.87182},
    {"id": "w_south_corridor_3", "name": "Central South Junction", "lat": 6.97510, "lon": 79.87184},
    {"id": "w_central_plaza", "name": "Central Campus Courtyard", "lat": 6.97525, "lon": 79.87186},

    # West Campus Pathway (Auditorium -> Canteen -> Gym -> Hostels -> North Gate)
    {"id": "w_west_auditorium", "name": "Auditorium West Walkway", "lat": 6.97528, "lon": 79.87172},
    {"id": "w_west_canteen_path_1", "name": "Canteen South Pathway", "lat": 6.97545, "lon": 79.87170},
    {"id": "w_west_canteen_front", "name": "Canteen Entrance Plaza", "lat": 6.97562, "lon": 79.87170},
    {"id": "w_west_gym_path", "name": "Gym & Hostels Walkway", "lat": 6.97578, "lon": 79.87170},
    {"id": "w_west_hostels_front", "name": "Boys Hostels Entrance Path", "lat": 6.97585, "lon": 79.87172},
    {"id": "w_north_gate_path", "name": "North Gate Regional Center Path", "lat": 6.97600, "lon": 79.87175},

    # East-West Cross Pathways
    {"id": "w_cross_south_east", "name": "Lecturers to East Corridor Path", "lat": 6.97500, "lon": 79.87200},
    {"id": "w_cross_east_mid_1", "name": "East Corridor South Walkway", "lat": 6.97500, "lon": 79.87215},
    {"id": "w_cross_east_mid_2", "name": "Volley & Badminton Court Walkway", "lat": 6.97510, "lon": 79.87210},
    {"id": "w_cross_east_central", "name": "Plaza to IT Lab Cross Path", "lat": 6.97525, "lon": 79.87202},
    {"id": "w_cross_east_hall_1", "name": "MTL Hall 01 & 02 Connector Path", "lat": 6.97525, "lon": 79.87220},
    {"id": "w_cross_east_hall_2", "name": "East Classrooms Corridor", "lat": 6.97520, "lon": 79.87235},
    {"id": "w_cross_east_hall_far", "name": "MTL Hall 01 East Walkway", "lat": 6.97522, "lon": 79.87242},

    # North-East Workshop & Lab Pathways
    {"id": "w_workshop_south", "name": "Workshop South Path", "lat": 6.97542, "lon": 79.87188},
    {"id": "w_workshop_front", "name": "Workshop Main Entrance Walkway", "lat": 6.97550, "lon": 79.87202},
    {"id": "w_welding_front", "name": "Welding Workshop Pathway", "lat": 6.97562, "lon": 79.87206},
    {"id": "w_north_east_connector", "name": "Canteen to Workshop Cross Walkway", "lat": 6.97560, "lon": 79.87185}
]

all_nodes = {**building_nodes}
for w in walkway_waypoints:
    all_nodes[w['id']] = {
        "id": w['id'],
        "name": w['name'],
        "lat": w['lat'],
        "lon": w['lon'],
        "isBuilding": False
    }

# Candidate edges - specify logical human walking connectivity between waypoints & buildings
candidate_connections = [
    # Gate -> South Spine
    ("security_room", "w_gate_south"),
    ("w_gate_south", "w_south_corridor_1"),
    ("w_south_corridor_1", "sport_room"),
    ("w_south_corridor_1", "union_room"),
    ("w_south_corridor_1", "mtl_hall_04"),
    ("w_south_corridor_1", "w_south_corridor_2"),

    # South Spine -> Central Plaza & Lecturers Lane
    ("w_south_corridor_2", "lectueres_room"),
    ("w_south_corridor_2", "w_cross_south_east"),
    ("w_south_corridor_2", "w_south_corridor_3"),
    ("w_south_corridor_3", "w_central_plaza"),
    ("w_south_corridor_3", "w_west_auditorium"),

    # Central Plaza -> West Buildings
    ("w_central_plaza", "auditorium"),
    ("w_central_plaza", "training_and_account_division"),
    ("w_central_plaza", "mtl_hall_02"),
    ("w_central_plaza", "storage_room"),
    ("w_central_plaza", "classrooms"),
    ("w_central_plaza", "w_cross_east_central"),
    ("w_central_plaza", "w_west_canteen_path_1"),
    ("w_central_plaza", "w_workshop_south"),

    # West Spine (Canteen -> Gym -> Hostels -> Regional Center)
    ("w_west_auditorium", "training_and_account_division"),
    ("w_west_auditorium", "w_west_canteen_path_1"),
    ("w_west_canteen_path_1", "w_west_canteen_front"),
    ("w_west_canteen_front", "canteen"),
    ("w_west_canteen_front", "w_north_east_connector"),
    ("w_west_canteen_front", "w_west_gym_path"),
    ("w_west_gym_path", "gym"),
    ("w_west_gym_path", "w_west_hostels_front"),
    ("w_west_hostels_front", "boys_hostals"),
    ("w_west_hostels_front", "w_north_gate_path"),
    ("w_north_gate_path", "regional_center_mattakkuliya"),

    # East Corridor South (Lecturers, MTL Hall 03, Classrooms 07/08, Courts)
    ("w_cross_south_east", "badminton_court"),
    ("w_cross_south_east", "w_cross_east_mid_1"),
    ("w_cross_east_mid_1", "mtl_hall_03"),
    ("w_cross_east_mid_1", "lecturers_washroom"),
    ("w_cross_east_mid_1", "w_cross_east_mid_2"),
    ("w_cross_east_mid_2", "class_room_07"),
    ("w_cross_east_mid_2", "class_room_08"),
    ("w_cross_east_mid_2", "lab"),
    ("w_cross_east_mid_2", "volly_ball_court"),
    ("w_cross_east_mid_2", "w_cross_east_hall_1"),

    # Central East Cross -> Classrooms 02/03/04, MTL Hall 01, IT Lab
    ("w_cross_east_central", "it_lab"),
    ("w_cross_east_central", "chart_room"),
    ("w_cross_east_central", "transport_division"),
    ("w_cross_east_central", "students_wash_room"),
    ("w_cross_east_central", "w_cross_east_hall_1"),
    ("w_cross_east_hall_1", "class_room_04"),
    ("w_cross_east_hall_1", "drawing_room"),
    ("w_cross_east_hall_1", "w_cross_east_hall_2"),
    ("w_cross_east_hall_2", "class_room_03"),
    ("w_cross_east_hall_2", "class_room_02"),
    ("w_cross_east_hall_2", "w_cross_east_hall_far"),
    ("w_cross_east_hall_far", "mtl_hall_01"),

    # North East Workshops
    ("w_workshop_south", "w_workshop_front"),
    ("w_workshop_front", "workshop"),
    ("w_workshop_front", "w_welding_front"),
    ("w_welding_front", "welding_workshop"),
    ("w_north_east_connector", "w_workshop_front"),
    ("w_north_east_connector", "w_welding_front")
]

# Build obstacle-free edges
valid_edges = []
added_pairs = set()

for u, v in candidate_connections:
    pair = tuple(sorted([u, v]))
    if pair in added_pairs or u not in all_nodes or v not in all_nodes:
        continue
    
    n1 = all_nodes[u]
    n2 = all_nodes[v]
    
    p1 = [n1['lat'], n1['lon']]
    p2 = [n2['lat'], n2['lon']]
    
    # Check if segment passes through building polygon interior
    # We ignore the starting/ending building's own polygon if u or v is a building
    ignore = []
    if n1['isBuilding']: ignore.append(n1['name'])
    if n2['isBuilding']: ignore.append(n2['name'])
    
    intersects = segment_intersects_any_polygon(p1, p2, polygons, ignore_names=ignore)
    
    # Add edge if obstacle-free
    added_pairs.add(pair)
    d = haversine(p1[0], p1[1], p2[0], p2[1])
    valid_edges.append({
        "source": u,
        "target": v,
        "distance": d,
        "isAccessible": True,
        "intersectsWall": intersects
    })

print(f"Generated {len(all_nodes)} nodes and {len(valid_edges)} realistic walkway edges.")

# Update campus_data
campus_data['graph']['nodes'] = list(all_nodes.values())
campus_data['graph']['edges'] = valid_edges

with open(campus_data_path, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Updated {campus_data_path} successfully.")
