from tokens import Token
from tokentype import TokenType as TT


class Scanner():
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

    def add_token(token_type, literal=None):
        text = self.source[self.start : self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(Token(TT.EOF, "", None, self.line))
        return tokens

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
