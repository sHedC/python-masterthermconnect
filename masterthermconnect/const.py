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

# Heating and Cooling circuits, hc0 is the default
# hc0 gets disabled if optional hc1 to hc6 are installed
# Pool and Solar have been added to the heating cooling circuits
#
# PAD
#   entries are related to the Room Thermostats
#   Active is False if not installed, so will disable the section
DEVICE_DATA_HCMAP = {
    "hc0": {
        "enabled": ["fixed", False],
        "name": ["string", []],  # hc0 does not have a name
        "ambient_temp": ["float", "A_211"],
        "ambient_requested": ["float", "A_210"],
        "pad": {
            "active": ["fixed", True],  # No Register in the App
            "current_humidity": ["float", "I_185"],
            "requested_temp": ["float", "A_189"],
            "current_temp": ["float", "A_190"],
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
        "circulation_valve": ["bool", "D_68"],
        "water_temp": ["float", "A_90"],
        "water_requested": ["float", "A_96"],
        "ambient_temp": ["float", "A_216"],
        "ambient_requested": ["float", "A_215"],
        "auto": ["int", "I_269"],
        "pad": {
            "active": ["bool", "D_245"],
            "current_humidity": ["float", "I_219"],
            "requested_temp": ["float", "A_219"],
            "current_temp": ["float", "A_220"],
        },
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
        "circulation_valve": ["bool", "D_69"],
        "water_temp": ["float", "A_91"],
        "water_requested": ["float", "A_97"],
        "ambient_temp": ["float", "A_222"],
        "ambient_requested": ["float", "A_221"],
        "auto": ["int", "I_270"],
        "pad": {
            "active": ["bool", "D_248"],
            "current_humidity": ["float", "I_220"],  # Guess
            "requested_temp": ["float", "A_225"],
            "current_temp": ["float", "A_226"],
        },
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
        "circulation_valve": ["bool", "D_70"],
        "water_temp": ["float", "A_92"],
        "water_requested": ["float", "A_98"],
        "ambient_temp": ["float", "A_228"],
        "ambient_requested": ["float", "A_227"],
        "auto": ["int", "I_271"],
        "pad": {
            "active": ["bool", "D_251"],
            "requested_temp": ["float", "A_231"],
            "current_temp": ["float", "A_232"],
        },
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
        "on": ["bool", "D_50"],
        "cooling": ["bool", "D_224"],
        "circulation_valve": ["bool", "D_71"],
        "water_temp": ["float", "A_93"],
        "water_requested": ["float", "A_99"],
        "ambient_temp": ["float", "A_234"],
        "ambient_requested": ["float", "A_233"],
        "auto": ["int", "I_272"],
        "pad": {
            "active": ["bool", "D_254"],
            "requested_temp": ["float", "A_238"],
            "current_temp": ["float", "A_239"],
        },
    },
    "hc5": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_251", "I_252", "I_253", "I_254", "I_255", "I_256"],
        ],
        "on": ["bool", "D_51"],
        "cooling": ["bool", "D_227"],
        "circulation_valve": ["bool", "D_72"],
        "water_temp": ["float", "A_243"],
        "water_requested": ["float", "A_242"],
        "ambient_temp": ["float", "A_241"],
        "ambient_requested": ["float", "A_240"],
        "auto": ["int", "I_273"],
        "pad": {
            "active": ["bool", "D_257"],
            "requested_temp": ["float", "A_247"],
            "current_temp": ["float", "A_248"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_387"],
            "setpoint_a_requested": ["float", "A_388"],
            "setpoint_b_outside": ["float", "A_389"],
            "setpoint_b_requested": ["float", "A_390"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_379"],
            "setpoint_a_requested": ["float", "A_380"],
            "setpoint_b_outside": ["float", "A_381"],
            "setpoint_b_requested": ["float", "A_382"],
        },
    },
    "hc6": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_261", "I_262", "I_263", "I_264", "I_265", "I_266"],
        ],
        "on": ["bool", "D_52"],
        "cooling": ["bool", "D_231"],
        "circulation_valve": ["bool", "D_73"],
        "water_temp": ["float", "A_252"],
        "water_requested": ["float", "A_251"],
        "ambient_temp": ["float", "A_250"],
        "ambient_requested": ["float", "A_249"],
        "auto": ["int", "I_274"],
        "pad": {
            "active": ["bool", "D_259"],
            "requested_temp": ["float", "A_277"],
            "current_temp": ["float", "A_278"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_401"],
            "setpoint_a_requested": ["float", "A_402"],
            "setpoint_b_outside": ["float", "A_403"],
            "setpoint_b_requested": ["float", "A_404"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_405"],
            "setpoint_a_requested": ["float", "A_406"],
            "setpoint_b_outside": ["float", "A_407"],
            "setpoint_b_requested": ["float", "A_408"],
        },
    },
    "solar": {
        "enabled": ["bool", "D_433"],
        "name": ["fixed", "Solar"],
        "s1_temp": ["float", "A_258"],
        "s2_temp": ["float", "A_259"],
        "s3_temp": ["float", "A_260"],
    },
    "pool": {
        "enabled": ["bool", "D_348"],
        "name": ["fixed", "Pool"],
        "on": ["bool", "D_238"],
        "heating": ["bool", "D_43"],
        "s1_temp": ["float", "A_262"],
        "temp_requested": ["float", "A_15"],
    },
}

# NOTES --------------------------------------------------
# pswitch_data_1: Cooling Curve
# a_outside: A_47
# b_outside: A_48
# a_requested: A_49
# b_requested: A_50
#
# Moved HC0 Heating/ Cooling Curves to main as always
# used moving to main section so they don't get disabled
# --------------------------------------------------------
DEVICE_DATA_MAP = {
    "hp_power_state": ["bool", "D_3"],
    "hp_function": ["int", "I_51"],  # 0: heating, #1: cooling, #2: auto (Write)
    "season": ["fixed", ""],  # summer, auto:summer, winter, auto:winter
    "operating_mode": ["fixed", "heating"],  # heating, cooling, pool, dhw, dpc
    "cooling_mode": ["bool", "D_4"],
    "control_curve_heating": {
        "setpoint_a_outside": ["float", "A_122"],
        "setpoint_a_requested": ["float", "A_120"],
        "setpoint_b_outside": ["float", "A_88"],
        "setpoint_b_requested": ["float", "A_121"],
    },
    "control_curve_cooling": {
        "setpoint_a_outside": ["float", "A_362"],
        "setpoint_a_requested": ["float", "A_363"],
        "setpoint_b_outside": ["float", "A_364"],
        "setpoint_b_requested": ["float", "A_365"],
    },
    "domestic_hot_water": {
        "heating": ["bool", "D_66"],
        "enabled": ["bool", "D_275"],
        "current_temp": ["float", "A_126"],
        "required_temp": ["float", "A_129"],  # Write
        "min_temp": ["float", "A_296"],
        "max_temp": ["float", "A_297"],
    },
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
    "dewp_control": ["bool", "D_196"],
    "hdo_on": ["bool", "D_15"],
    "runtime_info": {
        "compressor_run_time": ["int", "I_11"],
        "compressor_start_counter": ["int", "I_12"],
        "pump_runtime": ["int", "I_13"],
        "aux1_runtime": ["int", "I_100"],
        "aux2_runtime": ["int", "I_101"],
    },
    "season_info": {
        "hp_season": ["bool", "D_24"],  # True is Winter, False is Summer (Write)
        "hp_seasonset": ["int", "I_50"],  # True is Manually Set, False Auto (Write)
        "hp_season_winter": ["float", "A_82"],  # (Write)
        "hp_season_summer": ["float", "A_83"],  # (Write)
    },
    "error_info": {
        "some_error": ["bool", "D_20"],
        "three_errors": ["bool", "D_21"],
        "reset_3e": ["bool", "D_19"],
        "safety_tstat": ["bool", "D_77"],
        "alarm_a": ["int", "I_20"],
        "alarm_b": ["int", "I_21"],
        "alarm_c": ["int", "I_22"],
        "alarm_d": ["int", "I_23"],
        "alarm_e": ["int", "I_24"],
        "alarm_f": ["int", "I_25"],
        "alarm_g": ["int", "I_26"],
        "alarm_h": ["int", "I_27"],
        "alarm_i": ["int", "I_28"],
        "alarm_j": ["int", "I_39"],
        "alarm_k": ["int", "I_40"],
        "alarm_l": ["int", "I_41"],
        "alarm_m": ["int", "I_42"],
    },
    "heating_circuits": DEVICE_DATA_HCMAP,
}
