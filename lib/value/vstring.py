import re

from .. import exception
import value

class VString(value.Value):
    """The type of value that represents a string."""

    def __init__(self, value):
        super(VString, self).__init__(value)

    def Type(self):
        return value.Value.STRING

    def IsString(self):
        return True

    def AsInt(self):
        try:
            return int(self.value)
        except ValueError:
            raise exception.EvalException(
                exception.Error.ERR_FORMAT, 'string conversion')

    def AsFloat(self):
        try:
            return float(self.value)
        except ValueError:
            raise exception.EvalException(
                exception.Error.ERR_FORMAT, 'string conversion')

    def AsString(self):
        return self.value

    def IsValidFilename(self):
        """Checks whether this string represents a valid filename."""
        # Check the length first.
        if len(self.value) < 1 or len(self.value) > 40:
            return False

        # Check for bad characters.
        if re.match(r'[^-a-zA-Z0-9_. ]', self.value):
            return False
        
        # Check for leading or trailing whitespace.
        if self.value[0] == ' ' or self.value[-1] == ' ':
            return False

        # It must be okay!
        return True
