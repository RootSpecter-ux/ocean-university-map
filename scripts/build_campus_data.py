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

geojson_path = r'c:\Users\HP\OneDrive\Desktop\Map\Drawing.geojson'
output_dir = r'c:\Users\HP\OneDrive\Desktop\Map\public\data'
os.makedirs(output_dir, exist_ok=True)

with open(geojson_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Categorization mapping
category_map = {
    'Security Room': 'Entrance / Gates',
    'REGIONAL CENTER MATTAKKULIYA': 'Entrance / Gates',
    'MTL HALL 01': 'Academic & Lecture Halls',
    'MTL HALL 02': 'Academic & Lecture Halls',
    'MTL HALL 03': 'Academic & Lecture Halls',
    'MTL HALL 04': 'Academic & Lecture Halls',
    'CLASS ROOM 02': 'Academic & Lecture Halls',
    'CLASS ROOM 03': 'Academic & Lecture Halls',
    'CLASS ROOM 04': 'Academic & Lecture Halls',
    'CLASS ROOM 07': 'Academic & Lecture Halls',
    'CLASS ROOM 08': 'Academic & Lecture Halls',
    'classrooms': 'Academic & Lecture Halls',
    'DRAWING ROOM': 'Academic & Lecture Halls',
    'LECTUERE\'S ROOM': 'Academic & Lecture Halls',
    'IT LAB': 'Labs & Workshops',
    'LAB': 'Labs & Workshops',
    'WORKSHOP': 'Labs & Workshops',
    'WELDING WORKSHOP': 'Labs & Workshops',
    'CHART ROOM': 'Labs & Workshops',
    'TRAINING AND ACCOUNT DIVISION': 'Administrative',
    'TRANSPORT DIVISION': 'Administrative',
    'AUDITORIUM': 'Facilities & Dining',
    'CANTEEN': 'Facilities & Dining',
    'GYM': 'Facilities & Dining',
    'BOYS HOSTALS': 'Facilities & Dining',
    'SPORT ROOM': 'Facilities & Dining',
    'UNION ROOM': 'Facilities & Dining',
    'VOLLY BALL COURT': 'Sports & Recreation',
    'BADMINTON COURT': 'Sports & Recreation',
    'LECTURERS WASHROOM': 'Amenities',
    'STUDENTS WASH ROOM': 'Amenities',
    'STORAGE ROOM': 'Amenities'
}

# Multi-language translations dictionary
translations = {
    'Security Room': {'si': 'ආරක්ෂක කුටිය (ප්‍රධාන ද්වාරය)', 'ta': 'பாதுகாப்பு அறை (முதன்மை வாயில்)'},
    'REGIONAL CENTER MATTAKKULIYA': {'si': 'මට්ටක්කුලිය ප්‍රාදේශීය මධ්‍යස්ථානය', 'ta': 'மட்டக்குளி பிராந்திய மையம்'},
    'MTL HALL 01': {'si': 'MTL ශාලාව 01', 'ta': 'MTL அரங்கு 01'},
    'MTL HALL 02': {'si': 'MTL ශාලාව 02', 'ta': 'MTL அரங்கு 02'},
    'MTL HALL 03': {'si': 'MTL ශාලාව 03', 'ta': 'MTL அரங்கு 03'},
    'MTL HALL 04': {'si': 'MTL ශාලාව 04', 'ta': 'MTL அரங்கு 04'},
    'CLASS ROOM 02': {'si': 'දේශන කාමරය 02', 'ta': 'வகுப்பறை 02'},
    'CLASS ROOM 03': {'si': 'දේශන කාමරය 03', 'ta': 'வகுப்பறை 03'},
    'CLASS ROOM 04': {'si': 'දේශන කාමරය 04', 'ta': 'வகுப்பறை 04'},
    'CLASS ROOM 07': {'si': 'දේශන කාමරය 07', 'ta': 'வகுப்பறை 07'},
    'CLASS ROOM 08': {'si': 'දේශන කාමරය 08', 'ta': 'வகுப்பறை 08'},
    'classrooms': {'si': 'ප්‍රධාන දේශන කාමර සංකීර්ණය', 'ta': 'முதன்மை வகுப்பறை வளாகம்'},
    'DRAWING ROOM': {'si': 'ඇඳීම් ශාලාව', 'ta': 'வரைபட அறை'},
    'LECTUERE\'S ROOM': {'si': 'දේශකවරුන්ගේ කාමරය', 'ta': 'விரிவுரையாளர்கள் அறை'},
    'IT LAB': {'si': 'තොරතුරු තාක්ෂණ රසායනාගාරය', 'ta': 'தகவல் தொழில்நுட்ப ஆய்வகம்'},
    'LAB': {'si': 'විද්‍යාගාරය', 'ta': 'ஆய்வகம்'},
    'WORKSHOP': {'si': 'ඉංජිනේරු වැඩපල', 'ta': 'பொறியியல் பட்டறை'},
    'WELDING WORKSHOP': {'si': 'වෙල්ඩින් වැඩපල', 'ta': 'வெல்டிங் பட்டறை'},
    'CHART ROOM': {'si': 'සිතියම් හා සටහන් කාමරය', 'ta': 'வரைபட அறை'},
    'TRAINING AND ACCOUNT DIVISION': {'si': 'පුහුණු හා ගිණුම් අංශය', 'ta': 'பயிற்சி மற்றும் கணக்கு பிரிவு'},
    'TRANSPORT DIVISION': {'si': 'ප්‍රවාහන අංශය', 'ta': 'போக்குவரத்து பிரிவு'},
    'AUDITORIUM': {'si': 'ප්‍රධාන ශ්‍රවණාගාරය', 'ta': 'பிரதான அரங்கம்'},
    'CANTEEN': {'si': 'ශිෂ්‍ය ආපනශාලාව', 'ta': 'மாணவர் உணவகம்'},
    'GYM': {'si': 'ශාරීරික යෝග්‍යතා මධ්‍යස්ථානය (Gym)', 'ta': 'உடற்பயிற்சிகූடம்'},
    'BOYS HOSTALS': {'si': 'පිරිමි නේවාසිකාගාරය', 'ta': 'மாணவர்கள் விடுதி'},
    'SPORT ROOM': {'si': 'ක්‍රීඩා කාමරය', 'ta': 'விளையாட்டு அறை'},
    'UNION ROOM': {'si': 'ශිෂ්‍ය සංගම් කාමරය', 'ta': 'மாணவர் சங்க அறை'},
    'VOLLY BALL COURT': {'si': 'වොලිබෝල් ක්‍රීඩාංගනය', 'ta': 'வொலிபோல் மைதானம்'},
    'BADMINTON COURT': {'si': 'බැඩ්මින්ටන් ක්‍රීඩාංගනය', 'ta': 'பேட்மிண்டன் மைதானம்'},
    'LECTURERS WASHROOM': {'si': 'දේශක වැසිකිලි සංකීර්ණය', 'ta': 'விரிவுரையாளர்கள் கழிப்பறை'},
    'STUDENTS WASH ROOM': {'si': 'ශිෂ්‍ය වැසිකිලි සංකීර්ණය', 'ta': 'மாணவர்கள் கழிப்பறை'},
    'STORAGE ROOM': {'si': 'ගබඩා කාමරය', 'ta': 'சேமிப்பு அறை'}
}

# Floor plans template generator
def generate_floors(name, category):
    if name.startswith('MTL') or name == 'IT LAB' or name == 'AUDITORIUM' or name == 'REGIONAL CENTER MATTAKKULIYA':
        return [
            {
                "floor": 0,
                "label": "Ground Floor",
                "rooms": [
                    {"code": f"{name[:3]}-G01", "title": "Main Entrance & Lobby", "type": "lobby", "accessible": True},
                    {"code": f"{name[:3]}-G02", "title": "Lecture Hall Section A", "type": "classroom", "accessible": True},
                    {"code": f"{name[:3]}-G03", "title": "Staff Office / Control Room", "type": "office", "accessible": True},
                    {"code": f"{name[:3]}-WC", "title": "Accessible Washroom", "type": "amenity", "accessible": True}
                ]
            },
            {
                "floor": 1,
                "label": "1st Floor",
                "rooms": [
                    {"code": f"{name[:3]}-101", "title": "Advanced Lab / Gallery", "type": "lab", "accessible": True},
                    {"code": f"{name[:3]}-102", "title": "Presentation Theatre", "type": "classroom", "accessible": True},
                    {"code": f"{name[:3]}-103", "title": "Faculty Meeting Room", "type": "office", "accessible": True}
                ]
            }
        ]
    else:
        return [
            {
                "floor": 0,
                "label": "Ground Floor",
                "rooms": [
                    {"code": f"{name[:3]}-G01", "title": f"{name} Main Area", "type": "facility", "accessible": True},
                    {"code": f"{name[:3]}-INFO", "title": "Information Desk", "type": "office", "accessible": True}
                ]
            }
        ]

unique_locs = {}
features_list = data.get('features', [])

for idx, f in enumerate(features_list):
    props = f.get('properties', {})
    geom = f.get('geometry', {})
    gtype = geom.get('type')
    coords = geom.get('coordinates')
    name = props.get('name')
    if not name:
        continue
    name = name.strip()
    
    if gtype == 'Point':
        lon, lat = coords[0], coords[1]
        polygon = []
    elif gtype == 'Polygon':
        pts = coords[0]
        lon = sum(p[0] for p in pts) / len(pts)
        lat = sum(p[1] for p in pts) / len(pts)
        polygon = coords[0]
    else:
        continue
    
    loc_id = name.lower().replace(' ', '_').replace('\'', '').replace('-', '_')
    cat = category_map.get(name, 'Facilities & Dining')
    trans = translations.get(name, {'si': name, 'ta': name})
    
    if loc_id not in unique_locs or gtype == 'Polygon':
        unique_locs[loc_id] = {
            "id": loc_id,
            "name": name,
            "category": cat,
            "lat": round(lat, 6),
            "lon": round(lon, 6),
            "translations": {
                "en": name,
                "si": trans['si'],
                "ta": trans['ta']
            },
            "accessible": True,
            "status": "Open",
            "polygon": polygon,
            "floors": generate_floors(name, cat)
        }

locations = list(unique_locs.values())

nodes = {}
for loc in locations:
    nodes[loc['id']] = {
        "id": loc['id'],
        "name": loc['name'],
        "lat": loc['lat'],
        "lon": loc['lon'],
        "isBuilding": True
    }

junctions = [
    {"id": "j_south_gate", "name": "South Entrance Gate Walkway", "lat": 6.97482, "lon": 79.87180},
    {"id": "j_sports_square", "name": "Sports & Union Junction", "lat": 6.97495, "lon": 79.87178},
    {"id": "j_lecturers_lane", "name": "Lecturers Block Path", "lat": 6.97500, "lon": 79.87195},
    {"id": "j_classrooms_east", "name": "East Academic Corridor South", "lat": 6.97495, "lon": 79.87222},
    {"id": "j_central_plaza", "name": "Central Campus Plaza", "lat": 6.97525, "lon": 79.87188},
    {"id": "j_east_plaza", "name": "East Academic Plaza", "lat": 6.97520, "lon": 79.87225},
    {"id": "j_north_canteen_path", "name": "North Canteen Pathway", "lat": 6.97555, "lon": 79.87170},
    {"id": "j_hostel_gym_lane", "name": "Hostel & Gym Pathway", "lat": 6.97575, "lon": 79.87172},
    {"id": "j_workshop_cross", "name": "Workshop Crossroad", "lat": 6.97552, "lon": 79.87205},
    {"id": "j_north_gate", "name": "North Gate Access", "lat": 6.97600, "lon": 79.87180}
]

for j in junctions:
    nodes[j['id']] = {
        "id": j['id'],
        "name": j['name'],
        "lat": j['lat'],
        "lon": j['lon'],
        "isBuilding": False
    }

edges = []
added_pairs = set()

def add_edge(u, v, is_accessible=True, ramp_only=False):
    pair = tuple(sorted([u, v]))
    if pair in added_pairs or u not in nodes or v not in nodes:
        return
    added_pairs.add(pair)
    d = haversine(nodes[u]['lat'], nodes[u]['lon'], nodes[v]['lat'], nodes[v]['lon'])
    edges.append({
        "source": u,
        "target": v,
        "distance": d,
        "isAccessible": is_accessible,
        "rampOnly": ramp_only
    })

add_edge('security_room', 'j_south_gate')
add_edge('j_south_gate', 'j_sports_square')

add_edge('j_sports_square', 'sport_room')
add_edge('j_sports_square', 'union_room')
add_edge('j_sports_square', 'mtl_hall_04')
add_edge('j_sports_square', 'j_lecturers_lane')

add_edge('j_lecturers_lane', 'lectueres_room')
add_edge('j_lecturers_lane', 'badminton_court')
add_edge('j_lecturers_lane', 'mtl_hall_03')
add_edge('j_lecturers_lane', 'j_classrooms_east')

add_edge('j_classrooms_east', 'class_room_07')
add_edge('j_classrooms_east', 'lecturers_washroom')
add_edge('j_classrooms_east', 'class_room_08')
add_edge('j_classrooms_east', 'lab')
add_edge('j_classrooms_east', 'volly_ball_court')
add_edge('j_classrooms_east', 'j_east_plaza')

add_edge('j_sports_square', 'j_central_plaza')
add_edge('j_lecturers_lane', 'j_central_plaza')
add_edge('j_central_plaza', 'auditorium')
add_edge('j_central_plaza', 'training_and_account_division')
add_edge('j_central_plaza', 'mtl_hall_02')
add_edge('j_central_plaza', 'storage_room')
add_edge('j_central_plaza', 'classrooms')
add_edge('j_central_plaza', 'j_workshop_cross')
add_edge('j_central_plaza', 'j_east_plaza')

add_edge('j_east_plaza', 'mtl_hall_01')
add_edge('j_east_plaza', 'class_room_02')
add_edge('j_east_plaza', 'class_room_03')
add_edge('j_east_plaza', 'drawing_room')
add_edge('j_east_plaza', 'class_room_04')
add_edge('j_east_plaza', 'students_wash_room')
add_edge('j_east_plaza', 'transport_division')
add_edge('j_east_plaza', 'it_lab')
add_edge('j_east_plaza', 'chart_room')
add_edge('j_east_plaza', 'j_workshop_cross')

add_edge('j_workshop_cross', 'workshop')
add_edge('j_workshop_cross', 'welding_workshop')
add_edge('j_workshop_cross', 'j_north_canteen_path')

add_edge('j_central_plaza', 'j_north_canteen_path')
add_edge('j_north_canteen_path', 'canteen')
add_edge('j_north_canteen_path', 'j_hostel_gym_lane')
add_edge('j_hostel_gym_lane', 'gym')
add_edge('j_hostel_gym_lane', 'boys_hostals')
add_edge('j_hostel_gym_lane', 'j_north_gate')
add_edge('j_north_gate', 'regional_center_mattakkuliya')

for i, loc1 in enumerate(locations):
    for loc2 in locations[i+1:]:
        d = haversine(loc1['lat'], loc1['lon'], loc2['lat'], loc2['lon'])
        if d < 22:
            add_edge(loc1['id'], loc2['id'])

campus_data = {
    "info": {
        "title": "University Campus Navigation System",
        "center": [6.975235, 79.872020],
        "defaultZoom": 18,
        "gates": [
            {"id": "security_room", "name": "Main South Gate (Security Room)", "lat": 6.974777, "lon": 79.871797},
            {"id": "regional_center_mattakkuliya", "name": "North Gate (Regional Center)", "lat": 6.976040, "lon": 79.871814}
        ]
    },
    "locations": locations,
    "graph": {
        "nodes": list(nodes.values()),
        "edges": edges
    }
}

output_file = os.path.join(output_dir, 'campus_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(campus_data, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {output_file} with {len(locations)} locations, {len(nodes)} graph nodes, and {len(edges)} graph edges.")
