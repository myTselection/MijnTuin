import logging
import asyncio
from datetime import date, datetime, timedelta
import calendar

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

from . import DOMAIN, NAME
from .utils import *

_LOGGER = logging.getLogger(__name__)
_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.0%z"


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("username", default=""): cv.string,
        vol.Required("password", default=""): cv.string,
    }
)

MIN_TIME_BETWEEN_UPDATES = timedelta(hours=1)


async def dry_setup(hass, config_entry, async_add_devices):
    config = config_entry
    username = config.get("username")
    password = config.get("password")

    check_settings(config, hass)
    sensors = []
    
    componentData = ComponentData(
        username,
        password,
        hass
    )
    await componentData._force_update()
    
    generalSensor = ComponentSensorGeneral(componentData, hass)
    sensors.append(generalSensor)

    acitvityTypes = componentData._activities.keys()
    # assert componentData._usage_details is not None
    # acitvityTypes = ["Bekalken", "Bemesten", "Bloeien", "Maaien", "Oogsten", "Opruimen", "Overwinteren", "Planten", "Preventief behandelen", "Rooien", "Scheren", "Scheuren", "Snoeien", "Stekken", "Toppen", "Uitdunnen", "verpotten", "Water geven", "Zaaien"]

    _LOGGER.info(f"{NAME} Found activity types: {acitvityTypes}")
    for activityType in acitvityTypes:
        sensor = ComponentSensor(componentData, hass, activityType)
        sensors.append(sensor)
    
    # sensorInternet = ComponentInternetSensor(componentData, hass)
    # sensors.append(sensorInternet)

    # sensorSubscription = ComponentSubscriptionSensor(componentData, hass)
    # sensors.append(sensorSubscription)
    
    async_add_devices(sensors)


async def async_setup_platform(
    hass, config_entry, async_add_devices, discovery_info=None
):
    """Setup sensor platform for the ui"""
    _LOGGER.info("async_setup_platform " + NAME)
    await dry_setup(hass, config_entry, async_add_devices)
    return True


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform for the ui"""
    _LOGGER.info("async_setup_entry " + NAME)
    config = config_entry.data
    await dry_setup(hass, config, async_add_devices)
    return True


async def async_remove_entry(hass, config_entry):
    _LOGGER.info("async_remove_entry " + NAME)
    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the integration")
    except ValueError:
        pass
        

class ComponentData:
    def __init__(self, username, password, hass):
        self._username = username
        self._password = password
        self._session = ComponentSession()
        self._hass = hass
        self._lastupdate = None
        self._calendarData = None
        self._activities = dict()
        self._months = dict()
        self._plants = dict()
        
    # same as update, but without throttle to make sure init is always executed
    async def _force_update(self):
        _LOGGER.info("Fetching intit stuff for " + NAME)
        if not(self._session):
            self._session = ComponentSession()

        if self._session:
            calendarlink = await self._hass.async_add_executor_job(lambda: self._session.login(self._username, self._password))
            _LOGGER.info(f"{NAME} login completed")
            self._calendarData = await self._hass.async_add_executor_job(lambda: self._session.getCalendar(calendarlink))
            _LOGGER.info(f"{NAME} calendar data update")
            self._lastupdate = datetime.now()
            self._activities = dict()
            self._months = dict()
            self._plants = dict()
            for month, monthData in self._calendarData.items():
                month_name = calendar.month_name[int(month.split("-")[0])]
                # _LOGGER.info(f"Mijn Tuin updating month {month_name} for acitivty {self._activityType}")
                for activity, plants in monthData.items():
                    self._activities[activity] = self._activities.get(activity,0) + 1
                    self._months[month_name] = self._months.get(month_name,0) + 1
                    for plant in plants:
                        self._plants[plant.get("name")] = self._plants.get(plant.get("name"),0) + 1
            
    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def _update(self):
        await self._force_update()

    async def update(self):
        await self._update()
    
    def clear_session(self):
        self._session : None

class ComponentSensorGeneral(Entity):
    def __init__(self, data, hass):
        self._data = data
        self._hass = hass
        self._last_update = None
        self._activities = {}
        self._numberOfActivitiesThisMonth = 0

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._numberOfActivitiesThisMonth

    async def async_update(self):
        await self._data.update()
        self._last_update =  self._data._lastupdate
        month_name = datetime.now().strftime("%B")

        self._numberOfActivitiesThisMonth = self._data._months.get(month_name,0)
        # self._activities = {}
        # currMonth = datetime.now().strftime("%B")
        # for month, monthData in self._data._calendarData.items():
        #     month_name = calendar.month_name[int(month.split("-")[0])]
        #     # _LOGGER.info(f"Mijn Tuin updating month {month_name} for acitivty {self._activityType}")            
        #     for activity, plants in monthData.items():
        #         # _LOGGER.info(f"Mijn Tuin updating month {month_name} for acitivty {self._activityType}, curr activity {activity}")
        #         self._activities[month_name] = self._activities.get(month_name,0) + 1
            
        
    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + NAME)
        self._data.clear_session()


    @property
    def icon(self) -> str:
        """Shows the correct icon for container."""
        return "mdi:sprout-outline"
        
    @property
    def unique_id(self) -> str:
        """Return the name of the sensor."""
        return (
            NAME
        )

    @property
    def name(self) -> str:
        return self.unique_id

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: NAME,
            "last update": self._last_update,
            "activitiesThisMonth": self._numberOfActivitiesThisMonth,
            "Plants": ', '.join(str(key) for key in self._data._plants.keys()),
            "Activities": ', '.join(str(key) for key in self._data._activities.keys()),
            "January": self._data._months.get("January",0),
            "February": self._data._months.get("February",0),
            "March": self._data._months.get("March",0),
            "April": self._data._months.get("April",0),
            "May": self._data._months.get("May",0),
            "June": self._data._months.get("June",0),
            "July": self._data._months.get("July",0),
            "August": self._data._months.get("August",0),
            "September": self._data._months.get("September",0),
            "October": self._data._months.get("October",0),
            "November": self._data._months.get("November",0),
            "December": self._data._months.get("December",0)
        }

    @property
    def device_info(self) -> dict:
        """I can't remember why this was needed :D"""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": DOMAIN,
        }

    @property
    def unit(self) -> int:
        """Unit"""
        return int

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement this sensor expresses itself in."""
        return "#"

    @property
    def friendly_name(self) -> str:
        return self.unique_id
   

class ComponentSensor(Entity):
    def __init__(self, data, hass, activityType):
        self._data = data
        self._hass = hass
        self._last_update = None
        self._activityType = activityType
        self._activities = {}
        self._numberOfActionsThisMonth = 0


    @property
    def state(self):
        """Return the state of the sensor."""
        return self._numberOfActionsThisMonth

    async def async_update(self):
        await self._data.update()
        self._last_update =  self._data._lastupdate
        self._numberOfActionsThisMonth = 0
        self._activities = {}
        currMonth = datetime.now().strftime("%B")
        for month, monthData in self._data._calendarData.items():
            month_name = calendar.month_name[int(month.split("-")[0])]
            # _LOGGER.info(f"Mijn Tuin updating month {month_name} for acitivty {self._activityType}")
            
            for activity, plants in monthData.items():
                # _LOGGER.info(f"Mijn Tuin updating month {month_name} for acitivty {self._activityType}, curr activity {activity}")
                if activity.lower() == self._activityType.lower():                        
                    if currMonth == month_name:
                        self._numberOfActionsThisMonth += 1
                        if self._activities.get(month_name):
                            self._activities[month_name].append(plants)
                        else:
                            self._activities[month_name] = plants
                    else:
                        if self._activities.get(month_name):
                            self._activities[month_name] = self._activities.get(month_name, "") + ", " + ', '.join(plant.get("name","") for plant in plants)
                        else:
                            self._activities[month_name] = ', '.join(plant.get("name","") for plant in plants)

    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + NAME)
        self._data.clear_session()


    @property
    def icon(self) -> str:
        """Shows the correct icon for container."""
        return "mdi:sprout-outline"
        
    @property
    def unique_id(self) -> str:
        """Return the name of the sensor."""
        return (
            NAME + " " + self._activityType
        )

    @property
    def name(self) -> str:
        return self.unique_id

    @property
    def extra_state_attributes(self) -> dict:
        """Return the state attributes."""
        return {
            ATTR_ATTRIBUTION: NAME,
            "last update": self._last_update,
            "activityType": self._activityType,
            "actionsThisMonth": self._numberOfActionsThisMonth,
            "January": self._activities.get("January",0),
            "February": self._activities.get("February",0),
            "March": self._activities.get("March",0),
            "April": self._activities.get("April",0),
            "May": self._activities.get("May",0),
            "June": self._activities.get("June",0),
            "July": self._activities.get("July",0),
            "August": self._activities.get("August",0),
            "September": self._activities.get("September",0),
            "October": self._activities.get("October",0),
            "November": self._activities.get("November",0),
            "December": self._activities.get("December",0)
        }

    @property
    def device_info(self) -> dict:
        """I can't remember why this was needed :D"""
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": DOMAIN,
        }

    @property
    def unit(self) -> int:
        """Unit"""
        return int

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement this sensor expresses itself in."""
        return "#"

    @property
    def friendly_name(self) -> str:
        return self.unique_id
        
