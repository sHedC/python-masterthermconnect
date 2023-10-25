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
        "loop_type": [int, "I_62"],  # 0=none, 1=mix, 2=thermostatic, 3=hot water
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
        "loop_type": [int, "I_65"],
        "pad": {
            "enabled": [bool, "D_248"],
            "state": [bool, "I_6"],
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
        "loop_type": [int, "I_68"],
        "pad": {
            "enabled": [bool, "D_251"],
            "state": [int, "I_227"],
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
        "loop_type": [int, "I_69"],
        "pad": {
            "enabled": [bool, "D_254"],
            "state": [int, "I_230"],
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
        "loop_type": [int, "I_285"],
        "pad": {
            "enabled": [bool, "D_257"],
            "state": [int, "I_239"],
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
        "loop_type": [int, "I_290"],
        "pad": {
            "enabled": [bool, "D_259"],
            "state": [int, "I_210"],
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
        "solar_collector": [float, "A_258"],
        "water_tank1": [float, "A_259"],
        "water_tank2": [float, "A_260"],
    },
    "pool": {
        "name": [Special(str, Special.FIXED), "Pool"],
        "enabled": [bool, "D_348"],
        "on": [bool, "D_238"],
        "heating": [bool, "D_43"],
        "temp_actual": [float, "A_262"],
        "temp_requested": [float, "A_210"],
    },
}

# NOTES --------------------------------------------------
# Moved HC0 Heating/ Cooling Curves to main as always
# used moving to main section so they don't get disabled
# --------------------------------------------------------
DEVICE_READ_MAP = {
    "hp_type": [int, "I_14"],  # 0=A/W, 1=B/W, 2=W/W, 3=DX/W, 4=A/W R, 5=B/W R, 6=W/W R
    "hp_power_state": [bool, "D_3"],
    "hp_function": [int, "I_51"],  # 0: heating, #1: cooling, #2: auto (Write)
    "operating_mode": [
        Special(str, Special.FORMULA),
        [
            (
                "'dhw' if {0} else "
                "'pool' if {1} else "
                "'aux_heater' if not ({2} or {3}) and ({4} or {5}) else "
                "'heating' if {13} and ({8} or {9} or {10} or {11}) else "
                "'cooling_dpc' if {6} and ({7} or {12} or {8} or {9} or {10} or {11}) else "
                "'cooling' if {7} or {12} or {8} or {9} or {10} or {11} else "
                "'idle'"
            ),
            [
                [bool, "D_66"],  # 0 - domestic hot water
                [bool, "D_43"],  # 1 - pool
                [bool, "D_20"],  # 2 - some_error
                [bool, "D_21"],  # 3 - three_errors
                [bool, "D_6"],  # 4 - aux heater 1
                [bool, "D_7"],  # 5 - aux heater 2
                [bool, "D_196"],  # 6 - Dew Point
                [bool, "D_4"],  # 7 - Cooling Mode
                [bool, "D_5"],  # 8 - Compressor 1
                [bool, "D_32"],  # 9 - Compressor 2
                [bool, "D_10"],  # 10 - Ciculation
                [bool, "D_8"],  # 11 - Fan
                [bool, "D_277"],  # 12 - Cooling Pump On
                [bool, "D_24"],  # 13 - Operation Mode 1=Winter, 0=Summer
            ],
        ],
    ],
    "season": {
        "mode": [
            Special(str, Special.FORMULA),
            [
                "('' if {0} else 'auto-') + ('winter' if {1} else 'summer')",
                [[bool, "I_50"], [bool, "D_24"]],
            ],
        ],
        "manual_set": [bool, "I_50"],
        "winter": [bool, "D_24"],
        "winter_temp": [float, "A_82"],
        "summer_temp": [float, "A_83"],
    },
    "cooling_mode": [bool, "D_4"],
    "control_curve_heating": {
        "setpoint_a_outside": [float, "A_35"],
        "setpoint_a_requested": [float, "A_37"],
        "setpoint_b_outside": [float, "A_36"],
        "setpoint_b_requested": [float, "A_38"],
        "requested_min": [float, "A_299"],
        "requested_max": [float, "A_207"],
        "outside_min": [float, "A_300"],
        "outside_max": [float, "A_301"],
    },
    "control_curve_cooling": {
        "setpoint_a_outside": [float, "A_47"],
        "setpoint_a_requested": [float, "A_49"],
        "setpoint_b_outside": [float, "A_48"],
        "setpoint_b_requested": [float, "A_50"],
        "requested_min": [float, "A_305"],
        "requested_max": [float, "A_306"],
        "outside_min": [float, "A_307"],
        "outside_max": [float, "A_308"],
    },
    "domestic_hot_water": {
        "enabled": [bool, "D_275"],
        "state": [bool, "D_29"],
        "heating": [bool, "D_66"],
        "current_temp": [float, "A_126"],
        "required_temp": [float, "A_129"],
        "min_temp": [float, "A_296"],
        "max_temp": [float, "A_297"],
    },
    "compressor_running": [bool, "D_5"],
    "compressor2_running": [bool, "D_32"],
    "circulation_pump_running": [bool, "D_10"],
    "fan_running": [bool, "D_8"],  # Filtered by HP Type
    "brine_pump_running": [bool, "D_8"],  # Filtered by HP Type,
    "defrost_mode": [bool, "D_11"],
    "aux_heater_1": [bool, "D_6"],
    "aux_heater_2": [bool, "D_7"],
    "outside_temp": [float, "A_3"],
    "requested_temp_old": [float, "A_5"],
    "requested_temp": [  # Cooling temp does not show in A_5
        Special(str, Special.FORMULA),
        [
            "{0} if ({2} or {3} or {4} or {5}) else {1}",
            [
                [float, "A_5"],  # 0 - Main Requested Temp
                [float, "A_212"],  # 1 - Heating/Cooling Temp
                [bool, "D_66"],  # 2 - Hot Water
                [bool, "D_43"],  # 3 - Pool
                [bool, "D_6"],  # 4 - Aux Heater 1
                [bool, "D_7"],  # 5 - Aux Heater 2
            ],
        ],
    ],
    "actual_temp": [float, "A_1"],
    "dewp_control": [bool, "D_196"],
    "high_tariff_control": [
        Special(bool, Special.FORMULA),
        [
            "not {0}",
            [[bool, "D_15"]],
        ],
    ],
    "runtime_info": {
        "compressor_run_time": [int, "I_11"],
        "compressor_start_counter": [int, "I_12"],
        "pump_runtime": [int, "I_13"],
        "aux1_runtime": [int, "I_100"],
        "aux2_runtime": [int, "I_101"],
    },
    "error_info": {
        "some_error": [bool, "D_20"],  # Some Alarm has activated
        "three_errors": [bool, "D_21"],  # 3 error conditions met, manual reset required
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
