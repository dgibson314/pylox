from src.lox_token import Token
from src.token_type import TokenType as TT

class Scanner():
    keywords = {
        "and": TT.AND, "class": TT.CLASS, "else": TT.ELSE, "false": TT.FALSE,
        "for": TT.FOR, "fun": TT.FUN, "if": TT.IF, "nil": TT.NIL, "or": TT.OR,
        "print": TT.PRINT, "return": TT.RETURN, "super": TT.SUPER, "this": TT.THIS,
        "true": TT.TRUE, "var": TT.VAR, "while": TT.WHILE
    }
    def __init__(self, runtime, source):
        self.runtime = runtime
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while not self.at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TT.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        match c:
            case "(":
                self.add_token(TT.LEFT_PAREN)
            case ")":
                self.add_token(TT.RIGHT_PAREN)
            case "{":
                self.add_token(TT.LEFT_BRACE)
            case "}":
                self.add_token(TT.RIGHT_BRACE)
            case ",":
                self.add_token(TT.COMMA)
            case ".":
                self.add_token(TT.DOT)
            case "-":
                self.add_token(TT.MINUS)
            case "+":
                self.add_token(TT.PLUS)
            case ";":
                self.add_token(TT.SEMICOLON)
            case "*":
                self.add_token(TT.STAR)
            case "!":
                self.add_token(TT.BANG_EQUAL if self._match("=") else TT.BANG)
            case "=":
                self.add_token(TT.EQUAL_EQUAL if self._match("=") else TT.EQUAL)
            case "<":
                self.add_token(TT.LESS_EQUAL if self._match("=") else TT.LESS)
            case ">":
                self.add_token(TT.GREATER_EQUAL if self._match("=") else TT.GREATER)
            case "/":
                if self._match("/"):
                    while (self.peek() != "\n" and not self.at_end()):
                        self.advance()
                else:
                    self.add_token(TT.SLASH)
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                self.handle_string()

            case _ :
                if c.isnumeric():
                    self.handle_number()
                elif c.isalpha():
                    self.handle_identifier()
                else:
                    self.runtime.error(self.line, f"Unexpected character: {c}.")

    def handle_string(self):
        # Consume body of string
        while (self.peek() != '"' and not self.at_end()):
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.at_end():
            self.runtime.error(self.line, "Unterminated string.")
            return

        # The closing ".
        self.advance()

        # Trim the surrounding quotes
        string = self.source[self.start+1 : self.current-1]
        return self.add_token(TT.STRING, literal=string)

    def handle_number(self):
        # Consume first half of number (before decimal point)
        while (self.peek()).isnumeric():
            self.advance()

        # Look for decimal point
        if (self.peek() == "." and (self.peek_next()).isnumeric()):
            # Consume the "."
            self.advance()

            while (self.peek()).isnumeric():
                self.advance()
        
        number = float(self.source[self.start:self.current])
        return self.add_token(TT.NUMBER, literal=number)

    def handle_identifier(self):
        while (self.peek()).isalnum():
            self.advance()

        text = self.source[self.start:self.current]
        token_type = Scanner.keywords.get(text)
        if token_type is None:
            token_type = TT.IDENTIFIER
        return self.add_token(token_type)

    def advance(self):
        # Consumes the current character in the source file and returns it
        self.current += 1
        return self.source[self.current-1]

    def peek(self):
        # Returns current character but does not consume it
        if self.at_end():
            return "\0"
        return self.source[self.current]

    def peek_next(self):
        if (self.current + 1 >= len(self.source)):
            return "\0"
        return self.source[self.current + 1]

    def _match(self, expected):
        # Only consumes current character if it's equal to expected
        if self.peek() == expected:
            self.current += 1
            return True
        return False

    def add_token(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, text, literal, self.line))

    def at_end(self):
        return (self.current >= len(self.source))
