""" config flow """
from __future__ import annotations

import logging
import uuid
from collections import OrderedDict

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import holiday_list
from .const import (
    CONF_DATE_FORMAT,
    CONF_HOLIDAY,
    CONF_ICON_NORMAL,
    CONF_ICON_SOON,
    CONF_ICON_TODAY,
    CONF_SOON,
    CONF_UNIT_OF_MEASUREMENT,
    DEFAULT_DATE_FORMAT,
    DEFAULT_ICON_NORMAL,
    DEFAULT_ICON_SOON,
    DEFAULT_ICON_TODAY,
    DEFAULT_SOON,
    DEFAULT_UNIT_OF_MEASUREMENT,
    DOMAIN,
)

COMPONENT_CONFIG_URL = (
    "https://github.com/pinkywafer/Calendarific#sensor-configuration-parameters"
)

_LOGGER = logging.getLogger(__name__)


@callback
def calendarific_entries(hass: HomeAssistant):
    return set((entry.data) for entry in hass.config_entries.async_entries(DOMAIN))


class CalendarificConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    "handle config flow"
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        self._errors = {}
        self._data = {}
        self._data["unique_id"] = str(uuid.uuid4())

    async def async_step_user(self, user_input=None) -> FlowResult:
        if holiday_list == []:
            return self.async_abort(reason="no_holidays_found")
        self._errors = {}
        if user_input is not None:
            self._data.update(user_input)
            if self._errors == {}:
                if self._data["name"] == "":
                    self._data["name"] = self._data["holiday"]
                return self.async_create_entry(
                    title=self._data["name"], data=self._data
                )
        return await self._show_user_form(user_input)

    async def _show_user_form(self, user_input):
        name = ""
        holiday = ""
        icon_normal = DEFAULT_ICON_NORMAL
        icon_soon = DEFAULT_ICON_SOON
        icon_today = DEFAULT_ICON_TODAY
        date_format = DEFAULT_DATE_FORMAT
        days_as_soon = DEFAULT_SOON
        unit_of_measurement = DEFAULT_UNIT_OF_MEASUREMENT
        if user_input is not None:
            if CONF_NAME in user_input:
                name = user_input[CONF_NAME]
            if CONF_HOLIDAY in user_input:
                holiday = user_input[CONF_HOLIDAY]
            if CONF_ICON_NORMAL in user_input:
                icon_normal = user_input[CONF_ICON_NORMAL]
            if CONF_ICON_SOON in user_input:
                icon_soon = user_input[CONF_ICON_SOON]
            if CONF_ICON_TODAY in user_input:
                icon_today = user_input[CONF_ICON_TODAY]
            if CONF_DATE_FORMAT in user_input:
                date_format = user_input[CONF_DATE_FORMAT]
            if CONF_UNIT_OF_MEASUREMENT in user_input:
                unit_of_measurement = user_input[CONF_UNIT_OF_MEASUREMENT]
        data_schema = OrderedDict()
        data_schema[vol.Required(CONF_HOLIDAY, default=holiday)] = vol.In(holiday_list)
        data_schema[vol.Optional(CONF_NAME, default=name)] = str
        data_schema[
            vol.Required(CONF_UNIT_OF_MEASUREMENT, default=unit_of_measurement)
        ] = str
        data_schema[vol.Required(CONF_ICON_NORMAL, default=icon_normal)] = str
        data_schema[vol.Required(CONF_ICON_TODAY, default=icon_today)] = str
        data_schema[vol.Required(CONF_SOON, default=days_as_soon)] = int
        data_schema[vol.Required(CONF_ICON_SOON, default=icon_soon)] = str
        data_schema[vol.Required(CONF_DATE_FORMAT, default=date_format)] = str
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(data_schema),
            errors=self._errors,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
            },
        )

    async def async_step_import(self, user_input=None):
        """Import a config entry.
        Special type of import, we're not actually going to store any data.
        Instead, we're going to rely on the values that are in config file.
        """
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> CalendarificOptionsFlowHandler:
        """Options callback for Calendarific."""
        return CalendarificOptionsFlowHandler(config_entry)


class CalendarificOptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options for Calendarific. Does not actually store these into Options but updates the Config instead."""

    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        """Initialize Calendarific options flow."""
        self.config_entry = entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        self._errors = {}
        if user_input is not None:
            _LOGGER.debug(
                "[options_flow async_step_init] user_input initial: " + str(user_input)
            )
            # Bring in other keys not in the Options Flow
            for m in dict(self.config_entry.data).keys():
                user_input.setdefault(m, self.config_entry.data[m])
            # Remove any keys with blank values
            for m in dict(user_input).keys():
                _LOGGER.debug(
                    "[Options Update] "
                    + m
                    + " ["
                    + str(type(user_input.get(m)))
                    + "]: "
                    + str(user_input.get(m))
                )
                if isinstance(user_input.get(m), str) and not user_input.get(m):
                    user_input.pop(m)
            _LOGGER.debug("[Options Update] updated config: " + str(user_input))

            self._data.update(user_input)
            # if self._errors == {}:
            #    if self._data["name"] == "":
            #        self._data["name"] = self._data["holiday"]
            #    return self.async_create_entry(
            #        title=self._data["name"], data=self._data
            #    )
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=self._data, options=self.config_entry.options
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        OPTIONS_SCHEMA = vol.Schema(
            {
                # vol.Required(CONF_HOLIDAY, default=holiday)] = vol.In(holiday_list)
                # DEFAULT_DATE_FORMAT,
                #    DEFAULT_ICON_NORMAL,
                #    DEFAULT_ICON_SOON,
                #    DEFAULT_ICON_TODAY,
                #    DEFAULT_SOON,
                #    DEFAULT_UNIT_OF_MEASUREMENT,
                vol.Optional(CONF_NAME): str,
                vol.Required(
                    CONF_UNIT_OF_MEASUREMENT, default=DEFAULT_UNIT_OF_MEASUREMENT
                ): str,
                vol.Required(CONF_ICON_NORMAL): selector.IconSelector(
                    selector.IconSelectorConfig(placeholder=DEFAULT_ICON_NORMAL)
                ),
                vol.Required(CONF_ICON_TODAY): selector.IconSelector(
                    selector.IconSelectorConfig(placeholder=DEFAULT_ICON_TODAY)
                ),
                vol.Required(CONF_SOON, default=DEFAULT_SOON): int,
                vol.Required(CONF_ICON_SOON): selector.IconSelector(
                    selector.IconSelectorConfig(placeholder=DEFAULT_ICON_SOON)
                ),
                vol.Required(CONF_DATE_FORMAT, default=DEFAULT_DATE_FORMAT): str,
                # vol.Optional(
                #    CONF_MAP_PROVIDER,
                #    default=DEFAULT_MAP_PROVIDER,
                #    description={
                #        "suggested_value": self.config_entry.data[CONF_MAP_PROVIDER]
                #        if CONF_MAP_PROVIDER in self.config_entry.data
                #        else DEFAULT_MAP_PROVIDER
                #    },
                # ): selector.SelectSelector(
                #    selector.SelectSelectorConfig(
                #        options=MAP_PROVIDER_OPTIONS,
                #        multiple=False,
                #        custom_value=False,
                #        mode=selector.SelectSelectorMode.DROPDOWN,
                #    )
                # ),
            }
        )
        _LOGGER.debug("[Options Update] initial config: " + str(self.config_entry.data))

        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS_SCHEMA,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
                "sensor_name": self.config_entry.data[CONF_NAME],
            },
        )
