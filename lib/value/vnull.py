import value

class VNull(value.Value):
    """The null value, generated only for empty items in DATA statements.
    
    For the convenience of the user, a null value is both numeric and a string.
    """

    def __init__(self):
        super(VNull, self).__init__(None)

    def Type(self):
        return value.Value.NULL

    def IsInt(self):
        return True

    def IsFloat(self):
        return True

    def IsString(self):
        return True

    def __str__(self):
        return ""

    def AsInt(self):
        return 0

    def AsFloat(self):
        return 0.0

    def AsString(self):
        return ""
