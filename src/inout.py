from flask import Flask, jsonify, request
from flask_restful.reqparse import RequestParser

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from typing import List, Dict
from requests import get
from json import load

from datetime import datetime

# Database imports
import src.schema as schema
import src.db as db
import random

# Setup Flask
app = Flask(__name__)


# Setup the logging
api_key = "AIzaSyD-ZGKvZYM953e9CQOBdCeCPlQ_onDos6E"

# logging.basicConfig(filename="/opt/soroco/logs/inout.log",
#                     level=logging.DEBUG, format='%(asctime)s %(message)s')

with open("all_stops.json", "r") as f:
    all_bus_stops = load(f)

with open("all_routes.json", "r") as f:
    all_routes = load(f)

bus_stops_global = {}

def get_routes(start: str, end: str)->List:
    url = "https://narasimhadatta.info/cgi-bin/find.cgi"
    post_fields = {"from": start, "to": end, "how": "Direct Routes Only"}

    request1 = Request(url, urlencode(post_fields).encode())
    json = urlopen(request1).read().decode()
    soup = BeautifulSoup(json, 'html.parser')
    tr = soup.find_all('tr')

    route_number_list = []

    for rows in tr:
        td = rows.find_all('td')
        if td:
            route_number = td[0].get_text()
            route_number_list.append(route_number)
    return route_number_list

def find_stops(route_number: str)->List:
    url = "https://narasimhadatta.info/cgi-bin/find.cgi"
    post_fields = {"route": route_number}
    scraper_info = Request(url, urlencode(post_fields).encode())

    json = urlopen(scraper_info).read().decode()
    soup = BeautifulSoup(json, 'html.parser')
    stops = soup.find_all("li")

    bus_stops = []

    for item in stops:
        bus_stops.append(item.get_text())
    return bus_stops

@app.route('/v1/status')
def status()->jsonify:
    """
    A very simple status check
    @return: "OK" if status is good
    """
    status = {
                "healthy": True,
                "version": "1.0.1"
            }
    response = jsonify(status=status)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v1/track_buses', methods=["GET"])
def track_buses()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("start", type=str, required=True)
    reqparse.add_argument("end", type=str, required=True)

    args = reqparse.parse_args(request)

    if all_routes.get(args.start, {}).get(args.end, None) is None:
        route_number_list = get_routes(args.start, args.end)
        all_routes[args.start] = {args.end: route_number_list}
    else:
        route_number_list = all_routes.get(args.start).get(args.end)

    # Url Params
    result_bus_info = []

    for route in route_number_list:
        buses_data = {"route_number": route, "all_buses": []}
        to_select = [{"route_number": route}, {"tracking_status": True}]
        rows = db.select_values(schema.User, to_select)

        max_time_stamp = datetime(year=1900, month=1, day=1)
        data_row = ()

        for db_row in rows:
            if db_row[3] > max_time_stamp:
                max_time_stamp = db_row[3]
                data_row = db_row

        if data_row:
            buses_data["all_buses"].append({"bus_number": data_row[1], "longitude": data_row[5], "latitude": data_row[6]})

        result_bus_info.append(buses_data)

    response = jsonify(result_bus_info)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v1/all_stops')
def all_stops()->jsonify:
    response = jsonify([{"title": x} for x in all_bus_stops])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v1/share_bus_location')
def share_bus_location()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("user_id", type=str, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("latitude", type=str, required=True)
    reqparse.add_argument("longitude", type=str, required=True)

    args = reqparse.parse_args(request)
    db.create_table(schema.User)
    db.insert_values(schema.User, [{"user_name": args.user_id, "bus_number": args.bus_number, "tracking_status": True,
                                    "route_number": args.route_number,
                                    "last_lat": args.latitude, "last_long": args.longitude, "timestamp": datetime.now()}])

    response = jsonify(sucess=True)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v1/stop_sharing')
def stop_sharing_location()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("user_id", type=str, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("latitude", type=str, required=True)
    reqparse.add_argument("longitude", type=str, required=True)
    args = reqparse.parse_args(request)

    db.create_table(schema.User)
    db.insert_values(schema.User, [{"user_name": args.user_id, "bus_number": args.bus_number, "tracking_status": False,
                                    "route_number": args.route_number,
                                    "last_lat": args.latitude, "last_long": args.longitude, "timestamp": datetime.now()}])
    response = jsonify(sucess=True)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v1/get_stops')
def get_stops()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("bus_number", type=str, required=False)
    args = reqparse.parse_args(request)

    if bus_stops_global.get(args.route_number, None) is None:
        bus_stops = find_stops(args.route_number)
        bus_stops_global[args.route_number] = bus_stops
    else:
        bus_stops = bus_stops_global[args.route_number]

    response = jsonify([{"title": x} for x in bus_stops])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/v1/get_bus_info")
def bus_specific_info()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("bus_number", type=str, required=False)
    reqparse.add_argument("latitude", type=str, required=True)
    reqparse.add_argument("longitude", type=str, required=True)

    args = reqparse.parse_args(request)

    to_select = [{"route_number": args.route_number}, {"tracking_status": True}]
    rows = db.select_values(schema.User, to_select)

    max_time_stamp = datetime(year=1900, month=1, day=1)
    data_row = ()

    users = []

    for db_row in rows:
        users.append(db_row[0])

        if db_row[3] > max_time_stamp:
            max_time_stamp = db_row[3]
            data_row = db_row

    bus_longitude = data_row[5]
    bus_latitude = data_row[6]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins={}&destinations={}&key={}".format(
        "{},{}".format(bus_latitude, bus_longitude), "{},{}".format(args.latitude, args.longitude), api_key)

    distance_data = get(url)

    bus_current_location = distance_data.json()["origin_addresses"]
    metrics = distance_data.json()["rows"][0]["elements"][0]
    distance_left = metrics["distance"]["text"]
    estimated_time = metrics["duration"]["text"]

    response = jsonify({"crowd": len(users),
                    "current_location": {"longitude": data_row[5], "latitude": data_row[6]},
                    "nearest_area": bus_current_location,
                    "last_heard": data_row[3],
                    "distance_left": distance_left,
                    "estimated_time": estimated_time})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/v1/get_crowd_info")
def crowd_info()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("route_number", type=str, required=True)

    line_dict = {}
    bar_dict = {}

    args = reqparse.parse_args(request)

    if bus_stops_global.get(args.route_number, None) is None:
        bus_stops = find_stops(args.route_number)
        bus_stops_global[args.route_number] = bus_stops
    else:
        bus_stops = bus_stops_global[args.route_number]

    data = []
    data1 = []
    data2 = []
    background_color = []

    for i in range(len(bus_stops)):
        data.append(random.randint(0, 100))
        data1.append(random.randint(0, 100))
        data2.append(random.randint(0, 100))
        background_color.append('#000000')

    line_dict["labels"] = bus_stops
    line_dict["datasets"] = [
            {
                "label": "Number of passengers",
                "backgroundColor": background_color,
                "data": data,
                "fill": False
            }
        ]

    bar_dict["labels"] = bus_stops
    bar_dict["datasets"] = [
        {
            "label": "Winter",
            "backgroundColor": "#00FFFF",
            "data": data,
            "fill": False
        },
        {
            "label": "Summer",
            "backgroundColor": "#0000FF",
            "data": data1,
            "fill": False
        },
        {
            "label": "Rainy",
            "backgroundColor": "#FF00FF",
            "data": data2,
            "fill": False
        }
    ]

    response = {"bar_chart": bar_dict, "line_chart": line_dict}
    response = jsonify(response)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v1/route_numbers')
def get_all_route_numbers()->jsonify:

    with open("route_numbers.json", "r") as f:
        data = load(f)

    data_structured = [{"name": x, "value": x} for x in data]

    response = jsonify(data_structured)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v1/get_busy_routes')
def get_all_busy_routes()->jsonify:
    busy_routes = []

    with open("all_routes.json", "r") as f:
        data = load(f)

    for start, stop_info in data.items():
        for stop, buses in stop_info.items():
            busy_routes.append({"Route": "{} to {}".format(start, stop), "Buses": len(buses)})

    top_routes = sorted(busy_routes, key=lambda k: k['Buses'], reverse=True)
    response = jsonify(top_routes[:10])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response