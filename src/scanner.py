from tokens import Token
from tokens import TokenType as TT

class Scanner():
    keywords = {
        "and": TT.AND, "class": TT.CLASS, "else": TT.ELSE, "false": TT.FALSE,
        "for": TT.FOR, "fun": TT.FUN, "if": TT.IF, "nil": TT.NIL, "or": TT.OR,
        "print": TT.PRINT, "return": TT.RETURN, "super": TT.SUPER, "this": TT.THIS,
        "true": TT.TRUE, "var": TT.VAR, "while": TT.WHILE
    }

    def __init__(self, source):
        self.source = source
        self.tokens = []

        self.start = 0
        self.current = 0
        self.line = 1

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def add_token(self, token_type, literal=None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def error_token(self, message):
        self.tokens.append(Token(TT.ERROR, message, None, self.line))

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TT.EOF, "", None, self.line))
        return self.tokens

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    @staticmethod
    def is_alpha(c):
        return (c >= 'a' and c <= 'z') or \
               (c >= 'A' and c <= 'Z') or \
                c == '_'

    def is_alphanumeric(self, c):
        return self.is_alpha(c) or self.is_digit(c)

    @staticmethod
    def is_digit(c):
        return c >= '0' and c <= '9'

    def scan_token(self):
        c = self.advance()
        match c:
            case '(': self.add_token(TT.LEFT_PAREN)
            case ')': self.add_token(TT.RIGHT_PAREN)
            case '{': self.add_token(TT.LEFT_BRACE)
            case '}': self.add_token(TT.RIGHT_BRACE)
            case ',': self.add_token(TT.COMMA)
            case '.': self.add_token(TT.DOT)
            case '-': self.add_token(TT.MINUS)
            case '+': self.add_token(TT.PLUS)
            case ';': self.add_token(TT.SEMICOLON)
            case '*': self.add_token(TT.STAR)
            case '!':
                self.add_token(TT.BANG_EQUAL if self.match('=') else TT.BANG)
            case '=':
                self.add_token(TT.EQUAL_EQUAL if self.match('=') else TT.EQUAL)
            case '<':
                self.add_token(TT.LESS_EQUAL if self.match('=') else TT.LESS)
            case '>':
                self.add_token(TT.GREATER_EQUAL if self.match('=') else TT.GREATER)
            case '/':
                if self.match('/'):
                    # A comment goes until the end of the line
                    while (self.peek() != '\n' and not self.is_at_end()):
                        self.advance()
                else:
                    self.add_token(TT.SLASH)
            case ' ' | '\r' | '\t':
                pass
            case '\n':
                self.line += 1
            case '"': self.string()
            case _: 
                if self.is_digit(c):
                    self.number()
                elif self.is_alpha(c):
                    self.identifier()
                else:
                    self.error_token("Unexpected character.")

    def identifier(self):
        while self.is_alphanumeric(self.peek()):
            self.advance()

        text = self.source[self.start : self.current]

        token_type = Scanner.keywords.get(text)
        if token_type is None:
            token_type = TT.IDENTIFIER
        self.add_token(token_type)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        # Look for fractional part
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Consume the "."
            self.advance()

            while self.is_digit(self.peek()):
                self.advance()

        number = float(self.source[self.start : self.current])
        self.add_token(TT.NUMBER, literal=number)

    def string(self):
        while (self.peek() != '"' and not self.is_at_end()):
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self.is_at_end():
            self.error_token("Unterminated string.")
            return

        # The closing "
        self.advance()

        # Trim the surrounding quotes
        string = self.source[self.start+1 : self.current-1]
        self.add_token(TT.STRING, literal=string)

