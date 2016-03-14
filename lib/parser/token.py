# The token type are defined at top level for the convenience of external
# packages.
TYPE_EOF       = 1
TYPE_COLON     = 2
TYPE_COMMA     = 3
TYPE_COMMENT   = 4
TYPE_DIVIDE    = 5
TYPE_EQUAL     = 6
TYPE_FLOAT     = 7
TYPE_FUNCTION  = 8
TYPE_GEQ       = 9
TYPE_GT        = 10
TYPE_ID_FLOAT  = 11
TYPE_ID_INT    = 12
TYPE_ID_STRING = 13
TYPE_INT       = 14
TYPE_INT_BIN   = 15
TYPE_INT_HEX   = 16
TYPE_KEYWORD   = 17
TYPE_LEQ       = 18
TYPE_LPAREN    = 19
TYPE_LT        = 20
TYPE_MINUS     = 21
TYPE_NEQUAL    = 22
TYPE_PLUS      = 23
TYPE_POWER     = 24
TYPE_RPAREN    = 25
TYPE_SEMICOLON = 26
TYPE_STRING    = 27
TYPE_TIMES     = 28


class Token:
    """Encapsulates individual BASIC tokens."""

    def __init__(self, type, value=None):
        self.type = type
        self.value = value

        if self.value:
            # Promote ID token if possible.
            if self.type in (TYPE_ID_FLOAT, TYPE_ID_STRING):
                id = self.value.upper()

                # Try keywords first.
                if id in self.KEYWORDS:
                    this.type = TYPE_KEYWORD
                    this.value = id
                    return
                
                # Try functions second.
                if id in self.FUNCTIONS:
                    this.type = TYPE_FUNCTION
                    this.value = id
                    return

            # If this is an actual ID, force it into lowercase.
            if self.IsId():
                self.value = self.value.lower()

    # The set of valid function names.
    FUNCTIONS = set((
        'ABS', 'ACOS', 'ASC', 'ASIN', 'ATAN',
        'ATAN2', 'BIN$', 'CHR$', 'COS', 'DATE$',
        'EXP', 'HEX$', 'INSTR', 'INT', 'LEFT$',
        'LEN', 'LOG', 'LOOK', 'MID$', 'POS',
        'RIGHT$', 'RND', 'SGN', 'SIN', 'SIZE',
        'SPACE$', 'SQR', 'STR$', 'STRING$', 'TAB',
        'TAN', 'TIME$', 'VAL',
    ))

    # The set of valid keywords.
    KEYWORDS = set((
        'AND', 'CLEAR', 'CLS', 'COLOR', 'CURSOR',
        'DATA', 'DEF', 'DELETE', 'DIM', 'ELSE',
        'END', 'FILES', 'FOLDER', 'FOLDERS', 'FOR',
        'GET', 'GOSUB', 'GOTO', 'IF', 'INPUT',
        'LET', 'LIST', 'LOAD', 'LOCATE', 'MOD',
        'NEW', 'NEXT', 'NOT', 'PAUSE', 'PRINT',
        'OFF', 'ON', 'OR', 'RANDOMIZE', 'READ',
        'REMOVE', 'RENUM', 'RESTORE', 'RETURN', 'RUN',
        'SAVE', 'STEP', 'STOP', 'THEN', 'TO',
        'TROFF', 'TRON', 'WEND', 'WHILE', 'WIDTH',
    ))

    def IsFn(self):
        """Checks whether this token is a reference to an FN function."""
        return (self.IsId() and
                len(self.value) >= 3 and
                self.value[0:2] == 'fn')

    def IsId(self):
        """Checks whether this token is one of the ID types."""
        return self.type in (TYPE_ID_FLOAT, TYPE_ID_INT, TYPE_ID_STRING)

    def IsInt(self):
        """Checks whether this token is one of the integer types."""
        return self.type in (TYPE_INT, TYPE_INT_BIN, TYPE_INT_HEX)

    def IsKeyword(self, keyword):
        """Checks whether this token matches the given keyword."""
        return self.type == TYPE_KEYWORD and self.value == keyword

    def IsType(self, type):
        """Checks whether this token is of the given type."""
        return self.type == type

    def Debug(self):
        """Renders this token as a debugging string that ids the token type."""
        if self.type == TYPE_EOF:
            return ''
        elif self.type == TYPE_COLON:
            return '<COLON>'
        elif self.type == TYPE_COMMA:
            return '<COMMA>'
        elif self.type == TYPE_COMMENT:
            return '<COMMENT>'
        elif self.type == TYPE_DIVIDE:
            return '<DIVIDE>'
        elif self.type == TYPE_EQUAL:
            return '<EQUAL>'
        elif self.type == TYPE_FLOAT:
            return '<FLOAT:%f>' % self.value
        elif self.type == TYPE_GEQ:
            return '<GEQ>'
        elif self.type == TYPE_GT:
            return '<GT>'
        elif self.type == TYPE_ID_FLOAT:
            return '<ID_FLOAT:%s>' % self.value
        elif self.type == TYPE_ID_INT:
            return '<ID_INT:%s>' % self.value
        elif self.type == TYPE_ID_STRING:
            return '<ID_STRING:%s>' % self.value
        elif self.type == TYPE_INT:
            return '<INT:%d>' % self.value
        elif self.type == TYPE_INT_BIN:
            return '<BIN:%s>' % bin(self.value)
        elif self.type == TYPE_INT_HEX:
            return '<HEX:%s>' % hex(self.value)
        elif self.type == TYPE_KEYWORD:
            return '<%s>' % self.value
        elif self.type == TYPE_LEQ:
            return '<LEQ>'
        elif self.type == TYPE_LPAREN:
            return '<LPAREN>'
        elif self.type == TYPE_LT:
            return '<LT>'
        elif self.type == TYPE_MINUS:
            return '<MINUS>'
        elif self.type == TYPE_NEQUAL:
            return '<NEQUAL>'
        elif self.type == TYPE_PLUS:
            return '<PLUS>'
        elif self.type == TYPE_POWER:
            return '<POWER>'
        elif self.type == TYPE_RPAREN:
            return '<RPAREN>'
        elif self.type == TYPE_SEMICOLON:
            return '<SEMICOLON>'
        elif self.type == TYPE_STRING:
            return '<STRING:"%s">' % self.value
        elif self.type == TYPE_TIMES:
            return '<TIMES>'
        else:
            return '<ERROR>'

    def __str__(self):
        """Renders this token as a string."""
        if self.type == TYPE_EOF:
            return ''
        elif self.type == TYPE_COLON:
            return ':'
        elif self.type == TYPE_COMMA:
            return ','
        elif self.type == TYPE_COMMENT:
            return 'REM ' + self.value
        elif self.type == TYPE_DIVIDE:
            return '/'
        elif self.type == TYPE_EQUAL:
            return '='
        elif self.type == TYPE_FLOAT:
            return str(self.value)
        elif self.type == TYPE_GEQ:
            return '>='
        elif self.type == TYPE_GT:
            return '>'
        elif self.type == TYPE_ID_FLOAT:
            return self.value.lower()
        elif self.type == TYPE_ID_INT:
            return self.value.lower()
        elif self.type == TYPE_ID_STRING:
            return self.value.lower()
        elif self.type == TYPE_INT:
            return str(self.value)
        elif self.type == TYPE_INT_BIN:
            return '&B' + bin(self.value)[2:]
        elif self.type == TYPE_INT_HEX:
            return '&H' + hex(self.value)[2:]
        elif self.type == TYPE_KEYWORD:
            return self.value
        elif self.type == TYPE_LEQ:
            return '<='
        elif self.type == TYPE_LPAREN:
            return '('
        elif self.type == TYPE_LT:
            return '<'
        elif self.type == TYPE_MINUS:
            return '-'
        elif self.type == TYPE_NEQUAL:
            return '<>'
        elif self.type == TYPE_PLUS:
            return '+'
        elif self.type == TYPE_RPAREN:
            return ')'
        elif self.type == TYPE_SEMICOLON:
            return ';'
        elif self.type == TYPE_STRING:
            return '"%s"' % self.value
        elif self.type == TYPE_TIMES:
            return '*'
        else:
            return None
