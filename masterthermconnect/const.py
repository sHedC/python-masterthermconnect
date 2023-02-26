"""Constants used by the module."""
DATE_FORMAT = "%a, %d-%b-%Y %H:%M:%S %Z"
SUPPORTED_ROLES = ["400"]
SUPPORTED_API_VERSIONS = ["v1", "v2"]

# Old Mastertherm Devices Pre 2022
# This mostly uses POST methods
APP_CLIENTINFO = "os=android&osversion=7.0&ver=8&info=Google%2CAndroid"
URL_BASE = "https://mastertherm.vip-it.cz"
URL_LOGIN = "/plugins/mastertherm_login/client_login.php"
URL_PUMPINFO = "/plugins/get_pumpinfo/get_pumpinfo.php"
URL_PUMPDATA = "/mt/PassiveVizualizationServlet"
URL_POSTUPDATE = "/mt/ActiveVizualizationServlet"

# New Mastertherm Devices (Mastertherm Touch) Post 2022
# This uses GET to retrieve data and POST to submit, e.g. Login is Post, Update is Post
APP_CLIENTINFO_NEW = "client_id=mobile-android"
URL_BASE_NEW = "https://mastertherm.online"
URL_LOGIN_NEW = "/auth/realms/neobox/protocol/openid-connect/token"
URL_PUMPINFO_NEW = "/api/v1/hp_info"
URL_PUMPDATA_NEW = "/api/v1/hp_data"
URL_MODULES_NEW = "/api/v1/modules"
URL_POSTUPDATE_NEW = "/api/v1/hp_data"

# Used to setup the hc name from the registers,
# for some reason they don't like the letter Q
CHAR_MAP = [
    "-",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
]

# HC0 is the main heating cooling circuit which is enabled if HC1 to HC6 are not used.
# HC1 to HC6 are optional heating and cooling circuits that may be installed
# Pool and Solar are spencial circuit
HC_MAP = {
    0: {"id": "hc0", "pad": "padz", "register": "D_182", "default": "Home"},
    1: {"id": "hc1", "pad": "pada", "register": "D_278", "default": ""},
    2: {"id": "hc2", "pad": "padb", "register": "D_436", "default": ""},
    3: {"id": "hc3", "pad": "padc", "register": "D_298", "default": ""},
    4: {"id": "hc4", "pad": "padd", "register": "D_307", "default": ""},
    5: {"id": "hc5", "pad": "pade", "register": "D_316", "default": ""},
    6: {"id": "hc6", "pad": "padf", "register": "D_326", "default": ""},
}

DEVICE_INFO_MAP = {
    "name": "givenname",
    "surname": "surname",
    "country": "localization",
    "language": "lang",
    "hp_type": "type",
    "controller": "regulation",
    "serial_number": "serialnumber",
    "exp": "exp",
    "output": "output",
    "cooling": "reversation",  # 0 - Cooling Disabled, 1 - Cooling Enabled.
    "place": "city",
    "latitude": "password9",
    "longitude": "password10",
    "notes": "notes",
    "pada": "pada",
    "padb": "padb",
    "padc": "padc",
    "padd": "padd",
    "pade": "pade",
    "padf": "padf",
    "padz": "padz",
}
