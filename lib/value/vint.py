import value

class VInt(value.Value):
    """The type of value that represents an integer."""

    def __init__(self, value):
        super(VInt, self).__init__(value)

    def Type(self):
        return value.Value.INT

    def IsInt(self):
        return True

    def AsInt(self):
        return self.value

    def AsFloat(self):
        return float(self.value)
