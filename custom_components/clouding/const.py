"""Constants for the Clouding.io integration."""

from datetime import timedelta

DOMAIN = "clouding"

CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_NAME = "Clouding.io"
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)

ATTRIBUTION = "Data provided by Clouding API"

MANUFACTURER_NAME = "Clouding.io"
PORTAL_URL = "https://portal.clouding.io"

SERVICE_ARCHIVE_SERVER = "archive_server"
SERVICE_UNARCHIVE_SERVER = "unarchive_server"

SERVICE_HARD_REBOOT_SERVER = "hard_reboot_server"
SERVICE_REBOOT_SERVER = "reboot_server"

SERVICE_START_SERVER = "start_server"
SERVICE_STOP_SERVER = "stop_server"
