""" Calendarific Sensor """
import logging
from datetime import date

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION, CONF_NAME, UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .calendar import EntitiesCalendarData
from .const import (
    ATTR_DATE,
    ATTR_DESCRIPTION,
    ATTR_NAME,
    ATTRIBUTION,
    CALENDAR_NAME,
    CALENDAR_PLATFORM,
    CONF_COORDINATOR,
    CONF_DATE_FORMAT,
    CONF_HOLIDAY,
    CONF_ICON_NORMAL,
    CONF_ICON_SOON,
    CONF_ICON_TODAY,
    CONF_SOON,
    DOMAIN,
    SENSOR_PLATFORM,
)
from .coordinator import CalendarificCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Setup sensor entry."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][CONF_COORDINATOR]
    config = hass.data.get(DOMAIN).get(config_entry.entry_id)
    async_add_entities(Calendarific(config, coordinator))


class Calendarific(CoordinatorEntity[CalendarificCoordinator], SensorEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, config, coordinator: CalendarificCoordinator):
        """Initialize the sensor."""

        super().__init__(coordinator)

        # self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = UnitOfTime.DAYS
        self._attr_suggested_unit_of_measurement = UnitOfTime.DAYS
        self._config = config
        self._attr_unique_id = config.get("unique_id", None)
        self._holiday = config.get(CONF_HOLIDAY)
        self._attr_name = config.get(CONF_NAME)
        if not self._attr_name or self._attr_name == "":
            self._attr_name = self._holiday
        self._icon_normal = config.get(CONF_ICON_NORMAL)
        self._icon_today = config.get(CONF_ICON_TODAY)
        self._icon_soon = config.get(CONF_ICON_SOON)
        self._soon = config.get(CONF_SOON)
        self._date_format = config.get(CONF_DATE_FORMAT)
        self._attr_icon = self._icon_normal
        self._coordinator = coordinator
        self._description = self._coordinator.get_description(self._holiday)
        self._date = self._coordinator.get_date(self._holiday)
        if not self._date or self._date == "-":
            self._attr_date = self._date
        else:
            self._attr_date = self._date.strftime(self._date_format)
        self._attr_native_value = None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        # _LOGGER.debug(f"ESA {self._attr_name} Attr Date: {self._attr_date}")
        return {
            ATTR_DATE: self._attr_date,
            ATTR_DESCRIPTION: self._description,
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = self.coordinator.data[self.idx]["state"]
        self.async_write_ha_state()

    async def async_added_to_hass(self):
        """Once the entity is added we should update to get the initial data loaded. Then add it to the Calendar."""
        await super().async_added_to_hass()
        self.async_schedule_update_ha_state(True)
        if DOMAIN not in self.hass.data:
            self.hass.data[DOMAIN] = {}
        if SENSOR_PLATFORM not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][SENSOR_PLATFORM] = {}
        self.hass.data[DOMAIN][SENSOR_PLATFORM][self.entity_id] = self

        # if not self.hidden:
        if CALENDAR_PLATFORM not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][CALENDAR_PLATFORM] = EntitiesCalendarData(self.hass)
            _LOGGER.info("Creating Calendarific calendar")
            self.hass.async_create_task(
                async_load_platform(
                    self.hass,
                    CALENDAR_PLATFORM,
                    DOMAIN,
                    {ATTR_NAME: CALENDAR_NAME},
                    {ATTR_NAME: CALENDAR_NAME},
                )
            )

        # else:
        # _LOGGER.info("Calendarific calendar already exists")

        self.hass.data[DOMAIN][CALENDAR_PLATFORM].add_entity(self.entity_id)

    async def async_will_remove_from_hass(self):
        """When sensor is removed from hassio and there are no other sensors in the Calendarific calendar, remove it."""
        await super().async_will_remove_from_hass()
        _LOGGER.debug(f"Removing: {self._attr_name}")
        del self.hass.data[DOMAIN][SENSOR_PLATFORM][self.entity_id]
        self.hass.data[DOMAIN][CALENDAR_PLATFORM].remove_entity(self.entity_id)
        # _LOGGER.debug(f"Remaining Calendar Entries: {self.hass.data[DOMAIN][CALENDAR_PLATFORM]}")

    async def async_update(self):
        await self.hass.async_add_executor_job(self._coordinator.update)
        _LOGGER.debug(f"Update: {self._attr_name}")
        self._description = self._coordinator.get_description(self._holiday)
        self._date = self._coordinator.get_date(self._holiday)
        # _LOGGER.debug(f"[Update] Date: {self._date}")
        # _LOGGER.debug(f"[Update] Date Type: {type(self._date)}")
        if not self._date or self._date == "-":
            self._attr_native_value = None
            self._attr_date = self._date
            return
        self._attr_date = self._date.strftime(self._date_format)
        # _LOGGER.debug(f"[Update] Date Format: {self._date_format}")
        # _LOGGER.debug(f"[Update] Attr Date: {self._attr_date}")
        today = date.today()
        daysRemaining = 0
        if today < self._date:
            daysRemaining = (self._date - today).days
        elif today == self._date:
            daysRemaining = 0

        if daysRemaining == 0:
            self._attr_icon = self._icon_today
        elif daysRemaining <= self._soon:
            self._attr_icon = self._icon_soon
        else:
            self._attr_icon = self._icon_normal
        self._attr_native_value = daysRemaining
