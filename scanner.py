from token_type import TokenType as TT
from token import Token

class Scanner():
    keywords = {
        "and": TT.AND, "class": TT.CLASS, "else": TT.ELSE, "false": TT.FALSE,
        "for": TT.FOR, "fun": TT.FUN, "if": TT.IF, "nil": TT.NIL, "or": TT.OR,
        "print": TT.PRINT, "return": TT.RETURN, "super": TT.SUPER, "this": TT.THIS,
        "true": TT.TRUE, "var": TT.VAR, "while": TT.WHILE
    }
    def __init__(self, interpreter, source):
        self.interpreter = interpreter
        self.source = source
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        tokens = []
        while not self.at_end():
            self.start = self.current
            self.scan_token(tokens)

        tokens.append(Token(TT.EOF, "", None, self.line))
        return tokens

    def scan_token(self, tokens):
        c = self.advance()
        match c:
            case "(":
                tokens.append(self.tokenize(TT.LEFT_PAREN))
            case ")":
                tokens.append(self.tokenize(TT.RIGHT_PAREN))
            case "{":
                tokens.append(self.tokenize(TT.LEFT_BRACE))
            case "}":
                tokens.append(self.tokenize(TT.RIGHT_BRACE))
            case ",":
                tokens.append(self.tokenize(TT.COMMA))
            case ".":
                tokens.append(self.tokenize(TT.DOT))
            case "-":
                tokens.append(self.tokenize(TT.MINUS))
            case "+":
                tokens.append(self.tokenize(TT.PLUS))
            case ";":
                tokens.append(self.tokenize(TT.SEMICOLON))
            case "*":
                tokens.append(self.tokenize(TT.STAR))
            case "!":
                tokens.append(self.tokenize(TT.BANG_EQUAL if self._match("=") else TT.BANG))
            case "=":
                tokens.append(self.tokenize(TT.EQUAL_EQUAL if self._match("=") else TT.EQUAL))
            case "<":
                tokens.append(self.tokenize(TT.LESS_EQUAL if self._match("=") else TT.LESS))
            case ">":
                tokens.append(self.tokenize(TT.GREATER_EQUAL if self._match("=") else TT.GREATER))
            case "/":
                if self._match("/"):
                    while (self.peek() != "\n" and not self.at_end()):
                        self.advance()
                else:
                    tokens.append(tokenize(TT.SLASH))
            case " " | "\r" | "\t":
                pass
            case "\n":
                self.line += 1
            case '"':
                tokens.append(self.handle_string())

            case _ :
                if c.isnumeric():
                    tokens.append(self.handle_number())
                elif c.isalpha():
                    tokens.append(self.handle_identifier())
                else:
                    self.interpreter.error(self.line, "Unexpected character.")

    def handle_string(self):
        # Consume body of string
        while (self.peek() != '"' and not self.at_end()):
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.at_end():
            self.interpreter.error(self.line, "Unterminated string.")
            return

        # The closing ".
        self.advance()

        # Trim the surrounding quotes
        string = self.source[self.start+1 : self.current-1]
        return self.tokenize(TT.STRING, literal=string)

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
        return self.tokenize(TT.NUMBER, literal=number)

    def handle_identifier(self):
        while (self.peek()).isalnum():
            self.advance()

        text = self.source[self.start:self.current]
        token_type = Scanner.keywords.get(text)
        if token_type is None:
            token_type = TT.IDENTIFIER
        return self.tokenize(token_type)

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

    def tokenize(self, token_type, literal=None):
        text = self.source[self.start:self.current]
        return Token(token_type, text, literal, self.line)

    def at_end(self):
        return (self.current >= len(self.source))
