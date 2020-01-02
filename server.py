from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash

from geojson import Feature, Point
from pyproj import Proj, transform

import requests, json, time

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('APP_CONFIG_FILE', silent=True)

MAPBOX_ACCESS_KEY = app.config['MAPBOX_ACCESS_KEY']

ROUTE = [
    {"lat": 64.0027441, "long": -22.7066262, "name": "Keflavik Airport", "is_stop_location": True},
    {"lat": 64.0317168, "long": -22.1092311, "name": "Hafnarfjordur", "is_stop_location": True},
    {"lat": 63.99879, "long": -21.18802, "name": "Hveragerdi", "is_stop_location": True},
    {"lat": 63.4194089, "long": -19.0184548, "name": "Vik", "is_stop_location": True},
    {"lat": 63.5302354, "long": -18.8904333, "name": "Thakgil", "is_stop_location": True},
    {"lat": 64.2538507, "long": -15.2222918, "name": "Hofn", "is_stop_location": True},
    {"lat": 64.913435, "long": -14.01951, "is_stop_location": False},
    {"lat": 65.2622588, "long": -14.0179538, "name": "Seydisfjordur", "is_stop_location": True},
    {"lat": 65.2640083, "long": -14.4037548, "name": "Egilsstadir", "is_stop_location": True},
    {"lat": 66.0427545, "long": -17.3624953, "name": "Husavik", "is_stop_location": True},
    {"lat": 65.659786, "long": -20.723364, "is_stop_location": False},
    {"lat": 65.3958953, "long": -20.9580216, "name": "Hvammstangi", "is_stop_location": True},
    {"lat": 65.0722555, "long": -21.9704238, "is_stop_location": False},
    {"lat": 65.0189519, "long": -22.8767959, "is_stop_location": False},
    {"lat": 64.8929619, "long": -23.7260926, "name": "Olafsvik", "is_stop_location": True},
    {"lat": 64.785334, "long": -23.905765, "is_stop_location": False},
    {"lat": 64.174537, "long": -21.6480148, "name": "Mosfellsdalur", "is_stop_location": True},
    {"lat": 64.0792223, "long": -20.7535337, "name": "Minniborgir", "is_stop_location": True},
    {"lat": 64.14586, "long": -21.93955, "name": "Reykjavik", "is_stop_location": True},
]

BRISTOL_CENTRE = [51.520921,-2.248806]

@app.route('/mapbox_js')
def mapbox_js():

    route_data = get_sustrans_data();

    #route_data, waypoints = get_route_data(route)
    #stop_locations = create_stop_locations_details(route)

    return render_template('mapbox_js.html', 
        ACCESS_KEY=MAPBOX_ACCESS_KEY,
        route_data=route_data,
        map_centre=BRISTOL_CENTRE
        #,stop_locations = stop_locations
    )

# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"

BCC_URL = "https://opendata.bristol.gov.uk/api/records/1.0/search/?dataset={0}&rows={1}&geofilter.distance={2}%2C{3}%2C{4}"

def create_route_url(route):
    # Create a string with all the geo coordinates
    lat_longs = ";".join(["{0},{1}".format(point["long"], point["lat"]) for point in route])
    # Create a url with the geo coordinates and access token
    url = ROUTE_URL.format(lat_longs, MAPBOX_ACCESS_KEY)
    return url

def convert_coords(coord):
    inProj = Proj('epsg:3857')
    outProj = Proj('epsg:4326')
    x2,y2 = transform(inProj,outProj,coord[0],coord[1])
    return [x2, y2]

def get_route_data(route_list):
    # Get the route url
    route_data = []
    waypoints = []
    for route in route_list:
        #print(len(route))
        if len(route) < 25:
            data = send_route_request(route)
        else:
            data = {}
        route_key = "routes"
        #print(data.keys())
        if route_key in data.keys():
            #print("Not none")
            geometry = data["routes"][0]["geometry"]
            print(geometry)
            route_data.append(Feature(geometry = geometry, properties = {}))
            waypoints.append(data["waypoints"])
        else:
            # split the coordinates and make the requests again
            #print("Split")
            if "message" in data.keys():
                print(data["message"])
            half = len(route)//2
            route_data_2, waypoints_2 = get_route_data([route[:half], route[half:]])
            route_data = route_data + route_data_2
            waypoints = waypoints + waypoints_2
    return route_data, waypoints

def send_route_request(route):
    route_url = create_route_url(route)
    # Perform a GET request to the route API
    result = requests.get(route_url)
    if result.status_code == 429:
        print("Too many requests error - wait for 10 seconds")
        time.sleep(10)
        send_route_request(route)
    # Convert the return value to JSON
    json_result = result.json()
    if type(json_result) is dict:
        return json_result
    else:
        return json.loads(json_result)

def create_stop_locations_details(route_list):
    stop_locations = []
    for route in route_list:
        for location in route:
            # Skip anything that is not a stop location
            if not location["is_stop_location"]:
                continue
            # Create a geojson object for stop location
            point = Point([location['long'], location['lat']])
            properties = {
                'title': location['name'],
                'icon': 'campsite',
                'marker-color': '#3bb2d0',
                'marker-symbol': len(stop_locations) + 1
            }
            feature = Feature(geometry = point, properties = properties)
            stop_locations.append(feature)
    return stop_locations

def get_sustrans_data():
    #coords = convert_coords(BRISTOL_CENTRE)
    # Get the route url
    url = BCC_URL.format("sustrans-cycle-network", "2000", BRISTOL_CENTRE[0], BRISTOL_CENTRE[1], 100000)
    # Perform a GET request to the route API
    result = requests.get(url)
    # Convert the return value to JSON
    data = result.json()
    # Create a geo json object from the routing data
    records = data["records"]
    route_data = []
    for record in records:
        coordinates = record["fields"]["geo_shape"]["coordinates"]
        #for coordinates in coordinates_list:
        route_data.append(convert_to_geojson(record, coordinates))
    return route_data

def convert_to_route(record, coordinates):
    route = []
    for coord in coordinates:
        route.append({"lat": coord[1], "long": coord[0], "name": record["fields"]["description"], "is_stop_location": False});
    return route

def convert_to_geojson(record, coordinates):
    geometry = {"type": "LineString", "coordinates":coordinates}
    feature = Feature(geometry = geometry, properties = {"name": record["fields"]["description"]})
    return feature