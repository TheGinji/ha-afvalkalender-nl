"""Constants for the TrashAPI integration."""

DOMAIN = "trashapi"

CONF_LOCATION = "location"
CONF_ZIP_CODE = "zip_code"
CONF_HOUSE_NUMBER = "house_number"
CONF_SHOW_WHOLE_YEAR = "show_whole_year"
CONF_GET_CLEANPROFS_DATA = "get_cleanprofs_data"
CONF_IGNORE_CACHE = "ignore_cache"
CONF_SCAN_INTERVAL_HOURS = "scan_interval_hours"

# Address = identity of the entry (changed via "Herconfigureren"),
# settings = behaviour (changed via "Configureren")
ADDRESS_KEYS = (CONF_LOCATION, CONF_ZIP_CODE, CONF_HOUSE_NUMBER)
SETTING_KEYS = (
    CONF_SHOW_WHOLE_YEAR,
    CONF_GET_CLEANPROFS_DATA,
    CONF_IGNORE_CACHE,
    CONF_SCAN_INTERVAL_HOURS,
)

DEFAULT_SHOW_WHOLE_YEAR = True
DEFAULT_GET_CLEANPROFS_DATA = True
DEFAULT_IGNORE_CACHE = False
DEFAULT_SCAN_INTERVAL_HOURS = 6

API_URL = "https://trashapi.azurewebsites.net/Trash"
API_DOCS_URL = "https://trashapi.azurewebsites.net/index.html"

ICONS = {
    "restafval": "mdi:trash-can",
    "gft": "mdi:leaf",
    "papier": "mdi:newspaper-variant-multiple",
    "pmd": "mdi:recycle",
    "plastic": "mdi:recycle",
    "grofvuil": "mdi:sofa",
    "textiel": "mdi:tshirt-crew",
    "kerstbomen": "mdi:pine-tree",
}
DEFAULT_ICON = "mdi:delete-empty"
