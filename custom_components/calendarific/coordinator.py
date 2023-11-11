"""Example integration using DataUpdateCoordinator."""

import json
import logging
from datetime import date, datetime

import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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
    SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class CalendarificCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        # self.my_api = my_api
        self._country = entry.get(CONF_COUNTRY)
        self._state = entry.get(CONF_STATE)
        self._api_key = entry.get(CONF_API_KEY)
        self._lastupdated = None
        _LOGGER.info("CalendarificCoordinator loaded")
        self._holidays = []
        self._next_holidays = []
        self._holiday_dict = {}
        self._error_logged = False

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # try:
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        #    async with async_timeout.timeout(10):
        # Grab active context variables to limit data required to be fetched from API
        # Note: using context is not required if there is no need or ability to limit
        # data retrieved from API.
        #        listening_idx = set(self.async_contexts())
        #        return await self.my_api.fetch_data(listening_idx)
        # except ApiAuthError as err:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #    raise UpdateFailed(f"Error communicating with API: {err}")
        TODAY = date.today()
        if self._lastupdated == TODAY:
            return
        self._lastupdated = TODAY
        year = date.today().year
        params = {"country": self._country, "year": year, "location": self._state}
        calapi = CalendarificAPI(self._api_key)
        response = calapi.holidays(params)
        _LOGGER.info("Updating from Calendarific api")
        if "error" in response:
            if not self._error_logged:
                _LOGGER.error(response["meta"]["error_detail"])
                self._error_logged = True
            return
        self._holidays = response["response"]["holidays"]
        # _LOGGER.debug(f"API Holidays: {self._holidays}")
        params["year"] = year + 1
        response = calapi.holidays(params)
        if "error" in response:
            if not self._error_logged:
                _LOGGER.error(response["meta"]["error_detail"])
                self._error_logged = True
            return
        self._error_logged = False
        self._next_holidays = response["response"]["holidays"]
        # _LOGGER.debug(f"API Next Holidays: {self._next_holidays}")
        # global holiday_dict
        # holiday_dict = {}
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
                self._holiday_dict.update(
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
                self._holiday_dict.update(
                    {
                        holiday[
                            ATTR_NAME
                        ]: f"{holiday[ATTR_NAME]} [{holiday[ATTR_DATE]['iso']}]"
                    }
                )

        self._holiday_dict = dict(sorted(self._holiday_dict.items()))
        # _LOGGER.debug(f"Holiday Dict: {self._holiday_dict}")

        return True

    def get_date(self, holiday_name):
        _LOGGER.debug(f"[get_date] holiday_name: {holiday_name}")
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
        _LOGGER.debug(f"[get_date] holiday_datetime: {holiday_datetime}")
        return date(
            holiday_datetime["year"],
            holiday_datetime["month"],
            holiday_datetime["day"],
        )

    def get_description(self, holiday_name):
        _LOGGER.debug(f"[get_description] holiday_name: {holiday_name}")
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


class CalendarificAPI:
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
