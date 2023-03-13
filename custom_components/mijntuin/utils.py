import json
import logging
import pprint
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import List
import requests
from bs4 import BeautifulSoup

# from . import DOMAIN, NAME

DOMAIN = "mijntuin"
NAME = "Mijn Tuin"
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
        self.cookies = dict()
        self.calendarlink = None

    def login(self, username, password):
    # https://www.mijntuin.org/login, POST
    # example payload
    # form data: email=username%40gmail.com&password=password&login=Aanmelden
    # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
        response = self.s.get("https://www.mijntuin.org/",headers=header,timeout=10,allow_redirects=False)
        _LOGGER.debug(f"{NAME} https://www.mijntuin.org get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        self.cookies["PHPSESSID"] = response.cookies.get("PHPSESSID")
        self.cookies["session"] = response.cookies.get("session")
        self.s.cookies["PHPSESSID"] = response.cookies.get("PHPSESSID")
        self.s.cookies["session"] = response.cookies.get("session")
        _LOGGER.debug(f"cookies: {self.cookies}")
        response = self.s.get("https://www.mijntuin.org/login",headers=header, cookies=self.cookies,timeout=10,allow_redirects=False)
        # assert response.status_code == 200
        _LOGGER.debug(f"{NAME} https://www.mijntuin.org/login get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        data  = {"email": username, "password": password, "login": "Aanmelden"}
        # self.cookies = response.cookies
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE","referer":"https://www.mijntuin.org/login"}
        response = self.s.post("https://www.mijntuin.org/login",data=data,headers=header,cookies=self.cookies, timeout=10,allow_redirects=False)
        _LOGGER.debug(f"{NAME} login post result status code: {response.status_code}, response: {response.text}, login cookies: {response.cookies}")
        _LOGGER.debug(f"{NAME} response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        # assert response.status_code == 302
        # self.cookies = response.cookies
        response = self.s.get("https://www.mijntuin.org/",headers=header,cookies=self.cookies,timeout=10,allow_redirects=False)
        # self.cookies = response.cookies
        response = self.s.get("https://www.mijntuin.org/dashboard",headers=header,cookies=self.cookies,timeout=10,allow_redirects=False)
        # self.cookies = response.cookies
        _LOGGER.debug(f"{NAME} https://www.mijntuin.org/dashboard get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        _LOGGER.debug(f"{NAME} login post result status code: {response.status_code}, response: {response.text}, login cookies: {response.cookies}")
        # assert response.status_code == 200
        soup = BeautifulSoup(response.text, 'html.parser')
        li_calendar  = soup.select_one("li#calendar")
        if li_calendar:
            self.calendarlink = li_calendar.a.get('href')
        _LOGGER.debug(f"{NAME} calendarlink {self.calendarlink}")
        return self.calendarlink

    def getCalendar(self, calendarlink):
        # https://www.mijntuin.org/login, POST
        # example payload
        # form data: email=username%40gmail.com&password=password&login=Aanmelden
        # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
        response = self.s.get(calendarlink,headers=header,cookies=self.cookies,timeout=10,allow_redirects=False)
        # cookies = response.cookies
        _LOGGER.debug(f"{NAME} calendarlink response.status_code {response.status_code}, login header: {response.headers}")
        # _LOGGER.info(f"{NAME} calendarlink result status code: {response.status_code}, response: {response.text}")
        # assert response.status_code == 302
        soup = BeautifulSoup(response.text, 'html.parser')
        div_calendar = soup.find('div', class_='whitebox')
        # select all div elements whose id starts with "tab"
        tab_divs = div_calendar.select('div[id^="tab"]')

        # create an empty dictionary to store the data
        calendar = dict()

        # print the id and text content of each selected div element
        for tab_div in tab_divs:
            month = tab_div.get('id')
            month = month.replace("tab-","")
            # find all the li tags within the div tag
            li_tags = tab_div.find_all('li')

            # create an empty list to store the data for each section
            month_actions = {}

            currentSection = None

            # loop through each li tag
            for li_tag in li_tags:
                # check if the li tag has a class of 'title'
                if li_tag.has_attr('class') and 'title' in li_tag['class']:
                    # create a new section dictionary
                    currentSection = li_tag.text.strip()
                    # section = {'title': li_tag.text.strip(), 'items': []}
                    month_actions[currentSection] = []
                else:
                    # create a new item dictionary
                    item = {'name': '', 'description': '','photo': {}, 'link': '', 'buttons':{}}
                    item['photo']['alt'] = li_tag.find('img').get('alt', '')
                    item['photo']['src'] = li_tag.find('img').get('src', '')
                    nameAndDescription = li_tag.find('span', class_='name').text.strip().split(": ")
                    item['name'] = nameAndDescription[0]
                    item['description'] = nameAndDescription[1].capitalize()
                    item['link'] = li_tag.find('span', class_='extra').find('a').get('href', '')
                    if li_tag.find('span', class_='buttons'):
                        item['buttons']['text'] = li_tag.find('span', class_='buttons').text.strip()
                        item['buttons']['link'] = li_tag.find('span', class_='buttons').find('a').get('href', '')
                    # append the item to the current section
                    month_actions[currentSection].append(item)
                    # month_actions[-1]['items'].append(item)
            _LOGGER.debug(f"{NAME} calendar month {month}, month_actions {month_actions}")
            calendar[month] = month_actions

        return calendar
        