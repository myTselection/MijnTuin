import requests
import logging
import json
from urllib.parse import urlsplit, parse_qs
from bs4 import BeautifulSoup
# from "../custom_components/telenet_telemeter/utils" import .
# import sys
# sys.path.append('../custom_components/telenet_telemeter/')
# from utils import ComponentSession, dry_setup
# from sensor import *
from secret import USERNAME, PASSWORD
NAME = "Mijn Tuin"
_LOGGER = logging.getLogger(__name__)

config = dict();
config["username"]: USERNAME
config["password"]: PASSWORD
hass = "test"
def async_add_devices(sensors): 
     _LOGGER.debug(f"session.userdetails {json.dumps(sensorsindent=4)}")

#run this test on command line with: python -m unittest test_component_session

logging.basicConfig(level=logging.DEBUG)


s = requests.Session()
s.headers["User-Agent"] = "Python/3"
cookies = dict()
calendarlink = None
def login(username, password):
# https://www.mijntuin.org/login, POST
# example payload
# form data: email=username%40gmail.com&password=password&login=Aanmelden
# example response, HTTP 302
    header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
    response = s.get("https://www.mijntuin.org/",headers=header,timeout=10,allow_redirects=False)
    _LOGGER.info(f"{NAME} https://www.mijntuin.org get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
    s.cookies["PHPSESSID"] = response.cookies.get("PHPSESSID")
    s.cookies["session"] = response.cookies.get("session")
    cookies["PHPSESSID"] = response.cookies.get("PHPSESSID")
    cookies["session"] = response.cookies.get("session")
    _LOGGER.info(f"cookies: {s.cookies}")
    response = s.get("https://www.mijntuin.org/login",headers=header, cookies=cookies,timeout=10,allow_redirects=False)
    # assert response.status_code == 200
    _LOGGER.info(f"{NAME} https://www.mijntuin.org/login get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
    data  = {"email": username, "password": password, "login": "Aanmelden"}
    # cookies = response.cookies
    header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE","referer":"https://www.mijntuin.org/login"}
    response = s.post("https://www.mijntuin.org/login",data=data,headers=header,cookies=cookies, timeout=10,allow_redirects=False)
    _LOGGER.info(f"{NAME} login post result status code: {response.status_code}, response: {response.text}, login cookies: {response.cookies}")
    _LOGGER.info(f"{NAME} response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
    # assert response.status_code == 302
    # cookies = response.cookies
    response = s.get("https://www.mijntuin.org/",headers=header,cookies=cookies,timeout=10,allow_redirects=False)
    # cookies = response.cookies
    response = s.get("https://www.mijntuin.org/dashboard",headers=header,cookies=cookies,timeout=10,allow_redirects=False)
    # cookies = response.cookies
    _LOGGER.info(f"{NAME} https://www.mijntuin.org/dashboard get response.status_code {response.status_code}, login header: {response.headers}, login cookies: {response.cookies}")
    # _LOGGER.info(f"{NAME} login post result status code: {response.status_code}, response: {response.text}, login cookies: {response.cookies}")
    # assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    li_calendar  = soup.select_one("li#calendar")
    _LOGGER.info(f"li_calendar: {li_calendar}")
    if li_calendar:
        calendarlink = li_calendar.a.get('href')
    _LOGGER.info(f"{NAME} calendarlink {calendarlink}")
    return calendarlink

def getCalendar(calendarlink):
# https://www.mijntuin.org/login, POST
# example payload
# form data: email=username%40gmail.com&password=password&login=Aanmelden
# example response, HTTP 302
    header = {"Content-Type": "application/x-www-form-urlencoded","accept-language":"nl-BE"}
    response = s.get(calendarlink,headers=header,cookies=cookies,timeout=10,allow_redirects=False)
    # cookies = response.cookies
    _LOGGER.info(f"{NAME} calendarlink response.status_code {response.status_code}, login header: {response.headers}")
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
        month_actions = []

        # loop through each li tag
        for li_tag in li_tags:
            # check if the li tag has a class of 'title'
            if li_tag.has_attr('class') and 'title' in li_tag['class']:
                # create a new section dictionary
                section = {'title': li_tag.text.strip(), 'items': []}
                month_actions.append(section)
            else:
                # create a new item dictionary
                item = {'photo': {}, 'name': '', 'extra': {}, 'buttons': {}}
                item['photo']['alt'] = li_tag.find('img').get('alt', '')
                item['photo']['class'] = li_tag.find('img').get('class', [])
                item['name'] = li_tag.find('span', class_='name').text.strip()
                item['extra']['text'] = li_tag.find('span', class_='extra').text.strip()
                item['extra']['link'] = li_tag.find('span', class_='extra').find('a').get('href', '')
                if li_tag.find('span', class_='buttons'):
                    item['buttons']['text'] = li_tag.find('span', class_='buttons').text.strip()
                    item['buttons']['link'] = li_tag.find('span', class_='buttons').find('a').get('href', '')
                # append the item to the current section
                month_actions[-1]['items'].append(item)
        calendar[month] = month_actions

    # convert the dictionary into JSON format
    json_data = json.dumps(calendar)

    # print the JSON data
    print(json_data)
    return True

calendarlink = login(USERNAME,PASSWORD)
calendar = getCalendar(calendarlink)