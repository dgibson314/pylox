from src.exceptions import RuntimeException
from src.lox_callable import LoxCallable


class LoxClass(LoxCallable):
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name

    def __call__(self, interpreter, arguments):
        return LoxInstance(self)

    def arity(self):
        return 0

    def find_method(self, name):
        return self.methods.get(name, None)


class LoxInstance():
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def __str__(self):
        return f"{self.klass.name} instance"

    def get(self, name):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]

        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise RuntimeException(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name, value):
        self.fields[name.lexeme] = value
