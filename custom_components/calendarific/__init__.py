"""Calendarific Platform"""

import json
import logging
from datetime import date, datetime

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_DATE,
    ATTR_DATETIME,
    ATTR_DESCRIPTION,
    ATTR_ISO,
    ATTR_NAME,
    CONF_API_KEY,
    CONF_COUNTRY,
    CONF_STATE,
    DOMAIN,
    SENSOR_PLATFORM,
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Required(CONF_COUNTRY): cv.string,
                vol.Optional(CONF_STATE, default=""): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

_LOGGER = logging.getLogger(__name__)

holiday_dict = {}


def setup(hass, config):
    """Set up platform using YAML."""
    if DOMAIN in config:
        api_key = config[DOMAIN].get(CONF_API_KEY)
        country = config[DOMAIN].get(CONF_COUNTRY)
        state = config[DOMAIN].get(CONF_STATE)
        reader = CalendarificApiReader(api_key, country, state)

        hass.data[DOMAIN] = {"apiReader": reader}
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, SENSOR_PLATFORM)
    )
    return True


async def async_unload_entry(hass, entry):
    """Unload a config entry."""
    return await hass.config_entries.async_forward_entry_unload(entry, SENSOR_PLATFORM)


class CalendarificApiReader:
    def __init__(self, api_key, country, state):
        self._api_count = 0
        self._country = country
        self._state = state
        self._api_key = api_key
        self._lastupdated = None
        _LOGGER.info("apiReader loaded")
        self._holidays = []
        self._next_holidays = []
        self._error_logged = False
        self.update()

    def get_state(self):
        return "new"

    def get_date(self, holiday_name):
        # _LOGGER.debug(f"[get_date] Holiday Name: {holiday_name}")
        today = date.today()
        holiday_datetime = next(
            (i for i in self._holidays if i[ATTR_NAME] == holiday_name), None
        )
        if holiday_datetime:
            holiday_datetime = holiday_datetime[ATTR_DATE][ATTR_DATETIME]
            # _LOGGER.debug(f"[get_date] first holiday_datetime: {holiday_datetime}")
        if (
            not holiday_datetime
            or date(
                holiday_datetime["year"],
                holiday_datetime["month"],
                holiday_datetime["day"],
            )
            < today
        ):
            holiday_datetime = next(
                (i for i in self._next_holidays if i[ATTR_NAME] == holiday_name), None
            )
            if not holiday_datetime:
                _LOGGER.warning(f"{holiday_name}: Future date not found.")
                return None
            holiday_datetime = holiday_datetime[ATTR_DATE][ATTR_DATETIME]
            # _LOGGER.debug(f"[get_date] next holiday_datetime: {holiday_datetime}")
        _LOGGER.debug(f"[get_date] Holiday Date: {holiday_datetime}")
        return date(
            holiday_datetime["year"],
            holiday_datetime["month"],
            holiday_datetime["day"],
        )

    def get_description(self, holiday_name):
        # _LOGGER.debug(f"[get_description] Holiday Name: {holiday_name}")
        descr = next((i for i in self._holidays if i[ATTR_NAME] == holiday_name), None)
        if not descr:
            descr = next(
                (i for i in self._next_holidays if i[ATTR_NAME] == holiday_name), None
            )
            if not descr:
                _LOGGER.warning(f"{holiday_name}: Description not found.")
                return None
        _LOGGER.debug(f"[get_description] Description: {descr[ATTR_DESCRIPTION]}")
        return descr[ATTR_DESCRIPTION]

    def update(self):
        TODAY = date.today()
        if self._lastupdated == TODAY:
            _LOGGER.debug(f"[Init Update] Last Updated: {self._lastupdated} - Stopping")
            return
        _LOGGER.debug(f"[Init Update] Last Updated: {self._lastupdated}")
        self._lastupdated = TODAY
        year = date.today().year
        params = {"country": self._country, "year": year, "location": self._state}
        _LOGGER.info("Updating from Calendarific API")
        calapi = calendarificAPI(self._api_key)
        response = calapi.holidays(params)
        self._api_count += 1
        _LOGGER.debug(f"API Count: {self._api_count}")
        if "error" in response:
            if not self._error_logged:
                _LOGGER.error(response["meta"]["error_detail"])
                self._error_logged = True
            return
        self._holidays = response["response"]["holidays"]
        # _LOGGER.debug(f"API Holidays: {self._holidays}")
        params["year"] = year + 1
        response = calapi.holidays(params)
        self._api_count += 1
        _LOGGER.debug(f"API Count: {self._api_count}")
        if "error" in response:
            if not self._error_logged:
                _LOGGER.error(response["meta"]["error_detail"])
                self._error_logged = True
            return
        self._error_logged = False
        self._next_holidays = response["response"]["holidays"]
        # _LOGGER.debug(f"API Next Holidays: {self._next_holidays}")
        global holiday_dict
        holiday_dict = {}
        for holiday in self._next_holidays:
            good_date = False
            isodate = None
            try:
                isodate = date.fromisoformat(holiday[ATTR_DATE][ATTR_ISO])
            except ValueError:
                try:
                    isodate = datetime.fromisoformat(
                        holiday[ATTR_DATE][ATTR_ISO]
                    ).date()
                except ValueError:
                    pass
                else:
                    good_date = True
            else:
                good_date = True
            if good_date and isodate >= TODAY:
                holiday_dict.update(
                    {
                        holiday[
                            ATTR_NAME
                        ]: f"{holiday[ATTR_NAME]} [{holiday[ATTR_DATE]['iso']}]"
                    }
                )
        for holiday in self._holidays:
            good_date = False
            isodate = None
            try:
                isodate = date.fromisoformat(holiday[ATTR_DATE][ATTR_ISO])
            except ValueError:
                try:
                    isodate = datetime.fromisoformat(
                        holiday[ATTR_DATE][ATTR_ISO]
                    ).date()
                except ValueError:
                    pass
                else:
                    good_date = True
            else:
                good_date = True
            if good_date and isodate >= TODAY:
                holiday_dict.update(
                    {
                        holiday[
                            ATTR_NAME
                        ]: f"{holiday[ATTR_NAME]} [{holiday[ATTR_DATE]['iso']}]"
                    }
                )

        holiday_dict = dict(sorted(holiday_dict.items()))
        # _LOGGER.debug(f"Holiday Dict: {holiday_dict}")

        return True


class calendarificAPI:
    api_key = None

    def __init__(self, api_key):
        self.api_key = api_key

    def holidays(self, parameters):
        url = "https://calendarific.com/api/v2/holidays?"

        if "api_key" not in parameters:
            parameters["api_key"] = self.api_key

        response = requests.get(url, params=parameters)
        data = json.loads(response.text)

        if response.status_code != 200:
            if "error" not in data:
                data["error"] = "Unknown error."

        return data
