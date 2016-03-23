from .. import exception

class Expression:
    """The base class for all expressions."""

    def __init__(self):
        pass

    def Evaluate(self, rt):
        """Evaluates the expression in the given runtime environment.

        Args:
            rt (runtime.Runtime): The current runtime environment.

        Returns:
            value.Value: The value of the expression.
        """
        return exception.EvalException(exception.Error.ERR_INTERNAL)

    def EvaluateToNumeric(self, rt):
        """Evaluates the expression and makes sure that the result is numeric.

        Args:
            rt (runtime.Runtime): The current runtime environment.

        Returns:
            value.Value: The value of the expression.
        """
        val = self.Evaluate(rt)
        if val.IsNumeric():
            return val
        raise exception.EvaluationException(exception.Error.ERR_TYPE)

    def EvaluateToString(self, rt):
        """Evaluates the expression and makes sure that the result is a string.

        Args:
            rt (runtime.Runtime): The current runtime environment.

        Returns:
            value.Value: The value of the expression.
        """
        val = self.Evaluate(rt)
        if val.IsString():
            return val
        raise exception.EvaluationException(exception.Error.ERR_TYPE)

    def __str__(self):
        """Constructs a string representation of the expression."""
        return exception.EvalException(exception.Error.ERR_INTERNAL)
