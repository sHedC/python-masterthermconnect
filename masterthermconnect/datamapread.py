"""Mapping files for reading from the registries."""
from .special import Special

# Heating and Cooling circuits, hc0 is the default
# hc0 gets disabled if optional hc1 to hc6 are installed
# Pool and Solar have been added to the heating cooling circuits
#
# PAD
#   entries are related to the Room Thermostats
#   Active is False if not installed, so will disable the section
DEVICE_READ_HCMAP = {
    "hc0": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [Special(str, Special.NAMEARRAY), []],  # hc0 does not have a name
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_242"], [float, "A_191"], [float, "A_210"]],
            ],
        ],
        "ambient_temp": [float, "A_211"],
        "pad": {
            "enabled": [
                Special(bool, Special.FORMULA),
                ["not {0}", [[bool, "D_242"]]],
            ],  # Seems to be enabled if this is false.
            "current_humidity": [float, "I_185"],
        },
    },
    "hc1": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [
            Special(str, Special.NAMEARRAY),
            ["I_211", "I_212", "I_213", "I_214", "I_215", "I_216"],
        ],
        "on": [bool, "D_212"],
        "cooling": [bool, "D_213"],
        "circulation_valve": [bool, "D_68"],
        "water_temp": [float, "A_90"],
        "water_requested": [float, "A_96"],
        "auto": [int, "I_269"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_245"], [float, "A_219"], [float, "A_215"]],
            ],
        ],
        "ambient_temp": [float, "A_216"],
        "pad": {
            "enabled": [bool, "D_245"],
            "state": [int, "I_15"],  # 0 - Permanently Off, 1 - Scheduled Off, 2 - On
            "current_humidity": [float, "I_219"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": [float, "A_101"],
            "setpoint_a_requested": [float, "A_106"],
            "setpoint_b_outside": [float, "A_102"],
            "setpoint_b_requested": [float, "A_107"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": [float, "A_314"],
            "setpoint_a_requested": [float, "A_315"],
            "setpoint_b_outside": [float, "A_316"],
            "setpoint_b_requested": [float, "A_317"],
        },
    },
    "hc2": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [
            Special(str, Special.NAMEARRAY),
            ["I_221", "I_222", "I_223", "I_224", "I_225", "I_226"],
        ],
        "on": [bool, "D_216"],
        "cooling": [bool, "D_217"],
        "circulation_valve": [bool, "D_69"],
        "water_temp": [float, "A_91"],
        "water_requested": [float, "A_97"],
        "auto": [int, "I_270"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_248"], [float, "A_225"], [float, "A_221"]],
            ],
        ],
        "ambient_temp": [float, "A_222"],
        "pad": {
            "enabled": [bool, "D_248"],
            "current_humidity": [float, "I_220"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": [float, "A_108"],
            "setpoint_a_requested": [float, "A_84"],
            "setpoint_b_outside": [float, "A_109"],
            "setpoint_b_requested": [float, "A_85"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": [float, "A_330"],
            "setpoint_a_requested": [float, "A_331"],
            "setpoint_b_outside": [float, "A_332"],
            "setpoint_b_requested": [float, "A_333"],
        },
    },
    "hc3": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [
            Special(str, Special.NAMEARRAY),
            ["I_231", "I_232", "I_233", "I_234", "I_235", "I_236"],
        ],
        "on": [bool, "D_220"],
        "cooling": [bool, "D_221"],
        "circulation_valve": [bool, "D_70"],
        "water_temp": [float, "A_92"],
        "water_requested": [float, "A_98"],
        "auto": [int, "I_271"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_251"], [float, "A_231"], [float, "A_227"]],
            ],
        ],
        "ambient_temp": [float, "A_228"],
        "pad": {
            "enabled": [bool, "D_251"],
            "current_humidity": [float, "I_221"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": [float, "A_113"],
            "setpoint_a_requested": [float, "A_86"],
            "setpoint_b_outside": [float, "A_114"],
            "setpoint_b_requested": [float, "A_87"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": [float, "A_346"],
            "setpoint_a_requested": [float, "A_347"],
            "setpoint_b_outside": [float, "A_348"],
            "setpoint_b_requested": [float, "A_349"],
        },
    },
    "hc4": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [
            Special(str, Special.NAMEARRAY),
            ["I_241", "I_242", "I_243", "I_244", "I_245", "I_246"],
        ],
        "on": [bool, "D_50"],
        "cooling": [bool, "D_224"],
        "circulation_valve": [bool, "D_71"],
        "water_temp": [float, "A_93"],
        "water_requested": [float, "A_99"],
        "auto": [int, "I_272"],
        "current_humidity": [float, "I_222"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_254"], [float, "A_238"], [float, "A_233"]],
            ],
        ],
        "ambient_temp": [float, "A_234"],
        "pad": {
            "enabled": [bool, "D_254"],
            "current_humidity": [float, "I_222"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": [float, "A_122"],
            "setpoint_a_requested": [float, "A_120"],
            "setpoint_b_outside": [float, "A_88"],
            "setpoint_b_requested": [float, "A_121"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": [float, "A_362"],
            "setpoint_a_requested": [float, "A_363"],
            "setpoint_b_outside": [float, "A_364"],
            "setpoint_b_requested": [float, "A_365"],
        },
    },
    "hc5": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [
            Special(str, Special.NAMEARRAY),
            ["I_251", "I_252", "I_253", "I_254", "I_255", "I_256"],
        ],
        "on": [bool, "D_51"],
        "cooling": [bool, "D_227"],
        "circulation_valve": [bool, "D_72"],
        "water_temp": [float, "A_243"],
        "water_requested": [float, "A_242"],
        "auto": [int, "I_273"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_257"], [float, "A_247"], [float, "A_240"]],
            ],
        ],
        "ambient_temp": [float, "A_241"],
        "pad": {
            "enabled": [bool, "D_257"],
            "current_humidity": [float, "I_223"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": [float, "A_387"],
            "setpoint_a_requested": [float, "A_388"],
            "setpoint_b_outside": [float, "A_389"],
            "setpoint_b_requested": [float, "A_390"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": [float, "A_379"],
            "setpoint_a_requested": [float, "A_380"],
            "setpoint_b_outside": [float, "A_381"],
            "setpoint_b_requested": [float, "A_382"],
        },
    },
    "hc6": {
        "enabled": [Special(bool, Special.FIXED), False],
        "name": [
            Special(str, Special.NAMEARRAY),
            ["I_261", "I_262", "I_263", "I_264", "I_265", "I_266"],
        ],
        "on": [bool, "D_52"],
        "cooling": [bool, "D_231"],
        "circulation_valve": [bool, "D_73"],
        "water_temp": [float, "A_252"],
        "water_requested": [float, "A_251"],
        "auto": [int, "I_274"],
        "current_humidity": [float, "I_224"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "{1} if {0} else {2}",
                [[bool, "D_259"], [float, "A_249"], [float, "A_277"]],
            ],
        ],
        "ambient_temp": [float, "A_250"],
        "pad": {
            "enabled": [bool, "D_259"],
            "current_humidity": [float, "I_224"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": [float, "A_401"],
            "setpoint_a_requested": [float, "A_402"],
            "setpoint_b_outside": [float, "A_403"],
            "setpoint_b_requested": [float, "A_404"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": [float, "A_405"],
            "setpoint_a_requested": [float, "A_406"],
            "setpoint_b_outside": [float, "A_407"],
            "setpoint_b_requested": [float, "A_408"],
        },
    },
    "solar": {
        "enabled": [bool, "D_433"],
        "name": [Special(str, Special.FIXED), "Solar"],
        "s1_temp": [float, "A_258"],
        "s2_temp": [float, "A_259"],
        "s3_temp": [float, "A_260"],
    },
    "pool": {
        "name": [Special(str, Special.FIXED), "Pool"],
        "enabled": [bool, "D_348"],
        "on": [bool, "D_238"],
        "heating": [bool, "D_43"],
        "s1_temp": [float, "A_262"],
        "temp_requested": [float, "A_15"],
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
DEVICE_READ_MAP = {
    "hp_power_state": [bool, "D_3"],
    "hp_function": [int, "I_51"],  # 0: heating, #1: cooling, #2: auto (Write)
    "season": [
        Special(str, Special.FIXED),
        "",
    ],  # summer, auto:summer, winter, auto:winter
    "operating_mode": [
        Special(str, Special.FIXED),
        "heating",
    ],  # heating, cooling, pool, dhw, dpc
    "cooling_mode": [bool, "D_4"],
    "control_curve_heating": {
        "setpoint_a_outside": [float, "A_122"],
        "setpoint_a_requested": [float, "A_120"],
        "setpoint_b_outside": [float, "A_88"],
        "setpoint_b_requested": [float, "A_121"],
    },
    "control_curve_cooling": {
        "setpoint_a_outside": [float, "A_362"],
        "setpoint_a_requested": [float, "A_363"],
        "setpoint_b_outside": [float, "A_364"],
        "setpoint_b_requested": [float, "A_365"],
    },
    "domestic_hot_water": {
        "heating": [bool, "D_66"],
        "enabled": [bool, "D_275"],
        "current_temp": [float, "A_126"],
        "required_temp": [float, "A_129"],
        "min_temp": [float, "A_296"],
        "max_temp": [float, "A_297"],
    },
    "compressor_running": [bool, "D_5"],
    "compressor2_running": [bool, "D_32"],
    "circulation_pump_running": [bool, "D_10"],
    "fan_running": [bool, "D_8"],
    "defrost_mode": [bool, "D_11"],
    "aux_heater_1": [bool, "D_6"],
    "aux_heater_2": [bool, "D_7"],
    "outside_temp": [float, "A_3"],
    "requested_temp": [float, "A_5"],
    "actual_temp": [float, "A_1"],
    "dewp_control": [bool, "D_196"],
    "hdo_on": [bool, "D_15"],
    "runtime_info": {
        "compressor_run_time": [int, "I_11"],
        "compressor_start_counter": [int, "I_12"],
        "pump_runtime": [int, "I_13"],
        "aux1_runtime": [int, "I_100"],
        "aux2_runtime": [int, "I_101"],
    },
    "season_info": {
        "hp_season": [bool, "D_24"],  # True is Winter, False is Summer (Write)
        "hp_seasonset": [int, "I_50"],  # True is Manually Set, False Auto (Write)
        "hp_season_winter": [float, "A_82"],  # (Write)
        "hp_season_summer": [float, "A_83"],  # (Write)
    },
    "error_info": {
        "some_error": [bool, "D_20"],
        "three_errors": [bool, "D_21"],
        "reset_3e": [bool, "D_19"],
        "safety_tstat": [bool, "D_77"],
        "alarm_a": [int, "I_20"],
        "alarm_b": [int, "I_21"],
        "alarm_c": [int, "I_22"],
        "alarm_d": [int, "I_23"],
        "alarm_e": [int, "I_24"],
        "alarm_f": [int, "I_25"],
        "alarm_g": [int, "I_26"],
        "alarm_h": [int, "I_27"],
        "alarm_i": [int, "I_28"],
        "alarm_j": [int, "I_39"],
        "alarm_k": [int, "I_40"],
        "alarm_l": [int, "I_41"],
        "alarm_m": [int, "I_42"],
    },
    "heating_circuits": DEVICE_READ_HCMAP,
}