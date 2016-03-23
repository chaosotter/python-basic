from .. import value
import expression

class EAnd(expression.Expression):
    """This is an AND operation (no distinction between logical and bitwise)."""

    def __init__(self, exp_a, exp_b):
        """Initializes the expression.

        Args:
            exp_a (expression.Expression): The first expression.
            exp_b (expression.Expression): The second expression.
        """
        super(EAnd, self).__init__()
        self.exp_a = exp_a
        self.exp_b = exp_b

    def Evaluate(self, rt):
        val_a = self.exp_a.EvaluateToNumeric(rt)
        val_b = self.exp_b.EvaluateToNumeric(rt)

        return value.VInt(val_a.AsInt() & val_b.AsInt())

    def __str__(self):
        return str(self.exp_a) + ' AND ' + str(self.exp_b)
