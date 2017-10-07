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

import json
import hashlib
import logging
import binascii
import random
import string
import sqlalchemy

# Setup Flask
app = Flask(__name__)

def connect(user: str, password: str, db: str, host: str='localhost', port: int=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta


# Setup the logging
api_key = "AIzaSyD-ZGKvZYM953e9CQOBdCeCPlQ_onDos6E"

logging.basicConfig(filename="/opt/soroco/logs/inout.log",
                    level=logging.DEBUG, format='%(asctime)s %(message)s')

with open("all_stops.json", "r") as f:
    all_bus_stops = load(f)


def compute_bus_count(frequency: str)->int:
    frequency_map = {"rare": 2, "very rare": 1, "average": 5, "frequent": 8, "very frequent": 10}
    max_count = frequency_map.get(frequency.lower(), 1)
    return random.randint(max(0, max_count-2), max_count)


def generate_bus_numbers(count: int)->List:
    bus_numbers = []

    for item in range(count):
        number = "KA 01 {}{} {}".format(random.choice(string.ascii_uppercase), random.choice(string.ascii_uppercase),
                                   random.randint(100, 9999))
        bus_numbers.append(number)
    return bus_numbers


def find_geocoding(address: str)->Dict:
    url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(address, "AIzaSyD-ZGKvZYM953e9CQOBdCeCPlQ_onDos6E")
    response = get(url)
    return response.json()["results"][0]["geometry"]["location"]


class BusInfo:
    def __init__(self, bus_number: int, stops: List[str], bus_frequency: int) -> None:
        self.bus_number = bus_number
        self.stops = stops
        self.bus_frequency = bus_frequency


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


@app.route('/v1/bus_info', methods=["GET"])
def bus_info()->jsonify:
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

    required_bus_info = []

    for rows in tr:
        td = rows.find_all('td')
        if td:
            bus_number = td[0].get_text()

            all_stops = td[3].get_text().split(",")
            all_stops = [x.strip() for x in all_stops]
            b = BusInfo(bus_number, all_stops, compute_bus_count(td[4].get_text().strip()))
            required_bus_info.append(b)

    result_bus_info = []

    for item in required_bus_info:
        buses_data = {"route_number": item.bus_number, "all_buses": []}
        total_buses = generate_bus_numbers(item.bus_frequency)

        for bus in total_buses:
            try:
                buses_data["all_buses"].append({"bus_number": bus,
                                                "location": find_geocoding(item.stops[random.randint(0, item.stops.index(args.start))])})
            except:
                pass

        result_bus_info.append(buses_data)

    response = jsonify(result_bus_info)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v1/all_stops')
def all_stops()->jsonify:
    response = jsonify([{"title": x} for x in all_bus_stops])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v1/track_bus')
def track_bus()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("user_id", type=int, required=True)
    reqparse.add_argument("bus_number", type=str, required=True)
    reqparse.add_argument("latitude", type=str, required=True)
    reqparse.add_argument("longitude", type=str, required=True)

    args = reqparse.parse_args(request)
