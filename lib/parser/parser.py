import sys

from .. import exception
from .. import expression
from .. import runtime
from .. import statement
from .. import value
import print_item
import token

class Parser:
    """Recursive-descent parser for BASIC statements and expressions."""

    def __init__(self, stream):
        """Initializes the parser with a source of tokens."""
        self.stream = stream

    def Read(self):
        """Attempts to read one more statement.StatementSet from the stream.

        Returns:
            statement.StatementSet, or None if no more statements could be read.
        """
        return self._ReadCommand()

    def _ReadAssign(self):
        """Reads an assignment statement.

        [assign] ::= [ID] = [exp]

        Returns:
            statement.SAssignment: The statement read.
        """
        try:
            var = self._ReadLValue()
            self.stream.require(token.TYPE_EQUAL)
            exp = self._ReadExp()
            return statement.SAssignment(var, exp)
        except Exception as e:
            raise exception.ParserException('assignment', e)

    def _ReadCall(self):
        """Reads a function call.

        [call] ::= [FUNCTION] [exp-list]

        Returns:
            expression.Expression: The expression read.
        """
        try:
            # Read the function name.
            name = self.stream.Require(token.TYPE_FUNCTION).value

            # Handle zero-argument functions first.
            if name == 'RND' and self.stream.Peek().type != token.TYPE_LPAREN:
                return expression.fn.EFnRnd()
            elif name == 'DATE$':
                return expression.fn.EFnDateS()
            elif name == 'TIME$':
                return expression.fn.EFnTimeS()

            # Read the opening parenthesis.
            self.stream.Require(token.TYPE_LPAREN)

            # Read the list of argument expressions.
            exp = None
            if name == 'ABS':
                return expression.fn.EFnAbs(self._ReadExpList(1))
            elif name == 'ACOS':
                return expression.fn.EFnAcos(self._ReadExpList(1))
            elif name == 'ASC':
                return expression.fn.EFnAsc(self._ReadExpList(1))
            elif name == 'ASIN':
                return expression.fn.EFnAsin(self._ReadExpList(1))
            elif name == 'ATAN':
                return expression.fn.EFnAtan(self._ReadExpList(1))
            elif name == 'ATAN2':
                return expression.fn.EFnAtan2(self._ReadExpList(2))
            elif name == 'BIN$':
                return expression.fn.EFnBinS(self._ReadExpList(1))
            elif name == 'COS':
                return expression.fn.EFnCos(self._ReadExpList(1))
            elif name == 'CHR$':
                return expression.fn.EFnChrS(self._ReadExpList(1))
            elif name == 'EXP':
                return expression.fn.EFnExp(self._ReadExpList(1))
            elif name == 'HEX$':
                return expression.fn.EFnHexS(self._ReadExpList(1))
            elif name == 'INSTR':
                return expression.fn.EFnInstr(self._ReadExpList(2))
            elif name == 'INT':
                return expression.fn.EFnInt(self._ReadExpList(1))
            elif name == 'LEFT$':
                return expression.fn.EFnLeftS(self._ReadExpList(2))
            elif name == 'LEN':
                return expression.fn.EFnLen(self._ReadExpList(1))
            elif name == 'LOG':
                return expression.fn.EFnLog(self._ReadExpList(1))
            elif name == 'LOOK':
                return expression.fn.EFnLook(self._ReadExpList(2, 3))
            elif name == 'MID$':
                return expression.fn.EFnMidS(self._ReadExpList(3))
            elif name == 'POS':
                return expression.fn.EFnPos(self._ReadExpList(1))
            elif name == 'RIGHT$':
                return expression.fn.EFnRightS(self._ReadExpList(2))
            elif name == 'RND':
                return expression.fn.EFnRnd(self._ReadExpList(1))
            elif name == 'SGN':
                return expression.fn.EFnSgn(self._ReadExpList(1))
            elif name == 'SIN':
                return expression.fn.EFnSin(self._ReadExpList(1))
            elif name == 'SIZE':
                return expression.fn.EFnSize(self._ReadExpList(1, 2))
            elif name == 'SPACE$':
                return expression.fn.EFnSpaceS(self._ReadExpList(1))
            elif name == 'SQR':
                return expression.fn.EFnSqr(self._ReadExpList(1))
            elif name == 'STR$':
                return expression.fn.EFnStrS(self._ReadExpList(1))
            elif name == 'STRING$':
                return expression.fn.EFnStringS(self._ReadExpList(2))
            elif name == 'TAB':
                return expression.fn.EFnTab(self._ReadExpList(1))
            elif name == 'TAN':
                return expression.fn.EFnTan(self._ReadExpList(1))
            elif name == 'VAL':
                return expression.fn.EFnVal(self._ReadExpList(1))
            else:
                raise exception.ParserException('unknown function')
  
            # Read the closing parenthesis and we're done.
            self.stream.Require(token.TYPE_RPAREN)
            return exp

        except Exception as e:
            raise exception.ParserException('function call', e)

    def _ReadClear(self):
        """Reads a CLEAR statement.

        [clear] ::= CLEAR

        Returns:
            statement.SClear: The statement read.
        """
        try:
            self.stream.RequireKeyword('CLEAR')
            return statement.SClear()
        except Exception as e:
            raise exception.ParserException('CLEAR', e)

    def _ReadCls(self):
        """Reads a CLS statement.

        [cls] ::= CLS

        Returns:
            statement.SCls: The statement read.
        """
        try:
            self.stream.RequireKeyword('CLS')
            return statement.SCls()
        except Exception as e:
            raise exception.ParserException('CLS', e)

    def _ReadColor(self):
        """Reads a COLOR statement.

        [color] ::= COLOR [exp] | COLOR [exp] , [exp]

        Returns:
            statement.SColor: The statement read.
        """
        try:
            # Read the foreground color.
            self.stream.RequireKeyword('COLOR')
            fg_exp = self._ReadExp()

            # Also read the background color, if there is one.
            if self.stream.Peek().IsType(token.TOKEN_COMMA):
                self.stream.Get()
                return statement.SColor(fg_exp, self._ReadExp())
            else:
                return statement.SColor(fg_exp)
        except Exception as e:
            raise exception.ParserException('COLOR', e)

    def _ReadCommand(self):
        """Reads input from the command mode.

        [INT] [statement-list] | [statement-list]

        This is the top-level input function called by Read().

        If we read the form beginning with an integer, this is actually an
        editor command, and we return None.

        Returns:
            statement.StatementSet or None: The statements read.
        """
        try:
            # Get the next token.
            token = self.stream.Peek()

            # If it's a line number, we're adding to a program.
            if token.IsType(token.TYPE_INT):
                # Get the line number.
                line_number = self.stream.Require(token.TYPE_INT).value

                # Try to add the line to the program.
                try:
                    statement_set = self._ReadStatementList()
                    system.State.program.Add(line_number, statement_set)
                except Exception as e:
                    e.AtLine(line_number)
                return None
            else:
                return self._ReadStatementList()

        except Exception as e:
            raise exception.ParserException('line number', e)

    def _ReadComment(self):
        """Reads a comment (REM) statement.

        [comment] ::= [COMMENT]

        Returns:
            statement.SComment: The statement read.
        """
        try:
            token = self.stream.Require(token.TYPE_COMMENT)
            return statement.SComment(token.value)
        except Exception as e:
            raise exception.ParserException('comment', e)

    def _ReadCursor(self):
        """Reads a CURSOR statement.
        
        [cursor] ::= CURSOR [exp]

        Returns:
            statement.SCursor: The statement read.
        """
        try:
            token = self.stream.RequireKeyword('CURSOR')
            return statement.SCursor(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('CURSOR', e)

    def _ReadData(self):
        """Reads a DATA statement.

        [data] ::= DATA [data-list]

        Returns:
            statement.SData: The statement read.
        """
        try:
            token = self.stream.RequireKeyword('DATA')
            return statement.SData(self._ReadDataList())
        except Exception as e:
            raise exception.ParserException('DATA', e)

    def _ReadDataItem(self):
        """Reads a single item for a DATA statement.

        [data-item] ::= [STRING] | [INT] | [FLOAT] | [ID] | @

        Note that this is different from a literal -- empty data and ID tokens
        are valid, as a convenience to the user, and we allow negative numbers.

        Returns:
            value.Value: A single data value.
        """
        try:
            tok = self.stream.Peek()
            if tok.type == token.TYPE_INT:
                return value.VInt(self.stream.Get().value)

            elif tok.type == token.TYPE_FLOAT:
                return value.VFloat(self.stream.Get().value)

            elif tok.type in (token.TYPE_ID_FLOAT, token.TYPE_KEYWORD,
                                 token.TYPE_FUNCTION, token.TYPE_STRING):
                return value.VString(self.stream.Get().value)

            elif tok.type == token.TYPE_MINUS:
                val = self._ReadDataItem()
                if isinstance(val, value.VInt):
                    return value.VInt(-val.AsInt())
                elif isinstance(val, value.VFloat):
                    return value.VFloat(-val.AsFloat())
                elif isinstance(val, value.VString):
                    return value.VString('-' + val.AsString())

            else:
                return value.VNull()

        except Exception as e:
            raise exception.ParserException('DATA item', e)

    def _ReadDataList(self):
        """Reads a list of items for a DATA statement.

        [data-list] ::= [data-item] [data-list-rest]
        [data-list-rest] ::= @ | , [data-list]

        Returns:
            list of value.Value: The array of data values.
        """
        value_list = []
        try:
            value_list.append(self._ReadDataItem())
            while self.stream.Peek().IsType(token.TYPE_COMMA):
                self.stream.Get()
                value_list.append(self._ReadDataItem())
            return value_list
        except Exception as e:
            raise exception.ParserException('DATA list', e)

    def _ReadDefFn(self):
        """Reads a DEF FN statement.

        [def-fn] ::= DEF [fn] ( [id-list] ) = [exp]

        Returns:
            statement.SDefFn: The statement read.
        """
        try:
            self.stream.RequireKeyword('DEF')

            # Read the function name.
            name = self.stream.RequireId()
            if not name.IsFn():
                raise exception.ParserException('DEF FN')

            # Read the list of formals.
            self.stream.Require(token.TYPE_LPAREN)
            formals = self._ReadIdList()
            self.stream.Require(token.TYPE_RPAREN)

            # Finish up.
            self.stream.Require(token.TYPE_EQUAL)
            return statement.SDefFn(name.vale, formals, self._ReadExp())
        except Exception as e:
            raise exception.ParserException('DEF FN', e)

    def _ReadDelete(self):
        """Reads a DELETE statement.

        [delete] ::= DELETE [range]

        Returns:
            statement.SDelete: The statement read.
        """
        try:
            self.stream.RequireKeyword('DELETE')
            return statement.SDelete(self._ReadRange())
        except Exception as e:
            raise exception.ParserException('DELETE', e)

    def _ReadDim(self):
        """Reads a DIM statement.

        [dim] ::= DIM [lvalue-array-list]

        Returns:
            statement.SDim: The statement read.
        """
        try:
            self.stream.RequireKeyword('DIM')
            return statement.SDim(self._ReadLValueArrayList())
        except Exception as e:
            raise exception.ParserException('DIM', e)

    def _ReadEnd(self):
        """Reads an END statement.

        [end] ::= END

        Returns:
            statement.SEnd: The statement read.
        """
        try:
            self.stream.RequireKeyword('END')
            return statement.SEnd()
        except Exception as e:
            raise exception.ParserException('END', e)

    def _ReadExp(self):
        """Reads an expression.

        [exp] ::= [exp0]

        Returns:
            expression.Expression: The expression read.
        """
        return self._ReadExp0()

    def _ReadExp0(self):
        """Another precedence level in expression-parsing.

        [exp0] ::= [exp1] [exp0-rest]
        [exp0-rest] ::= @ | OR [exp1] [exp0-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp1()
        try:
            tok = self.stream.Peek()
            while tok.IsKeyword('OR'):
                self.stream.Get()
                exp = expression.EOf(exp, self._ReadExp1())
                tok = self.stream.Peek()
        except Exception as e:
            raise exception.ParserException('expression', e)
        return exp

    def _ReadExp1(self):
        """Another precedence level in expression-parsing.

        [exp1] ::= [exp2] [exp1-rest]
        [exp1-rest] ::= @ | AND [exp2] [exp1-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp2()
        try:
            tok = self.stream.Peek()
            while tok.IsKeyword('AND'):
                self.stream.Get()
                exp = expression.EAnd(exp, self._ReadExp2())
                tok = self.stream.Peek()
        except Exception as e:
            raise exception.ParserException('expression', e)
        return exp

    def _ReadExp2(self):
        """Another precedence level in expression-parsing.

        [exp2] ::= [exp3] [exp2-rest]
        [exp2-rest] ::= @ | =  [exp3] [exp2-rest] | <> [exp3] [exp2-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp3()
        try:
            tok = self.stream.Peek()
            while tok.IsType(token.TYPE_EQUAL) or tok.IsType(token.TYPE_NEQUAL):
                if tok.IsType(token.TYPE_EQUAL):
                    exp = expression.ERelational(
                        expression.RELATION_TYPE_EQ, exp, self._ReadExp3())
                elif tok.IsType(token.TYPE_NEQUAL):
                    exp = expression.ERelational(
                        expression.RELATION_TYPE_NEQ, exp, self._ReadExp3())
                tok = self.stream.Peek()
        except Exception as e:
            raise exception.ParserException('expression', e)
        return exp

    def _ReadExp3(self):
        """Another precedence level in expression-parsing.

        [exp3] ::= [exp4] [exp3-rest]
        [exp3-rest] ::= @ | <  [exp4] [exp3-rest] | <= [exp4] [exp3-rest]
            | >  [exp4] [exp3-rest] | >= [exp4] [exp3-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp4()
        try:
            tok = self.stream.Peek()
            while (tok.IsType(token.TYPE_GEQ) or tok.IsType(token.TYPE_GT) or
                   tok.IsType(token.TYPE_LEQ) or tok.IsType(token.TYPE_LT)):
                if tok.type == token.TYPE_GEQ:
                    self.stream.Get()
                    exp = expression.ERelational(
                        expression.RELATION_TYPE_GEQ, exp, self._ReadExp4())
                elif tok.type == token.TYPE_GT:
                    self.stream.Get()
                    exp = expression.ERelational(
                        expression.RELATION_TYPE_GT, exp, self._ReadExp4())
                elif tok.type == token.TYPE_LEQ:
                    self.stream.Get()
                    exp = expression.ERelational(
                        expression.RELATION_TYPE_LEQ, exp, self._ReadExp4())
                elif tok.type == token.TYPE_LT:
                    self.stream.Get()
                    exp = expression.ERelational(
                        expression.RELATION_TYPE_LT, exp, self._ReadExp4())
                tok = self.stream.Peek()
        except Exception as e:
            raise exception.ParserException('expression', e)
        return exp

    def _ReadExp4(self):
        """Another precedence level in expression-parsing.

        [exp4] ::= [exp5] [exp4-rest]
        [exp4-rest] ::= @ | + [exp5] [exp4-rest] | - [exp5] [exp4-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp5()
        try:
            tok = self.stream.Peek()
            while tok.IsType(token.TYPE_PLUS) or tok.IsType(token.TYPE_MINUS):
                if tok.IsType(token.TYPE_PLUS):
                    self.stream.Get()
                    exp = expression.EAdd(exp, self._ReadExp5())
                elif tok.IsType(token.TYPE_MINUS):
                    self.stream.Get()
                    exp = expression.ESubtract(exp, self._ReadExp5())
                tok = self.stream.Peek()
        except Exception as e:
            raise exception.ParserException('expression', e)
        return exp

    def _ReadExp5(self):
        """Another precedence level in expression-parsing.

        [exp5] ::= [exp6] [exp5-rest]
        [exp5-rest] ::= @ | * [exp6] [exp5-rest] | / [exp6] [exp5-rest]
            | MOD [exp6] [exp5-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp6()
        try:
            tok = self.stream.Peek()
            while (tok.IsType(token.TYPE_DIVIDE) or
                   tok.IsType(token.TYPE_TIMES) or
                   tok.IsKeyword('MOD')):
                if tok.IsType(token.TYPE_DIVIDE):
                    self.stream.Get()
                    exp = expression.EDivide(exp, self._ReadExp6())
                elif tok.IsType(token.TYPE_TIMES):
                    self.stream.Get()
                    exp = expression.EMultiply(exp, self._ReadExp6())
                elif tok.IsKeyword('MOD'):
                    self.stream.Get()
                    exp = expression.EMod(exp, self._ReadExp6())
                tok = self.stream.Peek()
        except Exception as e:
            raise exception.ParserException('expression', e)
        return exp

    def _ReadExp6(self):
        """Another precedence level in expression-parsing.

        [exp6] ::= [exp7] | + [exp6] | - [exp6] | NOT [exp6]

        Returns:
            expression.Expression: The expression read.
        """
        try:
            tok = self.stream.Peek()
            if tok.IsType(token.TYPE_EOF):
                return self._ReadExp7()
            elif tok.IsType(token.TYPE_PLUS):
                self.stream.Get()
                return self._ReadExp6()
            elif tok.IsType(token.TYPE_MINUS):
                self.stream.Get()
                return expression.ENegate(self._ReadExp6())
            elif tok.IsKeyword('NOT'):
                self.stream.Get()
                return expression.ENot(self._ReadExp6())
        except Exception as e:
            raise exception.ParserException('expression', e)
        return self._ReadExp7()

    def _ReadExp7(self):
        """Another precedence level in expression-parsing.

        [exp7] ::= [exp8] [exp7-rest]
        [exp7-rest] ::= @ | ^ [exp7] [exp7-rest]

        Returns:
            expression.Expression: The expression read.
        """
        exp = self._ReadExp8()
        try:
            tok = self.stream.Peek()
            if tok.IsType(token.TYPE_POWER):
                self.stream.Get()
                exp = expression.EPower(exp, self._ReadExp7())
        except Exception as e:
            raise exception.ParseException('expression', e)
        return exp

    def _ReadExp8(self):
        """Another precedence level in expression-parsing.

        [exp8] ::= [literal] | [lvalue] | [fn-call] | [function] [args]
            | ( [exp] )

        Returns:
            expression.Expression: The expression read.
        """
        try:
            tok = self.stream.Peek()
            if tok.IsType(token.TYPE_LPAREN):
                # This is a parenthetical expression.
                self.stream.Require(token.TYPE_LPAREN)
                exp = self._ReadExp()
                self.stream.Require(token.TYPE_RPAREN)
                return expression.EParen(exp)
            elif tok.IsType(token.TYPE_FUNCTION):
                # This is a built-in function call.
                return self._ReadCall()
            elif tok.IsFn():
                # This is an FN function call.
                return self._ReadFunction()
            elif tok.IsId():
                # This is an LValue.
                return self._ReadLValue()
            else:
                # This is a literal
                return self._ReadLiteral()
        except Exception as e:
            raise exception.ParserException('expression', e)

    def _ReadExpList(self, min_count=None, max_count=None):
        """Reads in a list of expressions.

        [exp-list] ::= [exp] [exp-list-rest]
        [exp-list-rest] ::= @ | , [exp] [exp-list-rest]

        Args:
            min_count (int): The (optional) minimum number of expressions.
            max_count (int): The (optional) maximum number of expressions.

        Returns:
            list of expression.Expression: The list of expressions read.
        """
        exps = []
        try:
            exps.append(self._ReadExp())
            while self.stream.Peek().IsType(token.TYPE_COMMA):
                self.stream.Get()
                exps.append(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('expression list', e)

        if min_count and not max_count:
            max_count = min_count

        if ((min_count and len(exps) < min_count) or
            (max_count and len(exps) > max_count)):
            raise exception.ParserException('argument count')

        return exps

    def _ReadFiles(self):
        """Reads a FILES statement.

        [files] ::= FILES
        
        Returns:
            statement.SFiles: The statement read.
        """
        try:
            self.stream.RequireKeyword('FILES')
            return statement.SFiles()
        except Exception as e:
            raise exception.ParserException('FILES', e)

    def _ReadFolder(self):
        """Reads a FOLDER statement.

        [folder] ::= FOLDER [exp]

        Returns:
            statement.SFolder: The statement read.
        """
        try:
            self.stream.RequireKeyword('FOLDER')
            return statement.SFolder(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('FOLDER', e)

    def _ReadFolders(self):
        """Reads a FOLDERS statement.

        [folders] ::= FOLDERS

        Returns:
            statement.SFolders: The statement read.
        """
        try:
            self.stream.RequireKeyword('FOLDERS')
            return statement.SFolders()
        except Exception as e:
            raise exception.ParserException('FOLDERS', e)

    def _ReadFor(self):
        """Reads a FOR statement.

        [for] ::= FOR [lvalue] = [exp] TO [exp] |
            FOR [lvalue] = [exp] TO [exp] STEP [exp]

        Returns:
            statement.SFor: The statement read.
        """
        try:
            # Read the FOR.
            self.stream.RequireKeyword('FOR')

            # Get the variable to use.
            var = self._ReadLValue()
            if not var.IsNumeric():
                raise exception.ParserException('FOR variable')

            # Read the range expression.
            self.stream.Require(token.TYPE_EQUAL)
            exp_start = self._ReadExp()
            self.stream.RequireKeyword('TO')
            exp_end = self._ReadExp()

            # See if there's a step specified.
            if self.stream.Peek().IsKeyword('STEP'):
                self.stream.Get()
                exp_step = self._ReadExp()
                return statement.SFor(var, exp_start, exp_end, exp_step)
            else:
                return statement.SFor(var, exp_start, exp_end)

        except Exception as e:
            raise exception.ParserException('FOR', e)

    def _ReadFunction(self):
        """Reads a FN function call expression.

        [fn-call] ::= [ID_INT] ( [exp-list] ) | [ID_FLOAT] ( [exp-list] ) |
            [ID_STRING] ( [exp-list] )

        Returns:
            expression.EFunction: The expression read.
        """
        try:
            name = expression.ELValue(self.stream.RequireId())
            self.stream.Require(token.TYPE_LPAREN)
            arg_exps = self._ReadExpList()
            self.stream.Require(token.TYPE_RPAREN)
        except Exception as e:
            raise exception.ParserException('function call', e)

    def _ReadGet(self):
        """Reads a GET statement.

        [get] ::= GET [lvalue]

        Returns:
            statement.SGet: The statement read.
        """
        try:
            self.stream.RequireKeyword('GET')
            return statement.SGet(self._ReadLValue())
        except Exception as e:
            raise exception.ParserException('GET', e)

    def _ReadGosub(self):
        """Reads a GOSUB statement.

        [gosub] ::= GOSUB [exp]
        
        Returns:
            statement.SGosub: The statement read.
        """
        try:
            self.stream.RequireKeyword('GOSUB')
            return statement.SGosub(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('GOSUB', e)

    def _ReadGoto(self):
        """Reads a GOTO statement.

        [goto] ::= GOTO [exp]

        Returns:
            statement.SGoto: The statement read.
        """
        try:
            self.stream.RequireKeyword('GOTO')
            return statement.SGoto(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('GOTO', e)

    def _ReadIdList(self):
        """Reads a list of IDs.

        [id-list] ::= [ID_INT] [id-list-rest] | [ID_FLOAT] [id-list-rest] |
            [ID_STRING] [id-list-rest]
        [id-list-rest] ::= @ | , [id-list]

        Returns:
            list of expression.ELValue: The array of IDs.
        """
        vars = []
        try:
            vars.append(expression.ELValue(self.stream.RequireId()))
            while self.stream.Peek().IsType(token.TYPE_COMMA):
                self.stream.Get()
                vars.append(self.expression.ELValue(self.stream.RequireId()))
            return vars
        except Exception as e:
            raise exception.ParserException('variable list', e)

    def _ReadIf(self):
        """Reads an IF statement.

        [if] ::= IF [exp] THEN [then-case] |
            IF [exp] THEN [then-case] ELSE [else-case]

        Returns:
            statement.SIf: The statement read.
        """
        try:
            # Read the IF and THEN.
            self.stream.RequireKeyword('IF')
            test_exp = self._ReadExp()
            self.stream.RequireKeyword('THEN')
            then_case = self._ReadThenCase()

            # See if there's an ELSE.
            if self.stream.Peek().IsKeyword('ELSE'):
                self.stream.RequireKeyword('ELSE')
                else_case = self._ReadThenCase()
                return statement.SIf(test_exp, then_case, else_case)

            # If not, return the one-armed version.
            return statement.SIf(test_exp, then_case)

        except Exception as e:
            raise exception.ParserException('IF', e)

    def _ReadInput(self):
        """Reads an INPUT statement.

        [input] ::= INPUT [lvalue-list] | INPUT [STRING] ; [lvalue-list]

        Returns:
            statement.SInput: The statement read.
        """
        try:
            self.stream.RequireKeyword('INPUT')
            if self.stream.Peek().IsType(token.TYPE_STRING):
                prompt = self.stream.Get().value
                self.stream.Require(token.TYPE_SEMICOLON)
                return statement.SInput(self._ReadLValueList(), prompt)
            else:
                return statement.SInput(self._ReadLValueList())
        except Exception as e:
            raise exception.ParserException('INPUT', e)

    def _ReadInt(self):
        """Reads an integer expression.

        [int] ::= [INT] | [BIN] | [HEX]

        Returns:
            expression.EInt: The expression read.
        """
        try:
            tok = self.stream.RequireInt()
            if tok.IsType(token.TYPE_INT):
                return expression.EInt(tok.value)
            elif tok.IsTyp(token.TYPE_INT_BIN):
                return expression.EInt(tok.value, 2)
            else:
                return expression.EInt(tok.value, 16)
        except Exception as e:
            raise exception.ParserException('constant', e)

    def _ReadLet(self):
        """Reads a LET statement.

        [let] ::= LET [assign]

        Returns:
            statement.SAssignment: The statement read.
        """
        try:
            self.stream.RequireKeyword('LET')
            return self._ReadAssign()
        except Exception as e:
            raise exception.ParserException('LET', e)

    def _ReadList(self):
        """Reads a LIST statement.

        [list] ::= LIST [range]

        Returns:
            statement.SList: The statement read.
        """
        try:
            self.stream.RequireKeyword('LIST')
            return statement.SList(self._ReadRange())
        except Exception as e:
            raise exception.ParserException('LIST', e)

    def _ReadLiteral(self):
        """Reads a literal expression.

        [literal] ::= [STRING] | [int] | [FLOAT]

        Returns:
            expression.Expression: The expression read.
        """
        try:
            tok = self.stream.Peek()
            if tok.IsType(token.TYPE_STRING):
                return expression.EString(self.stream.Get().value)
            elif tok.IsType(token.TYPE_FLOAT):
                return expression.EFloat(self.stream.Get().value)
            elif tok.IsInt():
                return self._ReadInt()
            else:
                raise exception.ParserException('expression')
        except Exception as e:
            raise exception.ParserException('constant', e)

    def _ReadLoad(self):
        """Reads a LOAD statement.

        [load] ::= LOAD [exp]

        Returns:
            statement.SLoad: The statement read.
        """
        try:
            self.stream.RequireKeyword('LOAD')
            return statement.SLoad(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('LOAD', e)

    def _ReadLocate(self):
        """Reads a LOCATE statement.

        [locate] ::= LOCATE [exp] , [exp]

        Returns:
            statement.SLocale: The statement read.
        """
        try:
            self.stream.RequireKeyword('LOCATE')
            row_exp = self._ReadExp()
            self.stream.Require(token.TYPE_COMMA)
            column_exp = self._ReadExp()
            return statement.SLocate(row_exp, column_exp)
        except Exception as e:
            raise exception.ParserException('LOCATE', e)

    def _ReadLValue(self):
        """Reads a LValue (assignable value).

        [lvalue] ::= [ID_INT] | [ID_FLOAT] | [ID_STRING] | [lvalue-array]

        Returns:
            expression.Expression: The assignable value read.
        """
        try:
            # Read the ID.
            tok = self.stream.RequireId()

            # Dispatch to the array or FN function versions if necessary.
            if self.stream.Peek().IsType(token.TYPE_LPAREN):
                return self._ReadLValueArray(tok)
            else:
                return expression.ELValue(tok)

        except Exception as e:
            raise exception.ParserException('variable reference', e)

    def _ReadLValueList(self):
        """Reads an array of LValues (assignable values).

        [lvalue-list] ::= [lvalue-list] [lvalue-list-rest]
        [lvalue-list-rest] ::= @ | , [lvalue-list]

        Returns:
            list of expression.ELValue: The assignable values read.
        """
        vals = []
        try:
            vals.append(self._ReadLValue())
            while self.stream.Peek().IsType(tok.TYPE_COMMA):
                self.stream.Get()
                vals.append(self._ReadLValue())
            return vals
        except Exception as e:
            raise exception.ParserException('variable list', e)

    def _ReadLValueArray(self, tok):
        """Reads an assignable array value.

        [lvalue-array] ::= [ID_INT] ( [exp-list] ) | [ID_FLOAT] ( [exp-list] ) |
            [ID_STRING] ( [exp-list] )

        Args:
            tok (token.Token): The variable name we've already read.

        Returns:
            expression.ELValueArray: The assignable array value read.
        """
        try:
            self.stream.Require(token.TYPE_LPAREN)
            exp_list = self._ReadExpList()
            self.stream.Require(token.TYPE_RPAREN)
            return expression.ELValueArray(tok, exp_list)
        except Exception as e:
            raise exception.ParserException('array subscript', e)

    def _ReadLValueArrayList(self):
        """Reads a list of assignable array values.

        [lvalue-array-list] ::= [lvalue-array] [lvalue-array-list-rest]
        [lvalue-array-list-rest] ::= @ | , [lvalue-array-list]

        Returns:
            list of expression.ELValueArray: The array of values read.
        """
        vars = []
        try:
            vars.append(self._ReadLValueArray(self.stream.RequireId()))
            while self.stream.Peek().IsType(token.TYPE_COMMA):
                self.stream.Get()
                vars.append(self._ReadLValueArray(self.stream.RequireId()))
            return vars
        except Exception as e:
            raise exception.ParserException('array list', e)

    def _ReadNew(self):
        """Reads a NEW statement.

        [new] ::= NEW

        Returns:
            statement.SNew: The statement read.
        """
        try:
            self.stream.RequireKeyword('NEW')
            return statement.SNew()
        except Exception as e:
            raise exception.ParserException('NEW', e)

    def _ReadNext(self):
        """Reads a NEXT statement.

        [next] ::= NEXT | NEXT [lvalue]

        Returns:
            statement.SNext: The statement read.
        """
        try:
            self.stream.RequireKeyword('NEXT')
            if self.stream.Peek().IsId():
                return statement.SNext(self._ReadLValue())
            else:
                return statement.SNext()
        except Exception as e:
            raise exception.ParserException('NEXT', e)

    def _ReadOn(self):
        """Reads an ON-GOTO or ON-GOSUB statement.

        [on-goto]  ::= ON [exp] GOTO [line-list]
        [on-gosub] ::= ON [exp] GOSUB [line-list]

        Returns:
            statement.Statement: The statement read.
        """
        try:
            self.stream.RequireKeyword('ON')
            index_exp = self._ReadExp()
            if self.stream.Peek().IsKeyword('GOTO'):
                self.stream.Get()
                return statement.SOnGoto(index_exp, self._ReadExpList())
            elif self.stream.Peek().IsKeyword('GOSUB'):
                self.stream.Get()
                return statement.SOnGosub(index_exp, self._ReadExpList())
            else:
                raise exception.ParserException('ON')
        except Exception as e:
            raise exception.ParserException('ON', e)

    def _ReadPause(self):
        """Reads a PAUSE statement.

        [pause] ::= PAUSE [exp]

        Returns:
            statement.SPause: The statement read.
        """
        try:
            self.stream.RequireKeyword('PAUSE')
            return statement.SPause(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('PAUSE', e)

    def _ReadPrint(self):
        """Reads a PRINT statement.

        [print] ::= PRINT [print-list]

        Returns:
            statement.SPrint: The statement read.
        """
        try:
            self.stream.RequireKeyword('PRINT')
        except Exception as e:
            raise exception.ParserException('PRINT', e)

    def _ReadPrintList(self):
        """Reads a list of PrintItem objects.

        [print-list] ::= @ | [exp] | [exp] ; [print-list] | [exp] , [print-list]

        Returns:
            list of parser.PrintItem: The PrintItem objects read.
        """
        items = []
        try:
            while not self.stream.AtTerminator():
                exp = self._ReadExp()
                tok = self.stream.Peek()
                if self.stream.AtTerminator():
                    items.append(
                        print_item.PrintItem(exp, print_item.TYPE_FINAL))
                elif tok.IsType(token.TYPE_SEMICOLON):
                    items.append(
                        print_item.PrintItem(exp, print_item.TYPE_SEMICOLON))
                elif tok.IsType(token.TYPE_COMMA):
                    items.append(
                        print_item.PrintItem(exp, print_item.TYPE_COMMA))
        except Exception as e:
            raise exception.ParserException('PRINT', e)
        return items

    def _ReadRandomize(self):
        """Reads a RANDOMIZE statement.

        [randomize] ::= RANDOMIZE [exp]

        Returns:
            statement.SRandomize: The statement read.
        """
        try:
            self.stream.RequireKeyword('RANDOMIZE')
            return statement.SRandomize(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('RANDOMIZE', e)

    def _ReadRange(self):
        """Reads a range of line numbers.

        [range] ::= @ | [INT] | - [INT] | [INT] - | [INT] - [INT]

        Returns:
            runtime.LineRange: The range of line numbers read.
        """
        start = 0
        try:
            # Handle the @ case.
            tok = self.stream.Peek()
            if not (tok.IsType(token.TYPE_INT) or tok.IsType(token.TYPE_MINUS)):
                return runtime.LineRange(start, sys.maxint)

            # Establish the beginning of the range.
            if tok.IsType(token.TYPE_INT):
                start = self.stream.Get().value
                tok = self.stream.Peek()

                # Handle the [INT] case.
                if not tok.IsType(token.TYPE_MINUS):
                    return runtime.LineRange(start, start)

            # Read the -
            self.stream.Get()
            tok = self.stream.Peek()

            # Establish the end of the range.
            if tok.IsType(token.TYPE_INT):
                return runtime.LineRange(start, self.stream.Get().value)
            else:
                return runtime.LineRange(start, sys.maxint)

        except Exception as e:
            raise exception.ParserException('line range', e)

    def _ReadRead(self):
        """Reads a READ statement.

        [read] ::= READ [lvalue-list]

        Returns:
            statement.SRead: The statement read.
        """
        try:
            self.stream.RequireKeyword('READ')
            return statement.SRead(self._ReadLValueList())
        except Exception as e:
            raise exception.ParserException('READ', e)

    def _ReadRemove(self):
        """Reads a REMOVE statement.

        [remove] ::= REMOVE [exp]

        Returns:
            statement.SRemove: The statement read.
        """
        try:
            self.stream.RequireKeyword('REMOVE')
            return statement.SRemove(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('REMOVE', e)

    def _ReadRenum(self):
        """Reads a RENUM statement.

        [renum] ::= RENUM [range] TO [INT] | RENUM [range] TO [INT] , [INT]

        Returns:
            statement.SRenum: The statement read.
        """
        try:
            # Read the basic version.
            self.stream.RequireKeyword('RENUM')
            ran = self._ReadRange()
            self.stream.RequireKeyword('TO')
            start = self.stream.Require(token.TYPE_INT).value

            # See if we have an increment as well.
            if self.stream.Peek().IsType(token.TYPE_COMMA):
                self.stream.Get()
                inc = self.stream.Require(token.TYPE_INT).value
                return statement.SRenum(ran, start, inc)
            else:
                return statement.SRenum(ran, start)

        except Exception as e:
            raise exception.ParserException('RENUM', e)

    def _ReadRestore(self):
        """Reads a RESTORE statement.

        [restore] ::= RESTORE | RESTORE [exp]

        Returns:
            statement.SRestore: The statement read.
        """
        try:
            self.stream.RequireKeyword('RESTORE')
            if self.stream.AtTerminator():
                return statement.SRestore()
            else:
                return statement.SRestore(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('RESTORE', e)

    def _ReadReturn(self):
        """Reads a RETURN statement.

        [return] ::= RETURN

        Returns:
            statement.SReturn: The statement read.
        """
        try:
            self.stream.RequireKeyword('RETURN')
            return statement.SReturn()
        except Exception as e:
            raise exception.ParserException('RETURN', e)

    def _ReadRun(self):
        """Reads a RUN statement.

        [run] ::= RUN | RUN <exp>

        Returns:
            statement.SRun: The statement read.
        """
        try:
            self.stream.RequireKeyword('RUN')
            if self.stream.AtTerminator():
                return statement.SRun()
            else:
                return statement.SRun(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('RUN', e)

    def _ReadSave(self):
        """Reads a SAVE statement.

        [save] ::= SAVE [exp]

        Returns:
            statement.SSave: The statement read.
        """
        try:
            self.stream.RequireKeyword('SAVE')
            return statement.SSave(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('SAVE', e)

    def _ReadStatement(self):
        """Reads a statement.

        [statement] ::= [cls] | [clear] | [color] | [cursor] | [data] |
            [def fn] | [delete] | [end] | [files] | [folder] | [for] | [gosub] |
            [goto] | [if] | [input] | [let] | [list] | [load] | [locate] |
            [new] | [next] | [pause] | [print] | [randomize] | [read] |
            [remove] | [renum] | [restore] | [return] | [run] | [save] |
            [stop] | [assign]

        Returns:
            statement.Statement: The statement read.
        """
        try:
            tok = self.stream.Peek()
            if tok.IsType(token.TYPE_EOF):
                return statement.SNull()
            elif tok.IsType(token.TYPE_COMMENT):
                return self._ReadComment()
            elif tok.IsKeyword('CLEAR'):
                return self._ReadClear()
            elif tok.IsKeyword('CLS'):
                return self._ReadCls()
            elif tok.IsKeyword('COLOR'):
                return self._ReadColor()
            elif tok.IsKeyword('CURSOR'):
                return self._ReadCursor()
            elif tok.IsKeyword('DATA'):
                return self._ReadData()
            elif tok.IsKeyword('DEF'):
                return self._ReadDefFn()
            elif tok.IsKeyword('DELETE'):
                return self._ReadDelete()
            elif tok.IsKeyword('DIM'):
                return self._ReadDim()
            elif tok.IsKeyword('END'):
                return self._ReadEnd()
            elif tok.IsKeyword('FILES'):
                return self._ReadFiles()
            elif tok.IsKeyword('FOLDER'):
                return self._ReadFolder()
            elif tok.IsKeyword('FOLDERS'):
                return self._ReadFolders()
            elif tok.IsKeyword('FOR'):
                return self._ReadFor()
            elif tok.IsKeyword('GET'):
                return self._ReadGet()
            elif tok.IsKeyword('GOSUB'):
                return self._ReadGosub()
            elif tok.IsKeyword('GOTO'):
                return self._ReadGoto()
            elif tok.IsKeyword('IF'):
                return self._ReadIf()
            elif tok.IsKeyword('INPUT'):
                return self._ReadInput()
            elif tok.IsKeyword('LET'):
                return self._ReadLet()
            elif tok.IsKeyword('LIST'):
                return self._ReadList()
            elif tok.IsKeyword('LOAD'):
                return self._ReadLoad()
            elif tok.IsKeyword('LOCATE'):
                return self._ReadLocate()
            elif tok.IsKeyword('NEW'):
                return self._ReadNew()
            elif tok.IsKeyword('NEXT'):
                return self._ReadNext()
            elif tok.IsKeyword('ON'):
                return self._ReadOn()
            elif tok.IsKeyword('PAUSE'):
                return self._ReadPause()
            elif tok.IsKeyword('PRINT'):
                return self._ReadPrint()
            elif tok.IsKeyword('RANDOMIZE'):
                return self._ReadRandomize()
            elif tok.IsKeyword('READ'):
                return self._ReadRead()
            elif tok.IsKeyword('REMOVE'):
                return self._ReadRemove()
            elif tok.IsKeyword('RENUM'):
                return self._ReadRenum()
            elif tok.IsKeyword('RESTORE'):
                return self._ReadRestore()
            elif tok.IsKeyword('RETURN'):
                return self._ReadReturn()
            elif tok.IsKeyword('RUN'):
                return self._ReadRun()
            elif tok.IsKeyword('SAVE'):
                return self._ReadSave()
            elif tok.IsKeyword('STOP'):
                return self._ReadStop()
            elif tok.IsKeyword('TROFF'):
                return self._ReadTroff()
            elif tok.IsKeyword('TRON'):
                return self._ReadTron()
            elif tok.IsKeyword('WEND'):
                return self._ReadWend()
            elif tok.IsKeyword('WHILE'):
                return self._ReadWhile()
            elif tok.IsKeyword('WIDTH'):
                return self._ReadWidth()
            elif tok.IsId():
                return self._ReadAssign()
            else:
                raise exception.ParserException('unknown statement')
        except Exception as e:
            raise exception.ParserException('statement', e)

    def _ReadStatementList(self):
        """Reads a set of statements.

        [statement-list] ::= [statement] [statement-list-rest]
        [statement-list-rest] ::= @ | : [statement-list]

        Returns:
            statement.StatementSet: The statement set read.
        """
        ls = []
        try:
            while True:
                ls.append(self._ReadStatement())
                tok = self.stream.Peek()
                if not tok.IsType(token.TYPE_COLON):
                    return statement.StatementSet(ls)
                self.stream.Get()
        except Exception as e:
            raise exception.ParserException('compound statement', e)

    def _ReadStop(self):
        """Reads a STOP statement.

        [stop] ::= STOP

        Returns:
            statement.SStop: The statement read.
        """
        try:
            self.stream.RequireKeyword('STOP')
            return statement.SSTop()
        except Exception as e:
            raise exception.ParserException('STOP', e)

    def _ReadThenCase(self):
        """Reads the THEN or ELSE case from an IF statement.

        [then-case] ::= [INT] | [statement-list]

        Note that [INT] is translated to GOTO [INT].

        Returns:
            statement.StatementSet: The set of statements read.
        """
        try:
            tok = self.stream.Peek()
            if tok.IsType(token.TYPE_INT):
                return statement.StatementSet(
                    [statement.SGoto(self._ReadInt())])
            else:
                return self._ReadStatementList()
        except Exception as e:
            raise exception.ParserException('THEN/ELSE', e)

    def _ReadTroff(self):
        """Reads a TROFF statement.

        [troff] ::= TROFF

        Returns:
            statement.STroff: The statement read.
        """
        try:
            self.stream.RequireKeyword('TROFF')
            return statement.STroff()
        except Exception as e:
            raise exception.ParserException('TROFF', e)

    def _ReadTron(self):
        """Reads a TRON statement.

        [tron] ::= TRON

        Returns:
            statement.STron: The statement read.
        """
        try:
            self.stream.RequireKeyword('TRON')
            return statement.STron()
        except Exception as e:
            raise exception.ParserException('TRON', e)

    def _ReadWend(self):
        """Reads a WEND statement.

        [wend] ::= WEND

        Returns:
            statement.SWend: The statement read.
        """
        try:
            self.stream.RequireKeyword('WEND')
            return statement.SWend()
        except Exception as e:
            raise exception.ParserException('WEND', e)

    def _ReadWhile(self):
        """Reads a WHILE statement.

        [while] ::= WHILE [exp]

        Returns:
            statement.SWhile: The statement read.
        """
        try:
            self.stream.RequireKeyword('WHILE')
            return statement.SWhile(self._ReadExp())
        except Exception as e:
            raise exception.ParserException('WHILE', e)

    def _ReadWidth(self):
        """Reads a WIDTH statement.

        [width] ::= WIDTH [exp] | WIDTH [exp] , [exp]

        Returns:
            statement.SWidth: The statement read.
        """
        try:
            self.stream.RequireKeyword('WIDTH')
            width_exp = self._ReadExp()
            if self.stream.Peek().IsType(token.TYPE_COMMA):
                self.stream.Get()
                return statement.SWidth(width_exp, self._ReadExp())
            else:
                return statement.SWidth(width_exp)
        except Exception as e:
            raise exception.ParserException('WIDTH', e)
