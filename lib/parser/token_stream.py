class TokenStream:
    """Provides a stream abstraction for tokens in the BASIC language."""

    def __init__(self, buffer):
        """Initializes based on a string to tokenize."""
        self.buffer = buffer
        self.offset = 0   # current offset within the buffer
        self.peek = None  # a single buffered token to peek at

    def AtTerminator(self):
        """Checks if the stream is at a statement terminator.
        
        Statement terminators include EOF, ELSE, and a colon.
        """
        token = self.Peek()
        return (token.IsType(token.TYPE_EOF) or
                token.IsType(token.TYPE_COLON) or
                token.IsKeyword('ELSE'))

    def EOF(self):
        """Checks if the stream is at its end."""
        return (self.offset >= len(self.buffer))

    def Get(self):
        """Return the next token in the stream.
        
        This will advance the state of the stream.  Use Peek instead for a read
        without side-effects.
        
        Returns:
            parser.Token: The next token.
        """
        if self.peek:
            token = self.peek
            self.peek = None
            return token
        return self._ReadToken()

    def Peek(self):
        """Returns the next token in the stream without advancing the pointer.

        This will not advance the state of the stream.  Use Get instead for a
        read with side-effects.

        Returns:
            parser.Token: The next token.
        """
        if not self.peek:
            self.peek = self._ReadToken()
        return self.peek

    def RequireId(self):
        """Reads the next token in the stream, which must be an ID token type.

        Returns:
            parser.Token: The next token.

        Raises:
            runtime.TokenException if the token is not an ID type.
        """
        token = self.Get()
        if token.IsId():
            return token
        raise runtime.TokenException('Unexpected input "%s"' % str(token))

    def RequireInt(self):
        """Reads the next token in the stream, which must be an integer type.

        Returns:
            parser.Token: The next token.

        Raises:
            runtime.TokenException if the token is not an integer type.
        """
        token = self.Get()
        if token.IsInt():
            return token
        raise runtime.TokenException('Unexpected input "%s"' % str(token))

    def RequireKeyword(self, keyword):
        """Reads the next token in the stream, which must be the given keyword.

        Args:
            keyword (str): The keyword to match.

        Returns:
            parser.Token: The next token.

        Raises:
            runtime.TokenException if the token is not the given keyword.
        """
        token = self.Get()
        if token.IsType(token.TYPE_KEYWORD) and token.value == keyword:
            return token
        raise runtime.TokenException('Unexpected input "%s"' % str(token))

    def Require(self, type):
        """Reads the next token in the stream, which must match the given type.

        Args:
            type (token.TYPE_*): The type to match.

        Returns:
            parser.Token: The next token.

        Raises:
            runtime.TokenException in the token is not of the required type.
        """
        token = self.Get()
        if token.type == type:
            return token
        raise exception.TokenException('Unexpected input "%s"' % str(token))

    def Reset(self):
        """Resets the internal state so that subsequent reads start over."""
        self.offset = 0
        self.peek = None

    # The states of the finite-state machine for reading tokens.
    STATE_INIT      = 1
    STATE_BASE      = 2
    STATE_COLON     = 3
    STATE_COMMA     = 4
    STATE_COMMENT   = 5
    STATE_DIVIDE    = 6
    STATE_EQUAL     = 7
    STATE_FLOAT1    = 8
    STATE_FLOAT2    = 9
    STATE_FLOAT3    = 10
    STATE_GT        = 11
    STATE_ID        = 12
    STATE_INT       = 13
    STATE_INT_BIN   = 14
    STATE_INT_HEX   = 15
    STATE_LPAREN    = 16
    STATE_LT        = 17
    STATE_MINUS     = 18
    STATE_PLUS      = 19
    STATE_POWER     = 20
    STATE_QUESTION  = 21
    STATE_REM1      = 22
    STATE_REM2      = 23
    STATE_REM3      = 24
    STATE_RPAREN    = 25
    STATE_SEMICOLON = 26
    STATE_STRING    = 27
    STATE_TIMES     = 28
    STATE_EOF       = 29
    STATE_ERROR     = 30

    def _IsDigit(self, ch):
        """Checks whether this character is a digit."""
        return ch >= '0' and ch <= '9'
    
    def _IsHex(self, ch):
        """Checks whether this character is a hexadecimal digit."""
        return ((ch >= '0' and ch <= '9') or
                (ch >= 'A' and ch <= 'F') or
                (ch >= 'a' and ch <= 'f'))

    def _IsLetter(self, ch):
        """Checks whether this character is a letter."""
        return (ch >= 'A' and ch <= 'Z') or (ch >= 'a' and ch <= 'z')

    def _IsWhitespace(self, ch):
        """Checks whether this character is whitespace."""
        return ch in (' ', '\t', '\n', '\r', '\f')

    def _ReadToken(self):
        """Reads the next token from the buffer and returns it.
    
        If no more tokens are available, returns the EOF token.
    
        Returns:
            parser.Token: The next token.
        """
        acc = ''
        state = self.STATE_INIT
        ch = None
    
        # Operate the FSM to create a token.
        while True:
            # Get a hold of the next character.
            ch = '\0' if self.Eof() else self.buffer[self.offset]
      
            # Dispatch based on the current state.
            if state == self.STATE_INIT:
                if ch == '0':
                    state = self.STATE_EOF
                elif ch == 'R' or ch == 'r':
                    acc += ch
                    self.offset += 1
                    state = self.STATE_REM1
                elif self._IsLetter(ch):
                    acc += ch
                    self.offset += 1
                    state = self.STATE_ID
                elif self._IsDigit(ch):
                    acc += ch
                    self.offset += 1
                    state = self.STATE_INT
                elif ch == '.':
                    acc += ch
                    self.offset += 1
                    state = self.STATE_FLOAT1
                elif ch == '&':
                    self.offset += 1
                    state = self.STATE_BASE
                elif ch == ':':
                    self.offset += 1
                    state = self.STATE_COLON
                elif ch == ',':
                    self.offset += 1
                    state = self.STATE_COMMA
                elif ch == "'":
                    self.offset += 1
                    state = self.STATE_COMMENT
                elif ch == '/':
                    self.offset += 1
                    state = self.STATE_DIVIDE
                elif ch == '=':
                    self.offset += 1
                    state = self.STATE_EQUAL
                elif ch == '>':
                    self.offset += 1
                    state = self.STATE_GT
                elif ch == '<':
                    self.offset += 1
                    state = self.STATE_LT
                elif ch == '(':
                    self.offset += 1
                    state = self.STATE_LPAREN
                elif ch == '-':
                    self.offset += 1
                    state = self.STATE_MINUS
                elif ch == '+':
                    self.offset += 1
                    state = self.STATE_PLUS
                elif ch == '^':
                    self.offset += 1
                    state = self.STATE_POWER
                elif ch == '?':
                    self.offset += 1
                    state = self.STATE_QUESTION
                elif ch == ')':
                    self.offset += 1
                    state = self.STATE_RPAREN
                elif ch == ';':
                    self.offset += 1
                    state = self.STATE_SEMICOLON
                elif ch == '"':
                    self.offset += 1
                    state = self.STATE_STRING
                elif ch == '*':
                    self.offset += 1
                    state = self.STATE_TIMES
                elif self._IsWhitespace(ch):
                    self.offset += 1
                    state = self.STATE_ERROR

            elif state == self.STATE_ID:
                if self._IsLetter(ch) or self._IsDigit(ch):
                    acc += ch
                    self.offset += 1
                elif ch == '%':
                    acc += ch
                    self.offset += 1
                    return token.Token(token.TYPE_ID_INT, acc)
                elif ch == '$':
                    acc += ch
                    self.offset += 1
                    return token.Token(token.TYPE_ID_STRING, acc)
                else:
                    return token.Token(token.TYPE_ID_FLOAT, acc)

            elif state == self.STATE_BASE:
                if ch == 'B' or ch == 'b':
                    self.offset += 1
                    state = self.STATE_INT_BIN
                elif ch == 'H' or ch == 'h':
                    self.offset += 1
                    state = self.STATE_INT_HEX
                else:
                    state = self.STATE_ERROR
          
            elif state == self.STATE_INT_BIN:
                if ch == '0' or ch == '1':
                    acc += ch
                    self.offset += 1
                else:
                    return token.Token(token.TYPE_INT_BIN, int(acc, 2))

            elif state == self.STATE_INT_HEX:
                if self._IsHex(ch):
                    acc += ch
                    self.offset += 1
                else:
                    return token.Token(token.TYPE_INT_HEX, int(acc, 16))

            elif state == self.STATE_FLOAT1:
                if self._IsDigit(ch):
                    acc += ch
                    self.offset += 1
                elif ch == 'E' or ch == 'e':
                    acc += ch
                    self.offset += 1
                    state = self.STATE_FLOAT2
                else:
                    return token.Token(token.TYPE_FLOAT, float(acc))

            elif state == self.STATE_FLOAT2:
                if ch == '+' or ch == '-' or self._IsDigit(ch):
                    acc += ch
                    self.offset += 1
                    state = self.STATE_FLOAT3
                else:
                    state = self.STATE_ERROR

            elif state == self.STATE_FLOAT3:
                if self._IsDigit(ch):
                    acc += ch
                    self.offset += 1
                else:
                    return token.Token(token.TYPE_FLOAT, float(acc))

            elif state == self.STATE_REM1:
                if ch == 'E' or ch == 'e':
                    acc += ch
                    self.offset += 1
                    state = self.STATE_REM2
                else:
                    state = self.STATE_ID

            elif state == self.STATE_REM2:
                if ch == 'M' or ch == 'm':
                    acc = ''
                    self.offset += 1
                    state = self.STATE_REM3
                else:
                    state = self.STATE_ID

            elif state == self.STATE_REM3:
                if ch == '\0':
                    return token.Token(token.TYPE_COMMENT, acc)
                elif ch == ' ':
                    self.offset += 1
                    state = self.STATE_COMMENT
                else:
                    acc = 'rem'
                    state = self.STATE_ID

            elif state == self.STATE_COMMENT:
                if ch == '\0':
                    return token.Token(token.TYPE_COMMENT, acc)
                else:
                    acc += ch
                    self.offset += 1

            elif state == self.STATE_STRING:
                if ch == '\0':
                    return token.Token(token.TYPE_STRING, acc)
                elif ch == '"':
                    self.offset += 1
                    return token.Token(token.TYPE_STRING, acc)
                else:
                    acc += ch
                    self.offset += 1

            elif state == self.STATE_GT:
                if ch == '=':
                    self.offset += 1
                    return token.Token(token.TYPE_GEQ)
                else:
                    return token.Token(token.TYPE_GT)

            elif state == self.STATE_LT:
                if ch == '=':
                    self.offset += 1
                    return token.Token(token.TYPE_LEQ)
                elif ch == '>':
                    self.offset += 1
                    return token.Token(token.TYPE_NEQUAL)
                else:
                    return token.Token(token.TYPE_LT)

            elif state == self.STATE_COLON:
                return token.Token(token.TYPE_COLON)

            elif state == self.STATE_COMMA:
                return token.Token(token.TYPE_COMMA)

            elif state == self.STATE_DIVIDE:
                return token.Token(token.TYPE_DIVIDE)

            elif state == self.STATE_EQUAL:
                return token.Token(token.TYPE_EQUAL)

            elif state == self.STATE_LPAREN:
                return token.Token(token.TYPE_LPAREN)

            elif state == self.STATE_MINUS:
                return token.Token(token.TYPE_MINUS)

            elif state == self.STATE_PLUS:
                return token.Token(token.TYPE_PLUS)

            elif state == self.STATE_POWER:
                return token.Token(token.TYPE_POWER)

            elif state == self.STATE_QUESTION:
                return token.Token(token.TYPE_KEYWORD, 'PRINT')

            elif state == self.STATE_RPAREN:
                return token.Token(token.TYPE_RPAREN)

            elif state == self.STATE_SEMICOLON:
                return token.Token(token.TYPE_SEMICOLON)

            elif state == self.STATE_TIMES:
                return token.Token(token.TYPE_TIMES)

            elif state == self.STATE_EOF:
                return token.Token(token.TYPE_EOF)
        
            elif state == self.STATE_ERROR:
                raise exception.TokenException(
                    "Unexpected char '%s' at column %d" % (ch, self.offset))
