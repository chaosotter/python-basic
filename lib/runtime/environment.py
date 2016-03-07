import math

from .. import system
from .. import value

class Environment:
    """Implements a data environment for the interpreter.
    
    Since BASIC has a primitive data model, this is basically just a collection
    of dictionaries from variable name to Value object: one for scalar
    variables, one for arrays, and one for FN functions.
    """

    def __init__(self, parent=None):
        """Initializes a new environment.
        
        Args:
            parent (Environment): Parent environment, if any.
        """
        self.parent = parent
        self.scalars = {}     # ID->value for scalar variables
        self.arrays = {}      # ID->value for arrays
        self.functions = {}   # ID->value for functions

        # Add the build-in variables.
        self.Set("pi", value.VFloat(math.pi))
        self.Set("folder$", system.State.folder)

    def Get(self, id):
        """Returns the value of this scalar variable, or None.
        
        Args:
            id (str): Name of the variable.
            
        Returns:
            value.Value: The value of the variable.
        """
        if id in self.scalars:
            return self.scalars[id]
        elif self.parent:
            return self.parent.Get(id)
        return None
        
    def GetArray(self, id, indices):
        """Returns the value at these indices for the given array variable.
        
        Args:
            id (str): Name of the variable.
            indices (list of int): The array subscripts.
            
        Returns:
            value.Value: The value at this location.
            
        Raises:
            runtime.EvalException if the array is undefined or the indices are
            invalid.
        """
        if id in self.arrays:
            return self.arrays[id].Get(indices)
        elif self.parent:
            return self.parent.GetArray(id, indices)
        raise runtime.EvalException(runtime.Error.ERR_BADVAR)

    def GetFunction(self, id):
        """Returns the value of the given FN function, or None.
        
        Args:
            id (str): Name of the variable.
            
        Returns:
            value.VFunction: The function with this name.
        """
        if id in self.functions:
            return self.functions[id]
        elif self.parent:
            return self.parent.GetFunction(id)
        return None

    def MakeArray(self, lvalue, dims):
        """Makes a new array variable with the given name and maximum indices.
        
        We express the name of the variable using the expression.LValue class so
        that we can reuse the automatic type detection code.class
        
        Right now, Python BASIC implicitly uses "OPTION BASE 0".  In other
        words, DIM A(2) gets you an array with three elements.  Incrementing
        each of the maximum indices by one to accomplish this is NOT the job of
        this method.  You have been warned!
        
        Args:
            lvalue (expression.LValue): The variable to create
            dims (list of int): The dimensions of the array.
        """
        self.arrays[lvalue.id] = value.ArrayValue(lvalue.type, dims)
        
    def Set(self, id, value):
        """Sets the value of the given scalar variable as specified.

        This is probably not what you want to cell.  Nobody really needs to use
        this, other than this class and the expression.LValue class.
        
        Args:
            id (str): The name of the variable.
            value (value.Value): The new value for the variable.
        """
        self.scalars[id] = value

    def SetArray(self, id, indices, value):
        """Sets the given location in this array as specified.
        
        This is probably not what you want to cell.  Nobody really needs to use
        this, other than this class and the expression.LValueArray class.
        
        Args:
            id (str): The name of the array.
            indices (list of int): The array subscripts.
            value (value.Value): The value to store.
            
        Raises:
            runtime.EvalException if the array does not exist or the indices are
            invalid.
        """
        if id in self.arrays:
            self.arrays[id].Set(indices, value)
        raise runtime.EvalException(runtime.Error.ERR_BADVAR)

    def SetFunction(self, id, value):
        """Sets an FN function to the given function value.
        
        This is called by the statement.SDefFn class and nobody else, so don't
        you call it either.
        
        Args:
            id (str): The name of the function.
            value (value.VFunction): The function value.
        """
        self.functions[id] = value
