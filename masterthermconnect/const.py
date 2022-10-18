"""Constants used by the module."""
APP_CLIENTINFO = "os=android&osversion=7.0&ver=8&info=Google%2CAndroid"
APP_OS = "android"
APP_VERSION = "1"

COOKIE_TOKEN = "PHPSESSID"
DATE_FORMAT = "%a, %d-%b-%Y %H:%M:%S %Z"
SUPPORTED_ROLES = ["400"]

URL_BASE = "https://mastertherm.vip-it.cz"
URL_LOGIN = "/plugins/mastertherm_login/client_login.php"
URL_PUMPINFO = "/plugins/get_pumpinfo/get_pumpinfo.php"
URL_PUMPDATA = "/mt/PassiveVizualizationServlet"

# Used to setup the pad name, for some reason they don't like the letter Q
CHAR_MAP = ["-","A","B","C","D","E","F","G",
    "H","I","J","K","L","M","N","O","P","R",
    "S","T","U","V","W","X","Y","Z"]

DEVICE_SWITCH_MAP = {
    0: "D_348",
    1: "D_433",
    2: "D_326",
    3: "D_316",
    4: "D_307",
    5: "D_298",
    6: "D_436",
    7: "D_278",
    8: "D_182",
}

PAD_MAP = {
    0: "heating",
    1: "cooling",
    2: "padf",
    3: "pade",
    4: "padd",
    5: "padc",
    6: "padb",
    7: "pada",
    8: "padz",
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

DEVICE_DATA_PADMAP = {
    "pada": {
        "enabled": ["fixed",False],
        "name": ["string",["I_211", "I_212", "I_213", "I_214", "I_215", "I_216"]],
        "on": ["bool","D_212"],
        "pump_running": ["bool",""],
        "water_temp": ["float","A_126"],
        "water_requested": ["decimal",""],
        "ambient_temp": ["float",""],
        "ambient_requested": ["float",""],
        "control_curve": {
            "setpoint_a_outside": ["float","A_101"],
            "setpoint_a_requested": ["float","A_106"],
            "setpoint_b_outside": ["float","A_102"],
            "setpoint_b_requested": ["float","A_107"],
        },
    },
    "padb": {
        "enabled": ["fixed",False],
        "name": ["string",["I_221", "I_222", "I_223", "I_224", "I_225", "I_226"]],
        "on": ["bool","D_216"],
        "pump_running": ["bool",""],
        "water_temp": ["float","A_91"],
        "water_requested": ["decimal",""],
        "ambient_temp": ["float",""],
        "ambient_requested": ["float",""],
        "control_curve": {
            "setpoint_a_outside": ["float","A_108"],
            "setpoint_a_requested": ["float","A_84"],
            "setpoint_b_outside": ["float","A_109"],
            "setpoint_b_requested": ["float","A_85"],
        },
    },
    "padc": {
        "enabled": ["fixed",False],
        "name": ["string",["I_231", "I_232", "I_233", "I_234", "I_235", "I_236"]],
    },
    "padd": {
        "enabled": ["fixed",False],
        "name": ["string",["I_241", "I_242", "I_243", "I_244", "I_245", "I_246"]],
    },
    "pade": {
        "enabled": ["fixed",False],
        "name": ["string",["I_251", "I_252", "I_253", "I_254", "I_255", "I_256"]],
    },
    "padf": {
        "enabled": ["fixed",False],
        "name": ["string",["I_261", "I_262", "I_263", "I_264", "I_265", "I_266"]],
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
    "on": ["bool","D_3"],
    "heating": ["bool",""],
    "compressor_running": ["bool",""],
    "circulation_pump_running": ["bool",""],
    "defrost_mode": ["bool",""],
    "outside_temp": ["float","A_3"],
    "requested_temp": ["float","A_1"],
    "actual_temp": ["float","A_90"],
    "compressor_run_time": ["int","I_11"],
    "compressor_start_counter": ["int","I_12"],
    "pump_runtime": ["int","I_13"],
    "heating_curve": {
        "setpoint_a_outside": ["float","A_35"],
        "setpoint_a_requested": ["float","A_37"],
        "setpoint_b_outside": ["float","A_36"],
        "setpoint_b_requested": ["float","A_38"],
    },
    "pads": DEVICE_DATA_PADMAP,
}
