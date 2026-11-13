DOMAIN = "pf_lookup"
NAME = "DHL Packstation"

CONF_PERSONS = "persons"
CONF_RADIUS = "radius"
CONF_RESULTS = "results"

DEFAULT_RADIUS = 5000
DEFAULT_RESULTS = 5

SERVICE_SEARCH = "search"
SERVICE_STATUS = "status"
SERVICE_PERSONS = "persons"

ATTR_PERSON = "person"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"
ATTR_KEY = "key"

BASE_URL = "https://www.dhl.de/int-postfinder/webservice/rest/v1"
PATH_NEARBY = "/nearbySearch"
PATH_LOCATION = "/locationByPrimaryKeyPF/{key}"

REQUEST_TIMEOUT = 25

DATA_API = "api"
DATA_CONFIG = "config"
DATA_STORE = "store"
DATA_FRONTEND = "frontend"

FRONTEND_URL_PATH = "/pf_lookup"
CARD_FILENAME = "pf-lookup-card.js"

RESULT_SLOTS = 5
RESULT_TTL = 300
ATTR_RESULT_MARKER = "pf_result"

LOCATION_TYPE_PACKSTATION = "PACKSTATION"
