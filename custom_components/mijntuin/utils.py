import json
import logging
import pprint
from collections import defaultdict
from datetime import date, datetime, timedelta
import calendar
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
        self.gardenlink = None

    def login(self, username, password):
    # https://www.mijntuin.org/login, POST
    # example payload
    # form data: email=username%40gmail.com&password=password&login=Aanmelden
    # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
        response = self.s.get("https://www.mijntuin.org/",headers=header,timeout=40,allow_redirects=False)
        _LOGGER.debug(f"{NAME} https://www.mijntuin.org get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        self.cookies["PHPSESSID"] = response.cookies.get("PHPSESSID")
        self.cookies["session"] = response.cookies.get("session")
        self.s.cookies["PHPSESSID"] = response.cookies.get("PHPSESSID")
        self.s.cookies["session"] = response.cookies.get("session")
        _LOGGER.debug(f"cookies: {self.cookies}")
        response = self.s.get("https://www.mijntuin.org/login",headers=header, cookies=self.cookies,timeout=40,allow_redirects=False)
        # assert response.status_code == 200
        _LOGGER.debug(f"{NAME} https://www.mijntuin.org/login get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        data  = {"email": username, "password": password, "login": "Aanmelden"}
        # self.cookies = response.cookies
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE","referer":"https://www.mijntuin.org/login"}
        response = self.s.post("https://www.mijntuin.org/login",data=data,headers=header,cookies=self.cookies, timeout=40,allow_redirects=False)
        _LOGGER.debug(f"{NAME} login post result status code: {response.status_code}, response: {response.text}, login cookies: {response.cookies}")
        _LOGGER.debug(f"{NAME} response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        # assert response.status_code == 302
        # self.cookies = response.cookies
        response = self.s.get("https://www.mijntuin.org/",headers=header,cookies=self.cookies,timeout=40,allow_redirects=False)
        # self.cookies = response.cookies
        response = self.s.get("https://www.mijntuin.org/dashboard",headers=header,cookies=self.cookies,timeout=40,allow_redirects=False)
        # self.cookies = response.cookies
        _LOGGER.debug(f"{NAME} https://www.mijntuin.org/dashboard get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
        _LOGGER.debug(f"{NAME} login post result status code: {response.status_code}, response: {response.text}, login cookies: {response.cookies}")
        # assert response.status_code == 200
        soup = BeautifulSoup(response.text, 'html.parser')
        li_calendar  = soup.select_one("li#calendar")
        if li_calendar:
            self.gardenlink = li_calendar.a.get('href')
        _LOGGER.debug(f"{NAME} calendarlink {self.gardenlink}")
        self.gardenlink = self.gardenlink.replace('/calendar','')
        return self.gardenlink
    
    def getTaskDetails(self, tasklink):
        # https://www.mijntuin.org/login, POST
        # example payload
        # form data: email=username%40gmail.com&password=password&login=Aanmelden
        # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
        response = self.s.get(tasklink,headers=header,cookies=self.cookies,timeout=40,allow_redirects=False)
        # cookies = response.cookies
        _LOGGER.debug(f"{NAME} tasklink response.status_code {response.status_code}, login header: {response.headers}")
        # _LOGGER.info(f"{NAME} calendarlink result status code: {response.status_code}, response: {response.text}")
        # assert response.status_code == 302
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #old code:
        div_plantAction = soup.find('div', {'class': 'plantActions'})
        # # select all div elements whose id starts with "tab"
        description = div_plantAction.find('div', {'class': 'description mt-3'})

        # # find the first <meta> tag with the property attribute equal to 'og:description'
        # tag = soup.find('meta', {'property': 'og:description'})

        # # extract the content attribute of the <meta> tag
        # description = tag.get('content')

        if description:
           description = description.text.strip().replace("\n","<br/>").replace("\r","<br/>")
        else:
           description =  ''

        # # Find the div tag with id "plants"
        # div_plants = soup.find('div', {'id': 'plants'})

        # # Find the link of the "Info" page of the plant within the div tag with id "plants"
        # link = div_plants.find('a')['href']
        
        # return [link, description]

        return description[:800]

    
    def getCalendar(self, plants):
        # https://www.mijntuin.org/login, POST
        # example payload
        # form data: email=username%40gmail.com&password=password&login=Aanmelden
        # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
        response = self.s.get(self.gardenlink+'/calendar',headers=header,cookies=self.cookies,timeout=40,allow_redirects=False)
        # cookies = response.cookies
        _LOGGER.debug(f"{NAME} calendarlink response.status_code {response.status_code}, login header: {response.headers}")
        # _LOGGER.info(f"{NAME} calendarlink result status code: {response.status_code}, response: {response.text}")
        # assert response.status_code == 302
        soup = BeautifulSoup(response.text, 'html.parser')
        div_calendar = soup.find('div', class_='whitebox')
        # select all div elements whose id starts with "tab"
        tab_divs = div_calendar.select('div[id^="tab"]')

        currMonth = datetime.now().strftime("%B")

        # create an empty dictionary to store the data
        calendarDict = dict()

        # print the id and text content of each selected div element
        for tab_div in tab_divs:
            month = tab_div.get('id')
            month = month.replace("tab-","")
            month_name = calendar.month_name[int(month.split("-")[0])]
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
                    item = {'name': '', 'description': '','photo': {}, 'link': ''}
                    item['photo']['alt'] = li_tag.find('img').get('alt', '')
                    item['photo']['src'] = li_tag.find('img').get('src', '')
                    nameAndDescription = li_tag.find('span', class_='name').text.strip().split(": ")
                    item['name'] = nameAndDescription[0]
                    item['description'] = nameAndDescription[1].capitalize()
                    item['link'] = li_tag.find('span', class_='extra').find('a').get('href', '')
                    plant_details = plants.get(nameAndDescription[0])
                    if plant_details:
                        item['plant_link'] = plant_details.get('link')
                        item['latin_name'] = plant_details.get('latin_name')
                    if currMonth == month_name and item.get('link'):
                        item['details'] = self.getTaskDetails(item.get('link'))
                    # if li_tag.find('span', class_='buttons'):
                    #     item['buttons']['text'] = li_tag.find('span', class_='buttons').text.strip()
                    #     item['buttons']['link'] = li_tag.find('span', class_='buttons').find('a').get('href', '')
                    # append the item to the current section
                    month_actions[currentSection].append(item)
                    # month_actions[-1]['items'].append(item)
            _LOGGER.debug(f"{NAME} calendar month {month}, month_actions {month_actions}")
            calendarDict[month] = month_actions

        return calendarDict
        


    def getPlants(self):
        # https://www.mijntuin.org/login, POST
        # example payload
        # form data: email=username%40gmail.com&password=password&login=Aanmelden
        # example response, HTTP 302
        header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
        response = self.s.get(self.gardenlink+'/all',headers=header,cookies=self.cookies,timeout=40,allow_redirects=False)
        # cookies = response.cookies
        _LOGGER.debug(f"{NAME} gardenlink response.status_code {response.status_code}, login header: {response.headers}")
        # _LOGGER.info(f"{NAME} calendarlink result status code: {response.status_code}, response: {response.text}")
        # assert response.status_code == 302
        soup = BeautifulSoup(response.text, 'html.parser')
        div_calendar = soup.find('div', class_='whitebox')

        plants = dict()
        index = 0
        for li in div_calendar.select('#grid li'):
            link = li.select_one('a')['href']
            name = li.select_one('.name').text
            photo = li.select_one('.photo img')['src']
            latin_name = li.select_one('.extra').text
            # remove_url = li.select_one('.removePlant')['href']
            # add_wishlist_url = li.select_one('.wish')['href']
            # add_exchange_url = li.select_one('.exchange')['href']
            plants[name] = {
                'name': name,
                'link': link,
                'photo': photo,
                'latin_name': latin_name
                #, 'remove_url': remove_url,
                # 'add_wishlist_url': add_wishlist_url,
                # 'add_exchange_url': add_exchange_url
            }
            index += 1
            if index > 100:
                _LOGGER.error(f"Many plants {index} detected, this may lead to overload & instability of HA!")

        return plants
        
