from flask import Flask, jsonify, request, Response as FlaskResponse
from flask_restful.reqparse import RequestParser
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

import json
import hashlib
import logging
import binascii

# Setup Flask
app = Flask(__name__)

# Setup the logging

logging.basicConfig(filename="/opt/soroco/logs/inout.log",
                    level=logging.DEBUG, format='%(asctime)s %(message)s')


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
    return jsonify(status=status)


@app.route('/v1/bus_info', methods=["GET"])
def bus_info()->jsonify:
    reqparse = RequestParser()
    reqparse.add_argument("start", type=str, required=True)
    reqparse.add_argument("end", type=str, required=True)

    args = reqparse.parse_args(request)
    print(args.start, args.end)

    # Url Params
    url = "https://narasimhadatta.info/cgi-bin/find.cgi"
    post_fields = {"from": args.start, "to": args.end, "how": "Direct Routes Only"}

    request1 = Request(url, urlencode(post_fields).encode())
    json = urlopen(request1).read().decode()
    soup = BeautifulSoup(json, 'html.parser')
    tr = soup.find_all('tr')
    required_bus_info = {}

    for rows in tr:
        td = rows.find_all('td')

        if td:
            bus_number = td[0].get_text()
            all_stops = td[3].get_text().split(",")
            all_stops = [x.strip() for x in all_stops]
            required_bus_info[bus_number] = all_stops

    return required_bus_info

@app.route('/v1/all_stops')
def all_stops()->jsonify:
    url = "https://narasimhadatta.info/bmtc_query.html"
    json = urlopen(url).read().decode()
    all_stops = []
    soup = BeautifulSoup(json, 'html.parser')

    for item in soup.find_all('option'):
        all_stops.append(item.get_text().strip())
    return jsonify(all_stops)