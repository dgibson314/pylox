class Token():
    def __init__(self, _type, lexeme, literal, line):
        self._type = _type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        return f"{self._type} {self.lexeme} {self.literal}"
