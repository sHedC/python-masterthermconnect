"""Mapping files for writing to the registries."""
from .special import Special

DEVICE_WRITE_HCMAP = {
    "hc0": {
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_191' if {0} else 'A_210'",
                [[bool, "D_242"]],
            ],
        ],
    },
    "hc1": {
        "on": [bool, "D_212"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_219' if {0} else 'A_215'",
                [[bool, "D_245"]],
            ],
        ],
        "pad": {
            "state": [int, "I_15"],  # 0 - Permanently Off, 1 - Scheduled Off, 2 - On
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
        "on": [bool, "D_216"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_225' if {0} else 'A_221'",
                [[bool, "D_248"]],
            ],
        ],
        "pad": {
            "state": [int, "I_6"],
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
        "on": [bool, "D_220"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_231' if {0} else 'A_227'",
                [[bool, "D_251"]],
            ],
        ],
        "pad": {
            "state": [int, "I_227"],
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
        "on": [bool, "D_50"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_238' if {0} else 'A_233'",
                [[bool, "D_254"]],
            ],
        ],
        "pad": {
            "state": [int, "I_230"],
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
        "on": [bool, "D_51"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_247' if {0} else 'A_240'",
                [[bool, "D_257"]],
            ],
        ],
        "pad": {
            "state": [int, "I_239"],
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
        "on": [bool, "D_52"],
        "ambient_requested": [
            Special(float, Special.FORMULA),
            [
                "'A_249' if {0} else 'A_277'",
                [[bool, "D_259"]],
            ],
        ],
        "pad": {
            "state": [int, "I_210"],
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
    "pool": {
        "on": [bool, "D_238"],
        "temp_requested": [float, "A_210"],
    },
}

DEVICE_WRITE_MAP = {
    "hp_power_state": [bool, "D_3"],
    "hp_function": [int, "I_51"],  # 0: heating, #1: cooling, #2: auto (Write)
    "season": {
        # Based on Average Temperature, set manual_set then winter if manual.
        "manual_set": [bool, "I_50"],  # True if Manual Set, False if Auto
        "winter": [bool, "D_24"],  # True is Winter, False is Summer
        "winter_temp": [float, "A_82"],  # -20.0 to 40.0 Below Winter Mode
        "summer_temp": [float, "A_83"],  # -20.0 to 40.0 Above Summer Mode
    },
    "control_curve_heating": {  # -99.9 to 99.9
        "setpoint_a_outside": [float, "A_35"],
        "setpoint_a_requested": [float, "A_37"],
        "setpoint_b_outside": [float, "A_36"],
        "setpoint_b_requested": [float, "A_38"],
    },
    "control_curve_cooling": {  # -99.9 to 99.9
        "setpoint_a_outside": [float, "A_47"],
        "setpoint_a_requested": [float, "A_48"],
        "setpoint_b_outside": [float, "A_49"],
        "setpoint_b_requested": [float, "A_50"],
    },
    "domestic_hot_water": {
        "state": [bool, "D_29"],
        "required_temp": [float, "A_129"],  # Range min_temp to max_temp
    },
    "heating_circuits": DEVICE_WRITE_HCMAP,
}
