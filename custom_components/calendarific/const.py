from datetime import timedelta

from homeassistant.const import Platform

""" Constants """

# Base component constants
DOMAIN = "calendarific"
VERSION = "v1.0.2"
ISSUE_URL = "https://github.com/Snuffy2/Calendarific/issues"

ATTRIBUTION = "Data provided by calendarific.com"
SENSOR_PLATFORM = Platform.SENSOR
CALENDAR_PLATFORM = Platform.CALENDAR
SCAN_INTERVAL = timedelta(seconds=30)

# Configuration
CONF_API_KEY = "api_key"
CONF_COUNTRY = "country"
CONF_STATE = "state"
CONF_ENABLED = "enabled"
CONF_ICON_NORMAL = "icon_normal"
CONF_ICON_TODAY = "icon_today"
CONF_ICON_SOON = "icon_soon"
CONF_DATE_FORMAT = "date_format"
CONF_SOON = "days_as_soon"
CONF_HOLIDAY = "holiday"
CONF_UNIT_OF_MEASUREMENT = "unit_of_measurement"
CONF_COORDINATOR = "coordinator"

# Defaults
DEFAULT_ICON_NORMAL = "mdi:calendar-blank"
DEFAULT_ICON_TODAY = "mdi:calendar-star"
DEFAULT_ICON_SOON = "mdi:calendar"
DEFAULT_DATE_FORMAT = "%x"
DEFAULT_SOON = 1
DEFAULT_UNIT_OF_MEASUREMENT = "Days"

# Calendar
CALENDAR_NAME = "Calendarific"

# Attributes
ATTR_DESCRIPTION = "description"
ATTR_DATE = "date"
ATTR_DATETIME = "datetime"
ATTR_ISO = "iso"
ATTR_NAME = "name"
