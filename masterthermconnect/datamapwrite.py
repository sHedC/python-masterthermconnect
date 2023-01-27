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
    },
    "pool": {
        "on": [bool, "D_238"],
        "temp_requested": [float, "A_210"],
    },
}

DEVICE_WRITE_MAP = {
    "hp_power_state": [bool, "D_3"],
    "hp_function": [int, "I_51"],  # 0: heating, #1: cooling, #2: auto (Write)
    "control_curve_heating": {
        "setpoint_a_outside": [float, "A_35"],
        "setpoint_a_requested": [float, "A_37"],
        "setpoint_b_outside": [float, "A_36"],
        "setpoint_b_requested": [float, "A_38"],
    },
    "control_curve_cooling": {
        "setpoint_a_outside": [float, "A_47"],
        "setpoint_a_requested": [float, "A_48"],
        "setpoint_b_outside": [float, "A_49"],
        "setpoint_b_requested": [float, "A_50"],
    },
    "domestic_hot_water": {
        "required_temp": [float, "A_129"],
    },
    "heating_circuits": DEVICE_WRITE_HCMAP,
}
