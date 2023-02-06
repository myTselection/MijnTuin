import json
import logging
import pprint
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import List
import requests
from pydantic import BaseModel

from . import DOMAIN, NAME
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.0%z"

def check_settings(config, hass):
    if not any(config.get(i) for i in ["username"]):
        _LOGGER.error("username was not set")
    else:
        return True
        
    if not config.get("password"):
        _LOGGER.error("password was not set")
    else:
        return True

    raise vol.Invalid("Missing settings to setup the sensor.")


class ComponentSession(object):
    def __init__(self):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "Python/3"

    def login(self, username, password):
    # https://www.mijntuin.org/login, POST
    # example payload
    # form data: email=username%40gmail.com&password=password&login=Aanmelden
    # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.s.get("https://www.mijntuin.org/",headers=header,timeout=10)
        # assert response.status_code == 200
        data  = {"email": username, "password": password, "login": "Aanmelden"}
        response = self.s.post("https://www.mijntuin.org/login",data=data,headers=header,timeout=10)
        _LOGGER.info(f"{NAME} login post result status code: " + str(response.status_code) + ", response: " + response.text)
        _LOGGER.info(f"{NAME} login header: " + str(response.headers))
        # assert response.status_code == 302
        response = self.s.get("https://www.mijntuin.org/dashboard",headers=header,timeout=10)
        _LOGGER.info(f"{NAME} login post result status code: " + str(response.status_code) + ", response: " + response.text)
        _LOGGER.info(f"{NAME} login header: " + str(response.headers))
        # assert response.status_code == 200
        return True

    def getCalendar(self, username, password):
    # https://www.mijntuin.org/login, POST
    # example payload
    # form data: email=username%40gmail.com&password=password&login=Aanmelden
    # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        data  = {"email": username, "password": password, "login": "Aanmelden"}
        response = self.s.post("https://www.mijntuin.org/login",data=data,headers=header,timeout=10)
        _LOGGER.info(f"{NAME} login post result status code: " + str(response.status_code) + ", response: " + response.text)
        _LOGGER.info(f"{NAME} login header: " + str(response.headers))
        # assert response.status_code == 302
        return True