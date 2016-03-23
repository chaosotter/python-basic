import value

class VFloat(value.Value):
    """The type of value that represents a float."""

    def __init__(self, value):
        super(VFloat, self).__init__(value)

    def Type(self):
        return value.Value.FLOAT

    def IsFloat(self):
        return True

    def AsInt(self):
        return int(self.value)

    def AsFloat(self):
        return self.value
