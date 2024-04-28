"""Modbus Mapping Data."""

# Registers are:
#    A_1 to A_500 - Analog Registers e.g. outside temperature
#    D_1 to D_496 - Digital Registers e.g. pump on/ off
#    I_1 to I_500 - Integer Registers e.g. pump runtime

# Mapping based on controller and possibly ext from info.
#   Also the value I_405 has Serial Port Used 0, 1, 2, 3, 4, not sure if useful.
CONROLLER_MAP = {
    "pco5_0": "default",
    "uPC_0": "mt_1",
}

# Currently known mappings:
# default is standard firmware for the CAREL
# mt_1 looks like custom firmware for certain devices
MAPPING = {
    "default": {
        "A": ["hold", 1],
        "D": ["coil", 1],
        "I": ["hold", 501],
    },
    "mt_1": {
        "A": ["hold", 3],
        "D": ["hold", 503],
        "I": ["hold", 999],
    },
}
