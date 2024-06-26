# Adapted from  bruxy70/Garbage-Collection
# https://github.com/bruxy70/Garbage-Collection/blob/master/custom_components/garbage_collection/calendar.py

"""Calendarific calendar."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import Throttle

from .const import (
    ATTR_DESCRIPTION,
    CALENDAR_NAME,
    CALENDAR_PLATFORM,
    DOMAIN,
    SENSOR_PLATFORM,
    THROTTLE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
) -> None:
    """Add calendar entities to HA, of there are calendar instances."""
    # Only single instance allowed
    if not CalendarificCalendar.instances:
        async_add_entities([CalendarificCalendar()], True)


class CalendarificCalendar(CalendarEntity):
    """The Calendarific collection calendar class."""

    instances = False

    def __init__(self) -> None:
        """Create empty calendar."""
        self._cal_data: dict = {}
        self._attr_name = CALENDAR_NAME
        CalendarificCalendar.instances = True

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self.hass.data[DOMAIN][CALENDAR_PLATFORM].event

    @property
    def name(self) -> str | None:
        """Return the name of the entity."""
        return self._attr_name

    async def async_update(self) -> None:
        """Update all calendars."""
        await self.hass.data[DOMAIN][CALENDAR_PLATFORM].async_update()

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        return await self.hass.data[DOMAIN][CALENDAR_PLATFORM].async_get_events(
            hass, start_date, end_date
        )

    @property
    def extra_state_attributes(self) -> dict | None:
        """Return the device state attributes."""
        if self.hass.data[DOMAIN][CALENDAR_PLATFORM].event is None:
            # No tasks, we don't need to show anything.
            return None
        return {}


class EntitiesCalendarData:
    """Class used by the Entities Calendar class to hold all entity events."""

    __slots__ = "_hass", "event", "entities", "_throttle"

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize an Entities Calendar Data."""
        self._hass = hass
        self.event: CalendarEvent | None = None
        self.entities: list[str] = []

    def add_entity(self, entity_id: str) -> None:
        """Append entity ID to the calendar."""
        if entity_id not in self.entities:
            self.entities.append(entity_id)

    def remove_entity(self, entity_id: str) -> None:
        """Remove entity ID from the calendar."""
        if entity_id in self.entities:
            self.entities.remove(entity_id)

    async def async_get_events(
        self, hass: HomeAssistant, start_datetime: datetime, end_datetime: datetime
    ) -> list[CalendarEvent]:
        """Get all events in a specific time frame."""
        events: list[CalendarEvent] = []
        _LOGGER.debug("[Get Events]")
        if SENSOR_PLATFORM not in hass.data[DOMAIN]:
            return events
        start_date = start_datetime.date()
        end_date = end_datetime.date()
        for ent in self.entities:
            _LOGGER.debug(f"[Get Events] Entity Name: {ent}")
            if (
                ent
                not in hass.data[DOMAIN][SENSOR_PLATFORM]
                # or hass.data[DOMAIN][SENSOR_PLATFORM][ent].hidden
            ):
                continue
            entity = self._hass.data[DOMAIN][SENSOR_PLATFORM][ent]
            _LOGGER.debug(f"[Get Events] Entity: {entity}")
            if (
                entity
                and entity.name
                and entity._date
                and start_date <= entity._date <= end_date
            ):
                event = CalendarEvent(
                    summary=entity.name,
                    start=entity._date,
                    end=entity._date,
                    description=entity.extra_state_attributes[ATTR_DESCRIPTION]
                    if ATTR_DESCRIPTION in entity.extra_state_attributes
                    else None,
                )
                events.append(event)
        return events

    @Throttle(THROTTLE_INTERVAL)
    @callback
    async def async_update(self) -> None:
        """Get the latest data."""
        for ent in self.entities:
            _LOGGER.debug(f"[Calendar Update] Entity ID: {ent}")
            entity = self._hass.data[DOMAIN][SENSOR_PLATFORM][ent]
            _LOGGER.debug(f"[Calendar Update] Holiday Name: {entity.name}")
            _LOGGER.debug(f"[Calendar Update] Holiday Date: {entity._date}")
            if entity and entity.name and entity._date and entity._date != "-":
                self.event = CalendarEvent(
                    summary=entity.name,
                    start=entity._date,
                    end=entity._date,
                    description=entity.extra_state_attributes[ATTR_DESCRIPTION]
                    if ATTR_DESCRIPTION in entity.extra_state_attributes
                    else None,
                )
