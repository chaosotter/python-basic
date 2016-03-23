from .. import exception
from .. import value
import expression

class EAdd(expression.Expression):
    """This expression represents an addition operation."""

    def __init__(self, exp_a, exp_b):
        """Initializes the expression.
        
        Args:
            exp_a (expression.Expression): The first expression.
            exp_b (expression.Expression): The second expression.
        """
        super(EAdd, self).__init__()
        self.exp_a = exp_a
        self.exp_b = exp_b

    def Evaluate(self, rt):
        val_a = self.exp_a.Evaluate(rt)
        val_b = self.exp_b.Evaluate(rt)

        if val_a.IsInt() and val_b.IsInt():
            return value.VInt(val_a.AsInt() + val_b.AsInt())
        elif val_a.IsNumeric() and val_b.IsNumeric():
            return value.VFloat(val_a.AsFloat() + val_b.AsFloat())
        elif val_a.IsString() and val_b.IsString():
            return value.VString(val_a.AsString() + val_b.AsString())
        else:
            raise exception.EvalException(exception.Error.ERR_TYPE)

    def __str__(self):
        return str(self.exp_a) + ' + ' + str(self.exp_b)
