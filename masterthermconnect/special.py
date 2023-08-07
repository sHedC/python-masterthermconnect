"""Special Class for use with the Mapping Files."""


class Special:
    """A Special Class Type for use in mappings."""

    FIXED = "fixed"
    NAMEARRAY = "namearray"
    FORMULA = "formula"

    def __init__(self, data_type: any, condition: str):
        """Initialise the Special Class with the Condition Needed."""
        self.data_type = data_type
        self.condition = condition

    def evaluate(self, formula: str, values: list) -> any:
        """Evalulate the items based on the condition."""
        converted_formula = formula.format(*values)
        result = eval(converted_formula, {}, {})  # pylint: disable=W0123
        return result
