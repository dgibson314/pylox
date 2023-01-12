from exceptions import RuntimeException


class Environment():
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value):
        self.values[name] = value

    def get(self, name):
        var = self.values.get(name.lexeme)
        if var:
            return var

        # If variable isn't found in this environment, we try the enclosing one
        if self.enclosing:
            return self.enclosing.get(name)

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")

    def assign(self, name, value):
        if name.lexeme in self.values.keys():
            self.define(name.lexeme, value)
            return

        if self.enclosing:
            self.enclosing.assign(name, value)

        raise RuntimeException(name, f"Undefined variable '{name.lexeme}'.")
