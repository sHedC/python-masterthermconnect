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
    1: {"id": "hc1", "pad": "pada", "register": "D_278", "default": "0"},
    2: {"id": "hc2", "pad": "padb", "register": "D_436", "default": "0"},
    3: {"id": "hc3", "pad": "padc", "register": "D_298", "default": "0"},
    4: {"id": "hc4", "pad": "padd", "register": "D_307", "default": "0"},
    5: {"id": "hc5", "pad": "pade", "register": "D_316", "default": "0"},
    6: {"id": "hc6", "pad": "padf", "register": "D_326", "default": "0"},
    7: {
        "id": "solar",
        "pad": "",
        "register": "D_433",
        "default": "Solar",
    },  # This is not correct
    8: {
        "id": "pool",
        "pad": "",
        "register": "D_348",
        "default": "Pool",
    },  # This is not correct
}

DEVICE_INFO_MAP = {
    "name": "givenname",
    "surname": "surname",
    "country": "localization",
    "language": "lang",
    "hp_type": "type",
    "controller": "regulation",
    "exp": "exp",
    "output": "output",
    "reservation": "reservation",
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


DEVICE_DATA_HCMAP = {
    "hc0": {
        "enabled": ["fixed", False],
        "name": ["string", []],  # hc0 does not have a name
        "on": ["bool", ""],
        "ambient_temp": ["float", "A_211"],
        "ambient_requested": ["float", "A_210"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_35"],
            "setpoint_a_requested": ["float", "A_37"],
            "setpoint_b_outside": ["float", "A_36"],
            "setpoint_b_requested": ["float", "A_38"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_47"],
            "setpoint_a_requested": ["float", "A_49"],
            "setpoint_b_outside": ["float", "A_48"],
            "setpoint_b_requested": ["float", "A_50"],
        },
    },
    "hc1": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_211", "I_212", "I_213", "I_214", "I_215", "I_216"],
        ],
        "on": ["bool", "D_212"],
        "cooling": ["bool", "D_213"],
        "water_temp": ["float", "A_90"],
        "water_requested": ["float", "A_96"],
        "ambient_temp": ["float", "A_216"],
        "ambient_requested": ["float", "A_215"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_101"],
            "setpoint_a_requested": ["float", "A_106"],
            "setpoint_b_outside": ["float", "A_102"],
            "setpoint_b_requested": ["float", "A_107"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_314"],
            "setpoint_a_requested": ["float", "A_315"],
            "setpoint_b_outside": ["float", "A_316"],
            "setpoint_b_requested": ["float", "A_317"],
        },
    },
    "hc2": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_221", "I_222", "I_223", "I_224", "I_225", "I_226"],
        ],
        "on": ["bool", "D_216"],
        "cooling": ["bool", "D_217"],
        "water_temp": ["float", "A_91"],
        "water_requested": ["float", "A_97"],
        "ambient_temp": ["float", "A_222"],
        "ambient_requested": ["float", "A_221"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_108"],
            "setpoint_a_requested": ["float", "A_84"],
            "setpoint_b_outside": ["float", "A_109"],
            "setpoint_b_requested": ["float", "A_85"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_330"],
            "setpoint_a_requested": ["float", "A_331"],
            "setpoint_b_outside": ["float", "A_332"],
            "setpoint_b_requested": ["float", "A_333"],
        },
    },
    "hc3": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_231", "I_232", "I_233", "I_234", "I_235", "I_236"],
        ],
        "on": ["bool", "D_220"],
        "cooling": ["bool", "D_221"],
        "water_temp": ["float", "A_92"],
        "water_requested": ["float", "A_98"],
        "ambient_temp": ["float", "A_228"],
        "ambient_requested": ["float", "A_227"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_108"],
            "setpoint_a_requested": ["float", "A_84"],
            "setpoint_b_outside": ["float", "A_109"],
            "setpoint_b_requested": ["float", "A_85"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_346"],
            "setpoint_a_requested": ["float", "A_347"],
            "setpoint_b_outside": ["float", "A_348"],
            "setpoint_b_requested": ["float", "A_349"],
        },
    },
    "hc4": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_241", "I_242", "I_243", "I_244", "I_245", "I_246"],
        ],
        "on": ["bool", "D_220"],
        "cooling": ["bool", "D_221"],
        "water_temp": ["float", "A_92"],
        "water_requested": ["float", "A_98"],
        "ambient_temp": ["float", "A_228"],
        "ambient_requested": ["float", "A_227"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_108"],
            "setpoint_a_requested": ["float", "A_84"],
            "setpoint_b_outside": ["float", "A_109"],
            "setpoint_b_requested": ["float", "A_85"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_346"],
            "setpoint_a_requested": ["float", "A_347"],
            "setpoint_b_outside": ["float", "A_348"],
            "setpoint_b_requested": ["float", "A_349"],
        },
    },
    "hc5": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_251", "I_252", "I_253", "I_254", "I_255", "I_256"],
        ],
        "on": ["bool", "D_220"],
        "cooling": ["bool", "D_221"],
        "water_temp": ["float", "A_92"],
        "water_requested": ["float", "A_98"],
        "ambient_temp": ["float", "A_228"],
        "ambient_requested": ["float", "A_227"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_108"],
            "setpoint_a_requested": ["float", "A_84"],
            "setpoint_b_outside": ["float", "A_109"],
            "setpoint_b_requested": ["float", "A_85"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_346"],
            "setpoint_a_requested": ["float", "A_347"],
            "setpoint_b_outside": ["float", "A_348"],
            "setpoint_b_requested": ["float", "A_349"],
        },
    },
    "hc6": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_261", "I_262", "I_263", "I_264", "I_265", "I_266"],
        ],
        "on": ["bool", "D_220"],
        "cooling": ["bool", "D_221"],
        "water_temp": ["float", "A_92"],
        "water_requested": ["float", "A_98"],
        "ambient_temp": ["float", "A_228"],
        "ambient_requested": ["float", "A_227"],
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_108"],
            "setpoint_a_requested": ["float", "A_84"],
            "setpoint_b_outside": ["float", "A_109"],
            "setpoint_b_requested": ["float", "A_85"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_346"],
            "setpoint_a_requested": ["float", "A_347"],
            "setpoint_b_outside": ["float", "A_348"],
            "setpoint_b_requested": ["float", "A_349"],
        },
    },
}

# NOTES --------------------------------------------------
# pswitch_data_1: Cooling Curve
# a_outside: A_47
# b_outside: A_48
# a_requested: A_49
# b_requested: A_50
# --------------------------------------------------------
DEVICE_DATA_MAP = {
    "hp_power_state": ["bool", "D_3"],
    "hp_function": ["int", "I_51"],  # 0: heating, #1: cooling, #3: auto
    "cooling_mode": ["bool", "D_4"],
    "shw_function": ["bool", "D_66"],  # sanitary hot water function available on device
    "shw_enabled": ["bool", "D_275"],  # sanitary hot water heating currently active
    "shw_temp": ["float", "A_126"],
    "shw_required_temp": ["float", "A_129"],
    "compressor_running": ["bool", "D_5"],
    "compressor2_running": ["bool", "D_32"],
    "circulation_pump_running": ["bool", "D_10"],
    "fan_running": ["bool", "D_8"],
    "defrost_mode": ["bool", "D_11"],
    "aux_heater_1": ["bool", "D_6"],
    "aux_heater_2": ["bool", "D_7"],
    "outside_temp": ["float", "A_3"],
    "requested_temp": ["float", "A_5"],
    "actual_temp": ["float", "A_1"],
    "compressor_run_time": ["int", "I_11"],
    "compressor_start_counter": ["int", "I_12"],
    "pump_runtime": ["int", "I_13"],
    "heating_circuits": DEVICE_DATA_HCMAP,
}
