""" config flow """
from __future__ import annotations

import logging
import uuid
from datetime import date

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import holiday_dict
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

_LOGGER = logging.getLogger(__name__)
TODAY = date.today()
COMPONENT_CONFIG_URL = (
    "https://github.com/snuffy2/Calendarific#sensor-configuration-parameters"
)
SOON_MIN = 0
SOON_MAX = 364
DATE_FORMAT_OPTIONS = [
    selector.SelectOptionDict(
        value="%x", label=f"{TODAY.strftime('%x')} (%x) Locale’s appropriate date"
    ),
    selector.SelectOptionDict(
        value="%B %-d, %Y", label=f"{TODAY.strftime('%B %-d, %Y')} (%B %-d, %Y)"
    ),
    selector.SelectOptionDict(
        value="%A, %B %-d, %Y",
        label=f"{TODAY.strftime('%A, %B %-d, %Y')} (%A, %B %-d, %Y)",
    ),
    selector.SelectOptionDict(
        value="%Y-%m-%d",
        label=f"{TODAY.strftime('%Y-%m-%d')} (%Y-%m-%d) WARNING: May show a day off",
    ),
]

HOLIDAY_LIST = []
for key, value in holiday_dict.items():
    HOLIDAY_LIST.append(
        selector.SelectOptionDict(
            value=key,
            label=value,
        )
    )


@callback
def calendarific_entries(hass: HomeAssistant):
    return set((entry.data) for entry in hass.config_entries.async_entries(DOMAIN))


class CalendarificConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    def __init__(self) -> None:
        self._errors = {}
        # self._data = {}
        # self.unique_id = str(uuid.uuid4())

    async def async_step_user(self, user_input=None) -> FlowResult:
        if holiday_dict == {}:
            return self.async_abort(reason="no_holidays_found")
        self._errors = {}
        if user_input is not None:
            # self._data.update(user_input)
            # if self._errors == {}:
            user_input.update({CONF_UNIQUE_ID: str(uuid.uuid4())})
            if not (CONF_NAME in user_input and user_input.get(CONF_NAME)):
                user_input.update({CONF_NAME: user_input.get(CONF_HOLIDAY)})
            return self.async_create_entry(
                title=user_input.get(CONF_NAME), data=user_input
            )
        DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_HOLIDAY): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=HOLIDAY_LIST,
                        multiple=False,
                        custom_value=False,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(
                    CONF_NAME,
                ): str,
                vol.Required(
                    CONF_UNIT_OF_MEASUREMENT,
                    default=DEFAULT_UNIT_OF_MEASUREMENT,
                ): str,
                vol.Required(
                    CONF_ICON_NORMAL,
                    default=DEFAULT_ICON_NORMAL,
                ): selector.IconSelector(selector.IconSelectorConfig()),
                vol.Required(
                    CONF_ICON_TODAY,
                    default=DEFAULT_ICON_TODAY,
                ): selector.IconSelector(selector.IconSelectorConfig()),
                vol.Required(
                    CONF_SOON,
                    default=DEFAULT_SOON,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=SOON_MIN,
                        max=SOON_MAX,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_ICON_SOON,
                    default=DEFAULT_ICON_SOON,
                ): selector.IconSelector(selector.IconSelectorConfig()),
                vol.Required(
                    CONF_DATE_FORMAT,
                    default=DEFAULT_DATE_FORMAT,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=DATE_FORMAT_OPTIONS,
                        multiple=False,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
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
        self._errors = {}
        # self._data = {}
        self.config_entry = entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        self._errors = {}
        if user_input is not None:
            _LOGGER.debug(
                "[options_flow async_step_init] initial user_input: " + str(user_input)
            )
            # Bring in other keys not in the Options Flow
            for m in dict(self.config_entry.data).keys():
                user_input.setdefault(m, self.config_entry.data[m])
            # Remove any keys with blank values
            for m in dict(user_input).keys():
                if isinstance(user_input.get(m), str) and not user_input.get(m):
                    user_input.pop(m)
            _LOGGER.debug("[Options Update] updated user_input: " + str(user_input))

            self.hass.config_entries.async_update_entry(
                self.config_entry, data=user_input, options=self.config_entry.options
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        OPTIONS_SCHEMA = vol.Schema(
            {
                vol.Required(
                    CONF_UNIT_OF_MEASUREMENT,
                    default=self.config_entry.data[CONF_UNIT_OF_MEASUREMENT]
                    if CONF_UNIT_OF_MEASUREMENT in self.config_entry.data
                    else DEFAULT_UNIT_OF_MEASUREMENT,
                ): str,
                vol.Required(
                    CONF_ICON_NORMAL,
                    default=self.config_entry.data[CONF_ICON_NORMAL]
                    if CONF_ICON_NORMAL in self.config_entry.data
                    else DEFAULT_ICON_NORMAL,
                ): selector.IconSelector(selector.IconSelectorConfig()),
                vol.Required(
                    CONF_ICON_TODAY,
                    default=self.config_entry.data[CONF_ICON_TODAY]
                    if CONF_ICON_TODAY in self.config_entry.data
                    else DEFAULT_ICON_TODAY,
                ): selector.IconSelector(selector.IconSelectorConfig()),
                vol.Required(
                    CONF_SOON,
                    default=self.config_entry.data[CONF_SOON]
                    if CONF_SOON in self.config_entry.data
                    else DEFAULT_SOON,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=SOON_MIN,
                        max=SOON_MAX,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_ICON_SOON,
                    default=self.config_entry.data[CONF_ICON_SOON]
                    if CONF_ICON_SOON in self.config_entry.data
                    else DEFAULT_ICON_SOON,
                ): selector.IconSelector(selector.IconSelectorConfig()),
                vol.Required(
                    CONF_DATE_FORMAT,
                    default=self.config_entry.data[CONF_DATE_FORMAT]
                    if CONF_DATE_FORMAT in self.config_entry.data
                    else DEFAULT_DATE_FORMAT,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=DATE_FORMAT_OPTIONS,
                        multiple=False,
                        custom_value=True,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        _LOGGER.debug(
            "[Options Update] initial self.config_entry.data: "
            + str(self.config_entry.data)
        )

        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS_SCHEMA,
            errors=self._errors,
            description_placeholders={
                "component_config_url": COMPONENT_CONFIG_URL,
                "sensor_name": self.config_entry.data[CONF_NAME],
            },
        )
