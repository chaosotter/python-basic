from .. import exception
import value

class VString(value.Value):
    """The type of value represents a string."""

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
        """Figures out whether this string represents a valid filename.
        
        TODO(chaosotter): Convert the original Javascript logic:

        // Check the length first.
        if (this.value.length < 1)  return false;
        if (this.value.length > 40)  return false;
  
        // Check for bad characters.
        var pattern = /[^-a-zA-Z0-9_. ]/;
        if (this.value.match(pattern))  return false;
  
        // Check for leading or trailing whitespace.
        if (this.value.charAt(0) == ' ')  return false;
        if (this.value.charAt(this.value.length - 1) == ' ')  return false;
  
        // It must be okay!
        return true;
        """
        return False
