"""Constants used by the module."""
APP_CLIENTINFO = "os=android&osversion=7.0&ver=8&info=Google%2CAndroid"
APP_OS = "android"
APP_VERSION = "1"

COOKIE_TOKEN = "PHPSESSID"
HEADER_TOKEN_EXPIRES = "Date"
DATE_FORMAT = "%a, %d-%b-%Y %H:%M:%S %Z"
SUPPORTED_ROLES = ["400"]

URL_BASE = "https://mastertherm.vip-it.cz"
URL_LOGIN = "/plugins/mastertherm_login/client_login.php"
URL_PUMPINFO = "/plugins/get_pumpinfo/get_pumpinfo.php"
URL_PUMPDATA = "/mt/PassiveVizualizationServlet"

DEVICEINFO_MAP = {
    "type": "type",
    "lang": "lang",
    "givenname": "givenname",
    "surname": "surname",
    "output": "output",
    "country": "localization",
    "longitude": "password9",
    "latitude": "password10",
    "city": "city",
    "notes": "notes",
    "regulation": "regulation",
}