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
        response = self.s.get("https://www.mijntuin.org/",headers=header,timeout=10,allow_redirects=False)
        _LOGGER.info(f"{NAME} https://www.mijntuin.org get response.status_code {response.status_code}, login header: {response.headers}")
        response = self.s.get("https://www.mijntuin.org/login",headers=header,timeout=10,allow_redirects=False)
        # assert response.status_code == 200
        _LOGGER.info(f"{NAME} https://www.mijntuin.org/login get response.status_code {response.status_code}, login header: {response.headers}")
        data  = {"email": username, "password": password, "login": "Aanmelden"}
        response = self.s.post("https://www.mijntuin.org/login",data=data,headers=header,timeout=10,allow_redirects=False)
        _LOGGER.info(f"{NAME} login post result status code: {response.status_code}, response: {response.text}")
        _LOGGER.info(f"{NAME} response.status_code {response.status_code}, login header: {response.headers}")
        # assert response.status_code == 302
        response = self.s.get("https://www.mijntuin.org/",headers=header,timeout=10,allow_redirects=False)
        response = self.s.get("https://www.mijntuin.org/dashboard",headers=header,timeout=10,allow_redirects=False)
        _LOGGER.info(f"{NAME} https://www.mijntuin.org/dashboard get response.status_code {response.status_code}, login header: {response.headers}")
        _LOGGER.info(f"{NAME} login post result status code: {response.status_code}, response: {response.text}")
        # assert response.status_code == 200
        soup = BeautifulSoup(response.text, 'html.parser')
        calendarlink = soup.find_all('li', id_='calendar').a.get('href')
        _LOGGER.info(f"{NAME} calendarlink {calendarlinks}")
        return calendarlink

    def getCalendar(self, calendarlink):
    # https://www.mijntuin.org/login, POST
    # example payload
    # form data: email=username%40gmail.com&password=password&login=Aanmelden
    # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded"}
        response = self.s.get(calendarlink,headers=header,timeout=10,allow_redirects=False)
        _LOGGER.info(f"{NAME} calendarlink response.status_code {response.status_code}, login header: {response.headers}")
        _LOGGER.info(f"{NAME} calendarlink result status code: {response.status_code}, response: {response.text}")
        # assert response.status_code == 302
        div_calendar = soup.find('div', class_='whitebox')
        div_months =   div_calendar.find_all('div', id_='tab*')
        
        for div_month in div_months:
            li_actions = div_month.find_all('li', 'title')
            for li_action in li_actions:
                _LOGGER.info(f"{NAME} li_action {li_action}")
        return True