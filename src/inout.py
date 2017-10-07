from flask import Flask, jsonify, request, Response as FlaskResponse, make_response
from flask_restful.reqparse import RequestParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from typing import List, Dict
from requests import get
from json import load

from sqlalchemy.engine import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

import json
import hashlib
import logging
import binascii
import random
import string
import sqlalchemy

# Database imports
import src.schema as schema
import src.db as db

# Setup Flask
app = Flask(__name__)


# Setup the logging
api_key = "AIzaSyD-ZGKvZYM953e9CQOBdCeCPlQ_onDos6E"

# logging.basicConfig(filename="/opt/soroco/logs/inout.log",
#                     level=logging.DEBUG, format='%(asctime)s %(message)s')

with open("all_stops.json", "r") as f:
    all_bus_stops = load(f)


def find_nearest_area(latitude: float, longitude: float) -> str:
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&key={}"
    reverse_geo = url.format(latitude, longitude, "AIzaSyD-ZGKvZYM953e9CQOBdCeCPlQ_onDos6E")
    response = get(reverse_geo)

    reverse_location = ""
    route = []

    for item in response.json().get("results", []):
        if "street_address" in item["types"]:
            route = item["address_components"]
    print(route)
    for route_search in route:
        if "sublocality" in route_search["types"]:
            reverse_location = route_search["long_name"]
            break

    return reverse_location

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

    # Url Params
    url = "https://narasimhadatta.info/cgi-bin/find.cgi"
    post_fields = {"from": args.start, "to": args.end, "how": "Direct Routes Only"}

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
            buses_data["all_buses"].append({"bus_number": data_row[1], "latitude": data_row[5], "longitude": data_row[6]})

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
    reqparse.add_argument("user_id", type=int, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("latitude", type=str, required=True)
    reqparse.add_argument("longitude", type=str, required=True)

    args = reqparse.parse_args(request)
    db.create_table(schema.User)
    db.insert_values(schema.User, [{"user_name": args.user_id, "bus_number": args.bus_number, "tracking_status": True,
                                    "route_number": args.route_number,
                                    "last_lat": args.latitude, "last_long": args.longitude, "timestamp": datetime.now()}])


@app.route('/v1/stop_sharing')
def stop_sharing_location()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("user_id", type=int, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
    args = reqparse.parse_args(request)

    db.insert_values(schema.User, [{"user_name": args.user_id, "bus_number": args.bus_number, "tracking_status": False}])

@app.route('/v1/get_stops')
def get_stops()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
    args = reqparse.parse_args(request)

    url = "https://narasimhadatta.info/cgi-bin/find.cgi"
    post_fields = {"route": args.route_number}
    scraper_info = Request(url, urlencode(post_fields).encode())

    json = urlopen(scraper_info).read().decode()
    soup = BeautifulSoup(json, 'html.parser')
    stops = soup.find_all("li")

    bus_stops = []

    for item in stops:
        bus_stops.append(item.get_text())

    response = jsonify(bus_stops)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route("/v1/get_bus_info")
def bus_specific_info()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("route_number", type=str, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
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

    return jsonify({"crowd": len(users), "current_location": {"latitude": data_row[5], "longitude": data_row[6]},
                    "nearest_area": find_nearest_area(data_row[5], data_row[6]),
                    "last_heard": data_row[3]})
